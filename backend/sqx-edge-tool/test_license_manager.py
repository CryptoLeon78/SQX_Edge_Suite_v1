import json
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import Mock, patch

from core import license_manager
from tools.license_issue import build_license_payload, issue_license
from tools.license_signer import sign_license_payload


# Test-only RSA key. Production private keys must never be committed.
TEST_PRIVATE_KEY = {
    "kty": "RSA",
    "kid": "sqx-test-key",
    "alg": "RS256",
    "n": "vH_X9apBc5eI6SIn0h-hURiP5gumuMdncTnz6N4zYRb02jUzwbEjfQr4kuQ49T_JWpUySPFlTgatTF3L89CsFmm97FfB3fPe0xlujJPnJKgXku5emo_9ff8dUPn7eGoW2PCmSRe2qm6GhjY6Bsi1mbjWJUcDcs_L6IHzXMR_-w0",
    "e": "AQAB",
    "d": "He1aNzm5vIVxijoPAnBdJ0f0CL0O0kVuae6eh_lHRQHlDAPoXLcoAEFOp9uuI1nmOQh4_FW_FL1ApGA78lDOEVbwz4vKW9FZ8M_sQWwhtcQaeYPqdtG_PDUlViq9IiGqRQJTPD62hon9E-LNvJ-xLpTR1MY7Znvo9hRGT7GUqk0",
}


class LicenseManagerTestCase(unittest.TestCase):
    def product(self, license_file: str = "config/license.json"):
        product = license_manager.load_product_manifest()
        product["build"]["channel"] = "free"
        product["build"]["defaultPlan"] = "free"
        product["licensing"]["licenseFile"] = license_file
        product["licensing"]["signatureMode"] = "rsa_sha256_pkcs1_v1_5"
        product["licensing"]["publicKey"] = {
            key: TEST_PRIVATE_KEY[key]
            for key in ("kty", "kid", "alg", "n", "e")
        }
        return product

    def signed_payload(self, **overrides):
        payload = {
            "schema_version": 1,
            "license_id": "LIC-TEST-001",
            "customer_name": "Test Customer",
            "plan": "pro_monthly",
            "issued_at": "2026-05-01",
            "expires_at": "2026-06-01",
        }
        payload.update(overrides)
        return sign_license_payload(payload, TEST_PRIVATE_KEY)

    def test_signed_pro_license_activates_pro_features(self):
        product = self.product()
        payload = self.signed_payload()

        with patch.object(license_manager, "load_product_manifest", return_value=product):
            status = license_manager.preview_license_payload(payload, today=date(2026, 5, 5))

        self.assertTrue(status["ok"])
        self.assertTrue(status["active"])
        self.assertTrue(status["signature_valid"])
        self.assertEqual(status["state"], "pro_active")
        self.assertIn("project_generator.generate", status["features"])
        self.assertIn("strategy_cleaner.apply", status["features"])

    def test_tampered_license_is_rejected(self):
        product = self.product()
        payload = self.signed_payload()
        payload["plan"] = "pro_annual"

        with patch.object(license_manager, "load_product_manifest", return_value=product):
            status = license_manager.preview_license_payload(payload, today=date(2026, 5, 5))

        self.assertFalse(status["ok"])
        self.assertFalse(status["active"])
        self.assertFalse(status["signature_valid"])
        self.assertEqual(status["state"], "invalid")
        self.assertEqual(status["signature_error"], "invalid_signature")

    def test_expired_signed_license_keeps_data_but_disables_pro(self):
        product = self.product()
        payload = self.signed_payload(expires_at="2026-04-01")

        with patch.object(license_manager, "load_product_manifest", return_value=product):
            status = license_manager.preview_license_payload(payload, today=date(2026, 5, 5))

        self.assertTrue(status["ok"])
        self.assertFalse(status["active"])
        self.assertTrue(status["signature_valid"])
        self.assertEqual(status["state"], "expired")
        self.assertNotIn("project_generator.generate", status["features"])

    def test_import_signed_license_writes_config_license_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            license_file = str(Path(tmp) / "license.json")
            product = self.product(license_file=license_file)
            payload = self.signed_payload()
            with patch.object(license_manager, "load_product_manifest", return_value=product):
                result = license_manager.import_license_payload(payload, today=date(2026, 5, 5))

            self.assertTrue(result["ok"])
            self.assertTrue(result["installed"])
            written = json.loads(Path(license_file).read_text(encoding="utf-8"))
            self.assertEqual(written["license_id"], "LIC-TEST-001")
            self.assertIn("signature", written)

    def test_manual_license_issuer_creates_signed_pro_license(self):
        with tempfile.TemporaryDirectory() as tmp:
            private_key_path = Path(tmp) / "test_private_key.json"
            out_path = Path(tmp) / "license_signed_customer.json"
            private_key_path.write_text(json.dumps(TEST_PRIVATE_KEY), encoding="utf-8")
            args = Mock(
                private_key=private_key_path,
                out=out_path,
                customer_name="Manual Customer",
                customer_email="manual@example.com",
                customer_id="CUS-001",
                order_id="ORDER-001",
                plan="pro_annual",
                license_id="LIC-MANUAL-001",
                issued_at="2026-05-06",
                expires_at="",
                duration_days=None,
                no_expires=False,
                machine_limit=1,
                support_level="priority",
                grace_days=7,
                distribution_channel="",
                tester_marker="",
                redistribution_allowed=False,
                notes="paid beta",
            )

            payload = build_license_payload(args, today=date(2026, 5, 6))
            signed = issue_license(args, today=date(2026, 5, 6))
            product = self.product()

            self.assertEqual(payload["expires_at"], "2027-05-07")
            self.assertEqual(signed["customer_email"], "manual@example.com")
            self.assertEqual(signed["support_level"], "priority")
            self.assertTrue(out_path.is_file())
            with patch.object(license_manager, "load_product_manifest", return_value=product):
                status = license_manager.preview_license_payload(signed, today=date(2026, 5, 7))
            self.assertEqual(status["state"], "pro_active")

    def test_manual_license_issuer_signs_tester_distribution_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            private_key_path = Path(tmp) / "test_private_key.json"
            out_path = Path(tmp) / "license_signed_tester.json"
            private_key_path.write_text(json.dumps(TEST_PRIVATE_KEY), encoding="utf-8")
            args = Mock(
                private_key=private_key_path,
                out=out_path,
                customer_name="Tester Customer",
                customer_email="tester@example.com",
                customer_id="TL12-T01",
                order_id="TL12-PILOT",
                plan="pro_tester_15",
                license_id="LIC-TL12-T01",
                issued_at="2026-05-12",
                expires_at="",
                duration_days=None,
                no_expires=False,
                machine_limit=1,
                support_level="standard",
                grace_days=0,
                distribution_channel="tester_pilot",
                tester_marker="TL12-T01",
                redistribution_allowed=False,
                notes="tester pilot",
            )

            signed = issue_license(args, today=date(2026, 5, 12))
            product = self.product()

            self.assertEqual(signed["expires_at"], "2026-05-27")
            self.assertEqual(signed["distribution"]["channel"], "tester_pilot")
            self.assertEqual(signed["distribution"]["tester_marker"], "TL12-T01")
            self.assertFalse(signed["distribution"]["redistribution_allowed"])
            with patch.object(license_manager, "load_product_manifest", return_value=product):
                status = license_manager.preview_license_payload(signed, today=date(2026, 5, 13))
            self.assertTrue(status["signature_valid"])
            self.assertEqual(status["distribution"]["tester_marker"], "TL12-T01")

    def test_manual_license_issuer_can_create_non_expiring_tester_license(self):
        with tempfile.TemporaryDirectory() as tmp:
            private_key_path = Path(tmp) / "test_private_key.json"
            out_path = Path(tmp) / "license_signed_tester_no_expiry.json"
            private_key_path.write_text(json.dumps(TEST_PRIVATE_KEY), encoding="utf-8")
            args = Mock(
                private_key=private_key_path,
                out=out_path,
                customer_name="Tester Customer",
                customer_email="tester@example.com",
                customer_id="TL12-T01",
                order_id="TL12-PILOT",
                plan="pro_tester_15",
                license_id="LIC-TL12-T01",
                issued_at="2026-05-31",
                expires_at="",
                duration_days=None,
                no_expires=True,
                machine_limit=1,
                support_level="standard",
                grace_days=0,
                distribution_channel="tester_pilot",
                tester_marker="TL12-T01",
                redistribution_allowed=False,
                notes="tester pilot",
            )

            signed = issue_license(args, today=date(2026, 5, 31))
            product = self.product()

            self.assertNotIn("expires_at", signed)
            self.assertEqual(signed["distribution"]["tester_marker"], "TL12-T01")
            with patch.object(license_manager, "load_product_manifest", return_value=product):
                status = license_manager.preview_license_payload(signed, today=date(2026, 12, 31))
            self.assertTrue(status["active"])
            self.assertEqual(status["state"], "pro_active")

    def test_signed_tester_license_activates_pro_with_distribution_marker(self):
        product = self.product()
        payload = self.signed_payload(
            license_id="LIC-TESTER-001",
            plan="pro_tester_15",
            customer_name="Tester One",
            customer_email="tester@example.com",
            expires_at="2026-05-16",
            machine_limit=1,
            distribution={
                "channel": "tester_pilot",
                "tester_marker": "TL11-TESTER-001",
                "redistribution_allowed": False,
            },
        )

        with patch.object(license_manager, "load_product_manifest", return_value=product):
            status = license_manager.preview_license_payload(payload, today=date(2026, 5, 10))

        self.assertTrue(status["ok"])
        self.assertTrue(status["active"])
        self.assertEqual(status["state"], "pro_active")
        self.assertEqual(status["customer_email"], "tester@example.com")
        self.assertEqual(status["machine_limit"], 1)
        self.assertEqual(status["distribution"]["channel"], "tester_pilot")
        self.assertEqual(status["distribution"]["tester_marker"], "TL11-TESTER-001")
        self.assertFalse(status["distribution"]["redistribution_allowed"])

    def test_tester_profile_without_license_stays_free_locked(self):
        product = self.product()
        product["build"]["channel"] = "tester"
        product["build"]["label"] = "Tester Build"
        product["build"]["defaultPlan"] = "free"
        product["build"]["activationMode"] = "signed_tester_file"

        with patch.object(license_manager, "load_product_manifest", return_value=product):
            with patch.object(license_manager, "load_license_payload", return_value=None):
                status = license_manager.license_status(today=date(2026, 5, 10))

        self.assertTrue(status["ok"])
        self.assertFalse(status["active"])
        self.assertEqual(status["state"], "free")
        self.assertEqual(status["build_channel"], "tester")
        self.assertNotIn("project_generator.generate", status["features"])


if __name__ == "__main__":
    unittest.main()

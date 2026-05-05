import json
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

from core import license_manager
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


if __name__ == "__main__":
    unittest.main()

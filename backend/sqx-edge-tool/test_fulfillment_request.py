import hashlib
import hmac
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

import core.fulfillment_queue as fulfillment_queue
from tools.fulfillment_request import (
    normalize_payload,
    verify_lemon_signature,
)
from tools.relay_bundle import sign_bundle

# Test-only RSA key. Production private keys must never be committed.
TEST_PRIVATE_KEY = {
    "kty": "RSA",
    "kid": "sqx-test-key",
    "alg": "RS256",
    "n": "vH_X9apBc5eI6SIn0h-hURiP5gumuMdncTnz6N4zYRb02jUzwbEjfQr4kuQ49T_JWpUySPFlTgatTF3L89CsFmm97FfB3fPe0xlujJPnJKgXku5emo_9ff8dUPn7eGoW2PCmSRe2qm6GhjY6Bsi1mbjWJUcDcs_L6IHzXMR_-w0",
    "e": "AQAB",
    "d": "He1aNzm5vIVxijoPAnBdJ0f0CL0O0kVuae6eh_lHRQHlDAPoXLcoAEFOp9uuI1nmOQh4_FW_FL1ApGA78lDOEVbwz4vKW9FZ8M_sQWwhtcQaeYPqdtG_PDUlViq9IiGqRQJTPD62hon9E-LNvJ-xLpTR1MY7Znvo9hRGT7GUqk0",
}


def lemon_order_payload(**overrides):
    attrs = {
        "identifier": "ls-order-uuid",
        "order_number": 42,
        "customer_id": 77,
        "user_name": "Cliente Demo",
        "user_email": "cliente@example.com",
        "status": "paid",
        "refunded": False,
        "test_mode": True,
        "first_order_item": {
            "id": 101,
            "order_id": 42,
            "product_id": 10,
            "variant_id": 999,
            "variant_name": "SQX Edge Pro Anual",
            "price": 19900,
            "test_mode": True,
        },
        "urls": {
            "receipt": "https://example.com/receipt",
        },
    }
    attrs.update(overrides)
    return {
        "meta": {
            "event_name": "order_created",
            "webhook_id": "wh_123",
        },
        "data": {
            "type": "orders",
            "id": "123",
            "attributes": attrs,
        },
    }


def lemon_subscription_payload(**overrides):
    attrs = {
        "order_id": 42,
        "customer_id": 77,
        "user_name": "Cliente Suscripcion",
        "user_email": "suscripcion@example.com",
        "status": "active",
        "variant_id": 111,
        "variant_name": "SQX Edge Pro Mensual",
        "renews_at": "2026-06-06T00:00:00Z",
        "ends_at": None,
        "test_mode": True,
    }
    attrs.update(overrides)
    return {
        "meta": {
            "event_name": "subscription_payment_success",
            "webhook_id": "wh_sub_123",
        },
        "data": {
            "type": "subscriptions",
            "id": "sub_123",
            "attributes": attrs,
        },
    }


class FulfillmentRequestTestCase(unittest.TestCase):
    def product(self):
        return {
            "upgrade": {
                "checkout": {
                    "variants": [
                        {
                            "plan": "pro_monthly",
                            "label": "SQX Edge Pro Mensual",
                            "providerVariantId": "111",
                            "licenseDurationDays": 31,
                            "activationLimit": 1,
                        },
                        {
                            "plan": "pro_annual",
                            "label": "SQX Edge Pro Anual",
                            "providerVariantId": "",
                            "licenseDurationDays": 366,
                            "activationLimit": 1,
                        },
                    ]
                }
            }
        }

    def test_verifies_lemon_hmac_signature(self):
        raw = b'{"hello":"world"}'
        secret = "sqx-secret"
        signature = hmac.new(secret.encode("utf-8"), raw, hashlib.sha256).hexdigest()

        self.assertTrue(verify_lemon_signature(raw, signature, secret))
        self.assertFalse(verify_lemon_signature(raw, "bad", secret))

    def test_normalizes_paid_order_to_license_request(self):
        request = normalize_payload(lemon_order_payload(), product=self.product(), today=date(2026, 5, 6))

        self.assertEqual(request["provider"], "Lemon Squeezy")
        self.assertEqual(request["source_event"], "order_created")
        self.assertEqual(request["order_id"], "ls-order-uuid")
        self.assertEqual(request["customer_email"], "cliente@example.com")
        self.assertEqual(request["plan"], "pro_annual")
        self.assertEqual(request["license_duration_days"], 366)
        self.assertTrue(request["eligible_for_fulfillment"])
        self.assertEqual(request["fulfillment_status"], "ready_for_license")

    def test_refunded_order_is_not_eligible(self):
        request = normalize_payload(
            lemon_order_payload(refunded=True, refunded_at="2026-05-06T00:00:00Z"),
            product=self.product(),
            today=date(2026, 5, 6),
        )

        self.assertFalse(request["eligible_for_fulfillment"])
        self.assertEqual(request["fulfillment_status"], "ignored")

    def test_subscription_payment_success_is_eligible(self):
        request = normalize_payload(
            lemon_subscription_payload(),
            product=self.product(),
            today=date(2026, 5, 6),
        )

        self.assertEqual(request["source_event"], "subscription_payment_success")
        self.assertEqual(request["plan"], "pro_monthly")
        self.assertEqual(request["license_duration_days"], 31)
        self.assertTrue(request["eligible_for_fulfillment"])
        self.assertEqual(request["fulfillment_status"], "ready_for_license")

    def test_cli_writes_normalized_request_with_signature(self):
        with tempfile.TemporaryDirectory() as tmp:
            payload_path = Path(tmp) / "webhook_event_test.json"
            out_path = Path(tmp) / "fulfillment_request_test.json"
            raw = json.dumps(lemon_order_payload()).encode("utf-8")
            payload_path.write_bytes(raw)
            secret = "sqx-secret"
            signature = hmac.new(secret.encode("utf-8"), raw, hashlib.sha256).hexdigest()

            result = subprocess.run(
                [
                    sys.executable,
                    str(Path(__file__).resolve().parent / "tools" / "fulfillment_request.py"),
                    "--payload",
                    str(payload_path),
                    "--out",
                    str(out_path),
                    "--signature",
                    signature,
                    "--secret",
                    secret,
                ],
                text=True,
                capture_output=True,
                timeout=20,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

            written = json.loads(out_path.read_text(encoding="utf-8"))
            self.assertEqual(written["plan"], "pro_annual")

    def test_relay_bundle_cli_writes_signed_bundle(self):
        with tempfile.TemporaryDirectory() as tmp:
            payload_path = Path(tmp) / "webhook_event_test.json"
            out_path = Path(tmp) / "relay_bundle_test.json"
            raw = json.dumps(lemon_order_payload()).encode("utf-8")
            payload_path.write_bytes(raw)

            result = subprocess.run(
                [
                    sys.executable,
                    str(Path(__file__).resolve().parent / "tools" / "relay_bundle.py"),
                    "--payload",
                    str(payload_path),
                    "--out",
                    str(out_path),
                    "--relay-secret",
                    "relay-secret",
                ],
                text=True,
                capture_output=True,
                timeout=20,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            bundle = json.loads(out_path.read_text(encoding="utf-8"))
            self.assertEqual(bundle["provider"], "lemon")
            self.assertIn("Relay signature:", result.stdout)

    @unittest.skipUnless(shutil.which("powershell"), "requires Windows PowerShell (fulfill_from_request.ps1)")
    def test_fulfill_from_request_prepares_delivery(self):
        with tempfile.TemporaryDirectory() as tmp:
            request_path = Path(tmp) / "fulfillment_request_test.json"
            private_key_path = Path(tmp) / "sqx-test_private_key.json"
            zip_path = Path(tmp) / "SQX_Edge_Tool_Portable_TEST.zip"
            out_dir = Path(tmp) / "deliveries"

            request_path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "provider": "Lemon Squeezy",
                        "source_event": "order_created",
                        "provider_event_id": "wh_123",
                        "order_id": "LS-TEST-001",
                        "customer_name": "Cliente Demo",
                        "customer_email": "cliente@example.com",
                        "customer_id": "77",
                        "plan": "pro_monthly",
                        "provider_variant_id": "111",
                        "license_duration_days": 31,
                        "machine_limit": 1,
                        "support_level": "standard",
                        "eligible_for_fulfillment": True,
                        "fulfillment_status": "ready_for_license",
                    }
                ),
                encoding="utf-8",
            )
            private_key_path.write_text(json.dumps(TEST_PRIVATE_KEY), encoding="utf-8")
            zip_path.write_text("portable-zip-placeholder", encoding="ascii")

            result = subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(Path(__file__).resolve().parent / "tools" / "fulfill_from_request.ps1"),
                    "-RequestPath",
                    str(request_path),
                    "-PrivateKey",
                    str(private_key_path),
                    "-ZipPath",
                    str(zip_path),
                    "-OutDir",
                    str(out_dir),
                    "-SupportEmail",
                    "soporte@example.com",
                ],
                text=True,
                capture_output=True,
                timeout=60,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            deliveries = list(out_dir.glob("SQX_delivery_*"))
            self.assertEqual(len(deliveries), 1)
            self.assertTrue((deliveries[0] / "SQX_Edge_Pro_license.json").is_file())
            self.assertTrue((deliveries[0] / "LEEME_PRIMERO.txt").is_file())
            self.assertTrue((deliveries[0] / "delivery_manifest.json").is_file())

    def test_queue_overview_tracks_operator_status_and_attempts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with patch.object(fulfillment_queue, "QUEUE_ROOT", root), \
                    patch.object(fulfillment_queue, "EVENTS_DIR", root / "events"), \
                    patch.object(fulfillment_queue, "REQUESTS_DIR", root / "requests"), \
                    patch.object(fulfillment_queue, "PROCESSED_DIR", root / "processed"):
                fulfillment_queue.ensure_queue_dirs()
                request_path = fulfillment_queue.REQUESTS_DIR / "fulfillment_request_demo.json"
                request_path.write_text(
                    json.dumps(
                        {
                            "request_file": "fulfillment_request_demo.json",
                            "provider_event_id": "wh_demo",
                            "plan": "pro_monthly",
                            "customer_email": "demo@example.com",
                            "eligible_for_fulfillment": True,
                            "fulfillment_status": "ready_for_license",
                            "operator_status": "failed",
                            "attempt_count": 2,
                            "last_error": "zip missing",
                            "stored_at": "2026-05-06T15:00:00",
                        }
                    ),
                    encoding="utf-8",
                )
                (fulfillment_queue.PROCESSED_DIR / "delivery_receipt_demo.json").write_text(
                    json.dumps({"request_file": "fulfillment_request_demo.json", "status": "failed", "attempt_number": 2}),
                    encoding="utf-8",
                )

                overview = fulfillment_queue.queue_overview()
                self.assertEqual(overview["summary"]["failed"], 1)
                self.assertEqual(overview["summary"]["processed_receipts"], 1)
                self.assertEqual(overview["requests"][0]["attempt_count"], 2)

    def test_store_relay_bundle_accepts_signed_payload(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with patch.object(fulfillment_queue, "QUEUE_ROOT", root), \
                    patch.object(fulfillment_queue, "EVENTS_DIR", root / "events"), \
                    patch.object(fulfillment_queue, "REQUESTS_DIR", root / "requests"), \
                    patch.object(fulfillment_queue, "PROCESSED_DIR", root / "processed"):
                fulfillment_queue.ensure_queue_dirs()
                bundle = {
                    "schema_version": 1,
                    "relay_event_id": "relay_001",
                    "relay_source": "trusted_remote_relay",
                    "provider": "lemon",
                    "normalized_request": {
                        "provider": "Lemon Squeezy",
                        "provider_event_id": "wh_777",
                        "order_id": "LS-777",
                        "customer_email": "relay@example.com",
                        "plan": "pro_monthly",
                        "eligible_for_fulfillment": True,
                        "fulfillment_status": "ready_for_license",
                    },
                }
                raw = json.dumps(bundle, sort_keys=True).encode("utf-8")
                signature = sign_bundle(raw, "relay-secret")
                result = fulfillment_queue.store_relay_bundle(raw, signature, "relay-secret")
                self.assertTrue(result["ok"])
                self.assertTrue(result["stored"])
                self.assertEqual(result["request"]["relay_event_id"], "relay_001")
                self.assertEqual(len(list(fulfillment_queue.REQUESTS_DIR.glob("fulfillment_request_*.json"))), 1)

    def test_update_request_status_changes_request_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with patch.object(fulfillment_queue, "QUEUE_ROOT", root), \
                    patch.object(fulfillment_queue, "EVENTS_DIR", root / "events"), \
                    patch.object(fulfillment_queue, "REQUESTS_DIR", root / "requests"), \
                    patch.object(fulfillment_queue, "PROCESSED_DIR", root / "processed"):
                fulfillment_queue.ensure_queue_dirs()
                request_path = fulfillment_queue.REQUESTS_DIR / "fulfillment_request_demo.json"
                request_path.write_text(
                    json.dumps(
                        {
                            "request_file": "fulfillment_request_demo.json",
                            "provider_event_id": "wh_demo",
                            "eligible_for_fulfillment": False,
                            "fulfillment_status": "ignored",
                            "operator_status": "needs_review",
                            "stored_at": "2026-05-06T15:00:00",
                        }
                    ),
                    encoding="utf-8",
                )

                updated = fulfillment_queue.update_request_status(
                    filename="fulfillment_request_demo.json",
                    operator_status="ignored",
                    note="manual skip",
                )
                self.assertEqual(updated["summary"]["operator_status"], "ignored")
                payload = json.loads(request_path.read_text(encoding="utf-8"))
                self.assertEqual(payload["operator_note"], "manual skip")
                self.assertEqual(payload["fulfillment_status"], "ignored_by_operator")


if __name__ == "__main__":
    unittest.main()

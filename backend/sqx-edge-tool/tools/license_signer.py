from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


TOOL_ROOT = Path(__file__).resolve().parents[1]
if str(TOOL_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOL_ROOT))

from core.license_manager import (  # noqa: E402
    DIGESTINFO_SHA256_PREFIX,
    b64url_decode,
    b64url_encode,
    canonical_license_payload,
)


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sign_license_payload(payload: dict, private_key: dict) -> dict:
    if private_key.get("kty") != "RSA":
        raise ValueError("private key must be RSA JSON with n/e/d")
    signed = dict(payload)
    signed["signature_algorithm"] = "RS256"
    signed["public_key_id"] = private_key.get("kid", "")
    signed.pop("signature", None)

    n = int.from_bytes(b64url_decode(str(private_key["n"])), "big")
    d = int.from_bytes(b64url_decode(str(private_key["d"])), "big")
    key_len = (n.bit_length() + 7) // 8
    digest = hashlib.sha256(canonical_license_payload(signed)).digest()
    digest_info = DIGESTINFO_SHA256_PREFIX + digest
    padding_len = key_len - len(digest_info) - 3
    if padding_len < 8:
        raise ValueError("RSA key is too small for RS256 PKCS#1 v1.5")
    encoded = b"\x00\x01" + (b"\xff" * padding_len) + b"\x00" + digest_info
    signature = pow(int.from_bytes(encoded, "big"), d, n).to_bytes(key_len, "big")
    signed["signature"] = b64url_encode(signature)
    return signed


def main() -> int:
    parser = argparse.ArgumentParser(description="Sign SQX Edge offline license JSON with an RSA private key.")
    parser.add_argument("--private-key", required=True, type=Path, help="Private RSA JSON file kept outside the repo.")
    parser.add_argument("--payload", required=True, type=Path, help="Unsigned license JSON payload.")
    parser.add_argument("--out", required=True, type=Path, help="Output signed license JSON.")
    args = parser.parse_args()

    private_key = _load_json(args.private_key)
    payload = _load_json(args.payload)
    signed = sign_license_payload(payload, private_key)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(signed, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Signed license written: {args.out}")
    print(f"License id: {signed.get('license_id')}")
    print(f"Public key id: {signed.get('public_key_id')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

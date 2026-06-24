"""
Guard tests for buyer-build hardening requirements (ADR-0003, H1 and H2).

These tests assert properties that the BUYER artifact (portable ZIP or compiled
.exe) MUST satisfy before any real sale.  Today, package_portable.ps1 copies
product_manifest.json verbatim — so both checks fail on the current artifact.

Both tests are therefore marked xfail with reason "release blocker pendiente"
so that the CI suite stays green while the blocker is unresolved.

When the build pipeline is updated to rewrite the manifest for buyer builds,
remove the @pytest.mark.xfail decorators and the tests will become hard guards.
"""

import json
import pytest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = PROJECT_ROOT / "backend" / "sqx-edge-tool" / "config" / "product_manifest.json"

_BLOCKER = "release blocker pendiente: package_portable.ps1 embarca product_manifest.json sin reescribir channel ni publicKey (ver ADR-0003)"


def _load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


class TestBuyerBuildHardening:

    @pytest.mark.xfail(reason=_BLOCKER, strict=True)
    def test_H1_buyer_artifact_channel_is_not_internal(self):
        """H1: build.channel must not be 'internal' in any buyer artifact.

        The 'internal' channel grants features=['*'], bypassing the entire
        licensing gate.  Buyer builds must use 'free' (or another non-internal
        value) so the license check is actually enforced.
        """
        manifest = _load_manifest()
        channel = manifest["build"]["channel"]
        assert channel != "internal", (
            f"BLOCKER: product_manifest.json ships with build.channel={channel!r}. "
            "Buyer artifacts must set channel='free' before any sale."
        )

    @pytest.mark.xfail(reason=_BLOCKER, strict=True)
    def test_H2_buyer_artifact_public_key_kid_is_not_placeholder(self):
        """H2: licensing.publicKey.kid must not contain 'placeholder' in buyer artifacts.

        A placeholder kid means the embedded public key is a stub.  Any license
        signed with the real production private key will fail signature verification
        in the field.  Replace with the real production key before emitting
        any real license.
        """
        manifest = _load_manifest()
        kid = manifest["licensing"]["publicKey"]["kid"]
        assert "placeholder" not in kid.lower(), (
            f"BLOCKER: product_manifest.json ships with kid={kid!r}. "
            "Replace with the real production public key before any sale."
        )

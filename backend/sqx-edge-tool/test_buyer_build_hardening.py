"""
Guard tests for buyer-build hardening (ADR-0003, H1/H2/H3).

harden_buyer_manifest() is a pure function — no I/O, no side effects — so
tests run against in-memory manifest copies and are always green regardless of
whether the repo manifest is in "internal" channel (dev default) or not.
"""

import copy
import json
import pytest
from pathlib import Path

from core.build_hardening import BuyerBuildError, harden_buyer_manifest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = PROJECT_ROOT / "backend" / "sqx-edge-tool" / "config" / "product_manifest.json"

_PROD_KID = "sqx-prod-2026-06"


def _dev_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _prod_manifest() -> dict:
    """Dev manifest with the placeholder kid swapped for a simulated production kid."""
    m = _dev_manifest()
    m["licensing"]["publicKey"]["kid"] = _PROD_KID
    return m


class TestBuyerBuildHardening:

    def test_H1_harden_sets_channel_free(self):
        """H1: harden_buyer_manifest sets build.channel to 'free'."""
        hardened = harden_buyer_manifest(_prod_manifest())
        assert hardened["build"]["channel"] == "free"

    def test_H2_harden_raises_on_placeholder_kid(self):
        """H2: harden_buyer_manifest raises BuyerBuildError for the placeholder kid."""
        dev = _dev_manifest()
        kid = dev["licensing"]["publicKey"]["kid"]
        assert "placeholder" in kid.lower(), (
            "Precondition: dev manifest must still carry the placeholder kid"
        )
        with pytest.raises(BuyerBuildError, match="placeholder"):
            harden_buyer_manifest(dev)

    def test_H3_harden_does_not_raise_for_prod_kid_and_returns_free(self):
        """H3: with a real production kid, harden_buyer_manifest succeeds and returns channel='free'."""
        hardened = harden_buyer_manifest(_prod_manifest())
        assert hardened["build"]["channel"] == "free"
        assert "placeholder" not in hardened["licensing"]["publicKey"]["kid"].lower()

    def test_harden_does_not_mutate_original(self):
        """harden_buyer_manifest must not modify the manifest passed in."""
        prod = _prod_manifest()
        original_channel = prod["build"]["channel"]
        harden_buyer_manifest(prod)
        assert prod["build"]["channel"] == original_channel

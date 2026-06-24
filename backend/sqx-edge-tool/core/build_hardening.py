import copy


class BuyerBuildError(Exception):
    pass


def harden_buyer_manifest(manifest: dict) -> dict:
    """Return a copy of *manifest* safe for buyer distribution.

    - Sets build.channel to "free".
    - Raises BuyerBuildError if licensing.publicKey.kid contains "placeholder"
      (case-insensitive): a placeholder key cannot verify real licenses, so the
      build is refused rather than silently shipping an unverifiable artifact.

    The original dict is never mutated; dev/repo manifests remain unchanged.
    """
    kid = manifest["licensing"]["publicKey"]["kid"]
    if "placeholder" in kid.lower():
        raise BuyerBuildError(
            f"Cannot package buyer build: licensing.publicKey.kid={kid!r} is a "
            "placeholder. Replace with the real production public key before "
            "emitting any buyer artifact (see ADR-0003 H2)."
        )

    hardened = copy.deepcopy(manifest)
    hardened["build"]["channel"] = "free"
    return hardened

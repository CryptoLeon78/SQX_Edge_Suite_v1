"""
plan.py - canonical mining plan loaded from config/plan.json.
"""
from __future__ import annotations

from dataclasses import dataclass

from .config_loader import load_manifest


@dataclass(frozen=True)
class Mining:
    num: int
    phase: int
    asset: str
    tf: str
    bs: str
    dir: str  # 'long' | 'short' | 'both'

    @property
    def name(self) -> str:
        return f"Mining{self.num:02d}_{self.asset}_{self.tf}_{self.bs}"


def normalize_direction(d: str) -> str:
    """Normalize dashboard directions to SQX internal direction names."""
    normalized = d.strip().upper()
    mapping = {
        "L": "long",
        "S": "short",
        "L/S": "both",
        "LONG": "long",
        "SHORT": "short",
        "BOTH": "both",
    }
    if normalized not in mapping:
        raise ValueError(f"Unknown mining direction: {d!r}")
    return mapping[normalized]


def _dir(d: str) -> str:
    return normalize_direction(d)


def _load_plan() -> list[Mining]:
    manifest = load_manifest("plan.json")
    minings = manifest.get("minings") or []
    return [
        Mining(
            num=int(item["num"]),
            phase=int(item["phase"]),
            asset=str(item["asset"]),
            tf=str(item["tf"]),
            bs=str(item["bs"]),
            dir=_dir(str(item["dir"])),
        )
        for item in minings
    ]


PLAN = _load_plan()


def get(num: int) -> Mining:
    """Return mining by number."""
    for mining in PLAN:
        if mining.num == num:
            return mining
    raise KeyError(f"Mining {num} not in plan")


def all_minings() -> list[Mining]:
    return list(PLAN)

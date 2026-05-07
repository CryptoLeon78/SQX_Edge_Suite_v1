from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


TOOL_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = TOOL_ROOT.parents[1]
DEFAULT_MANIFEST = PROJECT_ROOT / "docs" / "private_commercial_manifest.json"
DEFAULT_OUTPUT = PROJECT_ROOT / "commercial-private" / "sqx-edge-commercial-private"


def now_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_rel(path: Path) -> str:
    return path.relative_to(PROJECT_ROOT).as_posix()


def ignored_roots(manifest: dict[str, Any]) -> list[Path]:
    roots: list[Path] = []
    for item in manifest.get("localPrivateStagingIgnoredPaths", []):
        roots.append((PROJECT_ROOT / str(item).rstrip("/")).resolve())
    return roots


def assert_output_is_ignored(output_dir: Path, manifest: dict[str, Any], allow_outside_ignored: bool) -> None:
    if allow_outside_ignored:
        return
    resolved = output_dir.resolve()
    for root in ignored_roots(manifest):
        if resolved == root or root in resolved.parents:
            return
    allowed = ", ".join(str(path) for path in ignored_roots(manifest))
    raise ValueError(f"output_dir_must_be_inside_ignored_private_staging:{resolved}; allowed={allowed}")


def expand_move_pattern(pattern: str) -> list[Path]:
    clean = pattern.replace("\\", "/")
    base = PROJECT_ROOT / clean.rstrip("/")
    if clean.endswith("/") and base.is_dir():
        return sorted(path for path in base.rglob("*") if path.is_file())
    if "*" in clean:
        return sorted(path for path in PROJECT_ROOT.glob(clean) if path.is_file())
    if base.is_file():
        return [base]
    if base.is_dir():
        return sorted(path for path in base.rglob("*") if path.is_file())
    return []


def collect_sources(manifest: dict[str, Any]) -> list[Path]:
    collected: dict[str, Path] = {}
    for pattern in manifest.get("privateRepositoryMoves", []):
        for path in expand_move_pattern(str(pattern)):
            collected[normalize_rel(path)] = path
    return [collected[key] for key in sorted(collected)]


def build_index(manifest_path: Path, manifest: dict[str, Any], sources: list[Path], output_dir: Path) -> dict[str, Any]:
    entries = []
    for source in sources:
        rel = normalize_rel(source)
        entries.append(
            {
                "source": rel,
                "privateDestination": rel,
                "size": source.stat().st_size,
                "sha256": sha256_file(source),
            }
        )
    return {
        "createdAt": now_iso(),
        "phase": manifest.get("phase", "S2_private_commercial_docs_split_prepared"),
        "policy": manifest.get("policy", ""),
        "migrationStage": manifest.get("migrationStage", "prepared_not_deleted"),
        "manifest": normalize_rel(manifest_path),
        "outputDir": str(output_dir),
        "sourceCount": len(entries),
        "sources": entries,
        "publicRepositoryKeeps": manifest.get("publicRepositoryKeeps", []),
        "redactionRules": manifest.get("redactionRules", []),
        "traceabilityPolicy": manifest.get("traceabilityPolicy", ""),
    }


def markdown_index(index: dict[str, Any]) -> str:
    lines = [
        "# Private Commercial Migration Index",
        "",
        f"- Created: `{index['createdAt']}`",
        f"- Phase: `{index['phase']}`",
        f"- Migration stage: `{index['migrationStage']}`",
        f"- Source count: `{index['sourceCount']}`",
        "",
        "## Sources",
    ]
    for item in index["sources"]:
        lines.append(f"- `{item['source']}` -> `{item['privateDestination']}` (`{item['sha256']}`)")
    lines.extend(
        [
            "",
            "## Public Boundary",
            "",
            "Public files are not deleted by this export. Replace public material only after the private repository copy is verified.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_export(index: dict[str, Any], sources: list[Path], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for source in sources:
        destination = output_dir / normalize_rel(source)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    (output_dir / "MIGRATION_INDEX.json").write_text(json.dumps(index, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "MIGRATION_INDEX.md").write_text(markdown_index(index), encoding="utf-8")
    (output_dir / "README.md").write_text(
        "# SQX Edge Private Commercial Workspace\n\n"
        "This local export is ignored by git. Push it only to the operator-owned private commercial repository.\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare a private commercial docs export without deleting public sources.")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--allow-outside-ignored", action="store_true")
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    output_dir = Path(args.output_dir)
    manifest = load_json(manifest_path)
    assert_output_is_ignored(output_dir, manifest, args.allow_outside_ignored)
    sources = collect_sources(manifest)
    index = build_index(manifest_path, manifest, sources, output_dir)
    if not args.no_write:
        write_export(index, sources, output_dir)
    print(json.dumps(index, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

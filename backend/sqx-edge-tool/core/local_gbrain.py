from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from core import local_memory_outbox


LOCAL_GBRAIN_VERSION = "sqx-edge-local-gbrain-v1"
DEFAULT_GBRAIN_RELATIVE = Path(".local") / "gbrain" / "local_gbrain.sqlite"
TRACKED_DOC_GLOBS = ("*.md", "docs/**/*.md")


def default_db_path(project_root: str | Path) -> Path:
    return Path(project_root).resolve(strict=False) / DEFAULT_GBRAIN_RELATIVE


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _slugify(value: str, *, fallback: str = "page") -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or fallback


def _path_slug(relative_path: str) -> str:
    path = relative_path.replace("\\", "/")
    if path.lower() == "readme.md":
        return "readme"
    if path.lower() == "changelog.md":
        return "changelog"
    if path.lower() == "agents.md":
        return "agents"
    if path.lower().startswith("docs/") and path.lower().endswith(".md"):
        return "docs/" + _slugify(path[5:-3])
    return _slugify(path)


def _title_from_markdown(text: str, fallback: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip() or fallback
    return fallback


def _base_payload(action: str, db_path: Path) -> dict[str, Any]:
    return {
        "ok": False,
        "version": LOCAL_GBRAIN_VERSION,
        "action": action,
        "dbPresent": db_path.is_file(),
        "dbRelative": str(DEFAULT_GBRAIN_RELATIVE).replace("\\", "/"),
        "privacy": {
            "localPathsReturned": False,
            "tokensReturned": False,
            "licenseMaterialReturned": False,
            "externalNetworkRequired": False,
        },
    }


def ensure_db(path: str | Path) -> Path:
    db_path = Path(path).resolve(strict=False)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(db_path)) as conn:
        with conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS local_gbrain_pages (
                  slug TEXT PRIMARY KEY,
                  created_at TEXT NOT NULL,
                  updated_at TEXT NOT NULL,
                  title TEXT NOT NULL,
                  content TEXT NOT NULL,
                  source_kind TEXT NOT NULL,
                  source_ref TEXT NOT NULL,
                  tags_json TEXT NOT NULL,
                  content_sha256 TEXT NOT NULL
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_local_gbrain_source ON local_gbrain_pages(source_kind, source_ref)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_local_gbrain_updated ON local_gbrain_pages(updated_at)")
    return db_path


def _upsert_page(
    path: str | Path,
    *,
    slug: str,
    title: str,
    content: str,
    source_kind: str,
    source_ref: str,
    tags: list[str] | None = None,
) -> bool:
    db_path = ensure_db(path)
    normalized_slug = _slugify(slug.replace("\\", "/"), fallback="page")
    if "/" in slug:
        normalized_slug = "/".join(_slugify(part, fallback="page") for part in slug.replace("\\", "/").split("/") if part)
    now = _utc_now()
    digest = _sha256(content)
    with closing(sqlite3.connect(db_path)) as conn:
        existing = conn.execute(
            "SELECT content_sha256 FROM local_gbrain_pages WHERE slug = ?",
            (normalized_slug,),
        ).fetchone()
        changed = existing is None or existing[0] != digest
        with conn:
            conn.execute(
                """
                INSERT INTO local_gbrain_pages
                  (slug, created_at, updated_at, title, content, source_kind, source_ref, tags_json, content_sha256)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(slug) DO UPDATE SET
                  updated_at = excluded.updated_at,
                  title = excluded.title,
                  content = excluded.content,
                  source_kind = excluded.source_kind,
                  source_ref = excluded.source_ref,
                  tags_json = excluded.tags_json,
                  content_sha256 = excluded.content_sha256
                """,
                (
                    normalized_slug,
                    now,
                    now,
                    title.strip() or normalized_slug,
                    content.strip(),
                    source_kind,
                    source_ref,
                    json.dumps(tags or [], ensure_ascii=False),
                    digest,
                ),
            )
    return changed


def _iter_tracked_markdown(project_root: str | Path) -> Iterable[tuple[str, Path]]:
    root = Path(project_root).resolve(strict=False)
    seen: set[str] = set()
    for pattern in TRACKED_DOC_GLOBS:
        for path in sorted(root.glob(pattern)):
            if not path.is_file():
                continue
            rel = path.relative_to(root).as_posix()
            if rel.startswith(".local/"):
                continue
            if rel in seen:
                continue
            seen.add(rel)
            yield rel, path


def _connect(path: str | Path) -> sqlite3.Connection:
    conn = sqlite3.connect(ensure_db(path))
    conn.row_factory = sqlite3.Row
    return conn


def status_payload(project_root: str | Path, db_path: str | Path | None = None) -> dict[str, Any]:
    db = Path(db_path) if db_path else default_db_path(project_root)
    ensure_db(db)
    with closing(_connect(db)) as conn:
        counts = {
            row["source_kind"]: int(row["count"])
            for row in conn.execute(
                "SELECT source_kind, COUNT(*) AS count FROM local_gbrain_pages GROUP BY source_kind"
            ).fetchall()
        }
    outbox_status = local_memory_outbox.status_payload(local_memory_outbox.default_db_path(project_root))
    return _base_payload("status", Path(db)) | {
        "ok": True,
        "status": "ready",
        "mode": "local_first_mem_optional",
        "pageCounts": counts,
        "pageCount": sum(counts.values()),
        "outboxPendingCount": outbox_status["pendingCount"],
        "memQuotaBlockedSafe": True,
    }


def index_payload(project_root: str | Path, db_path: str | Path | None = None) -> dict[str, Any]:
    db = Path(db_path) if db_path else default_db_path(project_root)
    indexed = 0
    changed = 0
    for rel, path in _iter_tracked_markdown(project_root):
        text = path.read_text(encoding="utf-8")
        title = _title_from_markdown(text, Path(rel).stem)
        did_change = _upsert_page(
            db,
            slug=_path_slug(rel),
            title=title,
            content=text,
            source_kind="tracked_doc",
            source_ref=rel,
            tags=["tracked", "docs"],
        )
        indexed += 1
        changed += 1 if did_change else 0
    payload = status_payload(project_root, db)
    return payload | {
        "action": "index",
        "status": "indexed",
        "indexedCount": indexed,
        "changedCount": changed,
    }


def import_outbox_payload(
    project_root: str | Path,
    db_path: str | Path | None = None,
    *,
    status: str = "pending",
    limit: int = 500,
) -> dict[str, Any]:
    db = Path(db_path) if db_path else default_db_path(project_root)
    outbox_db = local_memory_outbox.default_db_path(project_root)
    outbox = local_memory_outbox.list_notes(outbox_db, status=status, limit=limit)
    imported = 0
    changed = 0
    with closing(sqlite3.connect(local_memory_outbox.ensure_db(outbox_db))) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT id, created_at, updated_at, status, source, title, content, tags_json
            FROM mem_outbox
            WHERE (? = 'all' OR status = ?)
            ORDER BY id ASC
            LIMIT ?
            """,
            (status, status, max(1, min(int(limit or 500), 1000))),
        ).fetchall()
    for row in rows:
        tags = json.loads(row["tags_json"] or "[]")
        content = (
            f"# {row['title']}\n\n"
            f"Outbox id: `{row['id']}`\n"
            f"Outbox status: `{row['status']}`\n"
            f"Source: `{row['source']}`\n"
            f"Created: `{row['created_at']}`\n"
            f"Updated: `{row['updated_at']}`\n\n"
            f"{row['content']}"
        )
        slug = f"outbox/{row['id']:04d}-{_slugify(row['title'])}"
        did_change = _upsert_page(
            db,
            slug=slug,
            title=row["title"],
            content=content,
            source_kind="local_memory_outbox",
            source_ref=f"outboxId={row['id']}",
            tags=["outbox"] + tags,
        )
        imported += 1
        changed += 1 if did_change else 0
    payload = status_payload(project_root, db)
    return payload | {
        "action": "import-outbox",
        "status": "outbox_imported",
        "requestedOutboxStatus": status,
        "outboxListedCount": len(outbox["notes"]),
        "importedCount": imported,
        "changedCount": changed,
        "marksMemSynced": False,
    }


def save_page_payload(
    project_root: str | Path,
    db_path: str | Path | None = None,
    *,
    title: str,
    content: str,
    slug: str = "",
    tags: list[str] | None = None,
) -> dict[str, Any]:
    if not title.strip():
        raise ValueError("title_required")
    if not content.strip():
        raise ValueError("content_required")
    db = Path(db_path) if db_path else default_db_path(project_root)
    final_slug = slug.strip() or f"notes/{_slugify(title)}"
    changed = _upsert_page(
        db,
        slug=final_slug,
        title=title,
        content=content,
        source_kind="local_gbrain_note",
        source_ref=final_slug,
        tags=tags or [],
    )
    return _base_payload("save-page", Path(db)) | {
        "ok": True,
        "status": "saved",
        "slug": final_slug,
        "changed": changed,
    }


def _tokens(query: str) -> list[str]:
    return [token for token in re.findall(r"[a-z0-9_/-]+", query.lower()) if len(token) >= 3]


def _snippet(content: str, tokens: list[str], *, width: int = 220) -> str:
    lowered = content.lower()
    positions = [lowered.find(token) for token in tokens if lowered.find(token) >= 0]
    if not positions:
        return content.strip().replace("\n", " ")[:width]
    start = max(0, min(positions) - 80)
    end = min(len(content), start + width)
    return content[start:end].strip().replace("\n", " ")


def search_payload(
    project_root: str | Path,
    db_path: str | Path | None = None,
    *,
    query: str,
    limit: int = 10,
) -> dict[str, Any]:
    if not query.strip():
        raise ValueError("query_required")
    db = Path(db_path) if db_path else default_db_path(project_root)
    terms = _tokens(query)
    with closing(_connect(db)) as conn:
        rows = conn.execute(
            """
            SELECT slug, title, content, source_kind, source_ref, tags_json, updated_at
            FROM local_gbrain_pages
            ORDER BY updated_at DESC
            """
        ).fetchall()
    results = []
    for row in rows:
        haystack = f"{row['title']}\n{row['content']}".lower()
        hit_terms = [term for term in terms if term in haystack]
        score = (
            len(hit_terms) * 1000
            + sum(haystack.count(term) for term in hit_terms)
            + sum(row["title"].lower().count(term) * 4 for term in hit_terms)
        )
        if score <= 0:
            continue
        results.append(
            {
                "slug": row["slug"],
                "title": row["title"],
                "sourceKind": row["source_kind"],
                "sourceRef": row["source_ref"],
                "score": score,
                "snippet": _snippet(row["content"], terms),
                "tags": json.loads(row["tags_json"] or "[]"),
            }
        )
    results.sort(key=lambda item: (-item["score"], item["slug"]))
    return _base_payload("search", Path(db)) | {
        "ok": True,
        "status": "searched",
        "query": query,
        "resultCount": len(results),
        "results": results[: max(1, min(int(limit or 10), 50))],
    }


def query_payload(
    project_root: str | Path,
    db_path: str | Path | None = None,
    *,
    query: str,
    limit: int = 5,
) -> dict[str, Any]:
    search = search_payload(project_root, db_path, query=query, limit=limit)
    answer_lines = []
    for item in search["results"]:
        answer_lines.append(f"- {item['title']} [{item['slug']}]: {item['snippet']}")
    return search | {
        "action": "query",
        "status": "answered_from_local_index" if answer_lines else "no_local_answer",
        "answer": "\n".join(answer_lines),
        "inferenceOnly": True,
    }


def get_page_payload(project_root: str | Path, db_path: str | Path | None = None, *, slug: str) -> dict[str, Any]:
    if not slug.strip():
        raise ValueError("slug_required")
    db = Path(db_path) if db_path else default_db_path(project_root)
    with closing(_connect(db)) as conn:
        row = conn.execute(
            """
            SELECT slug, title, content, source_kind, source_ref, tags_json, created_at, updated_at, content_sha256
            FROM local_gbrain_pages
            WHERE slug = ?
            """,
            (slug.strip(),),
        ).fetchone()
    if row is None:
        return _base_payload("get-page", Path(db)) | {
            "ok": False,
            "status": "not_found",
            "slug": slug,
        }
    return _base_payload("get-page", Path(db)) | {
        "ok": True,
        "status": "found",
        "page": {
            "slug": row["slug"],
            "title": row["title"],
            "content": row["content"],
            "sourceKind": row["source_kind"],
            "sourceRef": row["source_ref"],
            "tags": json.loads(row["tags_json"] or "[]"),
            "createdAt": row["created_at"],
            "updatedAt": row["updated_at"],
            "contentSha256": row["content_sha256"],
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Local gbrain-compatible memory for SQX Edge Suite")
    parser.add_argument("action", choices=("status", "index", "import-outbox", "search", "query", "get-page", "save-page"))
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--query", default="")
    parser.add_argument("--slug", default="")
    parser.add_argument("--title", default="")
    parser.add_argument("--content", default="")
    parser.add_argument("--tags", default="")
    parser.add_argument("--status", default="pending")
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args(argv)
    tags = [tag.strip() for tag in args.tags.split(",") if tag.strip()]
    if args.action == "status":
        payload = status_payload(args.project_root)
    elif args.action == "index":
        payload = index_payload(args.project_root)
    elif args.action == "import-outbox":
        payload = import_outbox_payload(args.project_root, status=args.status, limit=args.limit)
    elif args.action == "search":
        payload = search_payload(args.project_root, query=args.query, limit=args.limit)
    elif args.action == "query":
        payload = query_payload(args.project_root, query=args.query, limit=args.limit)
    elif args.action == "get-page":
        payload = get_page_payload(args.project_root, slug=args.slug)
    else:
        payload = save_page_payload(args.project_root, title=args.title, content=args.content, slug=args.slug, tags=tags)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import json
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


LOCAL_MEMORY_OUTBOX_VERSION = "sqx-edge-local-memory-outbox-v1"
DEFAULT_OUTBOX_RELATIVE = Path(".local") / "memory_outbox" / "memory_outbox.sqlite"


def default_db_path(project_root: str | Path) -> Path:
    return Path(project_root).resolve(strict=False) / DEFAULT_OUTBOX_RELATIVE


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def ensure_db(path: str | Path) -> Path:
    db_path = Path(path).resolve(strict=False)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(db_path)) as conn:
        with conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS mem_outbox (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  created_at TEXT NOT NULL,
                  updated_at TEXT NOT NULL,
                  status TEXT NOT NULL,
                  source TEXT NOT NULL,
                  title TEXT NOT NULL,
                  content TEXT NOT NULL,
                  tags_json TEXT NOT NULL,
                  mem_note_id TEXT,
                  last_error TEXT
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_mem_outbox_status ON mem_outbox(status)")
    return db_path


def enqueue_note(
    path: str | Path,
    *,
    title: str,
    content: str,
    source: str = "codex_mem_limit_fallback",
    tags: list[str] | None = None,
) -> dict[str, Any]:
    title = str(title or "").strip()
    content = str(content or "").strip()
    if not title:
        raise ValueError("title_required")
    if not content:
        raise ValueError("content_required")
    db_path = ensure_db(path)
    now = _utc_now()
    with closing(sqlite3.connect(db_path)) as conn:
        with conn:
            cur = conn.execute(
                """
                INSERT INTO mem_outbox
                  (created_at, updated_at, status, source, title, content, tags_json)
                VALUES (?, ?, 'pending', ?, ?, ?, ?)
                """,
                (now, now, source, title, content, json.dumps(tags or [], ensure_ascii=False)),
            )
            row_id = int(cur.lastrowid)
    return _base_payload("enqueue", db_path) | {
        "ok": True,
        "status": "pending",
        "outboxId": row_id,
        "pendingCount": count_pending(db_path),
    }


def count_pending(path: str | Path) -> int:
    db_path = ensure_db(path)
    with closing(sqlite3.connect(db_path)) as conn:
        return int(conn.execute("SELECT COUNT(*) FROM mem_outbox WHERE status = 'pending'").fetchone()[0])


def list_notes(path: str | Path, *, status: str = "pending", limit: int = 20) -> dict[str, Any]:
    db_path = ensure_db(path)
    with closing(sqlite3.connect(db_path)) as conn:
        rows = conn.execute(
                """
                SELECT id, created_at, updated_at, status, source, title, tags_json, mem_note_id, last_error
                FROM mem_outbox
                WHERE (? = 'all' OR status = ?)
                ORDER BY id DESC
                LIMIT ?
                """,
                (status, status, max(1, min(int(limit or 20), 200))),
            ).fetchall()
    notes = []
    for row in rows:
        notes.append({
            "id": row[0],
            "createdAt": row[1],
            "updatedAt": row[2],
            "status": row[3],
            "source": row[4],
            "title": row[5],
            "tags": json.loads(row[6] or "[]"),
            "memNoteId": row[7],
            "lastError": row[8],
        })
    return _base_payload("list", db_path) | {
        "ok": True,
        "status": "listed",
        "filter": status,
        "notes": notes,
        "pendingCount": count_pending(db_path),
    }


def mark_synced(path: str | Path, *, outbox_id: int, mem_note_id: str = "") -> dict[str, Any]:
    db_path = ensure_db(path)
    now = _utc_now()
    with closing(sqlite3.connect(db_path)) as conn:
        with conn:
            cur = conn.execute(
                """
                UPDATE mem_outbox
                SET status = 'synced', updated_at = ?, mem_note_id = ?, last_error = NULL
                WHERE id = ?
                """,
                (now, mem_note_id, int(outbox_id)),
            )
            rowcount = cur.rowcount
    return _base_payload("mark-synced", db_path) | {
        "ok": rowcount == 1,
        "status": "synced" if rowcount == 1 else "not_found",
        "outboxId": int(outbox_id),
        "pendingCount": count_pending(db_path),
    }


def status_payload(path: str | Path) -> dict[str, Any]:
    db_path = ensure_db(path)
    with closing(sqlite3.connect(db_path)) as conn:
        rows = conn.execute("SELECT status, COUNT(*) FROM mem_outbox GROUP BY status").fetchall()
    counts = {str(status): int(count) for status, count in rows}
    return _base_payload("status", db_path) | {
        "ok": True,
        "status": "ready",
        "counts": counts,
        "pendingCount": counts.get("pending", 0),
    }


def _base_payload(action: str, db_path: Path) -> dict[str, Any]:
    return {
        "ok": False,
        "version": LOCAL_MEMORY_OUTBOX_VERSION,
        "action": action,
        "dbPresent": db_path.is_file(),
        "dbRelative": str(DEFAULT_OUTBOX_RELATIVE).replace("\\", "/"),
        "privacy": {
            "localPathsReturned": False,
            "tokensReturned": False,
            "licenseMaterialReturned": False,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Local memory outbox for deferred Mem/gbrain writes")
    parser.add_argument("action", choices=("status", "enqueue", "list", "mark-synced"))
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--title", default="")
    parser.add_argument("--content", default="")
    parser.add_argument("--source", default="codex_mem_limit_fallback")
    parser.add_argument("--tags", default="")
    parser.add_argument("--status", default="pending")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--outbox-id", type=int, default=0)
    parser.add_argument("--mem-note-id", default="")
    args = parser.parse_args(argv)
    db_path = default_db_path(args.project_root)
    if args.action == "status":
        payload = status_payload(db_path)
    elif args.action == "enqueue":
        payload = enqueue_note(
            db_path,
            title=args.title,
            content=args.content,
            source=args.source,
            tags=[tag.strip() for tag in args.tags.split(",") if tag.strip()],
        )
    elif args.action == "list":
        payload = list_notes(db_path, status=args.status, limit=args.limit)
    else:
        payload = mark_synced(db_path, outbox_id=args.outbox_id, mem_note_id=args.mem_note_id)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

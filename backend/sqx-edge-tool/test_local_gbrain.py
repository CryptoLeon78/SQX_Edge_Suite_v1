import tempfile
import unittest
from pathlib import Path

from core import local_gbrain
from core import local_memory_outbox


class LocalGbrainTests(unittest.TestCase):
    def test_index_search_query_and_get_page_use_local_sqlite_without_external_network(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs").mkdir()
            (root / "README.md").write_text(
                "# SQX Edge Suite\n\nLOCAL_GBRAIN1 keeps Mem optional for project memory.",
                encoding="utf-8",
            )
            (root / "docs" / "LOCAL_GBRAIN.md").write_text(
                "# Local Gbrain\n\nMarker: `sqx-edge-local-gbrain-v1`.\n",
                encoding="utf-8",
            )
            db_path = root / "local_gbrain.sqlite"

            indexed = local_gbrain.index_payload(root, db_path)
            searched = local_gbrain.search_payload(root, db_path, query="Mem optional", limit=5)
            queried = local_gbrain.query_payload(root, db_path, query="local gbrain marker", limit=5)
            page = local_gbrain.get_page_payload(root, db_path, slug="docs/local-gbrain")

        self.assertTrue(indexed["ok"])
        self.assertEqual(indexed["indexedCount"], 2)
        self.assertFalse(indexed["privacy"]["externalNetworkRequired"])
        self.assertGreaterEqual(searched["resultCount"], 1)
        self.assertEqual(queried["status"], "answered_from_local_index")
        self.assertTrue(page["ok"])
        self.assertEqual(page["page"]["sourceKind"], "tracked_doc")
        self.assertIn("sqx-edge-local-gbrain-v1", page["page"]["content"])

    def test_save_page_creates_local_gbrain_note(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            db_path = root / "local_gbrain.sqlite"
            saved = local_gbrain.save_page_payload(
                root,
                db_path,
                title="SQX Durable Decision",
                content="Origin and institutional remotes mirror the same checkpoint.",
                slug="decisions/remote-mirror",
                tags=["git", "mirror"],
            )
            page = local_gbrain.get_page_payload(root, db_path, slug="decisions/remote-mirror")

        self.assertTrue(saved["ok"])
        self.assertTrue(page["ok"])
        self.assertEqual(page["page"]["sourceKind"], "local_gbrain_note")
        self.assertIn("institutional", page["page"]["content"])

    def test_import_outbox_indexes_pending_notes_without_marking_mem_synced(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            outbox_db = local_memory_outbox.default_db_path(root)
            enqueued = local_memory_outbox.enqueue_note(
                outbox_db,
                title="Remote Mirror PR Checkpoint",
                content="origin and institutional point to commit 79b1de36.",
                source="test",
                tags=["git", "pr"],
            )
            db_path = root / "local_gbrain.sqlite"
            imported = local_gbrain.import_outbox_payload(root, db_path)
            searched = local_gbrain.search_payload(root, db_path, query="institutional 79b1de36", limit=5)
            outbox_status = local_memory_outbox.status_payload(outbox_db)

        self.assertEqual(enqueued["pendingCount"], 1)
        self.assertTrue(imported["ok"])
        self.assertEqual(imported["importedCount"], 1)
        self.assertFalse(imported["marksMemSynced"])
        self.assertEqual(outbox_status["pendingCount"], 1)
        self.assertEqual(searched["results"][0]["sourceKind"], "local_memory_outbox")


if __name__ == "__main__":
    unittest.main()

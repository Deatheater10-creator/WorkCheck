import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from workcheck.storage import DraftStore, SaveError, empty_draft, default_draft_path


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "WorkCheck" / "draft.json"
        self.store = DraftStore(self.path)

    def draft(self):
        result = empty_draft()
        result.update(question="x^2*sin(x)", revision=3,
                      lines=[{"id": "a"*32, "text": "y=x^2*sin(x)"},
                             {"id": "b"*32, "text": "D(x^2)*sin(x)+x^2*D(sin(x))"}])
        return result

    def test_missing_file_normal(self):
        result = self.store.load()
        self.assertEqual(result.draft, empty_draft())
        self.assertFalse(result.warning)
        self.assertFalse(self.path.exists())

    def test_round_trip_and_new_store_restore(self):
        draft = self.draft()
        self.store.save(draft)
        self.assertEqual(DraftStore(self.path).load().draft, draft)

    def test_reordered_and_overlimit_raw_input(self):
        draft = self.draft()
        draft["question"] = "x"*501
        draft["lines"].reverse()
        draft["lines"][0]["text"] = "x"*1000
        self.store.save(draft)
        self.assertEqual(self.store.load().draft, draft)

    def test_topic_saved(self):
        draft = self.draft()
        draft["topic"] = "Partial fractions"
        self.store.save(draft)
        self.assertEqual(self.store.load().draft["topic"], "Partial fractions")

    def test_truncated_file_preserved_and_fresh_draft_usable(self):
        self.path.parent.mkdir()
        original = b'{"schema_version":1,"question":'
        self.path.write_bytes(original)
        result = self.store.load()
        self.assertTrue(result.warning)
        self.assertEqual(result.draft, empty_draft())
        backups = list(self.path.parent.glob("draft.damaged-*.json"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_bytes(), original)
        self.store.save(self.draft())
        self.assertEqual(self.store.load().draft, self.draft())
        self.assertEqual(backups[0].read_bytes(), original)

    def test_wrong_schema_and_invalid_types(self):
        for change in [{"schema_version": 2}, {"schema_version": True}, {"question": 42},
                       {"revision": -1}, {"revision": True}, {"lines": {}},
                       {"topic": "Unrecognized"}, {"lines": [{"id": "x", "text": "x"}]}]:
            with self.subTest(change=change):
                draft = self.draft()
                draft.update(change)
                self.path.parent.mkdir(exist_ok=True)
                self.path.write_text(json.dumps(draft), encoding="utf-8")
                self.assertTrue(self.store.load().warning)

    def test_duplicate_ids_rejected(self):
        draft = self.draft()
        draft["lines"][1]["id"] = draft["lines"][0]["id"]
        with self.assertRaises(SaveError):
            self.store.save(draft)

    def test_failed_atomic_replace_preserves_old_save_and_cleans_temp(self):
        self.store.save(self.draft())
        original = self.path.read_bytes()
        with patch("workcheck.storage.os.replace", side_effect=PermissionError("test write failure")):
            with self.assertRaises(SaveError):
                self.store.save(empty_draft())
        self.assertEqual(self.path.read_bytes(), original)
        self.assertEqual(list(self.path.parent.glob("*.tmp")), [])

    def test_failed_reset_preserves_old_save(self):
        self.store.save(self.draft())
        with patch("workcheck.storage.os.replace", side_effect=OSError("disk full")):
            with self.assertRaises(SaveError):
                self.store.save(empty_draft())
        self.assertEqual(self.store.load().draft, self.draft())

    def test_confirmed_reset_clears_durable_data(self):
        self.store.save(self.draft())
        self.store.save(empty_draft())
        self.assertEqual(DraftStore(self.path).load().draft, empty_draft())

    def test_failed_archive_cannot_overwrite_damaged_original(self):
        self.path.parent.mkdir()
        self.path.write_bytes(b"broken")
        with patch.object(Path, "rename", side_effect=PermissionError("archive blocked")):
            self.assertTrue(self.store.load().warning)
            with self.assertRaises(SaveError):
                self.store.save(empty_draft())
        self.assertEqual(self.path.read_bytes(), b"broken")

    def test_unreadable_file_untouched(self):
        self.store.save(self.draft())
        with patch.object(self.store, "_read", side_effect=PermissionError("read blocked")):
            self.assertTrue(self.store.load().warning)
            with self.assertRaises(SaveError):
                self.store.save(empty_draft())
        self.assertEqual(self.store.load().draft, self.draft())

    def test_oversize_file_preserved_without_reading(self):
        self.path.parent.mkdir()
        self.path.write_bytes(b"12345")
        with patch("workcheck.storage.MAX_SAVE_BYTES", 4):
            result = self.store.load()
        self.assertTrue(result.warning)
        backup = next(self.path.parent.glob("draft.damaged-*.json"))
        self.assertEqual(backup.read_bytes(), b"12345")

    def test_oversize_inmemory_draft_not_truncated_or_saved(self):
        draft = self.draft()
        with patch("workcheck.storage.MAX_SAVE_BYTES", 4):
            with self.assertRaises(SaveError):
                self.store.save(draft)
        self.assertEqual(draft, self.draft())
        self.assertFalse(self.path.exists())

    def test_save_archives_external_corruption(self):
        self.path.parent.mkdir()
        self.path.write_bytes(b"external damage")
        self.store.save(self.draft())
        self.assertEqual(next(self.path.parent.glob("draft.damaged-*.json")).read_bytes(), b"external damage")
        self.assertEqual(self.store.load().draft, self.draft())

    def test_local_path_and_test_override(self):
        with patch.dict("os.environ", {"LOCALAPPDATA": self.temp.name, "WORKCHECK_DRAFT_PATH": ""}):
            self.assertEqual(default_draft_path(), self.path)
        with patch.dict("os.environ", {"WORKCHECK_DRAFT_PATH": str(self.path)}):
            self.assertEqual(default_draft_path(), self.path.resolve())

    def test_invalid_encoding_and_excessive_json_number_recover(self):
        self.path.parent.mkdir()
        for original in [b"\xff\xfe", b'{"revision":' + b"1"*5000 + b"}"]:
            with self.subTest(content=original[:20]):
                self.path.write_bytes(original)
                result = self.store.load()
                self.assertTrue(result.warning)
                self.assertEqual(result.draft, empty_draft())
                self.assertFalse(self.path.exists())

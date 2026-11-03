"""Stdlib tests for scripts/drill.py. No network, no third-party packages."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "drill.py"
spec = importlib.util.spec_from_file_location("drill", SCRIPT)
assert spec and spec.loader, f"cannot load {SCRIPT}"
drill = importlib.util.module_from_spec(spec)
spec.loader.exec_module(drill)


def run(*argv: str) -> str:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        drill.main(list(argv))
    return buf.getvalue()


class TempStore(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.store = Path(self.tmp.name) / "reviews.json"
        self.old = os.environ.get("DRILL_STORE")
        os.environ["DRILL_STORE"] = str(self.store)

    def tearDown(self) -> None:
        if self.old is None:
            os.environ.pop("DRILL_STORE", None)
        else:
            os.environ["DRILL_STORE"] = self.old
        self.tmp.cleanup()


class SchedulingTest(unittest.TestCase):
    def test_intervals_then_mastery(self) -> None:
        base = date(2026, 1, 1)
        item = {"status": "new", "streak": 0, "interval_idx": -1, "lapses": 0}
        expected = [("2026-01-02", 1), ("2026-01-05", 2), ("2026-01-12", 3),
                    ("2026-01-27", 4), ("2026-02-26", 5)]
        for due_iso, streak in expected:
            drill.apply_grade(item, "right", base)
            self.assertEqual(item["due"], due_iso)
            self.assertEqual(item["streak"], streak)
            base = date.fromisoformat(due_iso)
        self.assertEqual(item["status"], "learning")
        drill.apply_grade(item, "right", base)
        self.assertEqual(item["status"], "mastered")
        self.assertIsNone(item["due"])

    def test_wrong_resets(self) -> None:
        base = date(2026, 1, 1)
        item = {"status": "learning", "streak": 3, "interval_idx": 2, "lapses": 0}
        drill.apply_grade(item, "wrong", base)
        self.assertEqual(item["due"], (base + timedelta(days=1)).isoformat())
        self.assertEqual((item["streak"], item["interval_idx"], item["lapses"]), (0, 0, 1))

    def test_partial_keeps_index(self) -> None:
        base = date(2026, 1, 1)
        item = {"status": "learning", "streak": 2, "interval_idx": 3, "lapses": 0}
        drill.apply_grade(item, "partial", base)
        self.assertEqual(item["due"], (base + timedelta(days=1)).isoformat())
        self.assertEqual(item["interval_idx"], 3)
        self.assertEqual(item["streak"], 0)

    def test_unknown_grade_raises(self) -> None:
        with self.assertRaises(ValueError):
            drill.apply_grade({}, "maybe", date(2026, 1, 1))


class CliTest(TempStore):
    def test_add_then_due_then_grade(self) -> None:
        run("add", "--topic", "t/a", "--question", "q?", "--answer", "a.")
        data = json.loads(self.store.read_text(encoding="utf-8"))
        self.assertEqual(len(data["items"]), 1)
        self.assertEqual(data["items"][0]["status"], "new")

        self.assertIn("#1", run("due"))
        self.assertIn("q?", run("card", "1"))
        self.assertIn("a.", run("reveal", "1"))

        run("grade", "1", "--result", "right")
        data = json.loads(self.store.read_text(encoding="utf-8"))
        item = data["items"][0]
        self.assertEqual(item["status"], "learning")
        self.assertEqual(item["streak"], 1)
        self.assertEqual(item["reviews"][0]["result"], "right")

    def test_import_both_shapes(self) -> None:
        rows = [{"topic": "t", "question": "q1", "answer": "a1"}]
        f = Path(self.tmp.name) / "rows.json"
        f.write_text(json.dumps(rows), encoding="utf-8")
        run("import", str(f))
        f2 = Path(self.tmp.name) / "rows2.json"
        f2.write_text(json.dumps({"items": [{"topic": "t", "question": "q2", "answer": "a2"}]}), encoding="utf-8")
        run("import", str(f2))
        data = json.loads(self.store.read_text(encoding="utf-8"))
        self.assertEqual([i["id"] for i in data["items"]], [1, 2])

    def test_mastered_not_counted_again(self) -> None:
        run("add", "--topic", "t", "--question", "q", "--answer", "a")
        data = json.loads(self.store.read_text(encoding="utf-8"))
        data["items"][0].update({"status": "mastered", "due": None, "streak": 6, "interval_idx": 5})
        self.store.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        out = run("grade", "1", "--result", "right")
        self.assertTrue(out.strip())
        data = json.loads(self.store.read_text(encoding="utf-8"))
        self.assertEqual(data["items"][0]["status"], "mastered")

    def test_corrupt_store_is_not_overwritten(self) -> None:
        self.store.write_text("{not json", encoding="utf-8")
        with self.assertRaises(SystemExit):
            run("due")
        self.assertEqual(self.store.read_text(encoding="utf-8"), "{not json")


if __name__ == "__main__":
    unittest.main()

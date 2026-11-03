"""Language selection and localized output."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


i18n = load("i18n")
drill = load("drill")
build_index = load("build_index")


class DetectTest(unittest.TestCase):
    def setUp(self) -> None:
        self.old = {k: os.environ.get(k) for k in ("DRILL_LANG", "LANG", "LC_ALL")}

    def tearDown(self) -> None:
        for k, v in self.old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    def test_cli_wins(self) -> None:
        os.environ["LANG"] = "zh_CN.UTF-8"
        self.assertEqual(i18n.detect("en"), "en")

    def test_env_then_locale(self) -> None:
        os.environ.pop("DRILL_LANG", None)
        os.environ["LANG"] = "zh_CN.UTF-8"
        self.assertEqual(i18n.detect(None), "zh")
        os.environ["DRILL_LANG"] = "en"
        self.assertEqual(i18n.detect(None), "en")

    def test_default_english(self) -> None:
        for k in ("DRILL_LANG", "LANG", "LC_ALL"):
            os.environ.pop(k, None)
        self.assertEqual(i18n.detect(None), "en")

    def test_unknown_locale_falls_back(self) -> None:
        os.environ.pop("DRILL_LANG", None)
        os.environ["LANG"] = "de_DE.UTF-8"
        self.assertEqual(i18n.detect(None), "en")


class MessageTest(unittest.TestCase):
    def test_both_tables_have_the_same_keys(self) -> None:
        self.assertEqual(set(i18n.MESSAGES["en"]), set(i18n.MESSAGES["zh"]))

    def test_formatting(self) -> None:
        self.assertIn("#7", i18n.t("no_item", "en", id=7))
        self.assertIn("7", i18n.t("no_item", "zh", id=7))


class CliLanguageTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.old = os.environ.get("DRILL_STORE")
        os.environ["DRILL_STORE"] = str(Path(self.tmp.name) / "reviews.json")

    def tearDown(self) -> None:
        if self.old is None:
            os.environ.pop("DRILL_STORE", None)
        else:
            os.environ["DRILL_STORE"] = self.old
        self.tmp.cleanup()

    def run_cli(self, *argv: str) -> str:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            drill.main(list(argv))
        return buf.getvalue()

    def test_chinese_output(self) -> None:
        out = self.run_cli("add", "--topic", "t", "--question", "q", "--answer", "a", "--lang", "zh")
        self.assertIn("已入库", out)

    def test_english_output(self) -> None:
        out = self.run_cli("add", "--topic", "t", "--question", "q", "--answer", "a", "--lang", "en")
        self.assertIn("Added", out)


class BuilderLanguageTest(unittest.TestCase):
    def test_index_page_locale(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "ch01.html"
            src.write_text('<title>One</title><meta name="note" content="n">', encoding="utf-8")
            build_index.build(Path(tmp), "Demo", lang="en")
            en = (Path(tmp) / "index.html").read_text(encoding="utf-8")
            build_index.build(Path(tmp), "演示", lang="zh")
            zh = (Path(tmp) / "index.html").read_text(encoding="utf-8")
        self.assertIn('<html lang="en"', en)
        self.assertIn('lang="zh-CN"', zh)
        self.assertNotEqual(en, zh)


if __name__ == "__main__":
    unittest.main()

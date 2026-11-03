"""Tiny message catalog shared by the drill CLI and the page builders.

Language resolution order: explicit argument > DRILL_LANG > LANG / LC_ALL > "en".
Only UI chrome is translated; identifiers, JSON keys and stored data stay English.
"""

from __future__ import annotations

import os

LANGS = ("en", "zh")

MESSAGES: dict[str, dict[str, str]] = {
    "en": {
        "parse_failed": "Failed to parse store ({store}): {exc}. Back it up and fix it; refusing to overwrite.",
        "bad_structure": "Unexpected store structure ({store}). Back it up and fix it; refusing to overwrite.",
        "no_item": "No item #{id}",
        "added": "Added [#{id}] {topic}, due today",
        "required_fields": "topic, question and answer are required",
        "nothing_due": "Nothing due today. Store holds {total} item(s).",
        "due_header": "{count} due:",
        "answer": "Answer: {text}",
        "source": "Source: {text}",
        "already_mastered": "Already mastered; not recounted",
        "mastered_after": "[#{id}] mastered after {streak} correct, no longer scheduled",
        "graded": "[#{id}] {result}, next due {due} (streak {streak})",
        "stats_line": "{total} item(s): new {new}, learning {learning}, mastered {mastered}",
        "due_today_line": "Due today: {today}; due within 3 days: {soon}",
        "in_progress": "In progress: {topics}",
        "no_match": "No items matched",
        "updated": "[#{id}] updated",
        "deleted": "Deleted [#{id}] {question}",
        "note_required": "--topic and --text are required",
        "appended": "Appended to {path}",
        "import_bad_json": "Import file is not valid JSON: {exc}",
        "imported": "Imported {count} item(s): {ids}",
        "selftest_ok": "selftest ok: 1/3/7/15/30 intervals, mastery on the sixth pass, wrong resets, partial backs off one day",
        "cli_description": "Predict-then-reveal spaced repetition store",
        "terms_written": "written {path} ({count} terms)",
        "index_written": "wrote {path} ({count} entries)",
        "glossary_written": "wrote {path} ({count} terms)",
        "index_suffix": "visual review",
        "index_subtitle": "{count} page(s), newest first. One concept per page; open a card to study.",
        "index_empty": "No pages in this folder yet.",
        "index_desc": "Build an entry page for a folder of lesson pages",
        "dir_missing": "Directory does not exist: {path}",
        "glossary_note": "Abbreviations with a one-line explanation; searchable and filterable.",
        "glossary_subtitle": "{count} terms. Search by abbreviation, full name or translation; click a category to filter.",
        "glossary_placeholder": "Search TOR, gateway, VLAN…",
        "glossary_empty": "No matching terms.",
        "glossary_all": "All",
        "glossary_other": "Other",
        "glossary_show": "showing",
        "glossary_desc": "Render a searchable glossary page from a terms JSON file",
        "glossary_h1": "Abbr",
        "glossary_h2": "Full name",
        "glossary_h3": "Local name",
        "glossary_h4": "One-line explanation",
        "glossary_h5": "Source",
    },
    "zh": {
        "parse_failed": "复习库解析失败（{store}）：{exc}。先备份再修，脚本不覆盖。",
        "bad_structure": "复习库结构不对（{store}）。先备份再修，脚本不覆盖。",
        "no_item": "没有编号 {id} 的题目",
        "added": "已入库 [#{id}] {topic}，今天到期",
        "required_fields": "topic、question、answer 都不能为空",
        "nothing_due": "今天没有到期。库内共 {total} 道。",
        "due_header": "到期 {count} 道：",
        "answer": "答：{text}",
        "source": "出处：{text}",
        "already_mastered": "该题已掌握，未重复计数",
        "mastered_after": "[#{id}] 已掌握（连对 {streak} 次），不再排期",
        "graded": "[#{id}] {result}，下次 {due}（连对 {streak}）",
        "stats_line": "共 {total} 道：新 {new}，在学 {learning}，已掌握 {mastered}",
        "due_today_line": "今天到期 {today} 道，三天内到期 {soon} 道",
        "in_progress": "在学主题：{topics}",
        "no_match": "没有符合条件的题目",
        "updated": "[#{id}] 已更新",
        "deleted": "已删除 [#{id}] {question}",
        "note_required": "--topic 与 --text 都不能为空",
        "appended": "已追加到 {path}",
        "import_bad_json": "导入文件不是合法 JSON：{exc}",
        "imported": "已导入 {count} 道：{ids}",
        "selftest_ok": "selftest ok：间隔 1/3/7/15/30 天、走完全轮后掌握、错题重置、半对退回一天",
        "cli_description": "先猜后揭 + 间隔重复复习库",
        "terms_written": "已写入 {path}（{count} 条术语）",
        "index_written": "已生成 {path}（{count} 页）",
        "glossary_written": "已生成 {path}（{count} 条术语）",
        "index_suffix": "可视化复习",
        "index_subtitle": "共 {count} 页，按最近修改排序。每页只讲一个概念，点进去就能看。",
        "index_empty": "目录里还没有页面。",
        "index_desc": "为 可视化/ 目录生成入口页",
        "dir_missing": "目录不存在：{path}",
        "glossary_note": "单位专业术语缩写与一句话解释，可搜索筛选。",
        "glossary_subtitle": "共 {count} 条。输入缩写、全称或中文都能搜；点分类可筛。",
        "glossary_placeholder": "搜 TOR、网关、VLAN…",
        "glossary_empty": "没有匹配的条目。",
        "glossary_all": "全部",
        "glossary_other": "其他",
        "glossary_show": "显示",
        "glossary_desc": "由术语 JSON 生成可搜索的术语表 HTML",
        "glossary_h1": "缩写",
        "glossary_h2": "全称",
        "glossary_h3": "中文",
        "glossary_h4": "一句话解释",
        "glossary_h5": "出处",
    },
}


def normalize(lang: str | None) -> str | None:
    if not lang:
        return None
    low = lang.strip().lower()
    if low.startswith("zh"):
        return "zh"
    if low.startswith("en"):
        return "en"
    return None


def detect(cli: str | None = None) -> str:
    """Pick a language: CLI flag, then DRILL_LANG, then LANG/LC_ALL, else English."""
    for candidate in (cli, os.environ.get("DRILL_LANG"),
                      os.environ.get("LANG"), os.environ.get("LC_ALL")):
        norm = normalize(candidate)
        if norm:
            return norm
    return "en"


def t(key: str, lang: str, **kwargs) -> str:
    table = MESSAGES.get(lang) or MESSAGES["en"]
    template = table.get(key) or MESSAGES["en"].get(key) or key
    try:
        return template.format(**kwargs)
    except (KeyError, IndexError):
        return template

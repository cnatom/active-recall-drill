#!/usr/bin/env python3
"""Spaced-repetition drill store: predict-then-reveal, 1/3/7/15/30 days.

Store lives at <skill>/data/reviews.json unless DRILL_STORE is set.
All writes are atomic and nothing is overwritten on parse failure.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path

INTERVALS = [1, 3, 7, 15, 30]
MASTERED_STREAK = len(INTERVALS) + 1  # 走完 1/3/7/15/30 全部间隔后再对一次
NEW = "new"
LEARNING = "learning"
MASTERED = "mastered"


# ---------------------------------------------------------------- store basics

def now() -> dt.datetime:
    return dt.datetime.now().astimezone()


def today() -> dt.date:
    return now().date()


def store_path() -> Path:
    env = os.environ.get("DRILL_STORE", "").strip()
    if env:
        return Path(env).expanduser()
    return Path(__file__).resolve().parent.parent / "data" / "reviews.json"


def notes_dir(store: Path) -> Path:
    return store.parent / "notes"


def load(store: Path) -> dict:
    if not store.exists():
        return {"version": 1, "next_id": 1, "items": []}
    try:
        db = json.loads(store.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        sys.exit(f"Failed to parse store ({store}): {exc}. Back it up and fix it; refusing to overwrite.")
    if not isinstance(db, dict) or not isinstance(db.get("items"), list):
        sys.exit(f"Unexpected store structure ({store}). Back it up and fix it; refusing to overwrite.")
    db.setdefault("version", 1)
    db.setdefault("next_id", 1 + max((i.get("id", 0) for i in db["items"]), default=0))
    return db


def save(store: Path, db: dict) -> None:
    store.parent.mkdir(parents=True, exist_ok=True)
    tmp = store.with_name(store.name + ".tmp")
    tmp.write_text(json.dumps(db, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(store)


def find(db: dict, item_id: int) -> dict:
    for item in db["items"]:
        if item.get("id") == item_id:
            return item
    sys.exit(f"No item #{item_id}")


# ---------------------------------------------------------------- scheduling

def apply_grade(item: dict, result: str, base: dt.date) -> dict:
    """Mutate item's schedule for one graded review. Pure apart from item."""
    if result == "right":
        item["streak"] = item.get("streak", 0) + 1
        item["interval_idx"] = item.get("interval_idx", -1) + 1
        if item["interval_idx"] >= len(INTERVALS):
            item["status"] = MASTERED
            item["due"] = None
        else:
            idx = min(item["interval_idx"], len(INTERVALS) - 1)
            item["status"] = LEARNING
            item["due"] = (base + dt.timedelta(days=INTERVALS[idx])).isoformat()
    elif result == "partial":
        item["streak"] = 0
        item["interval_idx"] = max(item.get("interval_idx", 0), 0)
        item["status"] = LEARNING
        item["due"] = (base + dt.timedelta(days=1)).isoformat()
    elif result == "wrong":
        item["streak"] = 0
        item["interval_idx"] = 0
        item["lapses"] = item.get("lapses", 0) + 1
        item["status"] = LEARNING
        item["due"] = (base + dt.timedelta(days=1)).isoformat()
    else:
        raise ValueError(result)
    return item


def due_items(db: dict, limit: int | None = None, topic: str | None = None) -> list[dict]:
    t = today().isoformat()
    items = [
        i for i in db["items"]
        if i.get("status") != MASTERED and (i.get("due") or t) <= t
    ]
    if topic:
        items = [i for i in items if i.get("topic") == topic]
    items.sort(key=lambda i: (i.get("due") or t, i.get("id", 0)))
    return items[:limit] if limit else items


# ---------------------------------------------------------------- rendering

def line(item: dict, show_topic: bool = True) -> str:
    head = f"[#{item['id']}]"
    if show_topic:
        head += f" {item.get('topic', '')}"
    streak = item.get("streak", 0)
    flag = "" if item.get("status") != LEARNING else f" streak {streak}"
    return f"{head} | {item['question']}{flag}"


def cmd_add(args, store, db) -> None:
    item = add_item(db, args.topic, args.question, args.answer, args.source, args.tags)
    save(store, db)
    print(f"Added [#{item['id']}] {item['topic']}, due today")


def add_item(db, topic, question, answer, source="", tags=None) -> dict:
    if not topic.strip() or not question.strip() or not answer.strip():
        sys.exit("topic, question and answer are required")
    item = {
        "id": db["next_id"],
        "topic": topic.strip(),
        "question": question.strip(),
        "answer": answer.strip(),
        "source": (source or "").strip(),
        "tags": [t.strip() for t in (tags or []) if t.strip()],
        "status": NEW,
        "due": today().isoformat(),
        "created": now().isoformat(timespec="seconds"),
        "last_reviewed": None,
        "streak": 0,
        "interval_idx": -1,
        "lapses": 0,
        "reviews": [],
    }
    db["next_id"] = item["id"] + 1
    db["items"].append(item)
    return item


def cmd_due(args, store, db) -> None:
    items = due_items(db, args.limit, args.topic)
    if args.json:
        print(json.dumps(items, ensure_ascii=False, indent=2))
        return
    if not items:
        total = len(db["items"])
        print(f"Nothing due today. Store holds {total} item(s).")
        return
    print(f"{len(items)} due:")
    for item in items:
        print("  " + line(item))


def cmd_card(args, store, db) -> None:
    item = find(db, args.id)
    print(f"[#{item['id']}] {item.get('topic', '')}")
    print(item["question"])


def cmd_reveal(args, store, db) -> None:
    item = find(db, args.id)
    print(f"Answer: {item['answer']}")
    if item.get("source"):
        print(f"Source: {item['source']}")


def cmd_grade(args, store, db) -> None:
    item = find(db, args.id)
    if item.get("status") == MASTERED and args.result == "right":
        print("Already mastered; not recounted")
        return
    apply_grade(item, args.result, today())
    item["last_reviewed"] = now().isoformat(timespec="seconds")
    item.setdefault("reviews", []).append(
        {"date": item["last_reviewed"], "result": args.result, "note": args.note or ""}
    )
    save(store, db)
    if item["status"] == MASTERED:
        print(f"[#{item['id']}] mastered after {item['streak']} correct, no longer scheduled")
    else:
        print(f"[#{item['id']}] {args.result}, next due {item['due']} (streak {item['streak']})")


def cmd_stats(args, store, db) -> None:
    items = db["items"]
    t = today()
    counts = {NEW: 0, LEARNING: 0, MASTERED: 0}
    for item in items:
        counts[item.get("status", NEW)] = counts.get(item.get("status", NEW), 0) + 1
    due_today = len(due_items(db))
    in3 = [
        i for i in items
        if i.get("due") and i.get("status") != MASTERED
        and dt.date.fromisoformat(i["due"]) <= t + dt.timedelta(days=3)
    ]
    if args.json:
        print(json.dumps({"total": len(items), "counts": counts,
                          "due_today": due_today, "due_within_3d": len(in3)},
                         ensure_ascii=False))
        return
    print(f"{len(items)} item(s): new {counts.get(NEW, 0)}, learning {counts.get(LEARNING, 0)}, mastered {counts.get(MASTERED, 0)}")
    print(f"Due today: {due_today}; due within 3 days: {len(in3)}")
    topics: dict[str, int] = {}
    for item in items:
        if item.get("status") != MASTERED:
            topics[item.get("topic", "")] = topics.get(item.get("topic", ""), 0) + 1
    if topics:
        print("In progress: " + ", ".join(f"{k} {v}" for k, v in sorted(topics.items())))


def cmd_list(args, store, db) -> None:
    items = db["items"]
    if args.topic:
        items = [i for i in items if i.get("topic") == args.topic]
    if args.status:
        items = [i for i in items if i.get("status") == args.status]
    if not items:
        print("No items matched")
        return
    for item in sorted(items, key=lambda i: i.get("id", 0)):
        due = item.get("due") or "已掌握"
        print(f"{line(item)}  [{item.get('status')} {due}]")


def cmd_edit(args, store, db) -> None:
    item = find(db, args.id)
    for field in ("topic", "question", "answer", "source"):
        value = getattr(args, field, None)
        if value:
            item[field] = value.strip()
    save(store, db)
    print(f"[#{item['id']}] updated")


def cmd_rm(args, store, db) -> None:
    item = find(db, args.id)
    db["items"] = [i for i in db["items"] if i.get("id") != args.id]
    save(store, db)
    print(f"Deleted [#{item['id']}] {item['question']}")


def cmd_note(args, store, db) -> None:
    topic = args.topic.strip()
    if not topic or not args.text.strip():
        sys.exit("--topic and --text are required")
    slug = topic.replace("/", "-").replace(" ", "-")
    target = notes_dir(store) / f"{slug}.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    stamp = now().strftime("%Y-%m-%d %H:%M")
    with target.open("a", encoding="utf-8") as fh:
        fh.write(f"- {stamp} {args.text.strip()}\n")
    print(f"Appended to {target}")


def cmd_import(args, store, db) -> None:
    raw = sys.stdin.read() if args.file == "-" else Path(args.file).expanduser().read_text(encoding="utf-8")
    try:
        rows = json.loads(raw)
    except json.JSONDecodeError as exc:
        sys.exit(f"Import file is not valid JSON: {exc}")
    if isinstance(rows, dict):
        rows = rows.get("items", [])
    added = []
    for row in rows:
        added.append(add_item(db, row["topic"], row["question"], row["answer"],
                              row.get("source", ""), row.get("tags")))
    save(store, db)
    print(f"Imported {len(added)} item(s): " + ", ".join(f"#{i['id']}" for i in added))


def cmd_selftest(args, store, db) -> None:
    base = dt.date(2026, 1, 1)
    item = {"status": NEW, "streak": 0, "interval_idx": -1, "lapses": 0}
    expected = [
        ("2026-01-02", 1), ("2026-01-05", 2), ("2026-01-12", 3),
        ("2026-01-27", 4), ("2026-02-26", 5),
    ]
    for due_iso, streak in expected:
        apply_grade(item, "right", base)
        assert item.get("due") == due_iso, (item, due_iso)
        assert item["streak"] == streak, (item, streak)
        base = dt.date.fromisoformat(due_iso)
    assert item["status"] == LEARNING, item
    apply_grade(item, "right", base)
    assert item["status"] == MASTERED and item["due"] is None, item
    wrong = apply_grade({"status": LEARNING, "streak": 3, "interval_idx": 2, "lapses": 0}, "wrong", base)
    assert wrong["due"] == (base + dt.timedelta(days=1)).isoformat(), wrong
    assert wrong["interval_idx"] == 0 and wrong["lapses"] == 1 and wrong["streak"] == 0, wrong
    partial = apply_grade({"status": LEARNING, "streak": 2, "interval_idx": 3, "lapses": 0}, "partial", base)
    assert partial["due"] == (base + dt.timedelta(days=1)).isoformat(), partial
    assert partial["interval_idx"] == 3 and partial["streak"] == 0, partial
    print("selftest ok: 1/3/7/15/30 intervals, mastery on the sixth pass, wrong resets, partial backs off one day")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Predict-then-reveal spaced repetition store")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("add")
    p.add_argument("--topic", required=True)
    p.add_argument("--question", required=True)
    p.add_argument("--answer", required=True)
    p.add_argument("--source", default="")
    p.add_argument("--tags", default="")
    p.set_defaults(func=cmd_add)

    p = sub.add_parser("import")
    p.add_argument("file")
    p.set_defaults(func=cmd_import)

    p = sub.add_parser("due")
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--topic")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_due)

    p = sub.add_parser("card")
    p.add_argument("id", type=int)
    p.set_defaults(func=cmd_card)

    p = sub.add_parser("reveal")
    p.add_argument("id", type=int)
    p.set_defaults(func=cmd_reveal)

    p = sub.add_parser("grade")
    p.add_argument("id", type=int)
    p.add_argument("--result", required=True, choices=["right", "partial", "wrong"])
    p.add_argument("--note", default="")
    p.set_defaults(func=cmd_grade)

    p = sub.add_parser("stats")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_stats)

    p = sub.add_parser("list")
    p.add_argument("--topic")
    p.add_argument("--status", choices=[NEW, LEARNING, MASTERED])
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("edit")
    p.add_argument("id", type=int)
    for name in ("topic", "question", "answer", "source"):
        p.add_argument(f"--{name}")
    p.set_defaults(func=cmd_edit)

    p = sub.add_parser("rm")
    p.add_argument("id", type=int)
    p.set_defaults(func=cmd_rm)

    p = sub.add_parser("note")
    p.add_argument("--topic", required=True)
    p.add_argument("--text", required=True)
    p.set_defaults(func=cmd_note)

    p = sub.add_parser("selftest")
    p.set_defaults(func=cmd_selftest)

    args = parser.parse_args(argv)
    if getattr(args, "tags", None):
        args.tags = args.tags.split(",")
    store = store_path()
    db = load(store)
    args.func(args, store, db)


if __name__ == "__main__":
    main()

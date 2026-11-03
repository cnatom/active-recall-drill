#!/usr/bin/env python3
"""Build an index.html entry page for a 可视化/ folder of learning pages.

Each page is a self-contained html with <title> and an optional
<meta name="note" content="one line summary">. The index is regenerated
on every run; do not hand-edit it.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import re
from pathlib import Path

CARD = """      <a class="card" href="{file}">
        <div class="t">{title}</div>
        <div class="d">{note}</div>
        <div class="m">{date}</div>
      </a>"""

PAGE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · 可视化复习</title>
<style>
  body {{ margin:0; background:#fbfbf9; color:#1b1f24;
          font: 16px/1.6 -apple-system, "PingFang SC", "Helvetica Neue", sans-serif; }}
  .wrap {{ max-width: 900px; margin:0 auto; padding:40px 24px 60px; }}
  h1 {{ font-size:24px; margin:0 0 6px; }}
  .sub {{ color:#6b7280; font-size:14px; margin-bottom:26px; }}
  .card {{ display:block; padding:18px 20px; border:1px solid #e2e6ea; border-radius:12px;
           background:#fff; text-decoration:none; color:inherit; margin-bottom:14px;
           transition: border-color .15s, transform .15s; }}
  .card:hover {{ border-color:#2f6fd0; transform: translateY(-1px); }}
  .t {{ font-size:17px; font-weight:600; }}
  .d {{ font-size:14px; color:#4b5563; margin-top:4px; }}
  .m {{ font-size:12px; color:#9aa3ad; margin-top:8px; }}
  .empty {{ color:#6b7280; }}
</style>
</head>
<body>
<div class="wrap">
  <h1>{title}</h1>
  <div class="sub">共 {count} 页，按最近修改排序。每页只讲一个概念，点进去就能看。</div>
{cards}
</div>
</body>
</html>
"""


def read_meta(path: Path) -> tuple[str, str]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    m = re.search(r"<title>(.*?)</title>", text, re.S | re.I)
    title = html.unescape(m.group(1).strip()) if m else path.stem
    m = re.search(r'<meta\s+name="note"\s+content="([^"]*)"', text, re.I)
    note = html.unescape(m.group(1).strip()) if m else ""
    return title, note


def build(target: Path, title: str, out_name: str = "index.html") -> Path:
    pages = sorted(
        (p for p in target.glob("*.html") if p.name != out_name),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    cards = []
    for page in pages:
        page_title, note = read_meta(page)
        stamp = dt.datetime.fromtimestamp(page.stat().st_mtime).strftime("%Y-%m-%d")
        cards.append(CARD.format(file=html.escape(page.name), title=html.escape(page_title),
                                 note=html.escape(note), date=stamp))
    body = "\n".join(cards) if cards else '      <div class="empty">目录里还没有页面。</div>'
    out = target / out_name
    out.write_text(PAGE.format(title=html.escape(title), count=len(pages), cards=body),
                   encoding="utf-8")
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="为 可视化/ 目录生成入口页")
    parser.add_argument("dir")
    parser.add_argument("--title", default="学习可视化")
    parser.add_argument("--out", default="index.html")
    args = parser.parse_args()
    target = Path(args.dir).expanduser()
    if not target.is_dir():
        raise SystemExit(f"目录不存在：{target}")
    out = build(target, args.title, args.out)
    count = len([p for p in target.glob("*.html") if p.name != args.out])
    print(f"已生成 {out}，收录 {count} 页")


if __name__ == "__main__":
    main()

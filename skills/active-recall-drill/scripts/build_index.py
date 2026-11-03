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
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # allow loading as a module
import i18n  # noqa: E402  (local module, resolved after sys.path fix)


CARD = """      <a class="card" href="{file}">
        <div class="t">{title}</div>
        <div class="d">{note}</div>
        <div class="m">{date}</div>
      </a>"""

PAGE = """<!DOCTYPE html>
<html lang="{langattr}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · {suffix}</title>
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
  <div class="sub">{subtitle}</div>
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


def build(target: Path, title: str, out_name: str = "index.html", lang: str = "en") -> Path:
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
    empty = i18n.t("index_empty", lang)
    body = "\n".join(cards) if cards else f'      <div class="empty">{html.escape(empty)}</div>'
    out = target / out_name
    out.write_text(PAGE.format(
        title=html.escape(title), count=len(pages), cards=body,
        suffix=html.escape(i18n.t("index_suffix", lang)),
        subtitle=html.escape(i18n.t("index_subtitle", lang, count=len(pages))),
        langattr="zh-CN" if lang == "zh" else "en",
    ), encoding="utf-8")
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=i18n.t("index_desc", i18n.detect()))
    parser.add_argument("dir")
    parser.add_argument("--title", default=None)
    parser.add_argument("--out", default="index.html")
    parser.add_argument("--lang", choices=list(i18n.LANGS), help="output language; default follows the system locale")
    args = parser.parse_args()
    lang = i18n.detect(args.lang)
    if args.title is None:
        args.title = "学习可视化" if lang == "zh" else "Study pages"
    target = Path(args.dir).expanduser()
    if not target.is_dir():
        raise SystemExit(i18n.t("dir_missing", lang, path=target))
    out = build(target, args.title, args.out, lang)
    count = len([p for p in target.glob("*.html") if p.name != args.out])
    print(i18n.t("index_written", lang, path=out, count=count))


if __name__ == "__main__":
    main()

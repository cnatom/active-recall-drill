#!/usr/bin/env python3
"""Build a searchable single-file glossary page from a terms JSON file.

JSON shape:
{
  "title": "Glossary example",
  "terms": [
    {"abbr": "TOR", "full": "Top of Rack", "cn": "柜顶交换机",
     "note": "一句话解释", "cat": "设备", "src": "课程2 第 8 页"}
  ]
}
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # allow loading as a module
import i18n  # noqa: E402  (local module, resolved after sys.path fix)


PAGE = """<!DOCTYPE html>
<html lang="{langattr}">
<head>
<meta charset="utf-8">
<meta name="note" content="{note}">
<title>{title}</title>
<style>
  body {{ margin:0; background:#fbfbf9; color:#1b1f24;
          font:16px/1.6 -apple-system,"PingFang SC","Helvetica Neue",sans-serif; }}
  .wrap {{ max-width:1080px; margin:0 auto; padding:26px 22px 48px; }}
  h1 {{ font-size:22px; margin:0 0 4px; }}
  .sub {{ color:#6b7280; font-size:14px; margin-bottom:14px; }}
  .ctl {{ display:flex; flex-wrap:wrap; gap:10px; align-items:center; margin-bottom:12px; }}
  input {{ font:inherit; font-size:15px; padding:8px 12px; border:1px solid #c8ced6; border-radius:9px; width:280px; }}
  .chip {{ font-size:13.5px; padding:6px 12px; border-radius:999px; border:1px solid #c8ced6; background:#fff; cursor:pointer; }}
  .chip.on {{ background:#eef2ff; border-color:#2f6fd0; color:#1b3f7a; }}
  .count {{ color:#6b7280; font-size:13px; margin-left:auto; }}
  table {{ border-collapse:collapse; width:100%; font-size:14px; }}
  th,td {{ border-bottom:1px solid #eceff3; padding:9px 10px; text-align:left; vertical-align:top; }}
  th {{ background:#f5f6f8; font-weight:600; font-size:13px; position:sticky; top:0; }}
  td.ab {{ font-family:ui-monospace,Menlo,monospace; font-weight:600; white-space:nowrap; }}
  td.cn {{ white-space:nowrap; }}
  td.src {{ color:#9aa3ad; font-size:12.5px; white-space:nowrap; }}
  mark {{ background:#fff3c4; padding:0 2px; }}
  .empty {{ color:#6b7280; padding:24px 0; }}
</style>
</head>
<body>
<div class="wrap">
  <h1>{title}</h1>
  <div class="sub">{subtitle}</div>
  <div class="ctl">
    <input id="q" placeholder="{placeholder}" autofocus>
    <span id="cats"></span>
    <span class="count" id="count"></span>
  </div>
  <table>
    <thead><tr><th style="width:110px">{h1}</th><th style="width:190px">{h2}</th><th style="width:130px">{h3}</th><th>{h4}</th><th style="width:120px">{h5}</th></tr></thead>
    <tbody id="rows"></tbody>
  </table>
  <div class="empty" id="empty" hidden>{empty}</div>
</div>
<script>
const TERMS = {data};
const UI = {ui};
const rows = document.getElementById('rows');
const q = document.getElementById('q');
const count = document.getElementById('count');
const empty = document.getElementById('empty');
const catsBox = document.getElementById('cats');
let cat = UI.all;

const cats = [UI.all, ...Array.from(new Set(TERMS.map(t => t.cat || UI.other)))];
cats.forEach(c => {{
  const b = document.createElement('button');
  b.className = 'chip' + (c === UI.all ? ' on' : '');
  b.textContent = c;
  b.onclick = () => {{ cat = c; document.querySelectorAll('.chip').forEach(x => x.classList.toggle('on', x === b)); draw(); }};
  catsBox.appendChild(b);
}});

function hl(text, term) {{
  if (!term) return text;
  const i = text.toLowerCase().indexOf(term.toLowerCase());
  if (i < 0) return text;
  return text.slice(0, i) + '<mark>' + text.slice(i, i + term.length) + '</mark>' + text.slice(i + term.length);
}}

function draw() {{
  const term = q.value.trim();
  const list = TERMS.filter(t => (cat === UI.all || (t.cat || UI.other) === cat) &&
    (!term || [t.abbr, t.full, t.cn, t.note].join(' ').toLowerCase().includes(term.toLowerCase())));
  rows.innerHTML = list.map(t => `<tr>
    <td class="ab">${{hl(t.abbr || '', term)}}</td>
    <td>${{hl(t.full || '', term)}}</td>
    <td class="cn">${{hl(t.cn || '', term)}}</td>
    <td>${{hl(t.note || '', term)}}</td>
    <td class="src">${{t.src || ''}}</td></tr>`).join('');
  count.textContent = UI.show + ' ' + list.length + ' / ' + TERMS.length;
  empty.hidden = list.length > 0;
}}
q.addEventListener('input', draw);
draw();
</script>
</body>
</html>
"""


def main() -> None:
    ap = argparse.ArgumentParser(description=i18n.t("glossary_desc", i18n.detect()))
    ap.add_argument("json_file")
    ap.add_argument("--out")
    ap.add_argument("--lang", choices=list(i18n.LANGS), help="output language; default follows the system locale")
    a = ap.parse_args()
    lang = i18n.detect(a.lang)
    src = Path(a.json_file).expanduser()
    data = json.loads(src.read_text(encoding="utf-8"))
    terms = data.get("terms") or []
    title = data.get("title") or src.stem
    out = Path(a.out).expanduser() if a.out else src.with_suffix(".html")
    ui = {k: i18n.t(k, lang) for k in ("glossary_all", "glossary_other", "glossary_show")}
    out.write_text(PAGE.format(
        title=title, count=len(terms),
        data=json.dumps(terms, ensure_ascii=False, indent=2),
        ui=json.dumps(ui, ensure_ascii=False),
        note=i18n.t("glossary_note", lang),
        subtitle=i18n.t("glossary_subtitle", lang, count=len(terms)),
        placeholder=i18n.t("glossary_placeholder", lang),
        empty=i18n.t("glossary_empty", lang),
        h1=i18n.t("glossary_h1", lang), h2=i18n.t("glossary_h2", lang),
        h3=i18n.t("glossary_h3", lang), h4=i18n.t("glossary_h4", lang),
        h5=i18n.t("glossary_h5", lang),
        langattr="zh-CN" if lang == "zh" else "en",
    ), encoding="utf-8")
    print(i18n.t("glossary_written", lang, path=out, count=len(terms)))


if __name__ == "__main__":
    main()

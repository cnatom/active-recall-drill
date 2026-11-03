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
from pathlib import Path

PAGE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="note" content="单位专业术语缩写与一句话解释，可搜索筛选。">
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
  <div class="sub">共 {count} 条。输入缩写、全称或中文都能搜；点分类可筛。</div>
  <div class="ctl">
    <input id="q" placeholder="搜 TOR、网关、VLAN…" autofocus>
    <span id="cats"></span>
    <span class="count" id="count"></span>
  </div>
  <table>
    <thead><tr><th style="width:110px">缩写</th><th style="width:190px">全称</th><th style="width:130px">中文</th><th>一句话解释</th><th style="width:120px">出处</th></tr></thead>
    <tbody id="rows"></tbody>
  </table>
  <div class="empty" id="empty" hidden>没有匹配的条目。</div>
</div>
<script>
const TERMS = {data};
const rows = document.getElementById('rows');
const q = document.getElementById('q');
const count = document.getElementById('count');
const empty = document.getElementById('empty');
const catsBox = document.getElementById('cats');
let cat = '全部';

const cats = ['全部', ...Array.from(new Set(TERMS.map(t => t.cat || '其他')))];
cats.forEach(c => {{
  const b = document.createElement('button');
  b.className = 'chip' + (c === '全部' ? ' on' : '');
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
  const list = TERMS.filter(t => (cat === '全部' || (t.cat || '其他') === cat) &&
    (!term || [t.abbr, t.full, t.cn, t.note].join(' ').toLowerCase().includes(term.toLowerCase())));
  rows.innerHTML = list.map(t => `<tr>
    <td class="ab">${{hl(t.abbr || '', term)}}</td>
    <td>${{hl(t.full || '', term)}}</td>
    <td class="cn">${{hl(t.cn || '', term)}}</td>
    <td>${{hl(t.note || '', term)}}</td>
    <td class="src">${{t.src || ''}}</td></tr>`).join('');
  count.textContent = `显示 ${{list.length}} / ${{TERMS.length}} 条`;
  empty.hidden = list.length > 0;
}}
q.addEventListener('input', draw);
draw();
</script>
</body>
</html>
"""


def main() -> None:
    ap = argparse.ArgumentParser(description="由术语 JSON 生成可搜索的术语表 HTML")
    ap.add_argument("json_file")
    ap.add_argument("--out")
    a = ap.parse_args()
    src = Path(a.json_file).expanduser()
    data = json.loads(src.read_text(encoding="utf-8"))
    terms = data.get("terms") or []
    title = data.get("title") or src.stem
    out = Path(a.out).expanduser() if a.out else src.with_suffix(".html")
    out.write_text(PAGE.format(title=title, count=len(terms),
                               data=json.dumps(terms, ensure_ascii=False, indent=2)),
                   encoding="utf-8")
    print(f"已生成 {out}，收录 {len(terms)} 条")


if __name__ == "__main__":
    main()

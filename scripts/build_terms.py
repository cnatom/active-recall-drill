"""把 术语.json 转成浏览器可直接加载的 assets/terms-data.js（file:// 也能用，无需本地服务）。

用法：python3 build_terms.py <术语.json> [输出路径]
默认输出到 术语.json 同目录的 assets/terms-data.js。
"""
import json
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    src = Path(sys.argv[1]).expanduser().resolve()
    data = json.loads(src.read_text(encoding="utf-8"))
    if isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        items = data.get("terms", [])
    else:
        raise SystemExit("terms file must be a JSON array or {\"terms\": [...]}")
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else src.parent / "assets" / "terms-data.js"
    out.parent.mkdir(parents=True, exist_ok=True)
    body = json.dumps(items, ensure_ascii=False, separators=(",", ":"))
    out.write_text(
        "// 由 术语.json 生成，勿手改；改完 json 重新跑 build_terms.py\n"
        f"window.__TERMS = {body};\n",
        encoding="utf-8",
    )
    print(f"written {out} ({len(items)} terms)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

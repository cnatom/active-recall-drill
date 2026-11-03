#!/usr/bin/env python3
"""Check an HTML teaching page for SVG connector/box collisions.

Reports connector segments (line/path with an id) that run through a node box.
Container boxes (room, cabinet) are ignored by size: anything wider than 250 px
or taller than 250 px is treated as a container.

Usage: python3 check_svg_overlap.py page.html [--allow l0,...]
Exit code 1 when a collision is found, so it can gate delivery.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

RATTR = re.compile(r'<rect[^>]*x="([\d.]+)"[^>]*y="([\d.]+)"[^>]*width="([\d.]+)"[^>]*height="([\d.]+)"')
LINE = re.compile(r'<line[^>]*id="(l\d+)"[^>]*x1="([\d.]+)"[^>]*y1="([\d.]+)"[^>]*x2="([\d.]+)"[^>]*y2="([\d.]+)"')
PATH = re.compile(r'<path[^>]*id="(l\d+)"[^>]*d="([^"]+)"')
POINT = re.compile(r'[ML] ([\d.]+) ([\d.]+)')


def load(path: Path) -> str:
    """Return every <svg> block, so pages with several diagrams are all checked."""
    text = path.read_text(encoding="utf-8", errors="ignore")
    blocks = re.findall(r"<svg.*?</svg>", text, re.S)
    if not blocks:
        print("no <svg> block found", file=sys.stderr)
        raise SystemExit(2)
    return "\n".join(blocks)


def boxes(svg: str) -> list[tuple[float, float, float, float]]:
    out = []
    for m in RATTR.finditer(svg):
        x, y, w, h = map(float, m.groups())
        if w > 250 or h > 250:  # container bands, rooms, cabinets
            continue
        out.append((x, y, w, h))
    return out


def segments(svg: str) -> list[tuple[str, float, float, float, float]]:
    out = []
    for m in LINE.finditer(svg):
        sid, x1, y1, x2, y2 = m.group(1), *map(float, m.groups()[1:])
        out.append((sid, x1, y1, x2, y2))
    for m in PATH.finditer(svg):
        pts = [(float(a), float(b)) for a, b in POINT.findall(m.group(2))]
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            out.append((m.group(1), x1, y1, x2, y2))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("html")
    ap.add_argument("--allow", default="", help="comma-separated connector ids that legitimately sit inside a box")
    args = ap.parse_args()

    svg = load(Path(args.html))
    allowed = {x.strip() for x in args.allow.split(",") if x.strip()}
    bad = 0
    for sid, x1, y1, x2, y2 in segments(svg):
        if sid in allowed:
            continue
        for rx, ry, rw, rh in boxes(svg):
            inside = sum(
                1 for i in range(301)
                if rx < x1 + (x2 - x1) * i / 300 < rx + rw and ry < y1 + (y2 - y1) * i / 300 < ry + rh
            )
            if inside > 5:
                print(f"collision: {sid} passes through box at ({rx:g},{ry:g}) {rw:g}x{rh:g}")
                bad += 1
    if bad:
        print(f"{bad} collision(s)")
        return 1
    print("no collisions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

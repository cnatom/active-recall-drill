#!/usr/bin/env python3
"""Tiny local recorder for course progress.

Pages opened from file:// cannot write to disk, so they POST to this server and
it appends to a JSON file the agent can read when the learner asks a question.

    python3 progress_server.py --file /path/to/可视化/progress.json [--port 8766]

Endpoints:
    POST /hit      {"file": "ch07.html", "id": "ch07", "num": "07", "title": "...", "step": 2}
    GET  /progress current map as JSON
    GET  /health   {"ok": true}

Only binds 127.0.0.1 and accepts any origin, because file:// pages send Origin: null.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

LOCK = threading.Lock()
STORE = Path("progress.json")


def read_store() -> dict:
    try:
        return json.loads(STORE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def write_store(data: dict) -> None:
    tmp = STORE.with_name(STORE.name + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, STORE)


class Handler(BaseHTTPRequestHandler):
    def _cors(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self._cors()
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        if self.path.startswith("/health"):
            self._json({"ok": True})
        elif self.path.startswith("/progress"):
            self._json(read_store())
        else:
            self._json({"error": "not found"}, 404)

    def do_POST(self) -> None:  # noqa: N802
        if not self.path.startswith("/hit"):
            self._json({"error": "not found"}, 404)
            return
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw.decode("utf-8"))
        except Exception:
            self._json({"error": "bad json"}, 400)
            return
        key = payload.get("id") or Path(payload.get("file", "")).stem
        if not key:
            self._json({"error": "missing id"}, 400)
            return
        with LOCK:
            data = read_store()
            record = data.get(key, {})
            record.update({
                "file": payload.get("file", record.get("file")),
                "num": payload.get("num", record.get("num")),
                "title": payload.get("title", record.get("title")),
                "step": payload.get("step", record.get("step")),
                "hits": record.get("hits", 0) + 1,
                "last": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
            })
            data[key] = record
            data["_last"] = {"key": key, "at": record["last"]}
            write_store(data)
        self._json({"ok": True, "key": key})

    def log_message(self, fmt: str, *args) -> None:  # quiet
        return


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True, help="progress.json path")
    ap.add_argument("--port", type=int, default=8766)
    args = ap.parse_args()
    global STORE
    STORE = Path(args.file).expanduser().resolve()
    STORE.parent.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"recording to {STORE} on http://127.0.0.1:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()

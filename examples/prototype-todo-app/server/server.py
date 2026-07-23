"""
Mock Todo backend server for Mavis Team Mode prototype.

This is a real, runnable Python script. It implements a minimal Todo API
with tag filtering, so the team can verify the SKILL.md workflow end-to-end.

Run: python server.py
Then: open client/index.html in a browser
"""

import json
import os
import threading
import time
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

# In-memory store
TODOS = [
    {"id": 1, "title": "Buy milk", "tag": "shopping", "done": False, "created_at": "2026-07-01"},
    {"id": 2, "title": "Read book", "tag": "personal", "done": True, "created_at": "2026-07-02"},
    {"id": 3, "title": "Fix bug #42", "tag": "work", "done": False, "created_at": "2026-07-03"},
    {"id": 4, "title": "Pay rent", "tag": "personal", "done": False, "created_at": "2026-07-04"},
    {"id": 5, "title": "Write tests", "tag": "work", "done": False, "created_at": "2026-07-05"},
    {"id": 6, "title": "Gym", "tag": "personal", "done": True, "created_at": "2026-07-06"},
    {"id": 7, "title": "Order groceries", "tag": "shopping", "done": False, "created_at": "2026-07-07"},
]
NEXT_ID = 8
LOCK = threading.Lock()


class TodoHandler(BaseHTTPRequestHandler):
    def _send_json(self, status, body):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PATCH, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(body, ensure_ascii=False).encode("utf-8"))

    def do_OPTIONS(self):
        self._send_json(204, {})

    def do_GET(self):
        if self.path == "/api/todos":
            self._send_json(200, TODOS)
        elif self.path == "/api/tags":
            tags = sorted({t["tag"] for t in TODOS})
            self._send_json(200, tags)
        elif self.path == "/api/health":
            self._send_json(200, {"status": "ok", "ts": datetime.now().isoformat()})
        else:
            self._send_json(404, {"error": "not found"})

    def do_POST(self):
        global NEXT_ID
        if self.path == "/api/todos":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length) or b"{}")
            with LOCK:
                new = {
                    "id": NEXT_ID,
                    "title": body.get("title", "Untitled"),
                    "tag": body.get("tag", "default"),
                    "done": False,
                    "created_at": datetime.now().strftime("%Y-%m-%d"),
                }
                TODOS.append(new)
                NEXT_ID += 1
            self._send_json(201, new)
        else:
            self._send_json(404, {"error": "not found"})

    def log_message(self, fmt, *args):
        # Quieter log
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {fmt % args}")


def main():
    port = int(os.environ.get("PORT", 8765))
    print(f"Starting Todo server on http://127.0.0.1:{port}")
    print("Try: curl http://127.0.0.1:%d/api/todos" % port)
    server = HTTPServer(("127.0.0.1", port), TodoHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()

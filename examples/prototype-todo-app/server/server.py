"""
Mock Todo backend server for Mavis Team Mode prototype.

This is a real, runnable Python script. It implements a minimal Todo API
with tag filtering, so the team can verify the SKILL.md workflow end-to-end.

Run: python server.py
Then: open client/index.html in a browser

Security notes:
- Binds to 127.0.0.1 only (not 0.0.0.0) — local dev only
- CORS restricted to localhost origins (not *)
- Input validation on title (1-200 chars) and tag (1-50 chars, alphanumeric+hyphen)
- Thread-safe via lock on writes
- Graceful 4xx for malformed JSON
"""
import json
import os
import re
import socket
import sys
import threading
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

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

# Limits
MAX_TITLE_LEN = 200
MAX_TAG_LEN = 50
MAX_BODY_BYTES = 64 * 1024  # 64KB request body cap
TAG_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{0,49}$")  # lowercase, digits, hyphens

# Allowed CORS origins (local dev only)
ALLOWED_ORIGINS = {
    "http://127.0.0.1:8765",
    "http://localhost:8765",
    "http://127.0.0.1:5500",   # VS Code Live Server default
    "http://localhost:5500",
    "null",                    # file:// origin for opening index.html directly
}


class TodoHandler(BaseHTTPRequestHandler):
    server_version = "TodoMavis/1.0"

    # Per-connection socket timeout. BaseHTTPServer's `server.timeout`
    # is the select-poll interval, NOT a per-socket read timeout, so it
    # does NOT protect against slowloris (a client that opens a socket
    # and dribbles bytes). We set timeout on the actual request socket
    # in setup() so a slow client fails the read in N seconds.
    # See: https://docs.python.org/3/library/socketserver.html#socketserver.BaseServer.timeout
    timeout = 30

    def setup(self):
        super().setup()
        # Defensive: also set on the raw socket in case `timeout` class
        # attr isn't honored by the thread dispatch.
        if hasattr(self, "request") and self.request is not None:
            try:
                self.request.settimeout(self.timeout)
            except OSError:
                pass

    def _get_cors_origin(self):
        origin = self.headers.get("Origin", "")
        if origin in ALLOWED_ORIGINS or not origin:
            return origin if origin in ALLOWED_ORIGINS else ""
        return ""

    def _send_json(self, status, body):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("X-Content-Type-Options", "nosniff")
        # Stdlib BaseHTTPRequestHandler defaults to HTTP/1.0, which means
        # connections are closed after each request. Tell the client
        # explicitly so it doesn't try to reuse the connection and get
        # connection-reset errors on the second request.
        self.send_header("Connection", "close")
        cors = self._get_cors_origin()
        if cors:
            self.send_header("Access-Control-Allow-Origin", cors)
            self.send_header("Vary", "Origin")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PATCH, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(body, ensure_ascii=False).encode("utf-8"))

    def _send_error(self, status, msg):
        self._send_json(status, {"error": msg, "status": status})

    def _validate_title(self, title):
        if not isinstance(title, str):
            return None, "title must be a string"
        title = title.strip()
        if not title:
            return None, "title cannot be empty"
        if len(title) > MAX_TITLE_LEN:
            return None, f"title too long (max {MAX_TITLE_LEN} chars)"
        return title, None

    def _validate_tag(self, tag):
        if not isinstance(tag, str):
            return None, "tag must be a string"
        tag = tag.strip().lower()
        if not tag:
            return None, "tag cannot be empty"
        if not TAG_PATTERN.match(tag):
            return None, f"tag must match {TAG_PATTERN.pattern}"
        return tag, None

    def _read_json(self):
        """Read and parse JSON body, with size limit and error handling."""
        try:
            length = int(self.headers.get("Content-Length", 0))
        except (ValueError, TypeError):
            self._send_error(411, "missing or invalid Content-Length")
            return None
        if length < 0:
            self._send_error(400, "invalid Content-Length")
            return None
        if length > MAX_BODY_BYTES:
            self._send_error(413, f"body too large (max {MAX_BODY_BYTES} bytes)")
            return None
        if length == 0:
            return {}
        try:
            raw = self.rfile.read(length)
        except OSError as e:
            self._send_error(400, "read error")
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError as e:
            self._send_error(400, "invalid JSON")
            return None

    def do_OPTIONS(self):
        # CORS preflight. RFC 7230 §3.3.2: 204 responses MUST NOT include
        # a message body. We send the CORS headers via _send_json, which
        # writes 'Content-Type: application/json' + 'Content-Length: 2'
        # (for '{}') and then writes '{}'. That violates RFC. Fix: for 204
        # specifically, skip the body and use send_response + headers only.
        cors = self._get_cors_origin()
        if not cors:
            self.send_response(403)
            self.end_headers()
            return
        # 204 No Content — no body, no Content-Type/Content-Length
        self.send_response(204)
        self.send_header("Connection", "close")
        if cors:
            self.send_header("Access-Control-Allow-Origin", cors)
            self.send_header("Vary", "Origin")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PATCH, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Max-Age", "86400")
        self.end_headers()

    def do_GET(self):
        if self.path == "/api/todos":
            self._send_json(200, TODOS)
        elif self.path.startswith("/api/todos/"):
            # GET /api/todos/{id} — single-todo lookup
            parts = self.path.strip("/").split("/")
            if len(parts) != 3 or parts[0] != "api" or parts[1] != "todos":
                self._send_error(404, "not found")
                return
            try:
                todo_id = int(parts[2])
            except ValueError:
                self._send_error(400, "id must be integer")
                return
            for t in TODOS:
                if t["id"] == todo_id:
                    self._send_json(200, t)
                    return
            self._send_error(404, f"todo {todo_id} not found")
        elif self.path == "/api/tags":
            tags = sorted({t["tag"] for t in TODOS})
            self._send_json(200, tags)
        elif self.path == "/api/health":
            self._send_json(200, {"status": "ok", "ts": datetime.now().isoformat()})
        else:
            self._send_error(404, "not found")

    def do_POST(self):
        if self.path != "/api/todos":
            self._send_error(404, "not found")
            return
        data = self._read_json()
        if data is None:
            return  # _read_json already sent error
        title, err = self._validate_title(data.get("title", ""))
        if err:
            self._send_error(400, err)
            return
        tag, err = self._validate_tag(data.get("tag", "default"))
        if err:
            self._send_error(400, err)
            return
        global NEXT_ID
        with LOCK:
            new = {
                "id": NEXT_ID,
                "title": title,
                "tag": tag,
                "done": False,
                "created_at": datetime.now().strftime("%Y-%m-%d"),
            }
            TODOS.append(new)
            NEXT_ID += 1
        self._send_json(201, new)

    def do_PATCH(self):
        """Toggle done status: PATCH /api/todos/{id} with {"done": true|false}"""
        # Parse path
        parts = self.path.strip("/").split("/")
        if len(parts) != 3 or parts[0] != "api" or parts[1] != "todos":
            self._send_error(404, "not found")
            return
        try:
            todo_id = int(parts[2])
        except ValueError:
            self._send_error(400, "id must be integer")
            return
        data = self._read_json()
        if data is None:
            return
        if "done" not in data or not isinstance(data["done"], bool):
            self._send_error(400, "done must be boolean")
            return
        with LOCK:
            for t in TODOS:
                if t["id"] == todo_id:
                    t["done"] = data["done"]
                    self._send_json(200, t)
                    return
        self._send_error(404, f"todo {todo_id} not found")

    def do_DELETE(self):
        parts = self.path.strip("/").split("/")
        if len(parts) != 3 or parts[0] != "api" or parts[1] != "todos":
            self._send_error(404, "not found")
            return
        try:
            todo_id = int(parts[2])
        except ValueError:
            self._send_error(400, "id must be integer")
            return
        with LOCK:
            for i, t in enumerate(TODOS):
                if t["id"] == todo_id:
                    TODOS.pop(i)
                    self._send_json(200, {"deleted": todo_id})
                    return
        self._send_error(404, f"todo {todo_id} not found")

    def log_message(self, fmt, *args):
        # Quieter log; only status + path
        try:
            msg = fmt % args
            # Truncate noisy parts
            sys.stderr.write(f"[{datetime.now().strftime('%H:%M:%S')}] {self.address_string()} {msg}\n")
            sys.stderr.flush()
        except Exception:
            pass


def is_port_free(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) != 0


def main():
    port = int(os.environ.get("PORT", 8765))
    host = os.environ.get("HOST", "127.0.0.1")
    if host == "0.0.0.0":
        print("[!] WARNING: binding to 0.0.0.0 exposes this to the network.")
        print("    This is a MOCK server with no auth. Don't run in production.")

    if not is_port_free(port):
        print(f"[!] Port {port} is already in use. Is another instance running?")
        sys.exit(1)

    print(f"Starting Todo server on http://{host}:{port}")
    print("Endpoints:")
    print(f"  GET    http://{host}:{port}/api/todos")
    print(f"  GET    http://{host}:{port}/api/todos/{{id}}")
    print(f"  GET    http://{host}:{port}/api/tags")
    print(f"  GET    http://{host}:{port}/api/health")
    print(f"  POST   http://{host}:{port}/api/todos")
    print(f"  PATCH  http://{host}:{port}/api/todos/{{id}}")
    print(f"  DELETE http://{host}:{port}/api/todos/{{id}}")
    print()
    print("Press Ctrl+C to stop.")

    try:
        server = ThreadingHTTPServer((host, port), TodoHandler)
    except OSError as e:
        print(f"[!] Failed to bind: {e}")
        sys.exit(1)
    # Defense-in-depth: select-poll timeout (the actual slowloris
    # protection is the per-connection socket timeout set in TodoHandler).
    # Kept here as a backstop in case some handler subclass forgets to
    # call super().setup().
    server.timeout = 30
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()

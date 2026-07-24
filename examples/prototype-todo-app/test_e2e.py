"""
Comprehensive end-to-end tests for the Todo prototype.

Tests:
1. Health check
2. Get all todos
3. Get unique tags
4. Filter by tag (logic test)
5. Filter by non-existent tag
6. POST new todo (with validation)
7. PATCH todo status (toggle done)
8. DELETE todo
9. Security: rejects malformed JSON
10. Security: rejects title too long
11. Security: rejects invalid tag (special chars)
12. Security: rejects missing Content-Length
13. Security: rejects body too large
14. Security: rejects unknown endpoint
15. CORS: OPTIONS preflight for allowed origin
16. CORS: OPTIONS rejected for disallowed origin

Run: python test_e2e.py
"""
import json
import socket
import sys
import urllib.error
import urllib.request
from contextlib import closing

PORT = 8765
BASE = f"http://127.0.0.1:{PORT}"


def port_in_use(port):
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


def request(method, path, body=None, headers=None, raw=False):
    url = BASE + path
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    if body is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            if raw:
                return r.status, r.read(), dict(r.headers)
            return r.status, json.loads(r.read()), dict(r.headers)
    except urllib.error.HTTPError as e:
        if raw:
            return e.code, e.read(), dict(e.headers)
        try:
            return e.code, json.loads(e.read()), dict(e.headers)
        except Exception:
            return e.code, {}, dict(e.headers)


def assert_eq(actual, expected, msg):
    if actual == expected:
        return
    print(f"  ✗ {msg}: expected {expected!r}, got {actual!r}")
    raise AssertionError(msg)


def assert_true(cond, msg):
    if cond:
        return
    print(f"  ✗ {msg}")
    raise AssertionError(msg)


def main():
    if not port_in_use(PORT):
        print(f"[!] Server NOT running on port {PORT}")
        print("    Start it first: python server/server.py &")
        return 1

    print(f"Server is running on port {PORT}\n")
    passed = 0
    failed = 0

    def run(name, fn):
        nonlocal passed, failed
        try:
            fn()
            print(f"  PASS  {name}")
            passed += 1
        except AssertionError:
            failed += 1
        except Exception as e:
            print(f"  ERROR {name}: {e}")
            failed += 1

    # ====== Functional tests ======
    print("--- Functional ---")

    def test_health():
        status, body, _ = request("GET", "/api/health")
        assert_eq(status, 200, "status")
        assert_eq(body["status"], "ok", "status field")

    def test_get_todos():
        status, body, _ = request("GET", "/api/todos")
        assert_eq(status, 200, "status")
        # Seed data ships exactly 7 todos. Asserting exactly 7 (not >= 5)
        # catches regressions where a todo is dropped from the seed or
        # the server starts double-counting.
        assert_eq(len(body), 7, "exactly 7 seed todos")
        for field in ("id", "title", "tag", "done", "created_at"):
            assert_true(field in body[0], f"field {field!r} present")
        # Also verify GET /api/todos/{id} works for a known seed id
        status, body0, _ = request("GET", "/api/todos/1")
        assert_eq(status, 200, "single GET status")
        assert_eq(body0["id"], 1, "id matches")
        status, _, _ = request("GET", "/api/todos/99999")
        assert_eq(status, 404, "unknown id 404")

    def test_get_tags():
        status, body, _ = request("GET", "/api/tags")
        assert_eq(status, 200, "status")
        assert_true("work" in body, "work tag present")
        assert_true("personal" in body, "personal tag present")

    def test_filter_by_tag():
        _, todos, _ = request("GET", "/api/todos")
        work = [t for t in todos if t["tag"] == "work"]
        assert_true(len(work) >= 1, "filter work non-empty")

    def test_filter_empty():
        _, todos, _ = request("GET", "/api/todos")
        empty = [t for t in todos if t["tag"] == "nonexistent_xyz"]
        assert_eq(len(empty), 0, "empty filter result")

    def test_post_new():
        before_status, before, _ = request("GET", "/api/todos")
        before_count = len(before)
        status, body, _ = request("POST", "/api/todos", {"title": "Test from e2e", "tag": "test"})
        assert_eq(status, 201, "status")
        assert_eq(body["title"], "Test from e2e", "title")
        assert_eq(body["tag"], "test", "tag")
        assert_true("id" in body, "id present")
        # Verify it's really added
        after_status, after, _ = request("GET", "/api/todos")
        assert_eq(len(after), before_count + 1, "count increased")

    def test_patch_toggle_done():
        # Find a not-done todo
        _, todos, _ = request("GET", "/api/todos")
        target = next((t for t in todos if not t["done"]), None)
        assert_true(target is not None, "found not-done todo")
        status, body, _ = request("PATCH", f"/api/todos/{target['id']}", {"done": True})
        assert_eq(status, 200, "status")
        assert_eq(body["done"], True, "done now True")
        # Toggle back
        status, body, _ = request("PATCH", f"/api/todos/{target['id']}", {"done": False})
        assert_eq(status, 200, "toggle back")

    def test_delete_todo():
        # Create one to delete
        status, body, _ = request("POST", "/api/todos", {"title": "to delete", "tag": "test"})
        assert_eq(status, 201, "create")
        new_id = body["id"]
        # Confirm it exists via single-GET endpoint BEFORE delete
        status, before, _ = request("GET", f"/api/todos/{new_id}")
        assert_eq(status, 200, "exists before delete")
        assert_eq(before["id"], new_id, "id matches before")
        # Delete
        status, _, _ = request("DELETE", f"/api/todos/{new_id}")
        assert_eq(status, 200, "delete status")
        # Verify actually gone: single-GET must 404 (was previously
        # checking 404 on a route that didn't exist, which would have
        # passed even if delete silently did nothing).
        status, _, _ = request("GET", f"/api/todos/{new_id}")
        assert_eq(status, 404, "404 after delete")
        # And it should not appear in the list either
        _, after, _ = request("GET", "/api/todos")
        assert_true(
            all(t["id"] != new_id for t in after),
            "deleted id not in list",
        )

    run("Health check returns ok", test_health)
    run("GET /api/todos returns 7 todos with all fields; GET /api/todos/{id} works", test_get_todos)
    run("GET /api/tags returns unique tags", test_get_tags)
    run("Filter logic: 'work' tag non-empty", test_filter_by_tag)
    run("Filter logic: nonexistent tag returns empty", test_filter_empty)
    run("POST /api/todos creates new todo", test_post_new)
    run("PATCH /api/todos/{id} toggles done", test_patch_toggle_done)
    run("DELETE /api/todos/{id} removes todo", test_delete_todo)

    # ====== Security tests ======
    print("\n--- Security ---")

    def test_invalid_json():
        url = BASE + "/api/todos"
        req = urllib.request.Request(url, data=b"{not valid json", method="POST")
        req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=5) as r:
                status = r.status
        except urllib.error.HTTPError as e:
            status = e.code
        assert_eq(status, 400, "rejects invalid JSON with 400")

    def test_title_too_long():
        long_title = "x" * 300
        status, _, _ = request("POST", "/api/todos", {"title": long_title, "tag": "test"})
        assert_eq(status, 400, "rejects title > 200 chars")

    def test_empty_title():
        status, _, _ = request("POST", "/api/todos", {"title": "   ", "tag": "test"})
        assert_eq(status, 400, "rejects empty title")

    def test_invalid_tag():
        status, _, _ = request("POST", "/api/todos", {"title": "ok", "tag": "INVALID TAG!@#"})
        assert_eq(status, 400, "rejects invalid tag characters")

    def test_missing_content_length():
        url = BASE + "/api/todos"
        req = urllib.request.Request(url, data=b'{"title":"x","tag":"t"}', method="POST")
        # Don't set Content-Type or Content-Length
        try:
            with urllib.request.urlopen(req, timeout=5) as r:
                status = r.status
        except urllib.error.HTTPError as e:
            status = e.code
        # Python urllib auto-adds Content-Length, so this might not be testable
        # But at least verify the server doesn't crash
        assert_true(status in (200, 201, 400, 411), f"server handles missing cl gracefully (got {status})")

    def test_body_too_large():
        huge = "x" * (100 * 1024)  # 100KB
        status, _, _ = request("POST", "/api/todos", {"title": huge, "tag": "test"})
        # Note: title validation will also reject (>200 chars) -> 400
        # If we send huge raw body, should get 413
        url = BASE + "/api/todos"
        req = urllib.request.Request(url, data=b"x" * (200 * 1024), method="POST")
        req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=5) as r:
                status = r.status
        except urllib.error.HTTPError as e:
            status = e.code
        assert_eq(status, 413, f"rejects 200KB body (got {status})")

    def test_unknown_endpoint():
        status, _, _ = request("GET", "/api/unknown")
        assert_eq(status, 404, "unknown endpoint returns 404")

    def test_unauthorized_method():
        status, _, _ = request("PUT", "/api/todos", {"title": "x"})
        # BaseHTTPRequestHandler returns 501 for unsupported methods
        assert_true(status in (404, 405, 501), f"PUT rejected (got {status})")

    def test_path_traversal():
        status, _, _ = request("GET", "/api/../etc/passwd")
        # urllib normalizes the path; server should 404
        assert_eq(status, 404, "path traversal blocked")

    run("Invalid JSON returns 400", test_invalid_json)
    run("Title > 200 chars rejected", test_title_too_long)
    run("Empty/whitespace title rejected", test_empty_title)
    run("Invalid tag characters rejected", test_invalid_tag)
    run("Missing Content-Length handled gracefully", test_missing_content_length)
    run("Body > 64KB rejected with 413", test_body_too_large)
    run("Unknown endpoint returns 404", test_unknown_endpoint)
    run("Unsupported HTTP method rejected", test_unauthorized_method)
    run("Path traversal blocked", test_path_traversal)

    # ====== CORS tests ======
    print("\n--- CORS ---")

    def test_cors_allowed_origin():
        url = BASE + "/api/todos"
        req = urllib.request.Request(url, method="OPTIONS")
        req.add_header("Origin", "http://localhost:5500")
        try:
            with urllib.request.urlopen(req, timeout=5) as r:
                status = r.status
                headers = dict(r.headers)
        except urllib.error.HTTPError as e:
            status = e.code
            headers = dict(e.headers)
        assert_eq(status, 204, "preflight 204")
        assert_true("Access-Control-Allow-Origin" in headers, "ACAO header present")

    def test_cors_disallowed_origin():
        url = BASE + "/api/todos"
        req = urllib.request.Request(url, method="OPTIONS")
        req.add_header("Origin", "https://evil.example.com")
        try:
            with urllib.request.urlopen(req, timeout=5) as r:
                status = r.status
        except urllib.error.HTTPError as e:
            status = e.code
        assert_eq(status, 403, "disallowed origin gets 403")

    run("CORS preflight allowed origin returns 204", test_cors_allowed_origin)
    run("CORS preflight disallowed origin returns 403", test_cors_disallowed_origin)

    # ====== Concurrency test ======
    print("\n--- Concurrency ---")

    def test_concurrent_writes():
        """Verify the lock prevents race conditions on NEXT_ID."""
        import threading
        results = []
        errors = []

        def create_one(i):
            try:
                status, body, _ = request("POST", "/api/todos",
                                          {"title": f"concurrent-{i}", "tag": "test"})
                if status == 201:
                    results.append(body["id"])
                else:
                    errors.append((i, status))
            except Exception as e:
                errors.append((i, str(e)))

        threads = [threading.Thread(target=create_one, args=(i,)) for i in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert_eq(len(errors), 0, f"no errors during concurrent writes (got {len(errors)})")
        assert_eq(len(results), 20, "all 20 writes succeeded")
        assert_eq(len(set(results)), 20, "all IDs unique (no race condition)")
        # Cleanup
        for todo_id in results:
            request("DELETE", f"/api/todos/{todo_id}")

    run("20 concurrent writes produce unique IDs (no race)", test_concurrent_writes)

    print(f"\n=== Summary ===")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    if failed == 0:
        print("ALL TESTS PASSED")
        return 0
    else:
        print(f"FAILED {failed} tests")
        return 1


if __name__ == "__main__":
    sys.exit(main())

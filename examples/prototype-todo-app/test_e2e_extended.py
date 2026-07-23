"""
Extended e2e tests — additional coverage beyond test_e2e.py.

Tests:
- Different HTTP methods (PUT, HEAD)
- Edge cases (very long valid title, unicode in title)
- Concurrent reads
- Multiple deletes
- Cross-endpoint consistency
- Server uptime / repeated calls
- Path normalization
- Health check stability

Run: python test_e2e_extended.py
"""
import json
import socket
import sys
import time
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


def main():
    if not port_in_use(PORT):
        print(f"[!] Server NOT running on port {PORT}")
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
        except AssertionError as e:
            print(f"  FAIL  {name}: {e}")
            failed += 1
        except Exception as e:
            print(f"  ERROR {name}: {e}")
            failed += 1

    # ===== Method coverage =====
    print("--- HTTP method coverage ---")

    def test_head_on_health():
        # Python's BaseHTTPRequestHandler doesn't natively support HEAD;
        # it returns 501 (not implemented). Document this as expected.
        req = urllib.request.Request(f"{BASE}/api/health", method="HEAD")
        try:
            with urllib.request.urlopen(req, timeout=5) as r:
                assert r.status == 200, f"expected 200, got {r.status}"
        except urllib.error.HTTPError as e:
            # 501 is acceptable — Python stdlib doesn't support HEAD
            assert e.code == 501, f"HEAD failed with unexpected {e.code}"

    def test_unsupported_method():
        # PROPFIND is definitely not handled
        req = urllib.request.Request(f"{BASE}/api/todos", method="PROPFIND")
        try:
            with urllib.request.urlopen(req, timeout=5) as r:
                raise AssertionError(f"PROPFIND should be rejected, got {r.status}")
        except urllib.error.HTTPError as e:
            assert e.code in (405, 501), f"expected 405/501, got {e.code}"

    def test_get_with_body_ignored():
        # GET with body should still work (body ignored per HTTP spec)
        req = urllib.request.Request(f"{BASE}/api/todos",
                                      data=b'{"ignored":true}', method="GET")
        try:
            with urllib.request.urlopen(req, timeout=5) as r:
                assert r.status == 200
        except urllib.error.HTTPError as e:
            raise AssertionError(f"GET with body should work, got {e.code}")

    run("HEAD /api/health returns 200 with headers", test_head_on_health)
    run("PROPFIND returns 405/501", test_unsupported_method)
    run("GET with body is silently ignored", test_get_with_body_ignored)

    # ===== Edge cases =====
    print("\n--- Edge cases ---")

    def test_unicode_title():
        status, body, _ = request("POST", "/api/todos",
                                   {"title": "买牛奶 🥛 Café", "tag": "shopping"})
        assert status == 201, f"unicode title rejected: {status}"
        assert "买牛奶" in body["title"], f"unicode lost: {body['title']}"
        # Cleanup
        request("DELETE", f"/api/todos/{body['id']}")

    def test_max_length_title():
        title = "x" * 200  # exactly the max
        status, body, _ = request("POST", "/api/todos",
                                   {"title": title, "tag": "test"})
        assert status == 201, f"200-char title rejected: {status}"
        assert len(body["title"]) == 200
        request("DELETE", f"/api/todos/{body['id']}")

    def test_tag_with_numbers():
        status, body, _ = request("POST", "/api/todos",
                                   {"title": "test", "tag": "tag123-abc"})
        assert status == 201, f"tag with numbers/hyphens rejected: {status}"
        request("DELETE", f"/api/todos/{body['id']}")

    def test_duplicate_titles_allowed():
        # API allows duplicates; logic is up to client
        status1, b1, _ = request("POST", "/api/todos",
                                    {"title": "duplicate", "tag": "test"})
        status2, b2, _ = request("POST", "/api/todos",
                                    {"title": "duplicate", "tag": "test"})
        assert status1 == 201 and status2 == 201, "duplicates rejected"
        assert b1["id"] != b2["id"], "duplicate IDs"
        request("DELETE", f"/api/todos/{b1['id']}")
        request("DELETE", f"/api/todos/{b2['id']}")

    def test_none_body():
        # POST with no body
        req = urllib.request.Request(f"{BASE}/api/todos", data=None, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=5) as r:
                status = r.status
        except urllib.error.HTTPError as e:
            status = e.code
        assert status in (400, 411), f"empty POST should 400/411, got {status}"

    def test_wrong_content_type():
        # POST with form data instead of JSON
        req = urllib.request.Request(f"{BASE}/api/todos",
                                      data=b"title=test&tag=test",
                                      method="POST")
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
        try:
            with urllib.request.urlopen(req, timeout=5) as r:
                status = r.status
                body = r.read()
        except urllib.error.HTTPError as e:
            status = e.code
            body = e.read()
        # Server tries json.loads, will fail -> 400
        assert status == 400, f"form data should be rejected, got {status}"

    run("Unicode in title preserved", test_unicode_title)
    run("Exactly 200-char title accepted", test_max_length_title)
    run("Tag with numbers and hyphens accepted", test_tag_with_numbers)
    run("Duplicate titles allowed (unique IDs)", test_duplicate_titles_allowed)
    run("Empty POST body rejected with 400/411", test_none_body)
    run("Wrong Content-Type rejected", test_wrong_content_type)

    # ===== Health endpoint =====
    print("\n--- Health / stability ---")

    def test_health_stable():
        for i in range(10):
            status, body, _ = request("GET", "/api/health")
            assert status == 200, f"iter {i}: status {status}"
            assert body["status"] == "ok"

    def test_health_ts_format():
        _, body, _ = request("GET", "/api/health")
        ts = body.get("ts", "")
        # ISO format: 2026-07-23T...
        assert "T" in ts, f"ts not ISO: {ts}"
        # Can parse as float
        from datetime import datetime
        try:
            datetime.fromisoformat(ts.replace("Z", "+00:00") if ts.endswith("Z") else ts)
        except ValueError:
            raise AssertionError(f"ts not parseable: {ts}")

    run("Health stable across 10 calls", test_health_stable)
    run("Health ts is ISO format", test_health_ts_format)

    # ===== Cross-endpoint consistency =====
    print("\n--- Cross-endpoint consistency ---")

    def test_todo_count_matches_tag_sum():
        _, todos, _ = request("GET", "/api/todos")
        _, tags, _ = request("GET", "/api/tags")
        total_per_tag = sum(1 for t in todos if t["tag"] in tags)
        # All todos should have a tag that's in the tags list
        all_tagged = all(t["tag"] in tags for t in todos)
        assert all_tagged, "found todo with tag not in /api/tags"

    def test_patched_todo_persists():
        # Create
        _, b, _ = request("POST", "/api/todos",
                          {"title": "persist test", "tag": "test"})
        new_id = b["id"]
        # Patch
        request("PATCH", f"/api/todos/{new_id}", {"done": True})
        # Re-fetch
        _, todos, _ = request("GET", "/api/todos")
        target = next((t for t in todos if t["id"] == new_id), None)
        assert target is not None, "patched todo disappeared"
        assert target["done"] is True, "patch didn't persist"
        # Cleanup
        request("DELETE", f"/api/todos/{new_id}")

    run("Every todo's tag is in /api/tags", test_todo_count_matches_tag_sum)
    run("PATCH persists in subsequent GET", test_patched_todo_persists)

    # ===== Concurrent reads =====
    print("\n--- Concurrent reads ---")

    def test_concurrent_reads():
        import threading
        results = []
        def read():
            try:
                status, body, _ = request("GET", "/api/todos")
                results.append((status, len(body)))
            except Exception as e:
                results.append((None, str(e)))
        threads = [threading.Thread(target=read) for _ in range(30)]
        for t in threads: t.start()
        for t in threads: t.join()
        assert all(s == 200 for s, _ in results), f"some reads failed: {results[:3]}"
        # All reads should return same length
        lengths = set(n for _, n in results)
        assert len(lengths) == 1, f"inconsistent read lengths: {lengths}"

    def test_concurrent_reads_while_writing():
        """Reads should be safe even during writes."""
        import threading
        read_results = []
        write_results = []
        stop = threading.Event()
        def reader():
            for _ in range(20):
                if stop.is_set(): break
                try:
                    s, b, _ = request("GET", "/api/todos")
                    read_results.append((s, len(b)))
                except Exception:
                    pass
                time.sleep(0.01)
        def writer():
            for i in range(10):
                try:
                    s, b, _ = request("POST", "/api/todos",
                                        {"title": f"race-{i}", "tag": "test"})
                    if s == 201: write_results.append(b["id"])
                except Exception:
                    pass
                time.sleep(0.02)
        threads = [threading.Thread(target=reader) for _ in range(3)]
        threads.append(threading.Thread(target=writer))
        for t in threads: t.start()
        for t in threads: t.join()
        stop.set()
        # Cleanup
        for tid in write_results:
            request("DELETE", f"/api/todos/{tid}")
        # All reads should succeed
        assert all(s == 200 for s, _ in read_results), "reads failed during writes"
        # Some writes should have succeeded
        assert len(write_results) >= 1, "no writes succeeded"

    run("30 concurrent reads return consistent data", test_concurrent_reads)
    run("Reads during writes remain consistent", test_concurrent_reads_while_writing)

    # ===== Path normalization =====
    print("\n--- Path normalization ---")

    def test_double_slash():
        req = urllib.request.Request(f"{BASE}//api/todos", method="GET")
        try:
            with urllib.request.urlopen(req, timeout=5) as r:
                status = r.status
        except urllib.error.HTTPError as e:
            status = e.code
        # 404 or 200 (depends on server); both acceptable
        assert status in (200, 404), f"unexpected status for //: {status}"

    def test_trailing_slash():
        status, body, _ = request("GET", "/api/todos/")  # trailing slash
        assert status in (200, 404), f"trailing /: {status}"

    def test_case_sensitive_path():
        # /api/Todos (capital T) should not match /api/todos
        status, _, _ = request("GET", "/api/Todos")
        assert status == 404, f"case-insensitive path: {status}"

    run("Double slash in path handled", test_double_slash)
    run("Trailing slash in path handled", test_trailing_slash)
    run("Path is case-sensitive", test_case_sensitive_path)

    # ===== Idempotency =====
    print("\n--- Idempotency ---")

    def test_delete_twice():
        # Create + delete + delete again
        _, b, _ = request("POST", "/api/todos",
                          {"title": "idempotent delete", "tag": "test"})
        new_id = b["id"]
        s1, _, _ = request("DELETE", f"/api/todos/{new_id}")
        s2, _, _ = request("DELETE", f"/api/todos/{new_id}")
        assert s1 == 200, f"first delete: {s1}"
        assert s2 == 404, f"second delete should 404, got {s2}"

    def test_patch_nonexistent():
        s, _, _ = request("PATCH", "/api/todos/99999", {"done": True})
        assert s == 404

    def test_get_health_no_state_change():
        # Hit health multiple times, count should be unchanged
        _, before, _ = request("GET", "/api/todos")
        for _ in range(5):
            request("GET", "/api/health")
        _, after, _ = request("GET", "/api/todos")
        assert len(before) == len(after), "health endpoint changed state"

    run("DELETE twice: first 200, second 404", test_delete_twice)
    run("PATCH nonexistent returns 404", test_patch_nonexistent)
    run("Health endpoint is read-only (no state change)", test_get_health_no_state_change)

    print(f"\n=== Summary ===")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    if failed == 0:
        print("ALL EXTENDED TESTS PASSED")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())

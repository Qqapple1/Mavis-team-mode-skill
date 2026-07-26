"""Additional e2e tests for the prototype server (Phase 3 demo)."""
import json
import socket
import sys
import urllib.error
import urllib.request
from contextlib import closing

PORT = 8765
BASE = f"http://127.0.0.1:{PORT}"


def port_in_use():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        return s.connect_ex(("127.0.0.1", PORT)) == 0


def request(method, path, body=None):
    url = BASE + path
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        try: return e.code, json.loads(e.read())
        except: return e.code, {}


def main():
    if not port_in_use():
        print("[!] server not running")
        return 1
    passed = failed = 0

    def run(name, fn):
        nonlocal passed, failed
        try: fn(); print(f"  PASS {name}"); passed += 1
        except AssertionError as e: print(f"  FAIL {name}: {e}"); failed += 1
        except Exception as e: print(f"  ERROR {name}: {e}"); failed += 1

    # 1. 慢速连接
    def test_slow_request():
        # send a POST with 100ms delay between headers
        s = socket.socket()
        s.settimeout(5)
        s.connect(("127.0.0.1", PORT))
        # send first byte
        s.send(b"PO")
        # wait, then continue
        import time; time.sleep(0.05)
        s.send(b"ST /api/todos HTTP/1.1\r\nHost: localhost\r\nContent-Length: 0\r\n\r\n")
        # small read
        time.sleep(0.1)
        data = s.recv(1024)
        s.close()
        assert b"HTTP/" in data, f"no HTTP response: {data[:50]!r}"
    run("slow client doesn't hang server", test_slow_request)

    # 2. Idempotency
    def test_post_with_same_data_twice():
        # Same content, two POSTs -> two different IDs
        s1, b1 = request("POST", "/api/todos", {"title": "idem", "tag": "test"})
        s2, b2 = request("POST", "/api/todos", {"title": "idem", "tag": "test"})
        assert s1 == 201 and s2 == 201
        assert b1["id"] != b2["id"], "duplicate IDs"
        # cleanup
        request("DELETE", f"/api/todos/{b1['id']}")
        request("DELETE", f"/api/todos/{b2['id']}")
    run("POST same data twice gets different IDs", test_post_with_same_data_twice)

    # 3. Filter
    def test_tags_endpoint_sorted_unique():
        s, tags = request("GET", "/api/tags")
        assert s == 200
        # 必须 sorted
        assert tags == sorted(tags), f"not sorted: {tags}"
        # 必须 unique
        assert len(tags) == len(set(tags)), f"duplicates: {tags}"
    run("/api/tags returns sorted unique", test_tags_endpoint_sorted_unique)

    # 4. Health response 字段
    def test_health_contains_iso_ts():
        s, body = request("GET", "/api/health")
        assert s == 200
        assert "status" in body and body["status"] == "ok"
        assert "ts" in body
        # ISO format: 2026-07-23T...
        assert "T" in body["ts"], f"ts not ISO: {body['ts']}"
    run("/api/health has ISO ts", test_health_contains_iso_ts)

    # 5. 大空白 title (200 chars)
    def test_max_length_boundary():
        s, b = request("POST", "/api/todos",
                        {"title": "x" * 200, "tag": "test"})
        assert s == 201, f"max len rejected: {s}"
        assert len(b["title"]) == 200
        request("DELETE", f"/api/todos/{b['id']}")
    run("Title at exactly 200 chars accepted", test_max_length_boundary)

    print(f"\nPassed: {passed}, Failed: {failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

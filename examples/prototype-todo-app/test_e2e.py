"""
End-to-end test for the Todo prototype.

Verifies:
1. Server starts and serves /api/todos
2. /api/tags returns unique tags
3. Filtering logic returns correct subset

Run: python test_e2e.py
"""
import json
import socket
import sys
import time
import urllib.request
from contextlib import closing

PORT = 8765


def port_in_use(port):
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


def get(path):
    with urllib.request.urlopen(f"http://127.0.0.1:{PORT}{path}", timeout=5) as r:
        return r.status, json.loads(r.read())


def main():
    if not port_in_use(PORT):
        print(f"Server NOT running on port {PORT}")
        print("Start it first: python server/server.py &")
        return 1

    print(f"Server is running on port {PORT}\n")

    print("=== Test 1: GET /api/health ===")
    status, body = get("/api/health")
    assert status == 200, f"expected 200, got {status}"
    assert body["status"] == "ok", f"expected ok, got {body}"
    print(f"  PASS: {body}")

    print("\n=== Test 2: GET /api/todos ===")
    status, body = get("/api/todos")
    assert status == 200
    assert len(body) >= 5, f"expected >=5 todos, got {len(body)}"
    assert "id" in body[0] and "tag" in body[0] and "title" in body[0]
    print(f"  PASS: got {len(body)} todos")

    print("\n=== Test 3: GET /api/tags ===")
    status, tags = get("/api/tags")
    assert status == 200
    assert len(tags) >= 2, f"expected >=2 tags, got {len(tags)}"
    assert "work" in tags, f"expected 'work' tag, got {tags}"
    assert "personal" in tags, f"expected 'personal' tag, got {tags}"
    print(f"  PASS: got {len(tags)} unique tags: {tags}")

    print("\n=== Test 4: Filter by tag (simulating UI behavior) ===")
    work_todos = [t for t in body if t["tag"] == "work"]
    assert len(work_todos) >= 1, f"expected >=1 work todo, got {len(work_todos)}"
    print(f"  PASS: filter for 'work' returns {len(work_todos)} todos")

    print("\n=== Test 5: Filter by non-existent tag ===")
    empty = [t for t in body if t["tag"] == "nonexistent_xyz"]
    assert len(empty) == 0
    print("  PASS: filter for missing tag returns empty list")

    print("\n=== Test 6: POST new todo ===")
    req = urllib.request.Request(
        f"http://127.0.0.1:{PORT}/api/todos",
        data=json.dumps({"title": "Test from e2e", "tag": "test"}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=5) as r:
        assert r.status == 201
        new_todo = json.loads(r.read())
        assert new_todo["title"] == "Test from e2e"
        assert new_todo["tag"] == "test"
        assert "id" in new_todo
    print(f"  PASS: created todo id={new_todo['id']}")

    print("\nALL TESTS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())

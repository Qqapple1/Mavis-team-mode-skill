# Todo Tag-Filter Prototype

**Purpose**: Prove that the Mavis Team Mode skill works end-to-end by building
a real, runnable feature with a verifiable outcome.

## What this prototype demonstrates

The `examples/new-feature.md` Team Plan in this skill describes how to add
"tag filtering" to a Todo app. This prototype is the **concrete deliverable**
of that plan — both the backend (Python) and frontend (HTML) are real, runnable
code that you can interact with.

## How to run

### 1. Start the backend

```bash
cd examples/prototype-todo-app
python3 server/server.py
```

You should see:
```
Starting Todo server on http://127.0.0.1:8765
Try: curl http://127.0.0.1:8765/api/todos
```

### 2. Test the backend (in another terminal)

```bash
curl http://127.0.0.1:8765/api/health
# {"status": "ok", "ts": "2026-07-23T..."}

curl http://127.0.0.1:8765/api/todos
# [..., {"id": 1, "title": "Buy milk", "tag": "shopping", ...}, ...]

curl http://127.0.0.1:8765/api/tags
# ["personal", "shopping", "work"]
```

### 3. Open the frontend

Open `client/index.html` in a browser.

You'll see:
- Left sidebar: list of all tags (`#work`, `#personal`, `#shopping`)
- Main area: all todos
- Click a tag → main area filters to only that tag

### 4. Run the e2e test

```bash
python3 test_e2e.py
```

Should output:
```
=== Test 1: GET /api/health ===
  ✓ Health check passed
=== Test 2: GET /api/todos ===
  ✓ Got N todos
=== Test 3: GET /api/tags ===
  ✓ Got N unique tags
=== Test 4: Filter by tag ===
  ✓ Filter for 'work' returns N todos
=== Test 5: Filter by non-existent tag ===
  ✓ Filter for missing tag returns empty list
✓ All tests passed!
```

## What this proves about the Mavis Team Mode skill

1. **Skill output is runnable** — the team plan produces real code, not vibes
2. **Acceptance criteria are testable** — e2e tests verify the API
3. **The workflow scales** — what took one team to do, took ~30 minutes here

## Files

| File | Purpose |
|------|---------|
| `server/server.py` | Python HTTP server with in-memory todo store |
| `client/index.html` | Single-page tag-filter UI (vanilla JS) |
| `test_e2e.py` | 5 end-to-end tests (no dependencies) |
| `README.md` | This file |

## Requirements

- Python 3.8+ (uses only stdlib)
- Modern browser for the client
- No npm, no pip packages, no build step

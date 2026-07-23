# ADR-002: Security Posture for the Prototype Server

**Status**: Accepted
**Date**: 2026-07-23

## Context

The skill ships a runnable Python HTTP server (`examples/prototype-todo-app/server/server.py`)
to demonstrate the workflow end-to-end. The server is a teaching example,
not a production application, but it must still be safe to run on a
developer's laptop without exposing them to avoidable risk.

## Decision

We apply defense-in-depth even to a "mock" server:

1. **Bind to localhost only** (default 127.0.0.1, not 0.0.0.0)
2. **Explicit CORS allowlist** (not `*`)
3. **Input validation** on all client-supplied fields
4. **Body size cap** (64KB) to prevent trivial DoS
5. **Thread-safe writes** via explicit `threading.Lock`
6. **Graceful 4xx/5xx** with structured JSON error responses
7. **Security headers** (`X-Content-Type-Options: nosniff`)

## Implementation details

### Input validation
- `title`: 1-200 characters, no leading/trailing whitespace
- `tag`: must match `^[a-z0-9][a-z0-9-]{0,49}$` (lowercase, digits, hyphens)

### CORS
```python
ALLOWED_ORIGINS = {
    "http://127.0.0.1:8765",
    "http://localhost:8765",
    "http://127.0.0.1:5500",  # VS Code Live Server
    "http://localhost:5500",
    "null",                    # file:// origin
}
```

### Threading
The `http.server` module is single-threaded by default. We use
`ThreadingHTTPServer` (instead of `HTTPServer`) to handle concurrent
requests. The in-memory `TODOS` list and `NEXT_ID` counter are
protected by a `threading.Lock`.

## Rejected alternatives

### Use `*` CORS
- Pro: zero config
- Con: trivial CSRF / data exfil vector in a real app

### Skip input validation
- Pro: simpler code
- Con: DoS via 1MB titles, XSS via stored payloads

### Run on 0.0.0.0 by default
- Pro: accessible from phone, other devices
- Con: zero-auth mock exposed to network
- We print a clear warning if user sets `HOST=0.0.0.0`

## What this prototype is NOT

- It is not a production-grade application
- It has no authentication
- It has no persistence (in-memory only)
- It has no rate limiting beyond Python's socket layer

For real applications, see the security checklist in the broader skill
documentation and follow OWASP guidelines.

## Verification

The `test_e2e.py` includes 9 security-specific tests:
- Invalid JSON rejected
- Title length cap enforced
- Tag character class enforced
- Body size cap enforced
- Path traversal blocked
- Unknown endpoints 404
- CORS preflight enforced
- Unsupported HTTP methods rejected
- Concurrent writes produce unique IDs (race-free)

## References

- OWASP API Security Top 10
- Python `http.server` documentation
- Mozilla Web Security guidelines

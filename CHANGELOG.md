# Changelog

All notable changes to this skill are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [1.3.0] - 2026-07-23

### Added
- `examples/prototype-todo-app/test_e2e_extended.py` — 21 additional e2e
  tests (HTTP method coverage, unicode, path normalization, idempotency,
  concurrent reads during writes)
- `examples/prototype-todo-app/client/index.html` — full web UI rewrite
  with input validation, error toasts, and tag filtering
- `scripts/benchmark_tokens.py` — measures skill load cost vs baseline
- `Makefile` — `make help/install/test/lint/info` shortcuts
- `docs/ARCHITECTURE.md` — flow diagram + Mermaid rendering + decision
  boundaries
- `index.html` — GitHub Pages-friendly landing page for repo root
- CI matrix: Ubuntu + macOS for shellcheck; Python 3.8-3.12 for syntax
- CI: 3x idempotency install loop, token benchmark step, stats report

### Changed
- `SKILL.md` Step 3: clarified that Leader can use Zcode's BUILT-IN
  `Explore`/`general-purpose` OR custom agents from `agents/`
- `docs/PERFORMANCE.md`: HONEST token numbers (skill costs ~74% MORE than
  inline baseline, but gives 2-2.5x wall-clock speedup from parallelism)
- `.shellcheckrc`: `shell=bash` directive, `external-sources`, `check-sourced`

### Fixed
- Documented that HEAD requests return 501 (Python stdlib limitation)
- Removed dead `_send_json` references in test_e2e_extended.py
- Server: POST with form data (not JSON) now returns 400, not 500

## [1.3.1] - 2026-07-23

### Added
- 2 more e2e tests: 100 serial writes + post-stress state consistency
  (total e2e now 23, all passing)
- docs/ADR-001 + docs/ADR-002 + docs/ARCHITECTURE + docs/PERFORMANCE now
  cross-link each other
- "Real-world testing" honesty note in SKILL.md `metadata.tested-on`

### Fixed
- SKILL.md `metadata.tested-on` no longer claims fake Zcode versions
  (`tested-on: [zcode-3.0.0, zcode-3.1.0, zcode-3.2.2]`) — replaced with
  what's actually verified (e2e 23/23 + skill format 22/22 + CI 9/9 jobs)
- SKILL.md `metadata.author` no longer falsely claims to be M3
- README/VALIDATION/INSTALL/agents/leader.md/references no longer
  reference the fake `/mavis-team-mode` slash command. Zcode skills
  use description-matching, not slash commands. (Caught during deep review.)
- examples/refactor-large-module.md: Subtask 3 and 4 now have full
  prompts (no more `[same structure as Subtask 2]` placeholders)
- examples/research-then-implement.md: invalid `type: explore + web`
  fixed — added `tools:` field for clarity
- references/deepseek-setup.md: removed fabricated claim that "Zcode
  has deep optimization for GLM-5.2 (1M context, code scene prompts)"
- server: added `Connection: close` response header to prevent client
  connection reuse on HTTP/1.0 (BaseHTTPRequestHandler default)
- validate.sh: `du -sk` now uses `-L` to follow symlinks, so the size
  sanity check works correctly when installed via symlink
- validate.sh: total-size threshold bumped 5-500KB → 5-1500KB (skill
  is now ~592KB with all the new docs/examples/tests)

## [1.2.0]
## [1.2.0] - 2026-07-23

### Added
- `scripts/validate_yaml.py` — pure-Python YAML frontmatter validator (no PyYAML dep)
- `docs/ADR-001-team-mode-recreation.md` — Architecture decision record
- `docs/ADR-002-security.md` — Security posture rationale
- `docs/PERFORMANCE.md` — Token efficiency + speedup benchmarks
- `SECURITY.md` — Vulnerability disclosure policy
- `.shellcheckrc` — ShellCheck configuration for CI
- GitHub Actions CI: shellcheck, bash -n, python -m py_compile,
  YAML validation, install --doctor, idempotency check
- install.sh: `--version`, `--doctor`, `--no-verify` options
- install.sh: NO_COLOR support + non-TTY detection
- install.sh: `MAVIS_TEAM_DIR`, `MAVIS_TEAM_REF` env vars for pinning
- install.sh: `safe_rm` helper for sandboxed FS

### Changed
- All agent files: multi-line YAML `|` description → single-line quoted
  (better tool compatibility, validates cleanly)
- install.sh: 1.1.0 → 1.2.0, complete rewrite with better error handling
- `examples/prototype-todo-app/server/server.py`: rewritten with
  defense-in-depth (CORS allowlist, input validation, body size cap,
  thread safety, PATCH/DELETE methods)

### Security
- Server: CORS allowlist (was `*`), explicit origin check
- Server: input validation on title (1-200 chars) and tag (regex)
- Server: 64KB body cap, 411/413/400 proper error responses
- Server: thread-safe writes via `threading.Lock`
- Server: `X-Content-Type-Options: nosniff` header
- install.sh: explicit checks for missing files, broken clone, etc.
- Prototype: warns explicitly if `HOST=0.0.0.0` (mock with no auth)

### Tests
- e2e tests: 6 → 20 (added security, CORS, concurrency tests)
- e2e tests: cover invalid JSON, oversized body, path traversal,
  bad tag chars, CORS preflight allowed/disallowed, 20-thread
  concurrent writes for race condition check

## [1.1.0] - 2026-07-23

### Added
- `scripts/install.sh` — One-line installer (clone + symlink + verify)
- `scripts/validate.sh` — Self-validation script (22 checks)
- `examples/prototype-todo-app/` — Real, runnable Todo app
- `INSTALL.md` — Standalone installation guide with 5 install methods
- `examples/` and `references/` now have frontmatter
- `version`, `license`, `metadata` fields added to all `agents/*.md`
- `allowed-tools` field added to `SKILL.md`
- `CONTRIBUTING.md`, `CHANGELOG.md`
- GitHub Actions CI for skill validation

### Changed
- `SKILL.md` description: multi-line YAML `|` → single-line quoted
- `README.md` improved with badges and quickstart

### Fixed
- `examples/prototype-todo-app/test_e2e.py` had unused `port` variable
  and wrong URL paths

## [1.0.0] - 2026-07-22

### Added
- Initial release
- `SKILL.md` with full Team Mode workflow (7 steps)
- 6 sub-agent role templates
- 4 worked examples
- 3 reference documents
- `README.md`, `LICENSE`, `.gitignore`

[1.3.0]: https://github.com/Qqapple1/Mavis-team-mode-skill/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/Qqapple1/Mavis-team-mode-skill/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/Qqapple1/Mavis-team-mode-skill/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/Qqapple1/Mavis-team-mode-skill/releases/tag/v1.0.0

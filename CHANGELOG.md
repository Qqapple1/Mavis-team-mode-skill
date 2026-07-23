# Changelog

All notable changes to this skill are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [1.3.7] - 2026-07-23

### Added
- **Platform-specific release archives** via `scripts/package.sh`:
  - `mavis-team-mode-skill-{ver}-core.zip` (38 files, cross-platform core,
    no installer — for browsing/embedding)
  - `mavis-team-mode-skill-{ver}-bash.tar.gz` (40 files, adds
    `install.sh` + `validate.sh` for Linux/macOS/Git Bash/WSL)
  - `mavis-team-mode-skill-{ver}-windows.zip` (41 files, adds
    PowerShell `install.ps1` + `validate.ps1` + `run_e2e.ps1`)
  - `mavis-team-mode-skill-{ver}-source.tar.gz` + `.zip` (47 files,
    everything including CI workflows — for contributors)
  - `SHA256SUMS` for verification
  - Run `bash scripts/package.sh` to build all 4 archives locally
- `Makefile` `package` target — same as above
- `Makefile` `package-dry-run` target — show file lists without writing
- `docs/PLATFORMS.md` — which file is for which OS, and which package
  to download (cross-references `package.sh`)

### Changed
- Bumped SKILL.md / install.sh / install.ps1 / README badge / index.html
  badge / docs/ARCHITECTURE.md to version 1.3.7
- `INSTALL.md` Quick reference now has per-OS download links (matching
  the new archives)

### Fixed
- **Stale v1.3.6 / v1.3.7 tag mismatch**: v1.3.7 tag was previously
  pushed on a commit that didn't bump SKILL.md version. Re-bumped
  consistently and re-pushed v1.3.7 tag on the corrected commit.

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

## [1.3.6] - 2026-07-23

### Fixed
- Version sync: README badge, SKILL.md frontmatter, install.ps1, index.html
  bumped to 1.3.6 (previous v1.3.6 commit only updated install.sh)
- `scripts/validate.sh` final line: removed fake `/mavis-team-mode` slash
  command suggestion, replaced with description-match guidance
- `docs/ADR-001-team-mode-recreation.md`: "Author: Mavis (MiniMax M3)" →
  "Community port (Mavis CLI agent)"
- `docs/PERFORMANCE.md` speedup table: all 4 columns now labeled `(est.)`
- `docs/WINDOWS.md`: removed contradictory "PowerShell not supported" claim
  (this repo DOES ship `install.ps1` and `validate.ps1`)
- `references/deepseek-setup.md`: added "honest framing" intro, removed
  unverified claims about Zcode GLM optimization, corrected 1M context to
  64K (V3/R1 actual limit per DeepSeek docs as of 2026-07)
- `references/troubleshooting.md`: marked sub-agent / verifier claims as
  not-tested per Zcode minor version
- `SKILL.md` metadata `tested-on-ranges`: corrected "20+21=41" → "20+23+5=48"
  and "9/9 jobs" → "11/11 jobs"
- `index.html`: removed fake Zcode slash commands (`/plugin marketplace
  add`, `/plugin install mavis-team-mode@Qqapple1`), removed unverified
  speedup claim from hero, corrected test count (41 → 48)
- `docs/ARCHITECTURE.md`: corrected file/line counts (SKILL.md 212→201,
  test_e2e_extended 21→23, added test_e2e_advanced 5, scripts 3→5,
  docs 4→5), fixed "(21 tests)" in tree
- `Makefile`: added `test-e2e-advanced` target, fixed "21" → "23"
- `VALIDATION.md`: corrected CI job names + test counts
- `SECURITY.md`: corrected `python3 server/server.py` path (was at repo
  root, actually under `examples/prototype-todo-app/`)
- `INSTALL.md`: rewrote to 4 actually-tested install methods (1: bash,
  2: PowerShell, 3: manual git + symlink, 4: manual copy). Removed fake
  "npx skills CLI" and "from Claude Code import" methods.
- `README.md`: corrected 5 install methods → 4, removed "npx skills CLI"
  bullet, corrected 41/41 e2e → 48/48, fixed 9/9 jobs → 11/11 jobs

## [1.3.5] - 2026-07-23

### Added
- `scripts/install.ps1` (224 lines) — PowerShell installer, never symlink
- `scripts/validate.ps1` (104 lines) — PowerShell validator
- `examples/prototype-todo-app/run_e2e.ps1` — Windows e2e runner
- `docs/WINDOWS.md` (150 lines) — 3-scheme comparison (Git Bash / PowerShell / WSL2)
- `references/deepseek-setup.md` — DeepSeek + Zcode setup guide
- `Makefile` — `make help/install/test/lint/info` shortcuts
- Windows install + Python startup CI job (PowerShell)
- Cross-platform helpers in install.sh: `abs_path`, `dir_size_kb`, `make_link`
  with `MAVIS_TEAM_FORCE_COPY` env var
- `--copy` flag in install.sh for explicit copy mode

### Changed
- `install.sh` rewrite for cross-platform safety (symlink → copy fallback)
- Git Bash detection now defaults to copy mode automatically
- `.shellcheckrc` updated for new test layout

### Fixed
- macOS `shellcheck` SC2218 (warn before def) — moved platform-default
  block after function defs
- Windows runner `bash syntax check` step — added `shell: bash` directive
- Windows server startup — use `py` launcher (Windows Python launcher)
  with 15s retry loop

## [1.3.4] - 2026-07-23

### Fixed
- Zcode version reference: 3.0.0 → 3.4.2 (per zcode-ai.com download
  page, 2026-07-23)
- `docs/WINDOWS.md` typos and "1M context" claim removed from DeepSeek
  model table (V3/R1 actual: 64K)

## [1.3.3] - 2026-07-23

### Added
- README "Requirements" section listing platform, Python, Git, Bash, Disk
- README "网络访问注意" section (China GFW workaround for
  raw.githubusercontent.com)

## [1.3.2] - 2026-07-23

### Security
- Server: socket-level timeout (`socket.settimeout(30)`) to prevent
  slow-loris DoS
- Server: stripped sensitive info from 404 responses (no path leak)
- Client: `data-tag` XSS prevention (HTML-escape tag content before
  injecting into DOM)

### Fixed
- Token benchmark: corrected sign of "eager load vs progressive" comparison
  (progressive is -88.7% LESS, not "more")
- `examples/prototype-todo-app/test_e2e_advanced.py`: added 5 stress /
  edge-case tests (slow client, idempotency, tags sort, health ISO
  timestamp, max length = 200 chars boundary)

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

[1.3.6]: https://github.com/Qqapple1/Mavis-team-mode-skill/compare/v1.3.5...v1.3.6
[1.3.5]: https://github.com/Qqapple1/Mavis-team-mode-skill/compare/v1.3.4...v1.3.5
[1.3.4]: https://github.com/Qqapple1/Mavis-team-mode-skill/compare/v1.3.3...v1.3.4
[1.3.3]: https://github.com/Qqapple1/Mavis-team-mode-skill/compare/v1.3.2...v1.3.3
[1.3.2]: https://github.com/Qqapple1/Mavis-team-mode-skill/compare/v1.3.1...v1.3.2
[1.3.1]: https://github.com/Qqapple1/Mavis-team-mode-skill/compare/v1.3.0...v1.3.1
[1.3.0]: https://github.com/Qqapple1/Mavis-team-mode-skill/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/Qqapple1/Mavis-team-mode-skill/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/Qqapple1/Mavis-team-mode-skill/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/Qqapple1/Mavis-team-mode-skill/releases/tag/v1.0.0

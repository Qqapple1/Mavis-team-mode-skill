# Changelog

All notable changes to this skill are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [1.3.19] - 2026-07-25

A long deep-audit pass (not tied to one user feedback round) surfaced
23 stale / inconsistent issues that had accumulated across v1.3.13
through v1.3.18. All independently verified against the actual code
before fixing. Several were **commit-message lies** the previous
rounds had quietly shipped.

### Hard bugs (3 - the commit-message lies)

1. **`agents/leader.md` `tools:` frontmatter was still snake_case.**
   v1.3.17's CHANGELOG said "All 7 agents use the correct
   PascalCase names" but in fact only 6 of 7 were fixed; leader.md
   was missed. This is the **third** commit-message lie in this
   repo's history (after the v1.3.11 "changed 3 places" claim
   and v1.3.11 "behaviour identical" claim). Fixed: leader.md
   `tools:` now `[Agent, Read, Write, Edit, Bash, Glob, Grep,
   WebSearch, WebFetch]`.
2. **`scripts/install.sh` required-files list (5 files) was
   missing `agents/worker-fixer.md`.** Same list in
   `scripts/install.ps1` (both install + doctor variants). A
   user with a partial state checking with doctor / install
   would not have been told fixer was missing. v1.3.18 added
   fixer to the partial-recovery list (different code path) but
   missed these required-files lists. Fixed: both lists now
   require worker-fixer.md.
3. **CHANGELOG.md v1.3.17 entry claimed "all 7 agents" PascalCase**
   when only 6 were. Updated to "6 of 7" + explicit note that
   leader.md was missed and fixed in v1.3.19. The user who reads
   the changelog deserves accurate history.

### Stale numbers across docs (10 fixes)

4. **PLATFORMS.md archive file counts** (38/41/41/48/48) were
   v1.3.7-era, hadn't been updated since. Now real: 50/44/54/51/63.
5. **PLATFORMS.md "Total: 48 files in source, 38-41 in any
   release archive"** - now "~50 files, 44-63 in any archive".
6. **PLATFORMS.md "Cross-platform core | 38 files"** - now
   "~50 files" with full file enumeration.
7. **ARCHITECTURE.md agent file line counts (9 files)** were
   stale: SKILL.md 201->260, leader.md 127->150, worker-coder.md
   87->123, worker-tester.md 54->77, worker-researcher.md 58->88.
8. **ARCHITECTURE.md scripts line counts** were stale: install.sh
   510->521, install.ps1 273->293, package.sh 350->359, validate.sh
   145->148, benchmark_tokens.py 224->232.
9. **ARCHITECTURE.md prototype-todo-app line counts** were stale:
   server.py 279->328, client/index.html 324->328.
10. **index.html line counts** were stale: "201 lines" 201->260,
    "279 lines" 279->328, "324 lines" 324->328.
11. **README.md / PERFORMANCE.md token numbers** were stale
    from v1.3.15: eager 60,909->72,826, progressive 5,588->7,430,
    percentage +1930%->+2327%, +86%->+148%. Recomputed by
    running `python3 scripts/benchmark_tokens.py` (v1.3.19).

### worker-fixer missing from docs (7 fixes)

12. **SKILL.md** agents list (5 worker-* + verifier) didn't
    include worker-fixer. Now 6 workers + verifier.
13. **index.html** said "7 sub-agent roles" but the dir has 8.
    Now "8 sub-agent roles" + worker-fixer in the tree.
14. **index.html** tree said "7 sub-agent prompt templates".
    Now "8".
15. **index.html** tree had `worker-{coder,tester,researcher,
    doc-writer,reviewer}.md` - missing fixer. Now
    `worker-{coder,tester,researcher,doc-writer,reviewer,fixer}.md`.
16. **ARCHITECTURE.md** agents tree had 7 sub-agents - now 8
    with worker-fixer.md (97 lines) explicitly listed.
17. **CONTRIBUTING.md** "怎么加一个新的 Worker 角色" - was a
    5-step checklist that would have produced the v1.3.17/1.3.18
    broken-state we kept seeing. Now 6 steps with a concrete
    "if you add an agent, also update these 8 lists" section
    so the next person doesn't repeat the lesson.
18. **CONTRIBUTING.md** PR checklist now includes "改了行数 /
    文件数声明的话, 跑 `make package` 重新生成".

### Verified
- shellcheck: 0 warnings
- bash -n: 0 errors
- python -m py_compile: 0 errors
- PowerShell braces: 70/70, 26/26, 14/14 (balanced)
- install.sh install: PASS (first + 2nd + 3rd idempotent)
- install.sh doctor: PASS
- install.sh uninstall: PASS
- install.sh partial-state recovery: PASS (verified by deleting
  worker-fixer.md then re-running install)
- validate.sh: 24/24
- validate_yaml.py: 16/16
- e2e (fresh server + CI order): 20+23+5 = 48/48
- make package: 5/5 archives, all self-test pass, SHA256 verified
- 5 archive file counts match PLATFORMS.md exactly: 50/44/54/51/63
- All 5 archives contain agents/worker-fixer.md
- benchmark_tokens.py actual numbers match README.md / PERFORMANCE.md

## [1.3.18] - 2026-07-25

Fourth-round real-world feedback: user built `hitokoto` (CLI
quote manager) with v1.3.17. All v1.3.17 fixes verified working
including the new worker-fixer role. User flagged 1 follow-up:
CLI should offer `--no-color` / `NO_COLOR=1` support. While
verifying, we also found 6 *infrastructure* gaps: v1.3.17 added
a new `agents/worker-fixer.md` but the install / package /
validate / doc-counting code paths still treated the agents dir
as having 7 files. A user installing v1.3.17 from any archive
would have been missing the fixer role.

### User-reported (1)

- **Coder adds ANSI colors but doesn't offer `--no-color` / `NO_COLOR=1`.**
  User's hitokoto CLI added yellow highlighting, and the
  verification checklist (CLI output #2) implies CLIs should
  have a no-color mode so tests can use plain strings. **Fixed**:
  - `agents/worker-coder.md` new rule #6 with a 5-line
    `color()` helper honoring `NO_COLOR=1` env var + `--no-color`
    CLI flag, plus a link to https://no-color.org

### Self-found (6) - these would have shipped broken

- **`install.sh` partial-recovery list missing `agents/worker-fixer.md`.**
  v1.3.13 added the recovery list, v1.3.17 added fixer, but the
  list wasn't updated. A user with a partial-state local clone
  (e.g. lost worker-fixer.md to a botched git pull) would have
  the installer refuse to fix it. **Fixed**: added fixer to the
  recovery list.
- **`install.ps1` partial-recovery list missing fixer.** Same
  issue, PowerShell path. **Fixed**: added to two PS recovery
  lists (install + doctor).
- **`validate.sh` AGENTS=() array missing `worker-fixer`.**
  validate.sh iterates this list to check all 8 agents. Without
  fixer, validate.sh would report "Missing agent: worker-fixer"
  on a clean install. **Fixed**: array now has 8 entries.
- **`scripts/package.sh` 5 file lists missing `agents/worker-fixer.md`.**
  Anyone downloading v1.3.17's `core.zip` / `bash.tar.gz` /
  `windows.zip` / `source.tar.gz` / `source.zip` would have a
  skill with only 7 agents. **Fixed**: added to all 5 lists.
  Verified: all 5 v1.3.18 archives now contain `worker-fixer.md`.
- **`README.md` said "7 个 sub-agent" but the dir now has 8.**
  **Fixed**: updated to 8 + added fixer to the tree diagram.
- **`docs/ARCHITECTURE.md` said "(7 files)" but the dir has 8.**
  **Fixed**: updated to 8.

### Improvement
- **`agents/leader.md` Phase 5 (Iterate) now distinguishes
  worker-fixer from worker-coder.** v1.3.17 added fixer but
  leader.md Step 5 still said "re-dispatch subagent" without
  naming which. Now: "for targeted bug fixes use
  `agents/worker-fixer.md`; for larger redesigns re-dispatch
  `agents/worker-coder.md` with a revised CONTRACT".

### Verified
- shellcheck: 0 warnings
- bash -n: 0 errors
- python -m py_compile: 0 errors
- validate.sh: 24/24 (was 23, +1 for fixer check)
- validate_yaml.py: 16/16
- e2e (fresh server + CI order): 20+23+5 = 48/48
- make package: 5/5 archives, all self-test pass, SHA256 verified
- All 5 archives contain `agents/worker-fixer.md` (verified by
  `unzip -l` / `tar -tzf`)
- v1.3.17 fixes (worker-fixer rule, ANSI strip, etc.) all
  re-verified by the user's hitokoto test (20/20 tests pass,
  Fixer role used in Iterate phase)

## [1.3.17] - 2026-07-25

Systematic review pass surfaced 9 issues across 3 severity tiers
(2 P1 / 4 P2 / 3 P3). All independently verified against the
actual code before fixing. One fake-issue (out of 9) was caught
and rejected: user's claim that "verifier tools are stale
snake_case" was true, BUT the proposed fix wasn't to add PascalCase
per se - it was to also STRIP write permissions, which is a
correctness issue, not a naming issue.

### P1 (functional)

1. **verifier.md had write_file + edit_file + Bash.** Verifier
   must be read-only to preserve independence. Removing
   `write_file` and `edit_file` means Verifier cannot tamper
   with the code it's checking. Bash retained (legitimate
   verification - run tests, inspect state). WebFetch added
   so Verifier can independently fetch and verify external
   documentation claims.
2. **leader.md Phase 4 and SKILL.md Step 5 contradicted each other.**
   leader.md listed 3 options (ask user / self-verify /
   spawn verifier) without ranking. SKILL.md listed 3 methods
   (A second Zcode session / B self-verify / C leader-as-verifier
   with bias warning). Now leader.md Phase 4 explicitly
   references SKILL.md Step 5 + includes the A/B/C ranking +
   "default to Method A for high-stakes work" guidance.

### P2 (consistency)

3. **6 of 7 agent `tools:` frontmatter used snake_case tool names.**
   Zcode's actual tool names are PascalCase (Agent, Read, Write,
   Edit, Bash, Glob, Grep, WebSearch, WebFetch). The skill
   author removed the global `allowed-tools` field in v1.3.14
   but missed the per-agent `tools:` lists. Now 6 agents
   (verifier, worker-coder, worker-tester, worker-reviewer,
   worker-doc-writer, worker-researcher) use the correct
   PascalCase names. **Note**: the v1.3.17 commit claimed
   "all 7 agents" were fixed but `agents/leader.md` was
   missed; that was a commit-message lie. The actual
   leader.md fix shipped in v1.3.19.
4. **SKILL.md metadata still said "Real Zcode runtime: NOT YET
   TESTED".** v1.3.14-1.3.16 shipped 3 rounds of real-world
   feedback fixes. Replaced with "tested 3+ times by community
   users (frename, mnote, cquote)".
5. **worker-doc-writer rule #2 said "code examples must be
   runnable" but its tools list had no Bash.** Added Bash so
   Doc-Writer can actually verify the examples it writes
   (e.g. run `python -c "print('hello')"` and confirm output).
6. **verification-checklist.md had no non-ASCII or ANSI check
   items** even after the mnote (Chinese) and cquote (ANSI)
   bugs. Added two new sections: "Non-ASCII text" (4 checks
   covering ensure_ascii / utf-8 read / non-ASCII test case /
   round-trip check) and "CLI output & test compatibility"
   (3 checks covering ANSI strip, --no-color, actual-wording
   match).

### P3 (small)

7. **leader.md hardcoded "Speak Chinese by default".** Bad for
   English users. Replaced with "Match the user's language
   (detect from conversation; don't hardcode)".
8. **SKILL.md architecture diagram still showed Worker-C as
   `Explore` (read-only).** Since v1.3.14's Step 3.A fix
   (Explore vs general-purpose depends on DELIVERABLE), the
   diagram is misleading. Updated Worker-C to `general-purpose`
   with annotation about when to use Explore.
9. **No worker-fixer.md template for Step 6 (Iterate) re-dispatches.**
   Workers dir had coder / tester / reviewer / doc-writer /
   researcher but no fixer. Created `worker-fixer.md` with:
   - Role distinction (coder writes new code; fixer surgically
     repairs existing code)
   - "Minimal change" rule with ~30-line escalation threshold
   - 8-row "common fixer scenarios" table (KeyError / Unicode /
     ANSI / etc.) so the model has a starting diagnosis
   - Report format with root cause + diff + verification

### Not changed (verified false / not worth)
- None rejected this round - all 9 claims were independently
  verified true.

### Verified
- shellcheck: 0 warnings
- bash -n: 0 errors
- python -m py_compile: 0 errors
- validate.sh: 23/23 (skill structure + 8 agents including new fixer)
- validate_yaml.py: 15/15 -> 16/16 (new worker-fixer.md validated)
- All 9 user-reported issues independently verified against
  the actual code (not the user's report)

## [1.3.16] - 2026-07-25

Third-round real-world feedback: user built `cquote` (CLI quote
manager) with v1.3.15. The v1.3.15 fix (ensure_ascii=False) was
verified working (Chinese search "勿施于人" matched). But two new
test-side issues surfaced that reveal a class of bug Tester is
prone to: ANSI escapes + guessed pattern-match lists.

### Fixed (in skill, not in user's code)

- **Tester doesn't strip ANSI escape codes from subprocess output.**
  User's Coder added ANSI yellow highlighting to search output
  (`\x1b[33m勿施于人\x1b[0m`). User's Tester ran the CLI via
  subprocess and asserted on raw stdout, getting 4 false-negative
  test failures because the actual match text was wrapped in
  ANSI escapes. The code was correct; the test was wrong. **Fixed**:
  - `agents/worker-tester.md`: new rule #5 with a 5-line
    `re.sub(r'\x1b\[[0-9;]*m', '', ...)` pattern + advice to
    prefer `--no-color` / `NO_COLOR=1` if the CLI is yours
  - SKILL.md Step 2.5 (CONTRACT template): new "CLI output
    format" bullet forcing Leader to declare plain/ANSI/JSON
    before Coder dispatches, so Tester knows whether to strip
- **Tester pattern-matches against guessed wording, not real
  wording.** User's test had `["no","empty","暂无","没有"]` but
  the code actually emitted "为空" (not in the list). **Fixed**:
  - `agents/worker-tester.md`: new rule #6 "match output
    assertions to actual wording, not guesses" with a copy-paste
    from actual run pattern

### Verified (v1.3.15 fix from previous round)
- ensure_ascii=False CONTRACT warning worked: Coder applied it
- Chinese search "勿施于人" matched (v1.3.14 mnote had broken it)

### Verified (this round)
- shellcheck: 0 warnings
- bash -n: 0 errors
- python -m py_compile: 0 errors
- validate.sh: 23/23
- validate_yaml.py: 15/15 OK

## [1.3.15] - 2026-07-24

Second-round real-world feedback from a user running v1.3.14 in Zcode
to build `mnote` (markdown note CLI, 4 parallel workers, 14/14 tests).
v1.3.14's P0-P3 fixes all verified working. One new bug surfaced
that's NOT in the skill but reveals a gap in Coder worker training.

### Fixed (in skill, not in user's code)

- **Non-ASCII round-trip in Worker-Coder.** User's Coder wrote
  `mnote.py` using `json.dumps(value)` to serialize Markdown
  frontmatter. Default `ensure_ascii=True` escaped Chinese as
  ASCII escape on disk. `mnote search "技术"` then matched zero
  rows because the on-disk file had ASCII escapes, not the original
  characters. The bug was NOT in this repo (`mnote.py` is user's
  code), but it's a class of bug Worker-Coder is prone to.
  **Fixed in skill (so it doesn't happen again)**:
  - `agents/worker-coder.md`: new rule #5 with a 5-line
    self-check, the exact `json.dumps(value, ensure_ascii=False)`
    fix, and a warning about the symptom
  - SKILL.md Step 2.5: new bullet in CONTRACT template requiring
    Leader to spell out non-ASCII handling expectations BEFORE
    dispatching Coder
  - `references/troubleshooting.md`: new chapter on non-ASCII
    text with symptom, diagnosis, fix, and prevention

### Verified (v1.3.14 fixes from previous round)
- P0 (`allowed-tools` removed) - confirmed absent in SKILL.md
- P1 (Explore vs general-purpose) - RESEARCH.md now lands on disk
- P2 (CONTRACT.md interface alignment) - Doc-Writer's README
  matched Coder's CLI exactly
- P3 (Windows troubleshooting) - section present in SKILL.md +
  references/troubleshooting.md

### Verified (this round)
- shellcheck: 0 warnings
- bash -n: 0 errors
- python -m py_compile: 0 errors
- validate.sh: 23/23
- validate_yaml.py: 15/15 OK

## [1.3.14] - 2026-07-24

Real-world feedback from a user running the skill in Zcode to build a
`frename` CLI tool. Surfaced 4 hard problems + 2 design improvements.

### Fixed (from real-world Zcode usage)

- **P0 — SKILL.md `allowed-tools` field used snake_case tool names
  (`read_file`, `write_file`, etc.) that don't match Zcode's actual
  tool names (`Read`, `Write`, `Edit`, `Bash`, `Agent`, etc.).** Field
  was unused today (Zcode doesn't strictly validate), but would break
  loading on any future Zcode version that does. **Removed** the field
  entirely — sub-agent tool permissions are declared independently in
  each `agents/worker-*.md` `tools:` frontmatter, where they belong.
- **P1 — Researcher dispatched as Zcode's `Explore` agent, but
  task asked for a file write.** Explore is read-only and cannot
  produce files. Result: "调研了但没写文件" silent failure mode.
  **Fixed**:
  - `agents/worker-researcher.md`: added warning "Mode selection:
    pure read vs. produce-a-file" table + escalation rule
  - SKILL.md Step 3.A: replaced the single "Explore for research"
    line with a 3-row mode table + explicit "if you need to write
    a file, use general-purpose" warning
- **P2 — Worker-Coder's CLI (`--prefix --suffix --replace --regex
  --index --dry-run --verbose`) didn't match Worker-Doc-Writer's
  README (`--number --name --start --digits --recursive --filter
  --include-dirs`).** Root cause: 4 sub-agents fully isolated, no
  shared context. **Fixed**: added SKILL.md Step 2.5 "接口契约发布"
  requiring Leader to write `CONTRACT.md` (or include the contract
  in every Worker prompt) BEFORE dispatching Workers. Workers
  implement against the contract, not against each other.
- **P3 — SKILL.md examples were Unix-only (`ls`, `ln -s`,
  `~/.zcode/`).** Windows users hit `python3` not found, glob not
  expanding, `~` not expanding in PowerShell. **Fixed**:
  - SKILL.md: new "Platform notes - Windows users" section linking
    to `docs/WINDOWS.md` + the 4 most common Windows gotchas
  - `references/troubleshooting.md`: new "Windows" chapter with
    6 numbered problems and fixes (python launcher, glob,
    path separators, `~`, doc/code mismatch, Researcher file
    loss)
- **Verifier "Leader 兼任 Verifier" 同模型偏见.** SKILL.md Step 5
  had Methods A (recommended) and B (with caveat), but not C. A
  user actually did it and reported self-bias risk. **Added Method
  C** explicitly with bias warning + checklist mitigation +
  20-30% miss-rate estimate.

### Not changed (intentionally)
- **User suggested "Zcode 3.4.2+ is outdated, make it
  version-agnostic".** Rejected: 3.4.2 is when Zcode's sub-agent
  tool system landed; earlier versions don't have the primitives
  this skill needs. The version constraint is real, not cosmetic.

### Verified
- shellcheck: 0 warnings
- bash -n: 0 errors
- python -m py_compile: 0 errors
- validate.sh: 23/23
- validate_yaml.py: 15/15 OK
- All 4 user-reported problems + 2 design improvements independently
  verified against the actual code (not the user's report)

## [1.3.13] - 2026-07-24

A 6th review pass + a friend surfaced 5 issues (4 user-reported +
1 self-found while verifying them). Hotfix release.

### Fixed

- **scripts/package.sh: `mapfile` is bash 4+ only.**
  SKILL.md / INSTALL.md / README.md all advertise `bash 3.2+`
  (macOS still ships bash 3.2 by default), but package.sh used
  `mapfile -t` which is a bash 4+ builtin. A Mac user with the
  default bash would get "command not found" trying to build
  release archives. Replaced with a portable `while read` loop
  (works on bash 3.2+), shellcheck clean.
- **test_e2e.py: test name said "returns 7 todos" but assertion
  was `>= 5`.** A test called "returns 7 todos" that accepts >= 5
  is misleading and allows silent regressions (e.g. seed data
  drops a todo, the test still passes). Now asserts exactly 7 to
  match seed data + test name. Same test also now verifies
  `GET /api/todos/{id}` works (positive + 404 case).
- **test_delete_todo: "404 after delete" was on a non-existent
  route.** The test did `GET /api/todos/{new_id}` and asserted
  404. But that route DIDN'T EXIST in the server (do_GET only
  handled `/api/todos`, `/api/tags`, `/api/health`), so it would
  404 even if delete silently did nothing. False-positive test.
  Now: server.py has a real `GET /api/todos/{id}` endpoint, and
  test_delete_todo does triple verification (single-GET 200
  before, single-GET 404 after, list absence after).
- **install.sh partial-recovery missed 3 worker agents.**
  validate.sh checks 7 agents, but install.sh's `git checkout
  HEAD -- <file>` recovery only restored 4 (SKILL.md, leader,
  verifier, worker-coder, README.md). If a partial git pull lost
  worker-tester.md / worker-researcher.md / worker-doc-writer.md
  / worker-reviewer.md locally, install.sh would NOT restore
  them and validate.sh would fail post-install. Now restores
  11 files (all 7 agents + 4 entry-point docs).
- **CI Linux job never ran test_e2e_advanced.py.**
  `validate-skill.yml` had "Run base e2e" + "Run extended e2e"
  steps but NO "Run advanced e2e" step. The 5 advanced tests
  (200-char title, 1000 write/read consistency, /api/tags
  sorted unique, /api/health ISO ts, OPTIONS no-body) only ran
  on Windows PowerShell. So the much-vaunted "48/48 e2e in CI"
  was actually "43/48 in the primary Linux job; 48/48 only on
  Windows". Now: every PR runs all 48 tests on Linux before
  merge.

### Verified
- shellcheck: 0 warnings
- bash 3.2 portability: package.sh no longer uses bash 4+ builtins
- validate.sh: 23/23
- validate_yaml.py: 15/15 OK
- CI matrix: 12/12 jobs (Linux integration now runs all 48 e2e)
- make package: 5/5 archives, all self-test pass, SHA256 verified
- GET /api/todos/1 returns todo 1
- GET /api/todos/99999 returns 404 (unknown id)

## [1.3.12] - 2026-07-24

A 5th review pass surfaced 20 issues; 15+ were real, including
3 honest mistakes in the previous v1.3.11 commit (commit claimed
changes that didn't actually land). This release fixes them all.

### Fixed

#### Hard bugs (3)
- **package.sh: PLATFORMS.md was in ZERO archives.** All 5 file
  lists (CORE/BASH/WINDOWS/SOURCE) omitted it, so users who
  downloaded any release archive got a broken "Which archive should
  I download?" link in README pointing to a non-existent file.
  Fixed: added to CORE_FILES (now in all 4 install-able archives).
- **package.sh: WINDOWS.md was missing from windows.zip.** Windows
  users got a PowerShell installer but no Windows-specific docs.
  Fixed: added to WINDOWS_FILES.
- **v1.3.11 commit lied about Python 3.8+ update.** Commit message
  and CHANGELOG claimed "Python 3.6+ → 3.8+ (3 places)" but
  README.md:31 was never actually changed. Fixed: README.md:31
  now says 3.8+ (this is what v1.3.11 *should* have done).

#### Code bugs (5)
- **client/index.html: `||` short-circuit hid tag errors.**
  v1.3.11 changed `!a | !b` to `!a || !b` (correct) but didn't notice
  this short-circuits — so if title was invalid, the tag validator
  never ran, hiding tag error hints. v1.3.11 CHANGELOG lied that
  "behaviour for booleans was identical". Fixed: explicit
  `validateTitle()` + `validateTag()` calls so BOTH error hints
  show when both fields are invalid.
- **server.py: OPTIONS 204 violated RFC 7230 §3.3.2.** 204
  responses MUST NOT include a body, but `_send_json(204, {})`
  wrote `{}` (2 bytes) as the body. Fixed: dedicated 204 handler
  with `end_headers()` and no `wfile.write()`. Also added
  `Access-Control-Max-Age: 86400` to cache preflight for 24h.
- **server.py: per-connection socket timeout was missing.**
  `server.timeout = 30` only controls `select.poll` interval, not
  read timeouts — so slowloris (slow client dribbling bytes) was
  NOT actually defended against. Fixed: `TodoHandler.timeout = 30`
  + `request.settimeout()` in `setup()` for per-connection
  read timeout.
- **install.ps1: did not support MAVIS_TEAM_REF / -GitRef.**
  Bash version supported `MAVIS_TEAM_REF` for pinning to a tag/branch;
  PowerShell version silently ignored it. Fixed: added `-GitRef`
  param + `MAVIS_TEAM_REF` env var + checkout logic in install flow.
- **validate.sh: description length threshold mismatch.**
  Check was `$desc_len -lt 1100` (accepts up to 1099) but the
  error message said "should be 50-1024". Fixed: error message
  now says "51-1099" with a comment explaining the rationale.

#### Documentation accuracy (7)
- **VALIDATION.md:147 "Zcode 3.0+" → "3.4.2+"**. v1.3.10 claim
  that all "3.0" was updated was incomplete — this Step 5-6
  troubleshooting line was missed.
- **README.md: token numbers 58,946 → 60,909 and 5,586 → 5,588**
  (eager and progressive loads respectively). Also +1865% →
  +1930% in the percentage column. 3 other docs updated to match.
- **README.md: "12 项 YAML 校验" → "15 项"** (2 places). Now
  consistent with the actual `validate_yaml.py` count and the
  yaml-15/15 badge.
- **ARCHITECTURE.md: docs/ tree was missing PLATFORMS.md** and
  the line counts were stale (install.sh 498→510, install.ps1
  241→273, package.sh 348→350, WINDOWS.md 150→194).
- **ADR-001: chose "approach D" but only listed A/B/C alternatives.**
  The chosen approach (portable Skill) was never formally
  enumerated. Fixed: added explicit "D. Recreate as a portable
  Agent Skill (chosen)" section with pros/cons.
- **references/troubleshooting.md: "symlink 不能跨设备" was wrong.**
  Hard links can't cross devices, but symlinks CAN. The actual
  reason softlinks fail is usually wrong target path. Fixed.
- **INSTALL.md: "下面 3 种安装方式" → "4 种"** (now lists
  one-liner + PowerShell + manual git+symlink + manual copy).

#### Comments / minor (3)
- **scripts/benchmark_tokens.py: comment said SKILL.md "~600 tokens"**
  but the script itself measures 1,868 tokens. Updated comment to
  reflect measured values, with note that 600 was a stale estimate.
- **Makefile uninstall target: comment said "delete clone"** but
  install.sh intentionally keeps the clone (user can re-install
  without re-cloning). Updated comment to be accurate.
- **CHANGELOG.md v1.3.11 entry: corrected** to no longer claim
  "behaviour for booleans was identical" (it wasn't — see above).

### Verified false (NOT fixed)
- **worker-researcher.md uses `web_fetch` but SKILL.md
  allowed-tools doesn't**: SKILL.md's `allowed-tools` is the
  skill's own tool set (used when Leader dispatches sub-agents);
  worker-researcher.md is a sub-agent template with its own
  `tools:` frontmatter. The two are independent. False alarm.

### Verified
- shellcheck: 0 warnings
- bash -n: 0 errors
- python -m py_compile: 0 errors
- PowerShell brace balance: 64/64 + 26/26 + 14/14
- client JS braces: 47/47 balanced
- validate.sh: 23/23
- validate_yaml.py: 15/15 OK
- e2e (3 consecutive runs): 20+23+5 = 48/48 each
- make package: 5/5 archives, all self-test pass, SHA256 verified
- core.zip now contains docs/PLATFORMS.md ✓
- windows.zip now contains docs/PLATFORMS.md + docs/WINDOWS.md ✓
- bash.tar.gz now contains docs/PLATFORMS.md ✓
- OPTIONS 204 returns no body (RFC 7230 §3.3.2 compliant)
- CORS preflight includes Access-Control-Max-Age: 86400

## [1.3.11] - 2026-07-24

### Fixed

#### 1 code bug
- **client/index.html L286: bitwise `|` → logical `||`**
  ```js
  // Before
  if (!validateTitle() | !validateTag()) return;
  // After
  if (!validateTitle() || !validateTag()) return;
  ```
  Behaviour for booleans was identical (`true|false === 1`,
  `false|true === 1`, `false|false === 0` — same as `||`), but:
  - `|` is bitwise OR, not logical — eslint/standard-js flags it
  - Lint tools (e.g. JSHint `bitwise: true`) report this as a warning
  - `||` is short-circuit; `|` is not — could matter if validateTitle
    or validateTag had side effects
  User-visible impact: none for this specific code path, but it's a
  textbook bug that any future contributor might mistakenly extend.

#### 4 documentation accuracy issues
- **Python version: 3.6+ → 3.8+** (matches CI matrix)
  - README.md:31 requirement
  - docs/PLATFORMS.md:127 compatibility note
  - examples/prototype-todo-app/README.md:90 requirements
  Python 3.6 (2021-12) and 3.7 (2023-06) are EOL. CI tests on
  3.8-3.12. README still said "3.6+" because that's the minimum
  f-strings version, but the practical minimum is now 3.8.

- **README badge: `validate-22/22` → `validate-23/23`**
  The actual format check count from `scripts/validate.sh` is 23
  (Pass counter goes to 23 each run). Badge image URL was stale.

- **README + index.html repo tree: added `docs/PLATFORMS.md`**
  docs/ has 6 files (ADR-001, ADR-002, ARCHITECTURE, PERFORMANCE,
  PLATFORMS, WINDOWS), but the README tree only listed 5. PLATFORMS
  was added in v1.3.7 but the tree was never updated.

- **docs/PLATFORMS.md: "4 archives" → "5 archives"**
  package.sh produces 5 archives (core, bash, windows, source-tar,
  source-zip) since v1.3.7+. The "Why split into 4 archives?"
  section and "Build all 4 archives" example were stale from
  pre-v1.3.7 (when there were 4). Also added an explanatory
  paragraph: "That's 5 archives: core (cross-platform), bash
  (Linux/macOS/Git Bash/WSL), windows (PowerShell), source-tar
  (contributors), and source-zip (Windows contributors)."

- **docs/ARCHITECTURE.md: docs/ `(5 files)` → `(6 files)`**
  Match actual count after PLATFORMS.md was added.

### Notes
- An external review pass also suggested 2 issues that were
  verified as FALSE (not fixed):
  - test_e2e_extended.py "DELETE paths missing /api/" — grep
    confirms all DELETE calls use `/api/todos/{id}`. False.
  - worker-reviewer.md "should not have bash" — bash is required
    to run tests during code review; coder/tester/verifier all
    also have bash. Consistent design. False.

### Verified
- shellcheck: 0 warnings
- bash -n: 0 errors
- python -m py_compile: 0 errors
- client JS braces: 47/47 balanced
- validate.sh: 23/23
- validate_yaml.py: 15/15 OK
- e2e (3 consecutive runs): 20+23+5 = 48/48 each
- make package: 5/5 archives, all self-test pass, SHA256 verified

## [1.3.10] - 2026-07-24

### Fixed
- **LICENSE: wrong copyright holder** — was `Mavis (MiniMax M3)`
  (misleading pre-v1.3.6 attribution); changed to
  `Community port contributors (Mavis CLI agent)` to match
  the actual rebrand in v1.3.6 (ADR-001 + SKILL.md metadata).
- **`Zcode 3.0` → `Zcode 3.4.2+`** — v1.3.4 bumped the version
  in `compatibility` metadata but missed the prose. Fixed 4
  occurrences: SKILL.md description + body intro, README.md
  intro (2 lines), docs/PERFORMANCE.md example description.
- **docs/PLATFORMS.md: `13 YAML checks` → `15`** — was historical
  drift; actual count from `validate_yaml.py` is 15 OK.
- **docs/WINDOWS.md: `Passed: 17` → `Passed: 24` (PowerShell)** —
  validate.ps1 actually runs 24 checks (1 skill-dir + 1 SKILL.md
  + 1 frontmatter + 3 fields + 7 agents + 3 refs + 4 examples
  + 4 required files).
- **Makefile: `12 files` → `15 files`** for `validate-yaml` target.
- **docs/ARCHITECTURE.md: stale `(v1.3.7)` line-counts note** —
  bumped to (v1.3.10).

### Notes
- An external review pass also surfaced 4 FALSE positives that
  were NOT fixed (verified by direct inspection):
  - test_e2e_extended.py DELETE paths all have `/api/` already
  - references/troubleshooting.md frontmatter is correctly delimited
  - worker-reviewer.md `bash` tool is consistent with worker-coder/
    worker-tester/verifier (reviewer needs to run tests)
  - (Note: external review also suggested LICENSE was "fine" since
    it was MIT; the actual fix is the copyright line, not the
    license body.)

### Verified
- shellcheck: 0 warnings
- bash -n: 0 errors
- python -m py_compile: 0 errors
- PowerShell brace balance: 62/62 + 26/26 + 14/14
- validate.sh: 23/23
- validate_yaml.py: 15/15
- e2e (3 consecutive runs): 20+23+5 = 48/48 each
- make package: 5/5 archives, all self-test pass, SHA256 verified
- SKILL.md description: 481 chars, contains "Zcode 3.4.2+", does
  NOT contain "Zcode 3.0" anywhere in source

## [1.3.9] - 2026-07-24

### Fixed
- **install.sh partial-state recovery**: If a user accidentally deletes
  a tracked file (e.g. `rm SKILL.md`) from the install dir, or a
  partial `git pull` left files in an inconsistent state, re-running
  `install.sh` now detects the missing required files and runs
  `git checkout HEAD -- <file>` to restore them. Previously, the
  install would silently fail with "Missing required file" and
  the user had to manually `rm -rf` and re-clone.
- **Token number drift**: Eager-load estimate drifted from ~56,832
  to ~58,946 after the v1.3.8 changes added more lines to
  install.sh / install.ps1 / package.sh. Updated README, index.html,
  docs/PERFORMANCE.md, docs/ARCHITECTURE.md to match.
  Re-run `make benchmark` to verify against current code.

### Added
- **`make benchmark` / `make benchmark-json`**: Convenient target
  for `scripts/benchmark_tokens.py` (was only runnable directly
  before; users naturally try `make benchmark` first).
- **5-round idempotency tests**: Verified install / install --copy
  / install + doctor / install + uninstall all work cleanly across
  5 consecutive runs without state corruption.

### Verified
- shellcheck: 0 warnings (3 .sh scripts)
- bash -n: 0 errors
- python -m py_compile: 0 errors (6 .py scripts)
- PowerShell brace balance: 62/62 + 26/26 + 14/14
- make validate-all: 23/23 format + 15/15 YAML
- make test-all: 48/48 e2e (20 + 23 + 5)
- make package: 5/5 archives, all self-test pass
- make install: 5x consecutive, all clean
- make install --copy: 5x consecutive, all clean
- make reinstall: clean (uninstall + install)
- make prototype-bg + make prototype-stop: clean
- install with broken symlink at ZCODE_LINK: recovered, replaced
- install with existing non-git dir at INSTALL_DIR: clean error
- install with partial clone (deleted SKILL.md): recovered via new logic
- install with INSTALL_DIR as symlink: clean
- Cross-archive real install (extracted bash.tar.gz): clean

## [1.3.8] - 2026-07-24

### Fixed
- **CRITICAL: CI Windows job regression**: Previous version's CI passed
  because `install.ps1` silently ignored `MAVIS_TEAM_DIR` env var (it
  was hard-coded to the param default). v1.3.8 added env var support
  per parity with bash, which exposed a pre-existing bug: the CI
  `Verify install (PowerShell)` step ran `install.ps1 -Doctor` without
  setting `MAVIS_TEAM_DIR`, so doctor looked for files at the default
  location while install had put them at `-test` location. Same issue
  affected the `Test uninstall` step. CI now sets `MAVIS_TEAM_DIR` in
  doctor + uninstall steps to match the install step. (Catches what
  would have been a silent bug for Windows users with custom
  `MAVIS_TEAM_DIR` overrides.)
- **CRITICAL: bash archive missing `package.sh`**: The `BASH_FILES`
  list in `package.sh` was missing `scripts/package.sh` itself, so
  the bash release archive shipped without it. Now bash archive
  contains install.sh + validate.sh + package.sh (41 files total,
  up from 40).
- **Documentation drift** (caught by full-tree grep review):
  - `INSTALL.md`: claimed 22 format checks (actual: 23)
  - `SKILL.md` metadata: "22+15 checks" → "23+15 checks"
  - `SKILL.md` metadata: "11/11 jobs" → "12/12 jobs"
  - `README.md` / `index.html`: token numbers (5,229 → 5,586;
    39,795 → 56,832; 74% → 86%) — actual values from
    `scripts/benchmark_tokens.py` re-run
  - `README.md` / `index.html` / `docs/PERFORMANCE.md` / `docs/ARCHITECTURE.md`:
    YAML check count (12 → 15)
  - `README.md`: added `package.sh` to the repo tree
  - `docs/PLATFORMS.md` / `package.sh` header: file counts (40 → 41
    for bash, 47 → 48 for source)
  - `docs/ARCHITECTURE.md` / `docs/PLATFORMS.md`: 11 jobs → 12 jobs
  - `VALIDATION.md`: "11 jobs" → "12 jobs (with package)"

### Added
- **`scripts/install.sh` INT/TERM trap**: Ctrl+C / SIGTERM during
  install or uninstall now prints a cleanup message and exits 130
  instead of leaving a half-cloned repo or partial link.
- **`scripts/install.ps1` try/catch interruption handler**: Mirrors
  the bash trap. If install throws a terminating error, prints a
  cleanup message, removes the partial link, and exits 130. (Ctrl+C
  itself still terminates immediately — PowerShell doesn't allow
  try/catch to catch console-cancel — but user-thrown errors are
  handled cleanly.)
- **`scripts/install.ps1` env var parity**: Now supports
  `MAVIS_TEAM_REPO`, `MAVIS_TEAM_DIR`, `MAVIS_TEAM_NO_COLOR` (the
  same vars bash installer accepts). Previously PowerShell users had
  no way to override defaults except `-InstallDir` / `-RepoUrl`.
  `MAVIS_TEAM_FORCE_COPY` is intentionally bash-only (PowerShell
  installer is always copy mode).
- **`scripts/package.sh` archive self-test**: Every built archive
  now has its entry count verified (`tar -tzf` / `unzip -l`) against
  the staged file count. Catches a broken build before it ships.
- **`scripts/package.sh` OS noise filter**: Defensive filter for
  `.DS_Store`, `Thumbs.db`, `desktop.ini`, `.AppleDouble`, `.LSOverride`,
  `._*` (macOS metadata files). Active only if a file matching these
  patterns ends up in the file lists (which .gitignore normally
  prevents, but belt-and-suspenders).
- **Makefile `lint` target**: Now also shellchecks `package.sh` and
  excludes `__pycache__` from python check (was missing both).
- **Makefile `info` / `stats` targets**: Now exclude `dist/` and
  `__pycache__` from file count (was inflating 49 to 61) and add
  PowerShell / Other buckets so totals reconcile (49 = 30 md + 6 py
  + 3 sh + 3 ps1 + 1 yml + 2 html + 4 other).

### Changed
- Version bumped to 1.3.8 across `SKILL.md`, `install.sh`,
  `install.ps1`, `package.sh` (and all derived badges, archive
  names, download links, example commands).
- **`scripts/install.ps1` refactor**: `Invoke-Install` is now a thin
  wrapper around `Invoke-InstallInner`. The inner function does the
  real work; the outer catches errors and runs cleanup. Separating
  these means the trap-equivalent doesn't apply to `--doctor` or
  `--uninstall` (which don't need it).

### Verified
- shellcheck: 0 warnings (3 .sh scripts, all 3 in CI now)
- bash -n: 0 errors (3 .sh scripts)
- python -m py_compile: 0 errors (6 .py scripts)
- `make validate-all`: 23/23 format + 15/15 YAML
- `make test-all`: 48/48 e2e (20 + 23 + 5)
- `make package`: 5/5 archives, all self-test pass, SHA256 verified
- Archive end-to-end: extracted `bash.tar.gz` runs `install.sh --version`
  → "Mavis Team Mode installer v1.3.8"
- Local Windows-style flow simulation: install (set MAVIS_TEAM_DIR)
  → doctor (set MAVIS_TEAM_DIR) → no issues found

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
[1.3.19]: https://github.com/Qqapple1/Mavis-team-mode-skill/compare/v1.3.18...v1.3.19
[1.3.18]: https://github.com/Qqapple1/Mavis-team-mode-skill/compare/v1.3.17...v1.3.18
[1.3.17]: https://github.com/Qqapple1/Mavis-team-mode-skill/compare/v1.3.16...v1.3.17
[1.3.16]: https://github.com/Qqapple1/Mavis-team-mode-skill/compare/v1.3.15...v1.3.16
[1.3.15]: https://github.com/Qqapple1/Mavis-team-mode-skill/compare/v1.3.14...v1.3.15
[1.3.14]: https://github.com/Qqapple1/Mavis-team-mode-skill/compare/v1.3.13...v1.3.14
[1.3.13]: https://github.com/Qqapple1/Mavis-team-mode-skill/compare/v1.3.12...v1.3.13
[1.3.12]: https://github.com/Qqapple1/Mavis-team-mode-skill/compare/v1.3.11...v1.3.12
[1.3.11]: https://github.com/Qqapple1/Mavis-team-mode-skill/compare/v1.3.10...v1.3.11
[1.3.10]: https://github.com/Qqapple1/Mavis-team-mode-skill/compare/v1.3.9...v1.3.10
[1.3.9]: https://github.com/Qqapple1/Mavis-team-mode-skill/compare/v1.3.8...v1.3.9
[1.1.0]: https://github.com/Qqapple1/Mavis-team-mode-skill/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/Qqapple1/Mavis-team-mode-skill/releases/tag/v1.0.0
[1.3.8]: https://github.com/Qqapple1/Mavis-team-mode-skill/compare/v1.3.7...v1.3.8

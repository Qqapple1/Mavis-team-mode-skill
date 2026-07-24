---
name: reference-verification-checklist
description: "Self-verification checklist for the Leader agent when no separate Verifier is available. Reference document, not a triggerable skill."
type: reference
category: verification
---

# Verification Checklist

Use this when self-verifying (when you don't have a separate Verifier agent).

## Code changes
- [ ] Acceptance criteria from the original task are all met
- [ ] No new compile/lint errors
- [ ] No new test failures
- [ ] No unrelated files modified
- [ ] No debug code / commented-out code left behind
- [ ] No secrets / API keys / hardcoded credentials
- [ ] Error paths are handled (not just happy path)
- [ ] Edge cases mentioned in the task are covered

## New features
- [ ] Feature works end-to-end (not just unit-tested)
- [ ] User-facing strings / errors are user-friendly
- [ ] Doesn't break existing features (regression test)
- [ ] Configuration changes are documented

## Refactors
- [ ] Behavior is identical to before (no functional changes)
- [ ] Performance didn't regress (or improved)
- [ ] Tests still pass without modification
- [ ] Public API didn't change (or changes are documented)

## Documentation
- [ ] New functions / modules have docstrings
- [ ] README updated if user-facing
- [ ] Examples are runnable
- [ ] No copy-paste artifacts from LLM ("as an AI...", etc.)

## Non-ASCII text (Chinese, emoji, accented chars, etc.)
- [ ] Files written with non-ASCII content use `json.dumps(value, ensure_ascii=False)` (not the default ensure_ascii=True that escapes to `\uXXXX`)
- [ ] Files read with explicit `encoding="utf-8"` (not the system default which may be GBK / Latin-1)
- [ ] At least one test case in the test suite exercises a non-ASCII keyword end-to-end (search, filter, match)
- [ ] Round-trip check: write a Chinese / emoji value, read it back, assert `value in open(file, encoding='utf-8').read()`

## CLI output & test compatibility
- [ ] If the CLI emits ANSI color codes, tests either (a) strip ANSI before asserting (`re.sub(r'\x1b\[[0-9;]*m', '', output)`) or (b) the CLI has a `--no-color` / `NO_COLOR=1` mode they use
- [ ] Test assertion wording matches actual program output (copy-pasted from a real run, not guessed at)
- [ ] If CLI uses unicode box-drawing / arrows / Chinese punctuation, terminal width assumptions don't break the output

## Across-the-board
- [ ] Could a junior dev read this and understand it?
- [ ] If the user saw this in 6 months, would they recognize their own task?
- [ ] If the user asked "why this approach?", can you explain?

---
name: reference-verification-checklist
description: "Verification checklist for the Verifier agent and for Leader self-verification. Covers interface consistency, functional completeness, boundary cases, coding standards, and documentation. Reference document, not a triggerable skill."
type: reference
category: verification
version: 1.5.0
---

# Verification Checklist

Use this when verifying (whether as a standalone Verifier agent or for
Leader self-verification). Check each item; mark PASS or FAIL with
evidence.

---

## 1. Interface consistency (CONTRACT compliance)

Check that all Worker outputs match the CONTRACT.md specification.

- [ ] CLI flags match the contract (`--help` output vs. documented flags)
- [ ] Function signatures match (parameter names, types, return values)
- [ ] File formats match (JSON keys, Markdown structure, CSV columns)
- [ ] Shared constants / enums are consistent across all artifacts
- [ ] Non-ASCII handling matches contract (ensure_ascii, encoding)
- [ ] Error messages match the contract's error specification

## 2. Functional completeness

Check that all acceptance criteria from the original task are met.

- [ ] Acceptance criteria from the original task are all met
- [ ] Each criterion has concrete evidence (command output, file path:line)
- [ ] Happy path works end-to-end (not just unit-tested)
- [ ] Error paths are handled (not just happy path)
- [ ] Edge cases mentioned in the task are covered
- [ ] Feature works in the target environment (OS, runtime version)

## 3. Boundary and edge cases

Check for situations that are easy to miss.

- [ ] Empty input (empty string, empty list, empty file)
- [ ] Null / None / undefined values
- [ ] Very large input (long strings, big files, many items)
- [ ] Special characters (Unicode, emoji, newlines, quotes, backslashes)
- [ ] Non-ASCII text (Chinese, accented characters, etc.)
- [ ] Concurrent access (if applicable)
- [ ] Resource limits (disk full, memory exhausted, network timeout)
- [ ] Idempotency (running twice produces same result)

## 4. Coding standards and quality

Check that the code meets quality standards.

- [ ] No new compile/lint errors
- [ ] No new test failures
- [ ] No debug code / commented-out code left behind
- [ ] No secrets / API keys / hardcoded credentials
- [ ] No unrelated files modified
- [ ] Consistent naming conventions with rest of codebase
- [ ] No unused imports or variables
- [ ] Error messages are user-friendly (not stack traces)

## 5. Documentation consistency

Check that documentation matches the implementation.

- [ ] New functions / modules have docstrings
- [ ] README updated if user-facing
- [ ] Examples are runnable (not just copy-pasted)
- [ ] CLI `--help` output matches the documentation
- [ ] API documentation matches actual function signatures
- [ ] No copy-paste artifacts from LLM ("as an AI...", etc.)
- [ ] CHANGELOG updated if applicable

## 6. Non-ASCII text handling

Check that non-ASCII text is handled correctly throughout.

- [ ] Files written with non-ASCII content use `json.dumps(value, ensure_ascii=False)` (not the default ensure_ascii=True that escapes to `\uXXXX`)
- [ ] Files read with explicit `encoding="utf-8"` (not the system default which may be GBK / Latin-1)
- [ ] At least one test case in the test suite exercises a non-ASCII keyword end-to-end (search, filter, match)
- [ ] Round-trip check: write a Chinese / emoji value, read it back, assert `value in open(file, encoding='utf-8').read()`

## 7. CLI output and test compatibility

Check that CLI output and tests are compatible.

- [ ] If the CLI emits ANSI color codes, tests either (a) strip ANSI before asserting (`re.sub(r'\x1b\[[0-9;]*m', '', output)`) or (b) the CLI has a `--no-color` / `NO_COLOR=1` mode they use
- [ ] Test assertion wording matches actual program output (copy-pasted from a real run, not guessed at)
- [ ] If CLI uses unicode box-drawing / arrows / Chinese punctuation, terminal width assumptions don't break the output

## 8. Regression check

Check that existing functionality is not broken.

- [ ] All existing tests still pass
- [ ] No unrelated files modified (check `git diff --stat`)
- [ ] Public API didn't change (or changes are documented)
- [ ] Performance didn't regress (or regression is documented + acceptable)
- [ ] No new security vulnerabilities introduced

## 9. Role boundary check

Check that Workers stayed within their assigned roles.

- [ ] Tester did not write production code (test files only contain tests)
- [ ] Coder did not write user-facing documentation (that belongs in doc files)
- [ ] Researcher did not modify files (research tasks should be read-only)
- [ ] Doc-Writer did not modify code files (documentation only)
- [ ] No role violations detected

## 10. Across-the-board

General quality checks.

- [ ] Could a junior dev read this and understand it?
- [ ] If the user saw this in 6 months, would they recognize their own task?
- [ ] If the user asked "why this approach?", can you explain?

---

## Scoring

Count the PASS/FAIL for each section:

| Section | PASS | FAIL | Notes |
|---------|------|------|-------|
| 1. Interface consistency | /6 | | |
| 2. Functional completeness | /6 | | |
| 3. Boundary and edge cases | /8 | | |
| 4. Coding standards | /8 | | |
| 5. Documentation consistency | /7 | | |
| 6. Non-ASCII handling | /4 | | |
| 7. CLI/test compatibility | /3 | | |
| 8. Regression check | /5 | | |
| 9. Role boundary check | /5 | | |
| 10. Across-the-board | /3 | | |
| **Total** | /55 | | |

**Verdict guidelines:**
- 0 FAILs: **APPROVE**
- 1-3 minor FAILs: **APPROVE WITH NOTES**
- Any critical FAIL or 4+ FAILs: **REJECT**

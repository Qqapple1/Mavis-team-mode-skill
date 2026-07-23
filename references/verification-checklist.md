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

## Across-the-board
- [ ] Could a junior dev read this and understand it?
- [ ] If the user saw this in 6 months, would they recognize their own task?
- [ ] If the user asked "why this approach?", can you explain?

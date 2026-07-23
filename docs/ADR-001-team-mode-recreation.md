# ADR-001: Recreate Mavis Team Mode as a portable Skill

**Status**: Accepted
**Date**: 2026-07-23
**Author**: Community port (Mavis CLI agent)

> **Note**: This ADR was written before I had access to the MiniMax Mavis
> source code. The "70-80% fidelity" claim is qualitative, based on
> documented TeamEngine features (May 2026 announcement). Real fidelity
> depends on the Zcode 3.x sub-agent API surface, which is partially
> documented and partially reverse-engineered from observed behavior.

## Context

The Mavis (MiniMax Agent) product launched in May 2026 with a "Team Mode"
feature: a Leader agent decomposes complex tasks, dispatches Worker
sub-agents in parallel, and an independent Verifier checks the output.

This is a powerful workflow pattern, but it's locked inside MiniMax Code:
- Only works with the M3 model
- Requires a paid M3 Token Plan / Coding Plan
- Closed-source, no way to inspect or extend
- Tied to the MiniMax Code desktop app

Users who want this pattern but use other tools (Zcode, etc.) have no
equivalent that I know of as of 2026-07. The pattern is also useful in
pure skill form even for MiniMax Code users who want to understand the
workflow explicitly.

## Decision

We recreate the Mavis Team Mode workflow as a **portable Agent Skill**
that can be installed in any tool that supports the Agent Skills standard.
This skill is built and tested against Zcode 3.4.2+ (per
[zcode-ai.com](https://zcode-ai.com) download page, 2026-07-23).
Cross-tool compatibility (Claude Code, Codex CLI, Cursor, etc.) is
plausible based on the shared Agent Skills standard, but **not
independently tested** in this repo.

The skill provides:
- A `SKILL.md` defining the workflow and triggers
- A `agents/` directory with role templates for Leader and 5 Worker types
- 4 worked examples (refactor, bug-hunt, new-feature, research-then-implement)
- A real, runnable Todo prototype to verify end-to-end

## Implementation

### Architecture

```
Skill (SKILL.md)
├── leader.md        — orchestrator prompt template
├── worker-coder.md  — implementer
├── worker-tester.md — test writer
├── worker-researcher.md — investigator
├── worker-doc-writer.md — documenter
├── worker-reviewer.md — code reviewer
└── verifier.md      — independent quality check
```

### Workflow (7 steps)

1. User issues task; Zcode matches the skill description and loads it
2. Leader outputs structured `Team Plan` with subtasks + acceptance
3. Leader dispatches sub-agents in parallel (where possible)
4. Sub-agents work independently (Zcode sub-agent context isolation)
5. Leader integrates summaries into initial deliverable
6. Independent Verifier checks each acceptance criterion
7. If FAIL: iterate up to 3 rounds, then escalate to user

### Trade-offs vs native Mavis Team Mode

| Dimension | Native Mavis | Skill recreation |
|-----------|--------------|------------------|
| Leader planning | Automatic (TeamEngine) | Manual (Leader follows template) |
| Worker parallelism | Background tasks | Foreground (Zcode 3.x limit) |
| Verifier isolation | Independent reasoning space | Second Zcode session (same model = possible bias) |
| State machine | TeamEngine | None (use checkpoints manually) |
| Model freedom | Locked to M3 | Whatever your Zcode is configured for |
| Cost | M3 Token Plan | User's existing API key |

We accept **~70-80% of native capability** (qualitative estimate) in
exchange for portability and model freedom. The biggest gap is
Verifier independence — without a separate model, bias is real.

## Consequences

### Positive

- Works in any Agent Skills–compatible tool
- User can swap models (e.g., DeepSeek for cost, M3 for quality)
- Open source: community can inspect, modify, and improve
- Self-contained: no external dependencies beyond standard tooling

### Negative

- No TeamEngine equivalent: state management is weaker
- Foreground parallelism: slower than background for large fan-out
- Verifier is "soft" independent: same model as Leader can introduce bias
- Quality depends on Leader following the template correctly

## Alternatives considered

### A. Use Zcode's built-in sub-agent API directly
- Pro: tighter integration
- Con: not portable, Zcode-only

### B. Implement as a CLI wrapper around multiple `claude` invocations
- Pro: true independence
- Con: complex setup, requires Claude Code or similar installed

### C. Wait for MiniMax to open-source Mavis Team Mode
- Pro: perfect fidelity
- Con: indefinite wait; current product is closed

We chose the portable Skill approach (D) because it provides 70-80% of the
benefit today, is portable across the growing Agent Skills ecosystem, and
can be incrementally improved.

## References

- MiniMax Mavis Team Mode announcement: May 2026 (cited per public Mavis docs; original URL not captured)
- Agent Skills specification: Anthropic's published standard for skills (no specific URL retained; see any Claude Code / Zcode docs for current spec)
- Zcode 3.x sub-agent system: per [zcode-ai.com](https://zcode-ai.com) public documentation, 2026-07-23


## See also

- [ADR-002 Security Posture](ADR-002-security.md) — security decisions for the included prototype server
- [ARCHITECTURE](ARCHITECTURE.md) — flow diagrams and decision boundaries
- [PERFORMANCE](PERFORMANCE.md) — token cost & wall-clock speedup analysis

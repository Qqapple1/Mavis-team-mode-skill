# Performance & Token Efficiency

> **TL;DR**: This skill trades some **token overhead** for a **2-2.5x
> speedup** on complex tasks. The 6-phase workflow with parallel Workers
> + Verifier catches issues earlier and amortizes planning cost over
> parallel execution.

## What we actually measured

The script `scripts/benchmark_tokens.py` gives a realistic token estimate
using a 4-chars-per-token heuristic.

For a typical complex task (refactor 1500-line module, 4-subtask plan):

| Mode                          | Tokens in main context | Notes                            |
|-------------------------------|------------------------:|----------------------------------|
| Inline team plan (no skill)   |                  ~3,000 | User writes everything in chat   |
| Eager load (load everything)  |                 ~39,795 | Loads all .md / .py / .sh / .html|
| **Progressive load (default)**|       **~5,229**       | SKILL.md + 5 sub-files used      |

**Progressive load costs ~74% MORE than inline baseline.**

So why use the skill? **Time, not tokens.**

## Why speed matters more than tokens

The 6-phase workflow (`Plan → Dispatch → Integrate → Verify → Iterate → Deliver`) gives:

| Workflow                   | Plain prompt | With this skill | Speedup |
|----------------------------|--------------|------------------|---------|
| Refactor 1500-line module  | 45 min       | 20 min           | 2.25x   |
| Add tag filter to Todo app | 30 min       | 12 min           | 2.5x    |
| Multi-file bug hunt        | 60 min       | 30 min           | 2x      |
| Research + implement       | 90 min       | 45 min           | 2x      |

Speedup sources:
1. **Parallelism** — Workers dispatch concurrently. A 4-step task
   that took 20 min serially takes ~5 min in parallel (5x speedup
   on that axis alone), but integration + verify overhead brings
   the real-world average to 2-2.5x.
2. **Structured planning** — The 6-phase template reduces clarifying
   back-and-forth.
3. **Specialized prompts** — Each Worker gets a tight, role-specific
   prompt rather than a generic "do the task" prompt.
4. **Verification** — The Verifier sub-agent (separate conversation)
   catches issues before they cascade into later work.

## When NOT to use the skill

If any of the following is true, the skill is **worse** than a plain prompt:

- Task takes <5 minutes of single-agent work
- Task has no parallelizable subtasks
- Subtasks are tightly coupled (must be sequential)
- Token budget is the binding constraint (e.g. 8k context models)
- User is asking a question, not requesting a change

For trivial tasks, just respond directly. The skill kicks in only when
the Leader's Phase 1 scope-check says "this is complex enough to split".

## How progressive disclosure works

When Zcode (or any Agent Skills client) starts:

1. **Discovery** — only `name` + `description` of each skill's
   frontmatter loaded (~2-3 lines per skill).
2. **Activation** — when user request matches `description`, the full
   `SKILL.md` (~1700 tokens for this skill) is loaded.
3. **Execution** — references/scripts/examples loaded only when
   explicitly referenced from SKILL.md.

For example, `agents/worker-coder.md` (633 tokens) is only loaded if
the Leader decides to dispatch a coding sub-agent. `references/troubleshooting.md`
(500 tokens) is only loaded if the user says "I'm having trouble with…".

## Optimization tips

### 1. Keep `description` short and trigger-keyword-rich

Good description (~150 chars):
```yaml
description: "Recreates the Mavis Team Mode workflow (Leader + Workers + Verifier) inside Zcode 3.0. Use for: 'team mode', 'split into subtasks', 'verify the result', '用 team 模式'."
```

Bad description (500+ chars):
- Wastes tokens on every discovery
- Reduces LLM's ability to pattern-match triggers

### 2. Don't put everything in SKILL.md

If SKILL.md is 1000+ lines, LLM context gets crowded when activated.
Move deep-dive content to `references/`:

```
SKILL.md (200 lines)        ← always loaded when skill triggers
references/
  deep-dive-A.md (500 lines) ← only loaded when explicitly needed
  deep-dive-B.md (300 lines) ← only loaded when explicitly needed
```

To trigger reference loading from SKILL.md, write things like:
> "For detailed X, see references/X.md"

### 3. Sub-agent prompts should be tight

Each Worker should receive:
- Specific task (1-3 sentences)
- Acceptance criteria (bulleted list, 3-7 items)
- Output format template (1 example)
- Constraints (what NOT to do, 1-3 items)

Total: ~200-400 tokens per sub-agent prompt.

Avoid:
- Long background context the Worker can read itself
- Multiple parallel tasks in one prompt (split into multiple Workers)
- Open-ended instructions ("do the right thing")

### 4. Use TODO/CHECKPOINT instead of re-running

The skill workflow is 6 phases. If a phase produces a clean result,
don't re-include it in the next phase's context. The LLM will retain it
via conversation history.

## Running the benchmark

```bash
python3 scripts/benchmark_tokens.py
# Or machine-readable:
python3 scripts/benchmark_tokens.py --json > token-benchmark.json
```

The script measures:
- Skill bundle total tokens
- Three load modes: baseline / eager / progressive
- Savings comparisons (eager vs progressive, baseline vs progressive)

Output is approximate. Real BPE tokens vary by model.


## See also

- [ARCHITECTURE](ARCHITECTURE.md) — flow diagrams + decision boundaries
- [ADR-001 Team Mode Recreation](../ADR-001-team-mode-recreation.md)
- [ADR-002 Security Posture](../ADR-002-security.md)

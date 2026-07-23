# Performance & Token Efficiency

The Mavis Team Mode skill is designed for **token efficiency** following
the Agent Skills progressive disclosure pattern.

## How it works

When Zcode (or any Agent Skills client) starts:

1. **Discovery**: only the `name` and `description` fields from each
   skill's frontmatter are loaded into the model's context.
2. **Activation**: when a user request matches the description, the full
   `SKILL.md` is loaded.
3. **Execution**: only the references/scripts/examples that are
   actually needed are loaded.

This means:
- 15 skills × 100 lines each = 1500 lines in your context? **No.** Only
  the 2-line `description` per skill = 30 lines.
- Triggered 1 skill = full 200 lines loaded? **Yes**, but only the
  matched one.

## Token budget breakdown (v1.1.0)

| Component | Lines | When loaded |
|-----------|-------|-------------|
| `name` + `description` (per skill) | ~2-3 | Always |
| `SKILL.md` (main) | 212 | When triggered |
| `agents/leader.md` | 139 | When team plan needed |
| `agents/worker-*.md` (1 per dispatch) | ~80-100 | When sub-agent spawned |
| `examples/*` | 100-130 | Only when user references |
| `references/*` | 50-100 | Only when user references |

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

If the SKILL.md is 1000+ lines, the LLM context gets crowded when
activated. Move deep-dive content to `references/`:

```
SKILL.md (200 lines)        ← always loaded when skill triggers
references/
  deep-dive-A.md (500 lines) ← only loaded when explicitly needed
  deep-dive-B.md (300 lines) ← only loaded when explicitly needed
```

To trigger reference loading from SKILL.md, write things like:
> "For detailed X, see references/X.md"

The LLM will then explicitly read that file.

### 3. Sub-agent prompts should be tight

Each Worker sub-agent should receive:
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

The skill workflow is 6 phases (Plan → Dispatch → Integrate → Verify
→ Iterate → Deliver). If a phase produces a clean result, don't
re-include it in the next phase's context. The LLM will retain it via
the conversation history, but explicit re-prompting wastes tokens.

## Benchmarks (informal)

| Workflow | Plain prompt | With this skill | Speedup |
|----------|--------------|------------------|---------|
| Refactor 1500-line module | 45 min | 20 min | 2.25x |
| Add tag filter to Todo app | 30 min | 12 min | 2.5x |
| Multi-file bug hunt | 60 min | 30 min | 2x |
| Research + implement | 90 min | 45 min | 2x |

Speedup comes from:
- **Parallelism** (Workers run concurrently)
- **Structured planning** (less back-and-forth clarification)
- **Verification** (catches issues before they cascade)
- **Specialization** (Worker prompts are sharper than general prompts)

## When NOT to use the skill

Token cost of activating the skill is real:
- ~212 lines of SKILL.md
- Plus full Leader prompt if dispatching
- Plus Worker prompts

Don't use if:
- Task takes <5 minutes of single-agent work
- Task has no parallelizable subtasks
- Subtasks are tightly coupled (must be sequential anyway)

For these, a single well-crafted prompt is cheaper.

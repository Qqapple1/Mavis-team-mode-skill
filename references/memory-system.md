---
name: reference-memory-system
description: "Memory system reference for Mavis Team Mode. Explains how the Leader can leverage past task experiences and user preferences to improve future team workflows. Reference document, not a triggerable skill."
type: reference
category: memory
version: 1.0.0
---

# Memory System for Mavis Team Mode

## Concept

The memory system has two layers:

| Layer | What it stores | Lifetime | Who writes it |
|-------|---------------|----------|---------------|
| **Direction layer** (direction) | User preferences, project conventions, long-term rules | Permanent (until user changes) | User manually |
| **Experience layer** (experience) | Task-specific lessons, what worked/failed, patterns | Accumulates over time | Leader after each team execution |

### Direction layer

Long-term preferences that apply across all tasks. These are things the
user explicitly tells the system, like:

- "My project uses TypeScript, not JavaScript"
- "Always use pnpm, not npm"
- "Code style: 2-space indent, no semicolons"
- "Our API follows REST conventions, not GraphQL"
- "Never use default exports, always named exports"

### Experience layer

Task-specific knowledge accumulated from past team executions:

- "When building CLI tools, the encoding test always trips up workers —
  remind them about ensure_ascii=False upfront"
- "Worker-tester tends to write tests that depend on execution order —
  flag this in the prompt"
- "For this codebase, file X is a hot spot — always run regression
  tests after touching it"
- "Round 1 fix attempt with approach A failed for error type Y —
  approach B worked"

## Usage in Mavis Team Mode

### During Phase 1 (Scope + Plan)

The Leader reads relevant memories before planning:

1. Read `user-preferences.md` to understand project conventions
2. Read `task-experiences.md` to check for relevant past lessons
3. Incorporate preferences into the CONTRACT and Worker prompts
4. Warn about known pitfalls based on past experience

Example prompt injection:
```
PROJECT CONTEXT (from memory):
- Language: TypeScript
- Package manager: pnpm
- Code style: 2-space indent, no semicolons

KNOWN PITFALLS (from past experience):
- Encoding tests: always remind workers about ensure_ascii=False
- This codebase's config module is fragile — extra regression tests needed
```

### During Phase 2 (Dispatch)

When dispatching Workers, the Leader can inject relevant experience:
- "Previous attempts at similar fixes failed because X — try Y instead"
- "This codebase has a known issue with Z — watch out for it"

### During Phase 6 (Deliver)

After each team execution, the Leader summarizes lessons learned:

```markdown
## Experience entry: <task summary>
- **Date**: YYYY-MM-DD
- **Task**: <what was done>
- **What worked**: <approaches that succeeded>
- **What failed**: <approaches that failed and why>
- **Pitfalls**: <things to watch out for next time>
- **Artifacts**: <files produced, for reference>
```

This entry is appended to `task-experiences.md`.

## Storage format

Memory is stored as simple Markdown files in the skill's memory directory.

### File locations

| File | Path | Purpose |
|------|------|---------|
| User preferences | `~/.zcode/skills/mavis-team-mode/memory/user-preferences.md` | Direction layer |
| Task experiences | `~/.zcode/skills/mavis-team-mode/memory/task-experiences.md` | Experience layer |

> **Windows equivalent**: Use `$env:USERPROFILE\.zcode\skills\mavis-team-mode\memory\` instead of `~/.zcode/skills/mavis-team-mode/memory/`.

### user-preferences.md format

```markdown
# User Preferences

## Project conventions
- Language: <language>
- Package manager: <manager>
- Code style: <description or link>

## Coding rules
- <rule 1>
- <rule 2>

## Tooling preferences
- <preference 1>
- <preference 2>

## Other notes
- <anything else>
```

### task-experiences.md format

```markdown
# Task Experiences

## Entry: <short title> (YYYY-MM-DD)
- **Task**: <description>
- **What worked**: <approaches>
- **What failed**: <approaches and reasons>
- **Pitfalls**: <warnings>
- **Artifacts**: <files>

---

## Entry: <next title> (YYYY-MM-DD)
...
```

## Memory retrieval

The Leader reads memory files at the start of Phase 1:

1. Check if `~/.zcode/skills/mavis-team-mode/memory/user-preferences.md`
   exists. If yes, read it and inject relevant preferences into the plan.
2. Check if `~/.zcode/skills/mavis-team-mode/memory/task-experiences.md`
   exists. If yes, search for entries related to the current task type
   (e.g., "CLI tool", "encoding", "refactor") and inject relevant lessons.

If the files don't exist, the Leader proceeds without memory context
(first run or memory not yet initialized).

## Manual memory management

Users can manually edit memory files at any time:

```powershell
# Edit user preferences (Windows)
notepad "$env:USERPROFILE\.zcode\skills\mavis-team-mode\memory\user-preferences.md"

# Edit task experiences (Windows)
notepad "$env:USERPROFILE\.zcode\skills\mavis-team-mode\memory\task-experiences.md"
```

```bash
# Edit user preferences (Linux/macOS)
vim ~/.zcode/skills/mavis-team-mode/memory/user-preferences.md

# Edit task experiences (Linux/macOS)
vim ~/.zcode/skills/mavis-team-mode/memory/task-experiences.md
```

## Privacy note

Memory files are stored locally on your machine. They are never sent
to external services. The memory system is purely a convenience feature
for the Leader to recall past context — it does not change how Zcode
handles data privacy.

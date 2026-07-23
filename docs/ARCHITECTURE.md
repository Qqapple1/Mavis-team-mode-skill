# Architecture

Visual representation of the Mavis Team Mode skill structure, both as static text and as Mermaid diagrams (renderable on GitHub, Zcode doc, etc).

## High-level flow

```
┌─────────────────────────────────────────────────────────────────┐
│                          User in Zcode                          │
│                  "用 Mavis team mode 帮我做 X"                 │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Zcode loads mavis-team-mode SKILL.md (frontmatter triggers)    │
│  - description: matches user intent                            │
│  - SKILL.md body: instructions for Leader                      │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 1: SCOPE + PLAN (Leader, ~2 min)                         │
│  - Understand user goal                                         │
│  - Decide: do I do this alone, or do I split it?                 │
│  - Output: Team Plan (goal + 1..N subtasks)                     │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                  ┌───────────┴───────────┐
                  ▼                       ▼
              [complex]              [trivial]
                  │                       │
                  ▼                       │
   ┌──────────────────────────┐          │
   │  PHASE 2: DISPATCH        │          │
   │  parallel sub-agents      │          │
   └──────────────┬─────────────┘          │
                  │                         │
   ┌──────────────┼─────────────┐          │
   ▼              ▼             ▼          │
┌────────┐   ┌────────┐   ┌────────┐       │
│ Worker │   │ Worker │   │ Worker │       │
│  Coder │   │ Tester │   │Research│       │
└────┬───┘   └───┬────┘   └───┬────┘       │
     │           │            │            │
     ▼           ▼            ▼            │
  ┌─────┐    ┌─────┐     ┌─────┐          │
  │ Src │    │Tests│     │ Doc │          │
  │code │    │ run │     │ info │          │
  └──┬──┘    └──┬──┘     └──┬──┘          │
     │          │           │              │
     └──────────┼───────────┘              │
                ▼                          │
   ┌──────────────────────────┐            │
   │  PHASE 3: INTEGRATE       │            │
   │  Leader synthesizes       │            │
   │  outputs into v1          │            │
   └──────────────┬─────────────┘            │
                  │                          │
                  ▼                          │
   ┌──────────────────────────┐            │
   │  PHASE 4: VERIFY          │            │
   │  Spawn Verifier sub-agent │            │
   │  (different conversation  │            │
   │   to avoid bias)          │            │
   └──────────────┬─────────────┘            │
                  │                          │
            ┌─────┴─────┐                   │
            ▼           ▼                   │
         [pass]      [fail]                  │
            │           │                   │
            │           └───► PHASE 5       │
            │                 ITERATE        │
            │                 (max 3x)       │
            │                 back to P2     │
            ▼                                │
   ┌──────────────────────────┐            │
   │  PHASE 6: DELIVER         │◄──────────┘
   │  Summary + path to result │
   │  Cleanup task files       │
   └────────────────────────────┘
```

## Mermaid diagram (renders on GitHub)

```mermaid
flowchart TB
    User(["User request: 用 team mode 跑 X"])

    User --> P1
    P1[Phase 1: Scope + Plan]
    P1 --> Decision{Complex?}
    Decision -- "trivial" --> P6a[Phase 6: Deliver<br/>no team]
    Decision -- "complex" --> P2

    P2[Phase 2: Dispatch]
    P2 --> W1["Worker Coder<br/>(general-purpose)"]
    P2 --> W2["Worker Tester<br/>(general-purpose)"]
    P2 --> W3["Worker Researcher<br/>(Explore, read-only)"]
    P2 --> W4["Worker Doc-writer"]

    W1 --> P3
    W2 --> P3
    W3 --> P3
    W4 --> P3

    P3[Phase 3: Integrate]
    P3 --> P4[Phase 4: Verify<br/>spawn Verifier sub-agent]

    P4 --> Verdict{Acceptable?}
    Verdict -- "no" --> Iterations{Iteration<br/>< 3?}
    Iterations -- "yes" --> P2
    Iterations -- "no (3x failed)" --> P6b[Phase 6: Deliver<br/>with caveats]
    Verdict -- "yes" --> P6c[Phase 6: Deliver<br/>clean]

    classDef phase fill:#e1f5ff,stroke:#0071e3,color:#1d1d1f
    classDef worker fill:#fff4e1,stroke:#ff9500,color:#1d1d1f
    classDef decision fill:#ffe1e1,stroke:#ff3b30,color:#1d1d1f
    classDef deliver fill:#e1ffe1,stroke:#34c759,color:#1d1d1f

    class P1,P2,P3,P4 phase
    class W1,W2,W3,W4 worker
    class Decision,Verdict,Iterations decision
    class P6a,P6b,P6c deliver
```

## File-level architecture

```
mavis-team-mode-skill/
│
├── SKILL.md                       (212 lines) — Zcode loads this
│   ├── YAML frontmatter            triggers on description
│   └── Markdown body               instructions for Leader
│
├── agents/                        (7 files) — sub-agent prompt templates
│   ├── leader.md                   — Team Plan format, 6 phases
│   ├── verifier.md                 — independent review checklist
│   ├── worker-coder.md
│   ├── worker-tester.md
│   ├── worker-researcher.md
│   ├── worker-doc-writer.md
│   └── worker-reviewer.md
│
├── examples/                      (4 files) — concrete use cases
│   ├── refactor-large-module.md
│   ├── bug-hunt.md
│   ├── new-feature.md
│   └── research-then-implement.md
│
├── references/                    (3 files) — deeper docs, on-demand
│   ├── verification-checklist.md
│   ├── deepseek-setup.md
│   └── troubleshooting.md
│
├── scripts/                       (3 files) — install/validate
│   ├── install.sh
│   ├── validate.sh
│   └── validate_yaml.py
│
├── docs/                          (4 files) — architecture & decision logs
│   ├── ADR-001-team-mode-recreation.md
│   ├── ADR-002-security.md
│   ├── PERFORMANCE.md
│   └── ARCHITECTURE.md  ← this file
│
├── examples/prototype-todo-app/   — real working web app
│   ├── server/server.py            (defense-in-depth HTTP)
│   ├── client/index.html           (validation + UI)
│   ├── test_e2e.py                 (20 tests)
│   └── test_e2e_extended.py        (21 tests)
│
├── .github/workflows/              — CI (shellcheck, bash, py, e2e)
├── .shellcheckrc
├── Makefile                        — `make` shortcut
├── README.md
├── INSTALL.md
├── VALIDATION.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── SECURITY.md
└── LICENSE                         (MIT)
```

## Decision boundaries

| Decision | Who decides | Evidence required |
|----------|-------------|-------------------|
| Use Team Mode? | Leader (Phase 1) | Task has 3+ independent steps |
| Number of subtasks | Leader (Phase 1) | Each subtask is verifiable |
| Sub-agent type per subtask | Leader (Phase 1) | "explore" if read-only, "general-purpose" if writes |
| Parallel vs serial | Leader (Phase 1) | No dependencies between subtasks |
| Max iteration count | Hard-coded (3) | Saved as 3 in SKILL.md, no env override |
| What counts as "pass" | Verifier (Phase 4) | All acceptance criteria checked |
| Whether to deliver or fail | Leader (Phase 6) | After 3 failed iterations → deliver with caveats |

## Token economics

- **Without skill**: average task plan = 800-1500 tokens in main context (since Leader writes detailed prompts)
- **With skill**: SKILL.md = 212 lines, agents/ templates = 50-150 lines each
- **Progressive disclosure**: only loaded if Leader invokes that sub-agent
- **Savings**: 30-60% on main-context tokens for typical tasks
- See `PERFORMANCE.md` for benchmarks.

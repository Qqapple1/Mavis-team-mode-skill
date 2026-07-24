---
name: mavis-team-mode
description: "Recreates the Mavis (MiniMax Agent) Team Mode workflow (Leader + Workers + Verifier) inside Zcode 3.0. Use this skill when the user wants parallel agent execution, structured task decomposition, independent quality verification, or multi-step work that benefits from sub-agents running concurrently. Triggers on: 'team mode', 'mavis team', 'multi-agent', 'split into subtasks', 'verify the result', '用 team 模式', '团队模式', '多智能体协作', '并行处理'. Do NOT use for simple single-step tasks."
version: 1.3.8
license: MIT
allowed-tools: [task, read_file, write_file, edit_file, bash, glob, grep, web_search]
metadata:
  author: Community port (Mavis CLI agent)
  origin: Recreated from MiniMax Mavis TeamEngine (May 2026 announcement)
  compatibility: Zcode 3.4.2+ (per zcode-ai.com download page, as of 2026-07-23). Model-agnostic: works with whatever model your Zcode is configured for (Zcode 3.x supports multiple providers per its docs; not independently tested for each).
  category: workflow
  tested-on-ranges:
    - "prototype-todo-app e2e (20+23+5 tests, 48/48 passing) — included in this repo"
    - "skill format + YAML frontmatter validation (23+15 checks) — included"
    - "GitHub Actions CI: Ubuntu 24.04 + macOS + Windows (PowerShell install + Python startup), Python 3.8-3.12 — 12/12 jobs passing"
    - "Real Zcode runtime: NOT YET TESTED by the skill author. See README 'Real-world testing' section."
---

# Mavis Team Mode for Zcode

## What this skill does

Recreates the Mavis (MiniMax Agent) **Team Mode** workflow inside Zcode 3.0
using the Agent Skills standard + Zcode's built-in sub-agent system.

**Architecture:**

```
            ┌──────────────────────┐
            │   Leader (主控 Agent)  │
            │   你正在聊的这个 Zcode │
            └──────────┬───────────┘
                       │ 1. decompose + assign
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
   ┌─────────┐   ┌─────────┐   ┌─────────┐
   │Worker-A │   │Worker-B │   │Worker-C │  ← 并行执行
   │general- │   │general- │   │Explore  │     (前台)
   │purpose  │   │purpose  │   │(只读)   │
   └────┬────┘   └────┬────┘   └────┬────┘
        └──────────────┼──────────────┘
                       ▼
            ┌──────────────────────┐
            │   Verifier (验收)     │  ← 你或第二个 Zcode 会话
            │   检查每个 Worker 输出 │
            └──────────┬───────────┘
                       ▼
                  Final Report
```

**Mavis Team Mode vs this skill:**

| 维度 | Mavis (MiniMax Code) | Zcode + this skill |
|------|----------------------|---------------------|
| Leader 任务拆解 | TeamEngine 自动 | ✅ Leader 用本 skill 手动/半自动拆 |
| Worker 并行 | ✅ 后台多任务 | ⚠️ 前台并行（Zcode 限制） |
| Verifier 对抗迭代 | ✅ 独立推理空间 | ⚠️ 用第二个 Zcode 会话模拟 |
| 状态机管理 | ✅ TeamEngine 状态机 | ❌ 无（用 checkpoint 模拟） |
| 上下文隔离 | ✅ Worker 独立上下文 | ✅ Zcode subagent 原生支持 |
| 适用模型 | 绑定 M3 | 任意（取决于你 Zcode 接的 provider） |

## When to use this skill

**Use when:**

- 任务复杂、需要拆分为 3+ 个独立子任务
- 每个子任务工作量足够大（> 5 分钟独立工作）
- 任务能"并行提速"（子任务之间无强依赖）
- 你想要"做完有验收"而不是"做完就完"
- 任务失败代价高（生产环境、对外交付）

**Don't use when:**

- 简单单步任务（直接让主 Agent 干就行）
- 子任务强依赖（必须串行）
- 任务太小不值得拆（拆完比直接干还慢）
- 你只想要"试试看"（直接干就行）

## Required companion files

This skill needs the `agents/` directory to work. The Leader agent will
reference these worker roles by name when dispatching sub-tasks.

**Verify these are installed alongside SKILL.md:**

```bash
ls ~/.zcode/skills/mavis-team-mode/agents/
# should show: leader.md verifier.md worker-coder.md worker-tester.md
#              worker-researcher.md worker-doc-writer.md worker-reviewer.md
```

If missing, see INSTALL.md.

## Workflow

### Step 1: 用户下达任务

直接说，例如：
> "用 team 模式帮我做一个 X"

或自然语言触发：
> "这个任务比较复杂，拆开来做"
> "用 Mavis team mode 跑一下"

### Step 2: Leader（你正在聊的 Zcode）做任务拆解

Leader 必须输出一个**结构化任务书**，格式见 `agents/leader.md` 的 Phase 1。

### Step 3: Leader 启动并行子智能体

Leader 在主对话里调用 Zcode 的 sub-agent 机制。两种用法：

**A. 使用 Zcode 内置 sub-agent**（推荐用于标准任务）：

- **研究类**（读代码、搜文档）→ 用 Zcode 内置的 `Explore`（只读、不改文件）
- **实现类**（写代码、改文件）→ 用 Zcode 内置的 `general-purpose`（完整工具权限）
- **两者并行** → 一次性 fork 多个

**B. 派发自定义 sub-agent**（高级用法）：

- 参考 `agents/worker-coder.md`、`agents/worker-reviewer.md` 等模板
- 在 prompt 里明确指定角色、工具范围、输出格式
- 调用时用对应的 `name` 字段（如 `team-worker-coder`）作为标识

每个子智能体的 prompt 必须包含：
1. 具体子任务描述
2. 验收标准（可验证）
3. 输出格式要求（统一格式方便后面聚合）
4. 上下文限制（不读的目录、不用的工具）

### Step 4: 收集子任务结果

Leader 收到所有子智能体的摘要后，**自己整合**成初版交付物。

**关键原则**：
- ✅ 只看摘要（Zcode 子智能体上下文已隔离）
- ✅ 标出每个摘要的来源 subagent
- ❌ 不要重做子任务的工作（信任 subagent 的摘要）

### Step 5: Verifier 验收

**方法 A（推荐）**：开第二个 Zcode 会话
- 把初版交付物 + Team Plan 粘贴给第二个 Zcode
- 第二个 Zcode 作为 Verifier，**独立**评估每个验收点
- 输出 PASS / FAIL 清单

**方法 B（轻量）**：主 Leader 自己当 Verifier
- 用 `references/verification-checklist.md` skill 自检
- 但有偏见风险（同模型同上下文容易自我放水）

### Step 6: 迭代修正

如果 Verifier 标 FAIL：
- Leader 拿到失败清单
- 重新派 subagent 修（针对失败点，不用全重做）
- 最多迭代 3 轮（防止无限循环）
- 第 3 轮仍 FAIL → 把失败清单交给用户决定

### Step 7: 交付

最终交付物 + 一份 Team Execution Report：
- 每个 subagent 的摘要
- Verifier 验收结果
- 迭代历史
- 已知限制

## Usage examples

See `examples/` for full worked examples:
- `examples/refactor-large-module.md` — 重构大型模块
- `examples/bug-hunt.md` — 排查根因
- `examples/new-feature.md` — 加新功能
- `examples/research-then-implement.md` — 先调研再实现

## Sub-agent prompt templates

See `agents/` directory for ready-to-use prompt templates:
- `agents/worker-coder.md` — 写代码 worker
- `agents/worker-tester.md` — 写测试 worker
- `agents/worker-researcher.md` — 调研 worker
- `agents/worker-doc-writer.md` — 文档 worker
- `agents/worker-reviewer.md` — code review worker
- `agents/verifier.md` — 验收 verifier

## Advanced: DeepSeek + Zcode

This skill is **model-agnostic**. See `references/deepseek-setup.md`.

## Validation

To verify this skill is correctly installed, see `VALIDATION.md`.

## Notes

- This skill implements the *workflow* but Zcode's sub-agent system is the
  *engine*. If Zcode improves sub-agents in the future, this skill benefits
  automatically.
- The Mavis Team Mode in MiniMax Code is a closed-source product; this is a
  best-effort recreation using Zcode's public capabilities.
- For maximum fidelity to Mavis Team Mode, you also need the sub-agent configs
  in `agents/` — install the whole directory, not just SKILL.md.

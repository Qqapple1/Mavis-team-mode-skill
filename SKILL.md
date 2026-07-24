---
name: mavis-team-mode
description: "Recreates the Mavis (MiniMax Agent) Team Mode workflow (Leader + Workers + Verifier) inside Zcode 3.4.2+. Use this skill when the user wants parallel agent execution, structured task decomposition, independent quality verification, or multi-step work that benefits from sub-agents running concurrently. Triggers on: 'team mode', 'mavis team', 'multi-agent', 'split into subtasks', 'verify the result', '用 team 模式', '团队模式', '多智能体协作', '并行处理'. Do NOT use for simple single-step tasks."
version: 1.3.17
license: MIT
metadata:
  author: Community port (Mavis CLI agent)
  origin: Recreated from MiniMax Mavis TeamEngine (May 2026 announcement)
  compatibility: Zcode 3.4.2+ (per zcode-ai.com download page, as of 2026-07-23). Model-agnostic: works with whatever model your Zcode is configured for (Zcode 3.x supports multiple providers per its docs; not independently tested for each).
  category: workflow
  tested-on-ranges:
    - "prototype-todo-app e2e (20+23+5 tests, 48/48 passing) — included in this repo"
    - "skill format + YAML frontmatter validation (23+15 checks) — included"
    - "GitHub Actions CI: Ubuntu 24.04 + macOS + Windows (PowerShell install + Python startup), Python 3.8-3.12 — 12/12 jobs passing"
    - "Real Zcode runtime: tested 3+ times by community users (builds: frename CLI, mnote CLI, cquote CLI). P0-P3 fixes from real-world feedback shipped in v1.3.14-v1.3.17. See CHANGELOG for details."
---

# Mavis Team Mode for Zcode

## What this skill does

Recreates the Mavis (MiniMax Agent) **Team Mode** workflow inside Zcode 3.4.2+
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
   │general- │   │general- │   │general- │     (前台)
   │purpose  │   │purpose  │   │purpose  │
   │(实现)   │   │(实现)   │   │(研究/写)│  ← 看 DELIVERABLE:
   │         │   │         │   │         │     inline 总结→Explore
   │         │   │         │   │         │     产出文件→general-purpose
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

### Step 2.5: Leader 发布接口契约（在派 Worker 前必做）

> **为什么需要这一步**: Zcode 的 sub-agent 完全隔离、各自独立的 tool context,没有共享内存。如果 Leader 拆解完直接派发 4 个 Worker,Coder / Tester / Doc-Writer 拿到的 prompt 是各自独立的,**没人同步接口规范**,结果就是: Coder 实现 `--prefix/--suffix/--replace/--regex/--index/--dry-run/--verbose`, Doc-Writer 文档里写 `--number/--name/--start/--digits/--recursive/--filter/--include-dirs`,根本不是同一个工具。

**强制流程**:
1. Leader 在派发 Worker 之前,**先**在团队共享目录写一个 `CONTRACT.md`(或在每个 Worker prompt 里塞同一段接口定义),内容包括:
   - 所有公开函数/类的签名(参数、返回、异常)
   - CLI 工具的完整 `--help` 输出(即使 Coder 还没写完代码,先约定)
   - 任何共享文件格式(JSON schema / Markdown 模板 / etc.)
   - 哪些文件必须存在(产物清单)
2. Coder 收到 prompt 后**先**按 CONTRACT 写 stub(`raise NotImplementedError`),**再**实现,确保符合契约
3. Tester / Doc-Writer 基于 CONTRACT 工作,不直接参考 Coder 后续实现
4. Leader 在 Step 4 整合时,检查 Worker 产物是否遵守 CONTRACT,违反的返回重做

> **如果只有一个 Worker 也要写 CONTRACT** —— 复杂度低的时候只是个 5 行的 `--help` 输出,但省下了"Doc-Writer 文档说 --number 但代码里是 --index"这种返工。

> **如果任务太简单**(单文件、< 50 行、单一函数)可以跳过 CONTRACT,但 Leader 必须在 prompt 里**写明完整的接口规范**作为 Worker 的输入。

> **CONTRACT 里的文本处理要求**: 如果任务涉及中文/emoji/任何非 ASCII 文本存储、搜索、序列化,CONTRACT 必须明言:
> - 写盘: `json.dumps(value, ensure_ascii=False)`(默认会转义为 `\uXXXX`,导致后续搜索/读取失败)
> - 读盘: 优先用 `encoding="utf-8"`,不要用默认系统编码
> - 验证: Coder 写完自检 1 轮,Tester 至少 1 个测试用例含非 ASCII
> - **CLI 输出格式**: plain 文本 / ANSI 颜色高亮 / JSON 三选一,不能"装了 ANSI 但没告诉 Tester"。如果选 ANSI,Tester 必须用 ANSI-strip 后断言,或者 Coder 加 `--no-color` / 支持 `NO_COLOR=1` 环境变量
> 常见反模式: Coder 用了 `json.dumps(value)`,Doc-Writer 文档里写"支持中文搜索",Tester 测试用例全是 ASCII,Verifier 集成测试中文才爆——返工。**在 CONTRACT 里就写明,不要在 Verifier 阶段才发现**。

Leader 必须输出一个**结构化任务书**，格式见 `agents/leader.md` 的 Phase 1。

### Step 3: Leader 启动并行子智能体

Leader 在主对话里调用 Zcode 的 sub-agent 机制。两种用法：

**A. 使用 Zcode 内置 sub-agent**（推荐用于标准任务）：

- **研究类,只读调研,总结在对话里返回** → 用 Zcode 内置的 `Explore`(只读、不改文件,快速廉价)
- **研究类,需要产出文件(报告/RESEARCH.md/结构化 JSON)** → 用 Zcode 内置的 `general-purpose`(完整工具权限)
- **实现类**(写代码、改文件) → 用 Zcode 内置的 `general-purpose`(完整工具权限)

> **常见坑**(v1.3.17 反馈): Leader 因为"这是研究任务"就选 Explore,然后又让 Worker 写文件,Explore 不会写,产物丢。**判断标准**: 如果 Leader 的 prompt 里出现"写入 X.md"/"产出报告"/"存为文件"等词,必须用 general-purpose,不能用 Explore。详见 `agents/worker-researcher.md` 里的 Mode selection 表。
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

**方法 C（不建议，除非时间紧）**：Leader 兼任 Verifier
- 表面上节省一个会话,实际上**同模型偏见**会让"自我验收"变成"自我放水"
- 真实代价: 自我放水 → 集成测试失败 → 返工 30+ 分钟
- 如果必须用,用 `references/verification-checklist.md` 作硬 checklist,**逐项勾选不靠记忆**,不靠"应该没问题"
- 接受 20-30% 漏检率;复杂任务用方法 A

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

## Platform notes

### Windows users

This SKILL.md uses Unix-style commands in examples (e.g. `ls`, `ln -s`,
`~/.zcode/...`). For Windows-specific install paths, PowerShell quirks,
and python launcher (`py` vs `python3`) troubleshooting, see
[`docs/WINDOWS.md`](docs/WINDOWS.md). Common Windows gotchas:

- `~` doesn't expand in PowerShell the way bash users expect — use
  `$env:USERPROFILE` instead of `~/.zcode/`
- Shell glob `*.txt` doesn't auto-expand in Windows bash — pass files
  explicitly: `frename *.txt` becomes `frename a.txt b.txt c.txt`
- Python may not be on `PATH` as `python3` — try `py` (the Windows
  launcher) or use the full path to your Zcode-bundled Python
  (often under `codex-runtime/`)
- Path separator: use forward slashes `/` in agent prompts (most
  workers / models handle both, but consistency helps)

For more Windows troubleshooting, see
[`references/troubleshooting.md`](references/troubleshooting.md#windows).


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

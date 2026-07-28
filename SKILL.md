---
name: teamforge
description: "Recreates the TeamForge workflow (Leader + Workers + Verifier) inside Zcode 3.4.2+. Use this skill when the user wants parallel agent execution, structured task decomposition, independent quality verification, or multi-step work that benefits from sub-agents running concurrently. Triggers on: 'teamforge', 'team mode', 'multi-agent', 'split into subtasks', 'verify the result', '用 teamforge', '团队模式', '多智能体协作', '并行处理'. Do NOT use for simple single-step tasks."
version: 2.4.0
license: MIT
metadata:
  author: Community port (TeamForge CLI agent)
  origin: TeamForge — multi-agent team collaboration skill for Zcode
  compatibility: Zcode 3.4.2+ (per zcode-ai.com download page, as of 2026-07-26). Model-agnostic: works with whatever model your Zcode is configured for (Zcode 3.x supports multiple providers per its docs; not independently tested for each).
  category: workflow
  tested-on-ranges:
    - "prototype-todo-app e2e (20+23+5 tests, 48/48 passing) — included in this repo"
    - "skill format + YAML frontmatter validation (24+16 checks) — included"
    - "GitHub Actions CI: Ubuntu 24.04 + macOS + Windows (PowerShell install + Python startup), Python 3.8-3.12 — 12/12 jobs passing"
    - "Real Zcode runtime: tested 5+ times by community users (builds: frename CLI, mnote CLI, cquote CLI, hitokoto CLI, infrastructure audit). P0-P3 fixes from real-world feedback shipped in v1.3.14-v1.4.0. See CHANGELOG for details."
---

# TeamForge for Zcode

## What this skill does

Recreates the **TeamForge** workflow inside Zcode 3.4.2+
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

**TeamForge vs 理想状态：**

| 维度 | 理想状态 | Zcode + TeamForge |
|------|----------------------|---------------------|
| Leader 任务拆解 | 自动拆解 | ✅ Leader 用本 skill 手动/半自动拆 |
| Worker 并行 | ✅ 后台多任务 | ⚠️ 前台并行（Zcode 限制） |
| Verifier 对抗迭代 | ✅ 独立推理空间 | ⚠️ 用第二个 Zcode 会话模拟 |
| 状态机管理 | ✅ 内置状态机 | ❌ 无（用 checkpoint 模拟） |
| 上下文隔离 | ✅ Worker 独立上下文 | ✅ Zcode subagent 原生支持 |
| 适用模型 | 绑定单一模型 | 任意（取决于你 Zcode 接的 provider） |

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
# Linux / macOS / Git Bash / WSL
ls ~/.zcode/skills/teamforge/agents/
```
```powershell
# Windows PowerShell
dir $env:USERPROFILE\.zcode\skills\teamforge\agents\
```
```text
# should show (30+ files):
#   leader.md  verifier.md
#   worker-coder.md  worker-tester.md  worker-researcher.md
#   worker-doc-writer.md  worker-reviewer.md  worker-fixer.md
#   worker-ai-engineer.md  worker-backend-architect.md  ...
#   TEMPLATE_INDEX.md
```

If missing, see INSTALL.md.

## Workflow

### Step 1: 用户下达任务

直接说，例如：
> "用 teamforge 帮我做一个 X"

或自然语言触发：
> "这个任务比较复杂，拆开来做"
> "用 teamforge 跑一下"

### Step 2: Leader（你正在聊的 Zcode）做任务拆解

### Step 2.5: Leader 发布接口契约（在派 Worker 前必做）

> **为什么需要这一步**: Zcode 的 sub-agent 完全隔离、各自独立的 tool context,没有共享内存。如果 Leader 拆解完直接派发 4 个 Worker,Coder / Tester / Doc-Writer 拿到的 prompt 是各自独立的,**没人同步接口规范**,结果就是: Coder 实现 `--prefix/--suffix/--replace/--regex/--index/--dry-run/--verbose`, Doc-Writer 文档里写 `--number/--name/--start/--digits/--recursive/--filter/--include-dirs`,根本不是同一个工具。

**强制流程**:
1. Leader 在派发 Worker 之前,**必须**在团队共享目录写一个 `CONTRACT.md`(或在每个 Worker prompt 里塞同一段接口定义),内容包括:
   - 所有公开函数/类的签名(参数、返回、异常)
   - CLI 工具的完整 `--help` 输出(即使 Coder 还没写完代码,先约定)
   - 任何共享文件格式(JSON schema / Markdown 模板 / etc.)
   - 哪些文件必须存在(产物清单)
2. Coder 收到 prompt 后**先**按 CONTRACT 写 stub(`raise NotImplementedError`),**再**实现,确保符合契约
3. Tester / Doc-Writer 基于 CONTRACT 工作,不直接参考 Coder 后续实现
4. Leader 在 Step 4 整合时,检查 Worker 产物是否遵守 CONTRACT,违反的返回重做

> **如果只有一个 Worker 也要写 CONTRACT** —— 复杂度低的时候只是个 5 行的 `--help` 输出,但省下了"Doc-Writer 文档说 --number 但代码里是 --index"这种返工。

> **如果任务太简单**(单文件、< 50 行、单一函数)可以跳过 CONTRACT,但 Leader 必须在 prompt 里**写明完整的接口规范**作为 Worker 的输入。

> **CONTRACT 里的文本处理要求**: 如果任务涉及中文/emoji/任何非 ASCII 文本存储、搜索、序列化,CONTRACT 必须明言写盘 (`ensure_ascii=False`)、读盘 (`encoding="utf-8"`)、验证（至少 1 个非 ASCII 测试用例）和 CLI 输出格式（plain / ANSI / JSON）。完整规范见 [`references/encoding-guidelines.md`](references/encoding-guidelines.md)。在 CONTRACT 里就写明,不要在 Verifier 阶段才发现。

> **CONTRACT 智能验证**: Leader 在 Step 4 整合时，**必须**验证 Worker 产出是否遵守 CONTRACT。验证策略按优先级：

**Level 1 — 结构验证（必须）**：
- 检查 CONTRACT 中定义的所有文件是否已创建（`ls` 命令）
- 检查每个文件非空（`wc -l` 命令）

**Level 2 — 接口验证（推荐）**：
- 对 Python 代码：使用 AST 验证脚本检查函数是否存在且签名正确
  ```bash
  python scripts/validate_contract_ast.py <file.py> <func1> <func2> ...
  ```
  示例：`python scripts/validate_contract_ast.py src/main.py scan_file scan_directory detect_language`
  这比 grep 健壮：即使函数是 `async def`、有装饰器、或在注释中出现同名，AST 也能准确识别。
  如果脚本报错"语法错误"，说明 Worker 产出的代码有语法问题，需要返工。
- 对 CLI 工具：运行 `--help` 并检查输出中是否包含 CONTRACT 定义的参数名
- 对 JSON 输出：运行工具并用 `python -c "import json; ..."` 验证输出格式

**Level 3 — 语义验证（高 stakes 任务）**：
- 运行测试套件，确认所有测试通过
- 对关键函数调用一次，验证返回值格式

**验证失败处理**：如果 Level 1 失败 → 立即返工。如果 Level 2 失败 → 标记为 CONTRACT VIOLATION，派 Fixer 修复。如果 Level 3 失败 → 按正常 FAIL 流程处理。

Leader 必须输出一个**结构化任务书**，格式见 `agents/leader.md` 的 Phase 1。

### Step 2.7: 拆解质量自检

Leader 在发布 Team Plan 之前，**必须**用以下 checklist 自检拆解质量：

- [ ] 每个子任务有明确的输入/输出描述
- [ ] 每个子任务有可验证的验收标准（不是"做好就行"）
- [ ] 子任务之间依赖关系已标注（无遗漏的隐式依赖）
- [ ] 没有重复工作（两个 Worker 不做同一件事）
- [ ] 没有遗漏工作（所有需求都被某个子任务覆盖）
- [ ] 子任务粒度合适（不会太粗以至于 Worker 不知从何下手，也不会太细以至于拆解本身比直接做还慢）
- [ ] CONTRACT 已覆盖所有跨 Worker 的接口约定
- [ ] Agent 类型选择正确（需要写文件的任务用 general-purpose，不误用 Explore）

如果任何一项不通过，Leader 必须修正后再派发。

### Step 2.8: 依赖图可视化

Leader 在 Team Plan 中**必须**输出执行顺序，按 Wave 分批：

```markdown
## 执行顺序 (Execution Waves)

### Wave 1（无依赖，立即并行执行）
- Subtask A
- Subtask B
- Subtask D

### Wave 2（依赖 Wave 1 完成）
- Subtask C（依赖 A）
- Subtask E（依赖 B + D）

### Wave 3（依赖 Wave 2 完成）
- Subtask F（依赖 C + E）
```

**规则**:
- Wave 1: 所有没有依赖的子任务
- Wave N: 所有依赖 Wave N-1（或更早 Wave）的子任务
- 同一 Wave 内的子任务**必须并行**派发
- 不同 Wave 之间**必须串行**（前一个 Wave 全部完成后才派发下一个）
- 如果某个子任务跨 Wave 依赖（如 Wave 3 依赖 Wave 1），仍按最早依赖的 Wave 归组

### Step 3: Leader 启动并行子智能体

Leader 在主对话里调用 Zcode 的 sub-agent 机制。两种用法：

**A. 使用 Zcode 内置 sub-agent**（推荐用于标准任务）：

- **研究类,只读调研,总结在对话里返回** → 用 Zcode 内置的 `Explore`(只读、不改文件,快速廉价)
- **研究类,需要产出文件(报告/RESEARCH.md/结构化 JSON)** → 用 Zcode 内置的 `general-purpose`(完整工具权限)
- **实现类**(写代码、改文件) → 用 Zcode 内置的 `general-purpose`(完整工具权限)

> **常见坑**(v1.4.0 反馈): Leader 因为"这是研究任务"就选 Explore,然后又让 Worker 写文件,Explore 不会写,产物丢。**判断标准**: 如果 Leader 的 prompt 里出现"写入 X.md"/"产出报告"/"存为文件"等词,必须用 general-purpose,不能用 Explore。详见 `agents/worker-researcher.md` 里的 Mode selection 表。
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

> **Worker 超时**: 如果 sub-agent 超过 **5 分钟**未返回结果，Leader 应视为该 Worker 失败。处理方式：记录为 FAILED，不阻塞其他 Worker；在 Step 4 整合时决定是否重试。Zcode 的 sub-agent 没有内置超时机制，Leader 需要自行通过时间戳判断。

**模板加载策略（Token 优化）**：

当前策略是 Leader 在 prompt 中注入 Worker 模板的全部内容，这会消耗大量 Token。
优化后的策略是"Worker 自读"：

1. Leader 在 prompt 中只写**核心指令**（任务描述、验收标准、CONTRACT 路径）
2. Leader 在 prompt 中附加一行：`请先读取你的角色定义文件: agents/worker-xxx.md`
3. Worker 启动后使用 `Read` 工具自行读取角色定义，获取完整的行为规范

**示例 prompt**：
```
TASK: 实现 xxx 功能
ACCEPTANCE: [具体验收标准]
CONTRACT: D:\Z code\project\CONTRACT.md
CONTEXT: [相关文件列表]

请先读取以下文件获取你的角色定义和行为规范:
- agents/worker-coder.md
- references/common-rules.md
```

**Token 节省效果**：
- 旧策略：每个 Worker prompt ~2000 Token（注入完整模板）
- 新策略：每个 Worker prompt ~300 Token（只写核心指令）
- 3 个 Worker 节省 ~5100 Token（约 60-70%）

### Step 3.5: Wave 间产物交接协议

当存在多个 Wave 时，Wave 间的产物交接**必须**通过文件显式传递，不能依赖 Leader 的记忆或摘要转述：

**规则**:
1. 前一个 Wave 的每个 Worker **必须**将关键产物写入磁盘（代码文件、报告文件等）
2. Leader 在派发下一个 Wave 前，**必须**确认前一个 Wave 的所有产物文件已存在且非空
3. 下一个 Wave 的 Worker prompt 中**必须**引用前一个 Wave 的产物文件路径
4. 如果 Wave 2 的 Worker 发现 Wave 1 的产物有误，**必须**标记 `NEEDS-ROLLBACK`，由 Leader 决定是否重做

**示例**:
```
Wave 1: Coder 写 src/auth.py → 文件必须存在
Wave 2: Tester 写 tests/test_auth.py → prompt 中引用 "参考 src/auth.py 的实现"
```

**回退机制**: 如果 Wave N 的 Worker 发现 Wave N-1 的产物有致命问题：
- Worker 在报告中标记 `NEEDS-ROLLBACK: <原因>`
- Leader 评估后决定：(a) 派 Fixer 修复, (b) 重做 Wave N-1 的相关子任务, (c) 缩小范围跳过

**失败传播规则**：
- 如果 Wave N 中某个子任务 FAILED，Leader 必须立即检查 Wave N+1 中是否有子任务依赖它
- 如果有依赖 → 该 Wave N+1 子任务标记为 **BLOCKED**，不派发，不消耗 Token
- Leader 优先处理 FAILED 子任务（派 Fixer 修复），修复成功后再派发被 BLOCKED 的子任务
- 如果 FAILED 子任务 3 轮修复失败 → 将 BLOCKED 子任务从计划中移除，输出降级版本

**状态矩阵**：Leader 必须维护一个子任务状态矩阵，格式如下：
```markdown
| 子任务 | Wave | 状态 | 依赖 | 产出文件 |
|--------|:----:|:----:|------|----------|
| Subtask 1 | 1 | ✅ DONE | — | src/main.py |
| Subtask 2 | 1 | ❌ FAILED | — | — |
| Subtask 3 | 2 | ⏸️ BLOCKED | Subtask 2 | — |
```

### Step 4: 收集子任务结果

Leader 收到所有子智能体的摘要后，**自己整合**成初版交付物。

**关键原则**：
- ✅ 只看摘要（Zcode 子智能体上下文已隔离）
- ✅ 标出每个摘要的来源 subagent
- ❌ 不要重做子任务的工作（信任 subagent 的摘要）

**任务完成度 checklist**（Phase 3 整合前必须逐项对照）：

- [ ] Team Plan 中每个子任务都有对应的 Worker 输出
- [ ] 没有 Worker 返回 FAILED 或超时未返回
- [ ] 每个 Worker 输出的文件路径与 CONTRACT 产物清单一致
- [ ] 用 `grep` 验证 Worker 产出包含 CONTRACT 定义的接口字符串
- [ ] 所有验收标准都有对应的证据（测试通过截图、文件存在性等）
- [ ] 子任务之间没有接口冲突（如 Coder 的函数签名与 Tester 的调用一致）

如果任何一项不通过，Leader 必须在整合前修复（重新派发对应 Worker 或手动补齐）。

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

**方法 D（自动化）**：Verifier 作为 sub-agent 自动派发
- Leader 在 Phase 4 中自动派发一个 Verifier sub-agent（使用 `agents/verifier.md` 模板）
- 传入：(1) 原始任务描述, (2) 整合后的交付物, (3) 验收标准
- Verifier sub-agent 独立执行检查，返回 PASS/FAIL 清单
- **不需要用户手动操作**，Leader 自动完成整个验证流程
- 推荐用于自动化流水线或用户希望"一键完成"的场景

### Step 5.5: 状态快照（断点恢复机制）

在每个 Wave 完成后，Leader **必须**将状态变更追加到 `.teamforge_state.log` 文件：

**日志追加模式**（替代 JSON 文件写入，避免并发损坏）：
```bash
# 每次状态变更追加一行（不会覆盖之前的数据）
echo '{"ts":"2026-07-29T10:00:00","wave":1,"task":"subtask_1","status":"done","files":["src/main.py"]}' >> .teamforge_state.log
echo '{"ts":"2026-07-29T10:05:00","wave":1,"task":"subtask_2","status":"done","files":["tests/test.py"]}' >> .teamforge_state.log
echo '{"ts":"2026-07-29T10:10:00","wave":2,"task":"subtask_3","status":"started"}' >> .teamforge_state.log
```

**恢复流程**：如果会话中断，用户说 "恢复上次的 teamforge 任务"，Leader 读取 `.teamforge_state.log` 并重放状态：
1. 解析日志，重建每个子任务的最新状态
2. 检查已完成子任务的产出文件是否仍然存在
3. 从最后一个未完成的 Wave 继续派发

**日志格式**：每行一个 JSON 对象，字段：
- `ts`: ISO 时间戳
- `wave`: Wave 编号
- `task`: 子任务 ID
- `status`: `started` | `done` | `failed` | `blocked`
- `files`: 产出文件列表（可选）
- `error`: 错误信息（可选）

### Step 6: 迭代修正

如果 Verifier 标 FAIL：
- Leader 拿到失败清单
- 重新派 subagent 修（针对失败点，不用全重做）
- 最多迭代 3 轮（防止无限循环）
- 第 3 轮仍 FAIL → 把失败清单交给用户决定

**降级策略**：如果 3 轮迭代后仍有 FAIL 项：
1. Leader 必须输出**当前可用的最小交付物**（标记哪些功能已通过、哪些未通过）
2. 列出剩余 FAIL 项的具体原因和修复建议
3. 将决策权交给用户：接受降级版本 / 手动修复 / 放弃
4. **不可静默失败**——即使全部 FAIL 也必须输出报告

**用户强制退出**：在迭代过程中，用户可以随时说以下指令来中止迭代：
- **"停止迭代"** / **"强制交付"** / **"输出当前最佳版本"** → Leader 立即跳过剩余迭代轮次，执行 Step 6 降级交付，输出当前最佳版本
- **"跳过验证"** / **"不需要验证"** → Leader 跳过 Step 5 Verifier，直接进入 Step 7 交付
- **"暂停"** → Leader 保存当前状态快照（Step 5.5），等待用户后续指令

这些指令优先级最高，Leader 必须立即响应，不可劝说用户继续迭代。

### Step 7: 交付

最终交付物 + 一份 Team Execution Report：
- 每个 subagent 的摘要
- Verifier 验收结果
- 迭代历史
- 已知限制

## Progress Reporting

每个 Phase 完成后，Leader **必须**输出进度更新，格式如下：

```
## 进度报告 (Progress Update)

### 当前 Phase: [Phase 名称]
- 已完成: [N/M 个子任务]
- 状态: [进行中/已完成/遇到阻塞]
- 下一步: [即将执行的操作]

### 子任务状态
| 子任务 | Worker | 状态 | 备注 |
|--------|--------|------|------|
| Subtask A | Worker-Coder | ✅ 完成 | - |
| Subtask B | Worker-Tester | ⏳ 进行中 | - |
| Subtask C | Worker-Researcher | ❌ 失败 | 超时，已重新派发 |
```

**规则**:
- Phase 1 完成后：输出 Team Plan 概要 + 子任务数量
- Phase 2 完成后：输出每个 Wave 的派发状态
- Phase 3 完成后：输出整合结果 + 完成度 checklist
- Phase 4 完成后：输出 Verifier 验收结果
- Phase 5 完成后：输出迭代历史（如有）
- Phase 6：最终报告包含所有 Phase 的进度汇总

## Usage examples

See `examples/` for full worked examples:
- `examples/refactor-large-module.md` — 重构大型模块
- `examples/bug-hunt.md` — 排查根因
- `examples/new-feature.md` — 加新功能
- `examples/research-then-implement.md` — 先调研再实现

## Sub-agent prompt templates

See `agents/` directory for ready-to-use prompt templates:
- `agents/leader.md` — Leader 主控 (Phase 1-6 流程)
- `agents/verifier.md` — 验收 verifier
- `agents/worker-coder.md` — 写代码 worker
- `agents/worker-tester.md` — 写测试 worker
- `agents/worker-researcher.md` — 调研 worker
- `agents/worker-doc-writer.md` — 文档 worker
- `agents/worker-reviewer.md` — code review worker
- `agents/worker-fixer.md` — 精准修复 worker (Step 6 Iterate, v1.4.0+)

## Common Pitfalls

See [`references/common-pitfalls.md`](references/common-pitfalls.md) for lessons learned from real-world usage, including:
- Explore agent 不能写文件
- `ensure_ascii=False` 必须在 CONTRACT 中声明
- Worker 角色不能越界
- 以及更多来自 CHANGELOG 的经验教训

## Advanced: DeepSeek + Zcode

This skill is **model-agnostic**. See `references/deepseek-setup.md`.

## Platform notes

### Windows users

This SKILL.md uses Unix-style commands in examples (e.g. `ls`, `ln -s`,
`~/.zcode/...`). For Windows users there are two paths, both fully
supported — see [`docs/WINDOWS.md`](docs/WINDOWS.md) for detailed
instructions:

- **Recommended**: WSL2 + `install.sh` — true symlinks, Linux file
  permissions, Zcode official support. Best for production / long-term use.
- **Alternative**: Native PowerShell + `install.ps1` — no WSL or Git Bash
  required. Best for quick trials or pure Windows environments.

Common Windows gotchas:

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
- TeamForge 是基于 Zcode 公开能力的开源工作流实现。
- For maximum fidelity, you also need the sub-agent configs
  in `agents/` — install the whole directory, not just SKILL.md.

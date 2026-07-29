# TeamForge

**多 Agent 团队协作技能 — 为 Zcode 3.4.2+ 设计**

> TeamForge 不是"提高效率"的工具，是"提高质量下限"的工具。
> 它用 **2-4 倍 Token** 换取 **结果的可预测性** 和 **质量的显著提升**。

[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Version](https://img.shields.io/badge/version-3.4.0-blue)](CHANGELOG.md)

---

## TeamForge 是什么

TeamForge 是一个 Zcode Skill，将复杂任务拆分为多个并行子任务，由专业化的 Agent 团队协作完成：

```
用户下达任务
    ↓
Leader 拆解任务 + 发布 CONTRACT 接口契约
    ↓
Wave 1: Worker-Coder + Worker-Doc-Writer（并行）
    ↓
Wave 2: Worker-Tester（依赖 Wave 1 产物）
    ↓
Leader 整合 + CONTRACT 字符串级验证
    ↓
Verifier 对抗式验证（Checker + Skeptic + Judge）
    ↓
交付 + 状态快照
```

**核心机制**：

| 机制 | 作用 |
|------|------|
| **CONTRACT 接口契约** | 所有 Worker 基于同一份接口规范工作，避免各说各话 |
| **Wave 并行执行** | 无依赖的子任务并行派发，有依赖的按 Wave 串行 |
| **DoD 清单** | 每个子任务附带"完成定义"，Worker 必须逐项打勾 |
| **对抗式验证** | Checker 按标准检查 + Skeptic 主动找茬 + Judge 最终裁决 |
| **产物交接协议** | Wave 间通过文件显式传递，不依赖 Leader 记忆 |
| **沙箱快照回溯** | Fixer 修复前先备份，失败可回退 |
| **状态快照** | 每个 Wave 完成后写入 `.teamforge_state.jsonl`，支持断点恢复 |

---

## 场景 × 成本 × 效果 一览

| 场景 | Token 消耗 | 墙钟时间 | 质量提升 | 值不值 |
|------|:----------:|:--------:|:--------:|:------:|
| 改个 typo / 调样式 | — | — | — | ❌ 直接单 Agent |
| 单文件 < 50 行 | — | — | — | ❌ 拆解 overhead 比直接写还慢 |
| 快速原型验证 | — | — | — | ❌ 速度优先，质量后补 |
| **小功能（2 Worker）** | **1.5-2x** | 快 30% | ✅ 提升 | ✅ 值得 |
| **标准任务（3 Worker + 验证）** | **2-3x** | 快 30-50% | ✅✅ 明显提升 | ✅ 推荐 |
| **高 stakes 项目（+ 对抗验证）** | **3-4x** | 快 20-40% | ✅✅✅ 显著提升 | ✅ 强烈推荐 |

> **为什么不是 4-6x？** 每个 Worker 只接收子任务 prompt + CONTRACT，不携带完整对话历史，实际消耗远低于"每个 Worker 都是完整 Agent"的理论值。

> *加速比数据源于并行 Worker 的理论模型推导，实际墙钟时间受 Zcode 宿主环境并发限制及任务图依赖关系影响。

**多花的 Token 换来了什么？**

| 收益 | 单 Agent 能做到吗？ |
|------|:------------------:|
| 并行执行，墙钟时间缩短 30-50% | ❌ 串行 |
| CONTRACT 接口契约，避免各说各话 | ❌ 没有机制 |
| 对抗式验证，多发现 30-40% 问题 | ❌ 同模型偏见 |
| DoD 清单，消除虚假完成 | ❌ 靠自觉 |
| 产物交接，Wave 间信息不丢失 | ❌ 上下文内隐式 |
| 断点恢复，会话中断可继续 | ❌ 从头开始 |

**一句话**：TeamForge 用 **2-4 倍 Token 换质量下限**。适合"宁可多花 Token 也不能出错"的场景。

---

## 快速开始

### 安装

```bash
# 方式 1: 一键脚本（推荐）
bash scripts/install.sh

# 方式 2: PowerShell（Windows 原生）
> **⚠️ Windows 用户注意**：TeamForge 的部分功能依赖 Unix 命令（如 `grep`、`wc`、`mv`）。
> 如果您使用原生 PowerShell（非 WSL），请确保已安装 [Git for Windows](https://git-scm.com/download/win) 并将其添加到 PATH。
> 推荐使用 WSL2 + `install.sh` 方案以获得最佳兼容性。

powershell -ExecutionPolicy Bypass -File scripts/install.ps1

> **编码提示**：如果执行 `install.ps1` 出现乱码或语法错误，请确保文件编码为 UTF-8 with BOM，或在 PowerShell 中执行 `chcp 65001` 切换到 UTF-8 代码页。

# 方式 3: 手动 clone
git clone https://github.com/Qqapple1/TeamForge.git ~/.zcode/skills/teamforge
```

### 使用

```bash
# 在 Zcode 中直接说：
"用 teamforge 帮我做一个 CLI 工具，支持 xxx 功能"

# 或者：
"这个任务比较复杂，拆开来做"
"用 teamforge 跑一下"
```

Zcode 会根据 description 自动匹配并加载 TeamForge skill。

---

## 仓库结构

```
teamforge/
├── SKILL.md                    # 核心 skill 定义
├── agents/                     # Agent 角色模板（33 个）
│   ├── leader.md               #   Leader 主控
│   ├── verifier.md             #   Verifier 对抗式验证
│   ├── worker-coder.md         #   写代码
│   ├── worker-tester.md        #   写测试
│   ├── worker-researcher.md    #   调研（只读）
│   ├── worker-doc-writer.md    #   文档
│   ├── worker-reviewer.md      #   代码审查
│   ├── worker-fixer.md         #   精准修复
│   ├── worker-ai-engineer.md   #   AI 工程师
│   ├── worker-backend-architect.md  # 后端架构
│   ├── ROLE_INDEX.yaml           #   角色关键词索引
│   └── ... (共 33 个角色)
├── references/                 # 参考文档（8 个）
│   ├── common-rules.md         #   通用行为规范
│   ├── common-pitfalls.md      #   15 条常见陷阱
│   ├── memory-system.md        #   记忆系统
│   ├── verification-checklist.md # 增强验证清单
│   └── meeting-templates/      #   8 种会议模板
├── memory/                     # 记忆存储目录
├── examples/                   # 使用案例
├── scripts/                    # 安装/验证脚本
│   ├── teamforge_utils.py        #   跨平台工具函数
│   ├── validate_contract_ast.py  #   AST 契约验证
└── docs/                       # 设计文档
```

---

## 版本历史

| 版本 | 日期 | 主要变更 |
|------|------|----------|
| **v3.1.0** | 2026-07-29 | 数据库编码规范 + 版本号统一 + 测试框架说明 |
| v2.0.0 | 2026-07-28 | 状态快照 + 权限修复 + Fixer 增强 + 公共规则 + 对抗式验证 |
| v1.5.1 | 2026-07-28 | 对抗式验证 + DoD 清单 + 产物交接 + 快照回溯 + 多视角分析 |
| v1.5.0 | 2026-07-28 | 核心工作流增强 + 25 个角色模板 + 8 种会议模板 + 记忆系统 |
| v1.4.0 | 2026-07-27 | 初始版本 |

详见 [CHANGELOG.md](CHANGELOG.md)。

---

## 已知限制

| 限制 | 原因 | 缓解方案 |
|------|------|----------|
| Worker 前台并行，非后台 | Zcode sub-agent 机制限制 | 等平台升级 |
| Verifier 同模型偏见 | 无法切换模型 | 对抗式验证模式 |
| 无真正的状态机 | 需要持久化存储 | `.teamforge_state.jsonl` 快照 |
| Agent 间无法直接通信 | 需要平台支持 | Leader 中转 + 文件交接 |
| Worker 工具权限无法差异化 | Zcode 不支持 per-agent 工具限制 | prompt 约束 |

---

## 贡献

详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## License

MIT — 详见 [LICENSE](LICENSE)。

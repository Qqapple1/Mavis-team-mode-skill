---
name: common-pitfalls
description: "常见陷阱和经验教训，来自 Mavis Team Mode 的真实使用反馈 (v1.3.14-v1.4.0)。Leader 和 Worker 在执行团队工作流时必须阅读。"
version: 1.5.0
---

# Common Pitfalls — 常见陷阱与经验教训

本文档汇总了 Mavis Team Mode 在真实 Zcode 运行环境中积累的教训。
来源：v1.3.14 至 v1.4.0 的 CHANGELOG，来自 5+ 次社区用户实测反馈。

---

## 1. Explore agent 不能写文件

**严重程度**: P1 (功能性)

**现象**: Leader 因为"这是研究任务"就选 Explore agent，然后让 Worker 写文件（如 `RESEARCH.md`、报告）。Explore 是只读的，不会写文件，结果"调研了但没写文件"——静默失败。

**根因**: Explore agent 的工具权限不包含 Write/Edit。Leader 的 prompt 里出现"写入 X.md"/"产出报告"/"存为文件"等词时，必须用 general-purpose。

**判断标准**:
| Worker 任务 | 正确的 Agent 类型 |
|---|---|
| 只读调研，总结在对话里返回 | Explore |
| 需要产出文件（报告/RESEARCH.md/JSON） | general-purpose |
| 写代码、改文件 | general-purpose |

**来源**: CHANGELOG v1.3.14 P1 修复

---

## 2. ensure_ascii=False 必须在 CONTRACT 中声明

**严重程度**: P1 (功能性)

**现象**: 用户的 Coder 写 `json.dumps(value)` 序列化中文到磁盘。默认 `ensure_ascii=True` 会把中文转义为 ASCII escape。后续 `mnote search "技术"` 匹配零行，因为磁盘上存的是 ASCII escape，不是原始中文字符。

**根因**: Python `json.dumps` 默认 `ensure_ascii=True`。Coder 不一定会意识到这个默认行为。

**修复**: CONTRACT 中**必须**声明：
- 写盘：`json.dumps(value, ensure_ascii=False)`
- 读盘：`open(..., encoding="utf-8")`
- 验证：至少 1 个非 ASCII 测试用例
- CLI 输出格式：plain / ANSI / JSON

**来源**: CHANGELOG v1.3.15 修复 + SKILL.md Step 2.5

---

## 3. Worker 角色不能越界

**严重程度**: P2 (一致性)

**现象**: Worker 之间职责混乱。例如 Tester 去改代码（应该只写测试），Reviewer 去实现功能（应该只 review）。

**根因**: Worker prompt 没有明确的职责边界。

**规则**:
| Worker 角色 | 允许 | 禁止 |
|---|---|---|
| Worker-Coder | 写代码、改代码、写 stub | 写测试、写文档 |
| Worker-Tester | 写测试、运行测试 | 改代码、写文档 |
| Worker-Doc-Writer | 写文档、README | 改代码、写测试 |
| Worker-Reviewer | 读代码、写 review 报告 | 改代码、写测试 |
| Worker-Fixer | 最小化修复（~30 行以内） | 重写、重构 |
| Worker-Researcher | 调研、搜索、总结 | 改代码、写测试 |

**来源**: 基于 agents/*.md 的角色定义

---

## 4. Tester 必须剥离 ANSI 转义码

**严重程度**: P1 (功能性)

**现象**: Coder 给 CLI 输出加了 ANSI 黄色高亮（`\x1b[33m关键词\x1b[0m`）。Tester 用 subprocess 跑 CLI 后直接 assert 原始 stdout，结果 4 个测试假阴性失败。代码是正确的，测试是错的。

**根因**: Tester 没有剥离 ANSI 转义码就做字符串匹配。

**修复**:
```python
import re
clean_output = re.sub(r'\x1b\[[0-9;]*m', '', raw_output)
```

或者优先使用 `--no-color` / `NO_COLOR=1` 环境变量。

**来源**: CHANGELOG v1.3.16 修复

---

## 5. Tester 不能猜输出文案

**严重程度**: P2 (一致性)

**现象**: Tester 的测试用例里写 `["no","empty","暂无","没有"]`，但代码实际输出的是"为空"（不在列表中）。测试永远通过，但匹配的是错误的文案。

**根因**: Tester 基于猜测写匹配列表，而不是基于实际运行输出。

**修复**: Tester 必须先运行一次 CLI，复制实际输出文案到测试断言中。不要猜。

**来源**: CHANGELOG v1.3.16 修复

---

## 6. CONTRACT 不一致是 Worker 产出不兼容的 #1 原因

**严重程度**: P1 (功能性)

**现象**: Coder 实现 `--prefix/--suffix/--replace/--regex/--index/--dry-run/--verbose`，Doc-Writer 文档里写 `--number/--name/--start/--digits/--recursive/--filter/--include-dirs`。根本不是同一个工具。

**根因**: 4 个 sub-agent 完全隔离，各自独立的 tool context，没有共享内存。没有 CONTRACT 就没有接口同步。

**修复**: Leader 在派发 Worker 之前**必须**创建 CONTRACT.md，包含完整的接口定义。所有 Worker 基于 CONTRACT 工作，不直接参考其他 Worker 的实现。

**来源**: CHANGELOG v1.3.14 P2 修复

---

## 7. CONTRACT 字符串级验证不可跳过

**严重程度**: P1 (功能性)

**现象**: Leader 写了 CONTRACT，但没有验证 Worker 产出是否遵守。结果 Coder 的代码里有 `--prefix`，但 Doc-Writer 的文档里写的是 `--number`。

**根因**: Leader 只"信任"Worker 的摘要，没有用 grep 做字符串级验证。

**修复**: Leader 在 Phase 3 整合时**必须**用 `grep` 检查每个 Worker 产出是否包含 CONTRACT 中定义的接口字符串。不匹配的视为 CONTRACT 违规，必须返工。

**来源**: SKILL.md Step 2.5 强化

---

## 8. Verifier 必须是只读的

**严重程度**: P1 (功能性)

**现象**: Verifier 有 `write_file` + `edit_file` + `Bash` 权限。Verifier 在"验证"过程中偷偷改了代码，然后报告 PASS。

**根因**: Verifier 的工具权限包含写入权限，破坏了独立验证的公正性。

**修复**: Verifier 的 tools 列表**必须**移除 `Write` 和 `Edit`。保留 `Bash`（用于运行测试）和 `Read`（用于读取代码）。添加 `WebFetch`（用于独立验证外部文档声明）。

**来源**: CHANGELOG v1.3.17 P1 修复

---

## 9. Leader 兼任 Verifier 有同模型偏见

**严重程度**: P2 (一致性)

**现象**: Leader 自己当 Verifier（Method C），结果"自我验收"变成"自我放水"。同模型同上下文容易对自己产出的内容过于宽容。

**根因**: 同模型偏见（self-bias）。

**修复**:
- 高风险任务：用 Method A（开第二个 Zcode 会话）
- 中风险任务：用 Method D（自动派发 Verifier sub-agent）
- 低风险任务：用 Method C 但配合硬 checklist，逐项勾选，接受 20-30% 漏检率

**来源**: CHANGELOG v1.3.14 修复

---

## 10. Coder 必须支持 --no-color / NO_COLOR=1

**严重程度**: P2 (一致性)

**现象**: Coder 给 CLI 加了 ANSI 颜色高亮，但没有提供禁用方式。Tester 的测试在 CI 环境中失败（CI 没有 TTY，ANSI 输出不一致）。

**根因**: Coder 没有考虑非交互式环境。

**修复**: Coder 的代码中**必须**包含：
```python
import os, sys

def color(text, code):
    if os.environ.get("NO_COLOR") or "--no-color" in sys.argv:
        return text
    return f"\033[{code}m{text}\033[0m"
```

参考 https://no-color.org

**来源**: CHANGELOG v1.3.18 修复

---

## 11. Doc-Writer 必须有 Bash 权限

**严重程度**: P2 (一致性)

**现象**: Doc-Writer 的 tools 列表没有 Bash。Doc-Writer 写的文档里有"运行 `python -c "print('hello')` 查看效果"，但它自己没法验证这个例子能不能跑。

**根因**: Doc-Writer 的工具权限不完整。

**修复**: Doc-Writer 的 tools 列表**必须**包含 Bash，这样它可以验证自己写的代码示例是否可运行。

**来源**: CHANGELOG v1.3.17 P2 修复

---

## 12. Leader 不能硬编码语言

**严重程度**: P3 (小问题)

**现象**: leader.md 硬编码"Speak Chinese by default"。英文用户收到中文输出。

**根因**: Leader 没有做语言检测。

**修复**: Leader **必须**匹配用户的语言（从对话中检测，不要硬编码）。

**来源**: CHANGELOG v1.3.17 P3 修复

---

## 13. Commit 不要撒谎

**严重程度**: P0 (信任问题)

**现象**: CHANGELOG 和 commit message 声称"已修复 X"，但实际上没有。例如 v1.3.17 声称"all 7 agents use PascalCase"，但实际上 leader.md 被遗漏了。这是该仓库历史上第 3 次 commit-message lie。

**根因**: 修改后没有验证就写了 commit message。

**修复**: 
- 每次修改后**必须**运行验证（`validate.sh` / `validate.ps1`）
- commit message 中的声明**必须**与实际修改一致
- 如果不确定，用"partial fix"而非"fixed"

**来源**: CHANGELOG v1.3.19 硬性 bug #1

---

## 14. Windows 路径和语法差异

**严重程度**: P3 (小问题)

**现象**: SKILL.md 示例用 Unix 命令（`ls`, `ln -s`, `~/.zcode/...`）。Windows 用户遇到 `python3` 找不到、glob 不展开、`~` 不展开等问题。

**修复**:
- `~` 不展开 → 用 `$env:USERPROFILE`
- `python3` 找不到 → 用 `py`（Windows Python launcher）
- glob 不展开 → 显式传文件名
- 路径分隔符 → 在 agent prompt 中用 `/`

**来源**: CHANGELOG v1.3.14 P3 修复

---

## 15. 子任务 prompt 不能用同一份泛型模板

**严重程度**: P2 (一致性)

**现象**: Leader 把所有子任务用同一个泛型 prompt 派发，导致 Worker 产出质量低、方向偏。

**根因**: Leader 偷懒，没有为每个子任务定制 prompt。

**修复**: 每个 sub-agent 的 prompt **必须**包含：
1. 具体子任务描述（不是"做 X"，而是"实现 X 的 Y 功能，包含 Z 参数"）
2. 验收标准（可验证）
3. 输出格式要求（统一格式方便后面聚合）
4. 上下文限制（不读的目录、不用的工具）

**来源**: leader.md 核心原则

---

## Checklist: 使用前快速自检

Leader 在派发 Worker 前，快速过一遍：

- [ ] CONTRACT 已创建（多 Worker 场景）
- [ ] CONTRACT 包含非 ASCII 处理要求（如涉及中文/emoji）
- [ ] Agent 类型选择正确（需要写文件 → general-purpose）
- [ ] 每个 Worker 的 prompt 是定制的，不是泛型模板
- [ ] 验收标准是可验证的，不是"看起来没问题"
- [ ] 依赖关系已标注，Wave 顺序已规划

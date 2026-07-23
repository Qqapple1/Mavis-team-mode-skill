---
name: example-refactor-large-module
description: "Worked example: refactor a 1500-line legacy module into 3 separate modules using Mavis Team Mode. Reference document, not a triggerable skill."
type: example
category: refactor
---

# Example: Refactor a Large Module

**User task**: "重构 src/legacy_auth.py（1500 行），按职责拆成 3 个模块，不改对外行为。"

## Phase 1: Leader Plan

```markdown
# Team Plan

## 目标
把 src/legacy_auth.py（1500 行）按职责拆成 3 个模块，对外 API 完全不变。

## 子任务清单

### Subtask 1: 分析 legacy_auth.py 的结构
- **type**: explore
- **prompt**: 阅读 src/legacy_auth.py，输出：
  1. 顶层函数/类清单
  2. 按职责归类（密码处理 / session 管理 / OAuth / 工具函数）
  3. 每个职责的代码行范围
  4. 哪些函数被外部模块 import
- **acceptance**:
  - [ ] 全部顶层定义被列出
  - [ ] 职责归类合理
  - [ ] 外部 import 清单完整
- **dependency**: none
- **estimated_minutes**: 5

### Subtask 2: 提取密码处理模块
- **type**: general-purpose
- **prompt**: 基于 Subtask 1 的分析结果，提取所有密码处理函数到 src/auth/password.py。
  - 不改函数签名
  - 不改函数逻辑
  - 完整保留所有 import
  - 写一个空 __init__.py
- **acceptance**:
  - [ ] legacy_auth.py 中所有密码相关函数都已提取
  - [ ] 新文件能 import
  - [ ] 原 legacy_auth.py 中相应位置已删干净（不留死代码）
- **dependency**: depends-on-subtask-1
- **estimated_minutes**: 15

### Subtask 3: 提取 session 管理模块
- **type**: general-purpose
- **prompt**: 基于 Subtask 1 的分析结果，提取所有 session 管理函数到 src/auth/session.py。
  - 不改函数签名
  - 不改函数逻辑
  - 完整保留所有 import
  - 写一个空 __init__.py
- **acceptance**:
  - [ ] legacy_auth.py 中所有 session 相关函数都已提取
  - [ ] 新文件能 import
  - [ ] 原 legacy_auth.py 中相应位置已删干净（不留死代码）
- **dependency**: depends-on-subtask-1
- **estimated_minutes**: 15

### Subtask 4: 提取 OAuth 模块
- **type**: general-purpose
- **prompt**: 基于 Subtask 1 的分析结果，提取所有 OAuth 相关代码到 src/auth/oauth.py。
  - 不改函数签名
  - 不改函数逻辑
  - 完整保留所有 import
  - 写一个空 __init__.py
- **acceptance**:
  - [ ] legacy_auth.py 中所有 OAuth 相关代码都已提取
  - [ ] 新文件能 import
  - [ ] 原 legacy_auth.py 中相应位置已删干净（不留死代码）
- **dependency**: depends-on-subtask-1
- **estimated_minutes**: 15

### Subtask 5: 更新所有 import
- **type**: general-purpose
- **prompt**: 全项目搜出所有 `from src.legacy_auth import X` 的地方，改成对应的新模块路径。
- **acceptance**:
  - [ ] 所有 import 路径已更新
  - [ ] 没有遗漏的旧 import
  - [ ] 项目能正常 import（无 ImportError）
- **dependency**: depends-on-subtask-2,3,4
- **estimated_minutes**: 10

### Subtask 6: 跑完整测试
- **type**: general-purpose
- **prompt**: 跑 `pytest tests/`，报告所有通过/失败的测试。
- **acceptance**:
  - [ ] 所有原有测试通过
  - [ ] 没有新的 test failure
- **dependency**: depends-on-subtask-5
- **estimated_minutes**: 5

## 验收标准
- [ ] legacy_auth.py 被拆成 3 个文件
- [ ] 对外 API 完全不变
- [ ] 所有原有测试通过
- [ ] 没有任何一行密码逻辑还在 legacy_auth.py 中

## 风险
- 拆分时漏掉某个工具函数 → fallback: Subtask 1 严格列出所有函数
- 循环 import → fallback: 保持原 import 顺序，必要时在 __init__.py 统一导出
- 行为改变 → fallback: Subtask 6 必须 0 修改通过所有测试
```

## Phase 2: Dispatch

Leader 派 Subtask 1（Explore）→ 等结果 → 然后并行派 Subtask 2、3、4（general-purpose）→ 等结果 → 派 Subtask 5 → 等结果 → 派 Subtask 6。

## Phase 3: Integration

Leader 拿到所有结果，输出一份"重构报告"：
- 拆出来的 3 个文件路径
- 每个文件多少行
- 删了多少行 legacy 代码
- 测试结果

## Phase 4: Verification

开第二个 Zcode 会话当 Verifier：
- 抽查 3 个新文件，验证职责划分合理
- 跑一次 `pytest`，确认 0 失败
- grep `legacy_auth`，确认没漏掉的引用
- 输出 PASS / FAIL

## Result

✅ 1500 行 → 3 个模块（avg 400-500 行/个）
✅ 所有测试通过
✅ 对外 API 不变
✅ 总耗时：单线程约 45 分钟；Team 模式约 20 分钟（并行加速 2x）

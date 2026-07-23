# Example: Bug Hunt + Fix

**User task**: "用户报告说下单成功后偶尔会扣两次款。找出根因并修。"

## Phase 1: Leader Plan

```markdown
# Team Plan

## 目标
定位"下单成功后偶尔扣两次款"的根因，实施修复，并通过回归测试。

## 子任务清单

### Subtask 1: 复现路径分析
- **type**: explore
- **prompt**: 阅读 `src/payment/` 下的所有文件，重点关注：
  1. 订单创建和扣款的调用关系
  2. 是否有 retry / 幂等性检查
  3. 异步任务队列（Celery / Sidekiq / 自研）
  4. 数据库事务边界
  输出：所有可能的"扣两次款"的代码路径。
- **acceptance**:
  - [ ] 所有相关文件被列出
  - [ ] 每条路径都有"为什么可能扣两次"的分析
- **dependency**: none
- **estimated_minutes**: 10

### Subtask 2: 历史 commit / PR 调查
- **type**: explore
- **prompt**: 查 `git log -- src/payment/` 过去 6 个月，找出：
  1. 是否有人改过重试逻辑
  2. 是否有过相关 bug fix 又被 revert
  3. 是否有可疑的 race condition commit
  输出：嫌疑 commit 列表。
- **acceptance**:
  - [ ] 列出了至少 3 个嫌疑 commit
  - [ ] 每个 commit 都有"为什么怀疑它"的说明
- **dependency**: none
- **estimated_minutes**: 5

### Subtask 3: 写复现测试
- **type**: general-purpose
- **prompt**: 基于 Subtask 1 的根因分析，写一个测试 case，能在本地稳定复现"扣两次款"的问题。
  - 不要 fix 任何代码
  - 只写失败的测试
  - 跑测试，截图 / 贴输出
- **acceptance**:
  - [ ] 测试能本地跑
  - [ ] 测试稳定失败（多次跑都失败）
  - [ ] 失败信息明确指向"扣两次"的证据
- **dependency**: depends-on-subtask-1
- **estimated_minutes**: 20

### Subtask 4: 实施修复
- **type**: general-purpose
- **prompt**: 修复扣两次款的问题。要求：
  1. 最小改动
  2. 保持对外 API 不变
  3. 修复后 Subtask 3 的测试必须通过
  4. 不破坏其他测试
- **acceptance**:
  - [ ] Subtask 3 的测试现在通过
  - [ ] 全部现有测试通过
  - [ ] 改动文件清单 + 改动说明
- **dependency**: depends-on-subtask-3
- **estimated_minutes**: 30

### Subtask 5: 加回归测试
- **type**: general-purpose
- **prompt**: 基于 Subtask 4 的修复，加 2-3 个针对此类 race condition 的回归测试。
- **acceptance**:
  - [ ] 新增至少 2 个测试
  - [ ] 覆盖 Subtask 1 分析的所有可疑路径
  - [ ] 全部通过
- **dependency**: depends-on-subtask-4
- **estimated_minutes**: 15

## 验收标准
- [ ] Subtask 3 的复现测试现在通过
- [ ] 没有引入新 bug（其他测试 0 失败）
- [ ] 根因在最终报告里说清楚
- [ ] 至少 2 个回归测试加入

## 风险
- 根因可能不在 payment 模块，而在调用方 → fallback: Subtask 1 扩大范围
- 修复可能影响性能 → fallback: 跑性能基准对比
- race condition 难以稳定复现 → fallback: 注入延时/重试让 race 更易触发
```

## Phase 2: Dispatch

并行：Subtask 1（Explore）+ Subtask 2（Explore）
↓
串行：Subtask 3 → Subtask 4 → Subtask 5

## Phase 3: Integration

Leader 拿到结果后，输出：
- **Root Cause Report**：
  - 根因是什么（具体文件 + 行号）
  - 为什么之前没被发现
  - 这次为什么会暴露
- **Fix Summary**：改了什么、为什么这样改
- **Test Coverage**：新增了哪些测试

## Phase 4: Verification

第二个 Zcode 会话当 Verifier：
- 独立复现 Subtask 3 的测试
- 验证 Subtask 5 的回归测试覆盖到位
- 检查修复没有引入新问题
- 评估：根因分析是否可信，还是只是治标

## Result

✅ 根因找到
✅ 测试覆盖
✅ 单线程：60+ 分钟；Team 模式：~35 分钟（并行加速）

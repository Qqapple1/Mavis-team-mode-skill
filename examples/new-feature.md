---
name: example-new-feature
description: "Worked example: add a tag-filter feature to a Todo app end-to-end using Mavis Team Mode. Reference document, not a triggerable skill."
type: example
category: feature
---

# Example: Add a New Feature End-to-End

**User task**: "给 Todo app 加一个'按标签筛选'功能：左侧显示所有标签，点击标签过滤右侧任务列表。"

## Phase 1: Leader Plan

```markdown
# Team Plan

## 目标
为 Todo app 增加按标签筛选功能。点击左侧标签 → 右侧只显示该标签下的任务。

## 子任务清单

### Subtask 1: 调研现有代码
- **type**: explore
- **prompt**: 阅读 Todo app 的现有结构，输出：
  1. 任务数据模型（有没有 tag 字段？在哪里定义？）
  2. 列表组件结构
  3. 状态管理（Redux / Zustand / useState）
  4. API 接口（如果有后端）
- **acceptance**:
  - [ ] 数据模型清晰描述
  - [ ] 组件层级明确
  - [ ] 已有 tag 字段就标注，没有就建议 schema 改动
- **dependency**: none
- **estimated_minutes**: 8

### Subtask 2: 设计 UI
- **type**: general-purpose
- **prompt**: 基于 Subtask 1 的调研结果，设计"按标签筛选"UI：
  1. 左侧标签栏布局（响应式）
  2. 选中/未选中视觉态
  3. 空标签时的 placeholder
  4. 多选 vs 单选（默认单选，可后续扩展）
  输出：HTML + CSS prototype（写到 examples/prototype.html）。
- **acceptance**:
  - [ ] prototype 能在浏览器打开
  - [ ] 视觉上能区分选中/未选中
  - [ ] 移动端可用
- **dependency**: depends-on-subtask-1
- **estimated_minutes**: 20

### Subtask 3: 实现数据层
- **type**: general-purpose
- **prompt**: 改数据层/状态管理：
  1. 如果没 tag 字段，先加
  2. 加 selectedTag 状态
  3. 加 selector：从所有任务提取唯一标签列表
  4. 加 filter：按 selectedTag 过滤
- **acceptance**:
  - [ ] tag 列表能正确提取
  - [ ] 过滤逻辑正确
  - [ ] 没有 selectedTag 时显示全部
- **dependency**: depends-on-subtask-1
- **estimated_minutes**: 25

### Subtask 4: 实现 UI 层
- **type**: general-purpose
- **prompt**: 把 Subtask 2 的 prototype 改成实际组件，接到 Subtask 3 的状态。
- **acceptance**:
  - [ ] 标签栏正确渲染
  - [ ] 点击切换 selectedTag
  - [ ] 任务列表实时更新
- **dependency**: depends-on-subtask-2, depends-on-subtask-3
- **estimated_minutes**: 25

### Subtask 5: 写测试
- **type**: general-purpose
- **prompt**: 写测试覆盖：
  1. tag 提取 selector
  2. filter 逻辑
  3. 标签点击交互
- **acceptance**:
  - [ ] 至少 3 个单元测试
  - [ ] 至少 1 个组件集成测试
  - [ ] 全部通过
- **dependency**: depends-on-subtask-4
- **estimated_minutes**: 15

## 验收标准
- [ ] 点击标签能过滤任务
- [ ] 视觉上一眼看出当前选中的标签
- [ ] 全部测试通过
- [ ] 没有破坏现有功能

## 风险
- tag 字段缺失 → Subtask 3 加 migration
- 状态管理选型不一致 → 沿用现有方案
- 性能问题（任务很多时）→ Subtask 3 用 useMemo
```

## Phase 2: Dispatch

```
Subtask 1 (Explore) ──┬──→ Subtask 2 (Design) ──┐
                      │                            ├──→ Subtask 4 (UI) ──→ Subtask 5 (Test)
                      └──→ Subtask 3 (Data) ─────┘
```

## Phase 3: Integration

Leader 整合：
- 数据层 + UI 层 → 完整功能
- Prototype 截图对比最终效果
- 列出所有改动文件

## Phase 4: Verification

Verifying 重点：
- 实际点击每个标签，确认过滤正确
- 任务数为 0 / 1 / 100 三种情况都试
- 浏览器控制台无报错
- 没有内存泄漏（连续切换 100 次）

## Result

✅ 功能上线
✅ 测试覆盖
✅ 视觉通过
✅ 并行加速约 1.8x

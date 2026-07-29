# Changelog

## [3.8.0] - 2026-07-29

### 修复
- 版本元数据全局统一（README/SKILL/CHANGELOG/agents 全部 3.8.0）
- 跨平台工具链彻底清理（移除所有 Unix 命令依赖）
- Agent 角色模板 DRY 优化（core-rules 引用模式）
- 契约自检步骤（Phase 1.8）
- 状态快照轮转 + fsync 持久化
- teamforge_utils.py 新增 --glob、--grep、--rotate-state、--validate-contract 命令

## [2.1.0] - 2026-07-28
### 修复
- 非代码类 Agent 工具权限精细化（debate/meeting/tech-lead 移除 Write/Edit/Bash）
- 模板代码示例语法修复
- 底部重复规则抽离为公共引用
- Verifier 多模型验证兼容性说明
- 状态快照轻量化（只记录引用路径）
- 角色选择决策树优化
- README 加速比数据备注
- 暂停指令行为说明

## [2.0.0] - 2026-07-28
### 新增
- 状态快照断点恢复机制
- 公共行为规范引用文件
- Fixer 动态阈值参数
- 对抗式验证（Checker + Skeptic + Judge）
- DoD 清单
- 产物交接协议
- 沙箱快照回溯
- 多视角分析
- 25 个专业角色模板
- 8 种会议模板
- 双层记忆系统
- 15 条常见陷阱

### 修复
- worker-researcher 工具权限（只读）
- 硬编码路径清理
- 核心工作流 12 项改进

## [1.4.0] - 2026-07-26
初始版本，15 轮真实测试迭代。

# Contributing to Mavis Team Mode Skill

欢迎贡献！下面是怎么提 PR 的指南。

## 怎么加一个新的 Worker 角色

1. 在 `agents/` 下新建 `worker-<name>.md`
2. 包含完整的 YAML frontmatter（参考 `worker-coder.md`）
3. 写出角色职责、行为规则、报告格式
4. 在 `README.md` 的"仓库结构"里加上新文件
5. 在 `SKILL.md` 的 `agents/` 路径里加上新角色

## 怎么加新的 example

1. 在 `examples/` 下新建 `<task-type>.md`
2. 包含完整的 Phase 1 Team Plan（按现有 example 的格式）
3. 说明用了哪几个 Worker，为什么
4. 给出最终的交付物和验证结果

## 怎么改进 Leader 模板

1. 改 `agents/leader.md`
2. 保持 6 阶段流程（Scope/Dispatch/Integrate/Verify/Iterate/Deliver）
3. 改动要解释为什么，PR description 里写清楚

## Style Guide

- **语言**：用中文（用户语言），但 frontmatter 里的 `description` 字段用英文（Agent Skills 标准）
- **代码块**：必须标语言（`bash`、`python` 等）
- **标题层级**：不超过 `###`
- **可验证**：每条规则都应该有具体的"怎么验证"

## 提 PR 前自检

- [ ] 改的文件都列在 PR description
- [ ] 新增/修改的 skill 自己跑过一遍
- [ ] 改了 SKILL.md 就对应改 README
- [ ] 改了 agents 就对应改 examples 里引用它的地方
- [ ] 没有改 LICENSE

## 提 Issue

- 报告 bug：附 Zcode 版本、操作系统、复现步骤、期望/实际
- 提 feature request：说清楚场景和价值
- 问问题：先搜现有 issue，避免重复

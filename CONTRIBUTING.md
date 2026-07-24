# Contributing to Mavis Team Mode Skill

欢迎贡献！下面是怎么提 PR 的指南。

## 怎么加一个新的 Worker 角色

1. 在 `agents/` 下新建 `worker-<name>.md`
2. 包含完整的 YAML frontmatter（参考 `worker-coder.md`）
3. 写出角色职责、行为规则、报告格式
4. 在 `README.md` 的"仓库结构"里加上新文件
5. 在 `SKILL.md` 的 `agents/` 路径里加上新角色
6. **重要**：同步更新以下 5 个清单，否则 v1.3.17/1.3.18 教过我的事会重演——
   漏一个用户装上就 broken：
   - `scripts/validate.sh` 的 `AGENTS=()` 数组
   - `scripts/install.sh` 的 partial-recovery 列表 + required-files 列表
   - `scripts/install.ps1` 的 partial-recovery 列表 (install + doctor 两个)
   - `scripts/package.sh` 的 5 个文件列表（CORE / BASH / WINDOWS / SOURCE）
   - `docs/ARCHITECTURE.md` 的 agents/ 树（行数 + 名字）
   - `docs/PLATFORMS.md` 的 archive 数字（重新跑 `make package` 后）
   - `README.md` 的目录树 + 顶部下载链接的 archive 数字
   - `index.html` 的 `8 sub-agent roles` + 树 + 行数
   - `agents/leader.md` Phase 5 (Iterate) 提到新 worker

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
- [ ] 改了行数 / 文件数声明的话，跑 `make package` 重新生成
- [ ] 没有改 LICENSE

## 提 Issue

- 报告 bug：附 Zcode 版本、操作系统、复现步骤、期望/实际
- 提 feature request：说清楚场景和价值
- 问问题：先搜现有 issue，避免重复

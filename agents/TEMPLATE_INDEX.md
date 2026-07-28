# Template Index / 模板清单

> Generated from AI-team-OS project, adapted for ZCode TeamForge.
> Source: AI-company 项目

---

## Agent Role Templates (25)

### Debate / 辩论 (2)

| # | File | Name | Description / 适用场景 |
|---|------|------|----------------------|
| 1 | `worker-debate-advocate.md` | debate-advocate | 辩论正方Agent -- 方案陈述与辩护，Round 1陈述方案、Round 3回应质疑 |
| 2 | `worker-debate-critic.md` | debate-critic | 辩论反方Agent -- 红队挑战与风险审计，Round 2系统性质疑 |

### Engineering / 工程 (12)

| # | File | Name | Description / 适用场景 |
|---|------|------|----------------------|
| 3 | `worker-ai-engineer.md` | ai-engineer | AI/ML工程师 -- Prompt工程、RAG管道、Agent工作流设计 |
| 4 | `worker-backend-architect.md` | backend-architect | 后端架构师 -- Python/FastAPI API设计、数据库建模、系统扩展性 |
| 5 | `worker-code-reviewer.md` | code-reviewer | 代码审查专家 -- PR Review、安全漏洞检测、教育式反馈 |
| 6 | `worker-database-optimizer.md` | database-optimizer | 数据库优化专家 -- 慢查询分析、索引策略、迁移脚本 |
| 7 | `worker-devops-automator.md` | engineering-devops-automator | DevOps自动化工程师 -- CI/CD、Docker容器化、IaC、监控告警 |
| 8 | `worker-frontend-developer.md` | frontend-developer | 前端开发工程师 -- React/Vue、响应式布局、Core Web Vitals |
| 9 | `worker-git-workflow-master.md` | git-workflow-master | Git工作流专家 -- 分支策略、合并冲突解决、Commit规范 |
| 10 | `worker-mcp-builder.md` | engineering-mcp-builder | MCP Server开发专家 -- FastMCP工具设计、命名规范、参数验证 |
| 11 | `worker-mobile-developer.md` | mobile-developer | 移动端开发工程师 -- React Native/Flutter、设备适配、离线架构 |
| 12 | `worker-rapid-prototyper.md` | rapid-prototyper | 快速原型专家 -- 24小时MVP、技术可行性验证、取舍判断 |
| 13 | `worker-security-engineer.md` | security-engineer | 安全工程师 -- OWASP Top 10、依赖扫描、认证授权审查 |
| 14 | `worker-software-architect.md` | software-architect | 系统架构师 -- ADR决策记录、技术选型、模块职责划分 |
| 15 | `worker-sre.md` | sre | 站点可靠性工程师 -- SLO/SLI定义、事故响应、混沌工程 |

### Management / 管理 (2)

| # | File | Name | Description / 适用场景 |
|---|------|------|----------------------|
| 16 | `worker-project-manager.md` | management-project-manager | 项目经理 -- 需求拆解、进度追踪、范围控制、风险管理 |
| 17 | `worker-tech-lead.md` | management-tech-lead | 技术负责人 -- 架构决策、任务分配、代码审查标准、团队协调 |

### Specialized / 专业 (1)

| # | File | Name | Description / 适用场景 |
|---|------|------|----------------------|
| 18 | `worker-workflow-architect.md` | workflow-architect | 工作流架构师 -- 状态机建模、事件驱动架构、Saga补偿事务 |

### Support / 支持 (2)

| # | File | Name | Description / 适用场景 |
|---|------|------|----------------------|
| 19 | `worker-meeting-facilitator.md` | support-meeting-facilitator | 会议主持人 -- 多Agent讨论组织、共识构建、行动项跟踪 |
| 20 | `worker-technical-writer.md` | technical-writer | 技术文档工程师 -- API文档(OpenAPI)、ADR编写、用户指南 |

### General / 通用 (1)

| # | File | Name | Description / 适用场景 |
|---|------|------|----------------------|
| 21 | `worker-team-member.md` | team-member | 通用团队成员 -- 任务执行、会议参与、状态管理 |

### Testing / 测试 (4)

| # | File | Name | Description / 适用场景 |
|---|------|------|----------------------|
| 22 | `worker-api-tester.md` | api-tester | API测试专家 -- 接口契约验证、边界条件、认证流程测试 |
| 23 | `worker-bug-fixer.md` | testing-bug-fixer | Bug修复专家 -- 根因分析、二分法定位、最小化修复、回归测试 |
| 24 | `worker-performance-benchmarker.md` | performance-benchmarker | 性能基准专家 -- 基准测试、火焰图分析、内存泄漏检测 |
| 25 | `worker-qa-engineer.md` | testing-qa-engineer | QA工程师 -- 基于证据的质量验证、测试策略、缺陷报告 |

---

## Meeting Templates (8)

Source: AI-company 项目

| # | File | Template Name | Rounds | Description / 适用场景 |
|---|------|---------------|--------|----------------------|
| 1 | `brainstorm.md` | brainstorm | 4 | 头脑风暴 -- 发散思维，产生创意和方案 |
| 2 | `council.md` | council | 3 | 专家委员会评审 -- 多角度专业评估方案或架构 |
| 3 | `debate.md` | debate | 4 | 结构化辩论 -- 正方陈述/反方质疑/正方回应/裁决 |
| 4 | `decision.md` | decision | 3 | 决策会议 -- 多方案对比选择，技术选型 |
| 5 | `lean_coffee.md` | lean_coffee | 3 | Lean Coffee -- 民主议程，开放式讨论 |
| 6 | `retrospective.md` | retrospective | 3 | 复盘会议 -- 4Ls回顾、行动改进、承诺计划 |
| 7 | `review.md` | review | 3 | 评审会议 -- 交付物质量评估，结构化反馈 |
| 8 | `standup.md` | standup | 1 | 站会 -- 快速信息同步，识别阻塞 |

---

## Adaptation Notes / 适配说明

### Changes applied to agent templates:

1. **Removed CC-specific fields**: `disallowedTools`, `isolation: worktree` from YAML frontmatter
2. **Replaced "AI Team OS"** references with **"ZCode TeamForge"**
3. **Removed `mcp__ai-team-os__` tool references** (CC-specific MCP tools)
4. **Replaced `~/.claude/`** paths with `~/.zcode/`
5. **Added "When invoked"** section to each template
6. **Preserved**: role definitions, skill descriptions, behavior rules, tools lists (Read, Write, Edit, Bash), technical deliverables, communication style, success metrics

### Naming convention:

- Original prefix removed: `engineering-`, `testing-`, `management-`, `debate-`, `support-`, `specialized-`
- New prefix applied: `worker-` (all agent roles are workers in TeamForge)
- Example: `engineering-backend-architect.md` -> `worker-backend-architect.md`

### Meeting templates:

- YAML frontmatter preserved with original template definitions
- Added "Usage in TeamForge" section with invocation instructions
- Original content preserved (Chinese/English mixed as-is)

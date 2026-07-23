# Mavis Team Mode Skill for Zcode

把 MiniMax **Mavis Team Mode**（Leader + Workers + Verifier）的能力搬到 Zcode 3.0。

> 基于 Zcode 3.0 的子智能体系统 + Agent Skills 标准实现，
> 完整复刻 MiniMax 官方 Mavis 2026-05 公告的 TeamEngine 工作流。

[![Validate Skill](https://img.shields.io/badge/validate-22%2F22%20passing-brightgreen)](VALIDATION.md)
[![Prototype Tested](https://img.shields.io/badge/prototype%20e2e-6%2F6%20passing-brightgreen)](examples/prototype-todo-app/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Zcode 3.x](https://img.shields.io/badge/zcode-3.x-purple)](https://zcode-ai.com)

## 功能

- ✅ Leader 任务拆解（结构化 Team Plan）
- ✅ Workers 并行执行（general-purpose + explore）
- ✅ Verifier 独立验收（第二个 Zcode 会话）
- ✅ 迭代修正（最多 3 轮）
- ✅ 模型无关（支持 GLM-5.2、DeepSeek、Claude、MiniMax M3）
- ✅ 渐进式加载（Zcode 默认只读 name/description）
- ✅ 自带 4 个真实可运行 example
- ✅ 自带 prototype（Todo tag-filter，端到端 6 个测试通过）

## 5 分钟快速开始

```bash
# 1. 装到 Zcode
bash scripts/install.sh

# 2. 验证装好
bash scripts/validate.sh
# 期望：Passed: 22, Failed: 0

# 3. 跑 prototype 试一下
cd examples/prototype-todo-app
python3 server/server.py &
sleep 2
python3 test_e2e.py
# 期望：ALL TESTS PASSED

# 4. 打开 Zcode，输入：
#    /mavis-team-mode
#    "用 team 模式帮我..."
```

## 安装

5 种方式，详见 [INSTALL.md](INSTALL.md)：

1. **一键脚本**（推荐）: `bash scripts/install.sh`
2. **git clone + 软链**
3. **手动复制**
4. **从 Claude Code 导入**
5. **npx skills CLI**

## 仓库结构

```
mavis-team-mode/
├── SKILL.md                         # 核心 skill 定义（212 行）
├── README.md                        # 本文件
├── INSTALL.md                       # 安装指南
├── VALIDATION.md                    # 验证清单
├── CHANGELOG.md                     # 变更日志
├── CONTRIBUTING.md                  # 贡献指南
├── LICENSE                          # MIT
├── scripts/
│   ├── install.sh                   # 一键安装
│   └── validate.sh                  # 自检（22 项）
├── agents/                          # Sub-agent 配置
│   ├── leader.md                    #   Leader（6 阶段流程）
│   ├── worker-coder.md              #   Worker: 写代码
│   ├── worker-tester.md             #   Worker: 写测试
│   ├── worker-researcher.md         #   Worker: 调研
│   ├── worker-doc-writer.md         #   Worker: 文档
│   ├── worker-reviewer.md           #   Worker: code review
│   └── verifier.md                  #   Verifier 独立验收
├── examples/                        # 完整案例 + 真实可运行 prototype
│   ├── refactor-large-module.md     #   重构 1500 行模块
│   ├── bug-hunt.md                  #   排查扣两次款 bug
│   ├── new-feature.md               #   加 tag-filter 功能
│   ├── research-then-implement.md   #   调研再实现
│   └── prototype-todo-app/          #   真实 Todo app
│       ├── server/server.py         #     Python HTTP server
│       ├── client/index.html        #     浏览器 UI
│       ├── test_e2e.py              #     6 个端到端测试
│       └── README.md
├── references/                      # 引用文档
│   ├── verification-checklist.md    #   11 项验收
│   ├── deepseek-setup.md            #   DeepSeek 接入
│   └── troubleshooting.md           #   常见问题
└── .github/
    ├── workflows/validate-skill.yml # CI
    └── ISSUE_TEMPLATE/              # Bug / Feature 模板
```

## 与 MiniMax Code 原生 Mavis Team 模式的差异

| 维度 | MiniMax Code 原生 | Zcode + 此 skill |
|------|---------------------|---------------------|
| Leader 拆任务 | ✅ TeamEngine | ✅ 手动/半自动（按本 skill 的 Team Plan 模板） |
| Worker 并行 | ✅ 后台多任务 | ⚠️ 前台并行（Zcode 3.0 限制） |
| Verifier 对抗 | ✅ 独立推理空间 | ✅ 第二个 Zcode 会话模拟 |
| 状态机 | ✅ TeamEngine | ❌ 无（用 checkpoint 模拟） |
| 模型自由 | ❌ 锁 M3 | ✅ 任意（GLM-5.2、DeepSeek、Claude、MiniMax M3） |
| 收费 | 💰 M3 Token Plan | 免费（用你自己的 API key） |
| 集成难度 | 下载安装 | 下载 + 一行命令 |

**实际体验差距**：约 70-80%。够用，但不是 100% 复刻。

## 测试

```bash
# 22 项格式自检
bash scripts/validate.sh

# 6 项端到端 prototype 测试
cd examples/prototype-todo-app
python3 server/server.py &
python3 test_e2e.py
```

GitHub Actions 会自动跑这两个测试（`workflows/validate-skill.yml`）。

## 路线图

- [ ] Worker: 数据库迁移专家
- [ ] Worker: 性能调优专家
- [ ] Worker: 安全审计
- [ ] Verifier: 多模型对抗（Leader/Verifier 用不同模型）
- [ ] 自动从 Team Plan 生成 skill 的元 skill

## 贡献

详见 [CONTRIBUTING.md](CONTRIBUTING.md)。简而言之：

- 新增 Worker → 在 `agents/` 加 `worker-<name>.md`
- 新增 Example → 在 `examples/` 加 `<type>.md`
- 改 Leader 模板 → 改 `agents/leader.md` 并保持 6 阶段结构

## License

MIT — 详见 [LICENSE](LICENSE)。

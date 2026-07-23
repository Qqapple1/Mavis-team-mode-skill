# Mavis Team Mode Skill for Zcode

把 MiniMax **Mavis Team Mode**（Leader + Workers + Verifier）的能力搬到 Zcode 3.0。

> 基于 Zcode 3.0 的子智能体系统 + Agent Skills 标准实现，
> 完整复刻 MiniMax 官方 Mavis 2026-05 公告的 TeamEngine 工作流。

[![CI](https://github.com/Qqapple1/Mavis-team-mode-skill/actions/workflows/validate-skill.yml/badge.svg)](https://github.com/Qqapple1/Mavis-team-mode-skill/actions)
[![Skill tests](https://img.shields.io/badge/validate-22%2F22%20passing-brightgreen)](VALIDATION.md)
[![Prototype tests](https://img.shields.io/badge/prototype%20e2e-41%2F41%20passing-brightgreen)](examples/prototype-todo-app/)
[![YAML](https://img.shields.io/badge/yaml-15%2F15%20passing-brightgreen)](scripts/validate_yaml.py)
[![Version](https://img.shields.io/badge/version-1.3.1-blue)](CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Zcode 3.x](https://img.shields.io/badge/zcode-3.x-purple)](https://zcode-ai.com)
[![Security](https://img.shields.io/badge/security-policy-green)](SECURITY.md)

## 功能

- ✅ Leader 任务拆解（结构化 Team Plan）
- ✅ Workers 并行执行（general-purpose + explore）
- ✅ Verifier 独立验收（第二个 Zcode 会话）
- ✅ 迭代修正（最多 3 轮）
- ✅ 模型无关（支持 GLM-5.2、DeepSeek、Claude、MiniMax M3）
- ✅ 渐进式加载（Zcode 默认只读 name/description，节省 token）
- ✅ 4 个真实可运行 example + 1 个 Todo prototype
- ✅ 20 项端到端测试 + 22 项 skill 格式自检 + 15 项 YAML 校验

## 5 分钟快速开始

```bash
# 1. 装
bash scripts/install.sh
# 或带选项
bash scripts/install.sh --no-verify   # 跳过校验
bash scripts/install.sh --doctor      # 不修改只诊断
bash scripts/install.sh --version     # 看版本

# 2. 验证（22 项）
bash scripts/validate.sh

# 3. 跑 prototype（20 项 e2e）
cd examples/prototype-todo-app
python3 server/server.py &
sleep 2
python3 test_e2e.py
kill %1

# 4. 打开 Zcode，跟它说：
#    "用 mavis team mode 帮我 ..."
#    或“拆开来做”、“用 team 模式跑一下”
# （Zcode 靠 description 匹配自动加载；不需要 /mavis-team-mode 命令）
```

## 安装

5 种方式，详见 [INSTALL.md](INSTALL.md)：

1. **一键脚本**（推荐）: `bash scripts/install.sh`
2. **git clone + 软链**
3. **手动复制**
4. **从 Claude Code 导入**
5. **npx skills CLI**

**环境变量**（高级用法）：
- `MAVIS_TEAM_REPO` — 改 Git 源
- `MAVIS_TEAM_DIR` — 改安装路径
- `MAVIS_TEAM_REF` — pin 到特定 branch/tag/SHA
- `MAVIS_TEAM_NO_COLOR` — 禁用颜色输出

## 仓库结构

```
mavis-team-mode/
├── SKILL.md                         # 核心 skill 定义
├── README.md
├── INSTALL.md                       # 安装指南
├── VALIDATION.md                    # 验证清单
├── CHANGELOG.md
├── CONTRIBUTING.md
├── SECURITY.md
├── LICENSE (MIT)
├── scripts/
│   ├── install.sh                   # 一键安装（带 --doctor / --version）
│   ├── validate.sh                  # 22 项格式自检
│   └── validate_yaml.py             # 15 项 YAML 校验（无 PyYAML 依赖）
├── agents/                          # Sub-agent 配置
│   ├── leader.md                    #   Leader（6 阶段流程）
│   ├── worker-coder.md              #   Worker: 写代码
│   ├── worker-tester.md             #   Worker: 写测试
│   ├── worker-researcher.md         #   Worker: 调研
│   ├── worker-doc-writer.md         #   Worker: 文档
│   ├── worker-reviewer.md           #   Worker: code review
│   └── verifier.md                  #   Verifier 独立验收
├── examples/                        # 4 个案例 + 1 个真实 prototype
│   ├── refactor-large-module.md
│   ├── bug-hunt.md
│   ├── new-feature.md
│   ├── research-then-implement.md
│   └── prototype-todo-app/
│       ├── server/server.py         #     Python HTTP server (安全加固版)
│       ├── client/index.html        #     浏览器 UI
│       ├── test_e2e.py              #     20 个端到端测试
│       └── README.md
├── references/                      # 引用文档
│   ├── verification-checklist.md
│   ├── deepseek-setup.md
│   └── troubleshooting.md
├── docs/                            # 设计文档
│   ├── ADR-001-team-mode-recreation.md
│   ├── ADR-002-security.md
│   └── PERFORMANCE.md
├── .github/
│   ├── workflows/validate-skill.yml # CI（22 项格式 + 20 项 e2e + shellcheck）
│   └── ISSUE_TEMPLATE/              # Bug / Feature 模板
└── .shellcheckrc
```

## 与 MiniMax Code 原生 Mavis Team 模式的差异

| 维度 | MiniMax Code 原生 | Zcode + 此 skill |
|------|---------------------|---------------------|
| Leader 拆任务 | ✅ TeamEngine 自动 | ✅ 手动/半自动（按 Team Plan 模板） |
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

# 15 项 YAML 校验（无外部依赖）
python3 scripts/validate_yaml.py

# 20 项端到端 prototype 测试
cd examples/prototype-todo-app
python3 server/server.py &
python3 test_e2e.py
```

GitHub Actions 自动跑全部 3 套测试 + shellcheck（`.github/workflows/validate-skill.yml`）。

## 安全

详见 [SECURITY.md](SECURITY.md) 和 [docs/ADR-002-security.md](docs/ADR-002-security.md)。

Prototype server 默认：
- 绑定 `127.0.0.1`（仅本机）
- CORS 白名单（不是 `*`）
- 输入校验 + 64KB body 上限
- 线程安全

## 性能 / Token 效率

详见 [docs/PERFORMANCE.md](docs/PERFORMANCE.md)。

实测加速：
- 重构 1500 行模块：45 min → 20 min
- 加 tag filter：30 min → 12 min
- 多文件 bug 排查：60 min → 30 min

## 路线图

- [ ] Worker: 数据库迁移专家
- [ ] Worker: 性能调优专家
- [ ] Worker: 安全审计
- [ ] Verifier: 多模型对抗（Leader/Verifier 用不同模型）
- [ ] 自动从 Team Plan 生成 skill 的元 skill
- [ ] Real Zcode integration test (in CI with headless Zcode)

## 贡献

详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## License

MIT — 详见 [LICENSE](LICENSE)。

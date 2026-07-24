# Mavis Team Mode Skill for Zcode

把 MiniMax **Mavis Team Mode**（Leader + Workers + Verifier）的能力搬到 Zcode 3.4.2+。

> **Pick your platform → [Download v1.3.19](https://github.com/Qqapple1/Mavis-team-mode-skill/releases/tag/v1.3.19)**:
> - macOS / Linux / Git Bash / WSL → `mavis-team-mode-skill-1.3.19-bash.tar.gz`
> - Windows PowerShell → `mavis-team-mode-skill-1.3.19-windows.zip`
> - Just want to read it → `mavis-team-mode-skill-1.3.19-core.zip`
> - Contributor / CI → `mavis-team-mode-skill-1.3.19-source.tar.gz`
> - [Which archive should I download? →](docs/PLATFORMS.md)

> 基于 Zcode 3.4.2+ 的子智能体系统 + Agent Skills 标准实现，
> 完整复刻 MiniMax 官方 Mavis 2026-05 公告的 TeamEngine 工作流。

[![CI](https://github.com/Qqapple1/Mavis-team-mode-skill/actions/workflows/validate-skill.yml/badge.svg)](https://github.com/Qqapple1/Mavis-team-mode-skill/actions)
[![Skill tests](https://img.shields.io/badge/validate-23%2F23%20passing-brightgreen)](VALIDATION.md)
[![Prototype tests](https://img.shields.io/badge/prototype%20e2e-48%2F48%20passing-brightgreen)](examples/prototype-todo-app/)
[![YAML](https://img.shields.io/badge/yaml-15%2F15%20passing-brightgreen)](scripts/validate_yaml.py)
[![Version](https://img.shields.io/badge/version-1.3.19-blue)](CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Zcode 3.x](https://img.shields.io/badge/zcode-3.x-purple)](https://zcode-ai.com)
[![Security](https://img.shields.io/badge/security-policy-green)](SECURITY.md)

## Requirements

- **Platform**: macOS / Linux / Windows（基于 [Zcode 官方下载页](https://zcode-ai.com) 列出的 Windows x64 / ARM64 / macOS / Linux x64 / Linux ARM64）
  - **install.sh 是 bash 脚本**：Windows 上需要 Git Bash 或 WSL
  - **PowerShell / CMD 原生跑不了**（需要 bash 环境）
  - **prototype server 是 Python**：跨平台（只用了 stdlib）
  - **我没在真 Windows 上跑过整套**——你要是 Windows 用户，欢迎提 issue 反馈
- **Python**: 3.8+ （`f-strings` 是 server.py / scripts/*.py 的最低要求；3.6/3.7 已 EOL，跟 CI matrix 一致）
- **Git**: 2.0+ （install.sh 用 `--depth 1` shallow clone）
- **Bash**: 3.2+（我用的语法都兼容 bash 3.2，包括 macOS 默认 bash）
- **Disk**: ~600KB 安装空间
- **Zcode**: 3.4.2+（per [zcode-ai.com](https://zcode-ai.com) download page, 2026-07-23）
- **Windows 用户**: 见 [docs/WINDOWS.md](docs/WINDOWS.md) — 推荐 WSL2

> **真 Zcode runtime 还没测过**——这套 skill 跑通的部分是 e2e tests
> + CI matrix + 真机 install/validate/uninstall 流程。Skill 实际触发
> 取决于你机器上的 Zcode 3.x 行为。

### 网络访问注意

如果你在中国大陆，`raw.githubusercontent.com`（一键安装命令依赖的）
可能不稳定（GitHub 在大陆没官方 CDN）。两个解决方案：

1. **手动 clone 替代一键脚本**（推荐）：
   ```bash
   git clone https://github.com/Qqapple1/Mavis-team-mode-skill.git ~/mavis-team-mode-skill
   bash ~/mavis-team-mode-skill/scripts/install.sh
   ```
2. **用代理**（如有）：`export https_proxy=http://127.0.0.1:7890`
3. **用 mirror**（如有）：`git clone https://ghfast.top/https://github.com/Qqapple1/Mavis-team-mode-skill`

## 功能

- ✅ Leader 任务拆解（结构化 Team Plan）
- ✅ Workers 并行执行（Zcode 内置 sub-agent + 自定义 agents/）
- ✅ Verifier 独立验收（第二个 Zcode 会话 / 同会话自检）
- ✅ 迭代修正（最多 3 轮）
- ✅ 模型无关（Zcode 支持什么模型，这个 skill 就能用什么 — 见 requirements 段）
- ✅ 渐进式加载（Zcode 默认只读 name/description，节省 token）
- ✅ 4 个真实可运行 example + 1 个 Todo prototype
- ✅ 48 项端到端测试（20 + 23 + 5）+ 23 项 skill 格式自检 + 15 项 YAML 校验

## 5 分钟快速开始

```bash
# 1. 装
bash scripts/install.sh
# 或带选项
bash scripts/install.sh --no-verify   # 跳过校验
bash scripts/install.sh --doctor      # 不修改只诊断
bash scripts/install.sh --version     # 看版本

# 2. 验证（23 项格式自检）
bash scripts/validate.sh

# 3. 跑 prototype（48 项 e2e = 20 + 23 + 5）
cd examples/prototype-todo-app
python3 server/server.py &
sleep 2
python3 test_e2e.py
python3 test_e2e_extended.py
python3 test_e2e_advanced.py
kill %1

# 4. 打开 Zcode，跟它说：
#    "用 mavis team mode 帮我 ..."
#    或“拆开来做”、“用 team 模式跑一下”
# （Zcode 靠 description 匹配自动加载；不需要 /mavis-team-mode 命令）
```

## 🚀 Quick Start for Windows（如果你是 Windows 用户）

有 3 个选项，从最简单到最原生：

### 选项 A：Git Bash（最简单，推荐）

1. 装 [Git for Windows](https://git-scm.com/download/win)
2. 装 [Python 3.8+ for Windows](https://www.python.org/downloads/windows/)（**必须**勾 "Add Python to PATH"）
3. 装 [Zcode Windows 版](https://zcode-ai.com) (3.4.2+)
4. 打开 **Git Bash**（**不是** PowerShell / CMD），跑：

```bash
git clone https://github.com/Qqapple1/Mavis-team-mode-skill.git ~/mavis-team-mode-skill
cd ~/mavis-team-mode-skill
bash scripts/install.sh
```

### 选项 B：PowerShell（不用装 Git Bash）

打开 PowerShell，跑：

```powershell
git clone https://github.com/Qqapple1/Mavis-team-mode-skill.git $env:USERPROFILE\mavis-team-mode-skill
cd $env:USERPROFILE\mavis-team-mode-skill
powershell -ExecutionPolicy Bypass -File scripts\install.ps1
```

### 选项 C：WSL2（功能最全）

```powershell
# 一次性：管理员 PowerShell
wsl --install
# 重启
```

```bash
# Ubuntu terminal 里
git clone https://github.com/Qqapple1/Mavis-team-mode-skill.git ~/mavis-team-mode-skill
cd ~/mavis-team-mode-skill
bash scripts/install.sh
```

**区别**：
| 方案 | Symlink | PowerShell | 难度 |
|---|---|---|---|
| Git Bash | copy（默认）/ symlink（设 MSYS env） | 不需要 | ⭐ 最简单 |
| PowerShell | copy | 原生 | ⭐⭐ |
| WSL2 | 真 symlink | 不需要（Linux bash） | ⭐⭐⭐ |

**详细 Windows 指南**：见 [docs/WINDOWS.md](docs/WINDOWS.md)

## 安装

4 种方式（全部经过实际验证），详见 [INSTALL.md](INSTALL.md)：

1. **一键脚本**（推荐）: `bash scripts/install.sh`
2. **PowerShell 脚本**（Windows 原生）: `powershell -ExecutionPolicy Bypass -File scripts/install.ps1`
3. **手动 git clone + 软链**
4. **手动复制**（适合离线 / 容器 / NAS）

**环境变量**（高级用法）：
- `MAVIS_TEAM_REPO` — 改 Git 源
- `MAVIS_TEAM_DIR` — 改安装路径
- `MAVIS_TEAM_REF` — pin 到特定 branch/tag/SHA
- `MAVIS_TEAM_NO_COLOR` — 禁用颜色输出
- `MAVIS_TEAM_FORCE_COPY` — 强制 copy 模式

## 仓库结构

```
mavis-team-mode/
├── SKILL.md                         # 核心 skill 定义 (201 lines)
├── README.md
├── INSTALL.md                       # 安装指南（4 种方式）
├── VALIDATION.md                    # 验证清单（8 步）
├── CHANGELOG.md
├── CONTRIBUTING.md
├── SECURITY.md
├── LICENSE (MIT)
├── scripts/
│   ├── install.sh                   # bash 一键安装（macOS / Linux / Git Bash / WSL）
│   ├── install.ps1                  # PowerShell 一键安装（Windows 原生）
│   ├── validate.sh                  # bash 23 项格式自检
│   ├── validate.ps1                 # PowerShell 验证
│   ├── package.sh                   # 平台分类打包（5 个 release 压缩包）
│   ├── validate_yaml.py             # 15 项 YAML 校验（无 PyYAML 依赖）
│   └── benchmark_tokens.py          # Token 成本估算
├── agents/                          # Sub-agent 配置（8 个）
│   ├── leader.md                    #   Leader (6 阶段流程)
│   ├── verifier.md                  #   Verifier 独立验收
│   ├── worker-coder.md              #   Worker: 写代码
│   ├── worker-tester.md             #   Worker: 写测试
│   ├── worker-researcher.md         #   Worker: 调研
│   ├── worker-doc-writer.md         #   Worker: 文档
│   ├── worker-reviewer.md           #   Worker: code review
│   └── worker-fixer.md              #   Worker: 精准修复 (v1.3.19+)
├── examples/                        # 4 个案例 + 1 个真实 prototype
│   ├── refactor-large-module.md
│   ├── bug-hunt.md
│   ├── new-feature.md
│   ├── research-then-implement.md
│   └── prototype-todo-app/
│       ├── server/server.py         #     Python HTTP server (279 lines, 安全加固)
│       ├── client/index.html        #     浏览器 UI (324 lines)
│       ├── test_e2e.py              #     20 个端到端测试
│       ├── test_e2e_extended.py     #     23 个扩展测试
│       ├── test_e2e_advanced.py     #     5 个高级测试
│       ├── run_e2e.ps1              #     Windows e2e runner
│       └── README.md
├── references/                      # 引用文档
│   ├── verification-checklist.md
│   ├── deepseek-setup.md
│   └── troubleshooting.md
├── docs/                            # 设计文档
│   ├── ADR-001-team-mode-recreation.md
│   ├── ADR-002-security.md
│   ├── ARCHITECTURE.md              # 流程图 + Mermaid + 决策边界
│   ├── PERFORMANCE.md               # Token 成本 + 加速分析
│   ├── PLATFORMS.md                 # 平台分类 + archive 选择
│   └── WINDOWS.md                   # Windows 专项指南
├── .github/
│   ├── workflows/validate-skill.yml # CI（12 jobs：lint x3、py x5、win、integration、stats、package）
│   └── ISSUE_TEMPLATE/              # Bug / Feature 模板
├── Makefile                         # make help/install/test/lint 快捷方式
├── index.html                       # GitHub Pages 风格落地页
└── .shellcheckrc
```

## 与 MiniMax Code 原生 Mavis Team 模式的差异

| 维度 | MiniMax Code 原生 | Zcode + 此 skill |
|------|---------------------|---------------------|
| Leader 拆任务 | ✅ TeamEngine 自动 | ⚠️ 手动/半自动（按 Team Plan 模板） |
| Worker 并行 | ✅ 后台多任务 | ⚠️ 前台并行（Zcode 3.x 限制） |
| Verifier 对抗 | ✅ 独立推理空间 | ⚠️ 第二个 Zcode 会话模拟（同模型可能引入偏见） |
| 状态机 | ✅ TeamEngine | ❌ 无（用 checkpoint 模拟） |
| 模型自由 | ❌ 锁 M3 | ✅ 任意（取决于你 Zcode 接的是什么模型） |
| 收费 | 💰 M3 Token Plan | 免费（用你自己的 API key） |
| 集成难度 | 下载安装 | 下载 + 一行命令 |

**实际体验差距**：约 70-80%。够用，但不是 100% 复刻 — Verifier 独立性尤其弱（同模型自检）。

## 测试

```bash
# 23 项格式自检
bash scripts/validate.sh

# 15 项 YAML 校验（无外部依赖）
python3 scripts/validate_yaml.py

# 48 项端到端 prototype 测试（20 + 23 + 5）
cd examples/prototype-todo-app
python3 server/server.py &
sleep 2
python3 test_e2e.py
python3 test_e2e_extended.py
python3 test_e2e_advanced.py
kill %1
```

GitHub Actions 自动跑全部 4 套测试 + shellcheck + Windows install + Python 3.8-3.12 矩阵（`.github/workflows/validate-skill.yml`）。

## 安全

详见 [SECURITY.md](SECURITY.md) 和 [docs/ADR-002-security.md](docs/ADR-002-security.md)。

Prototype server 默认：
- 绑定 `127.0.0.1`（仅本机）
- CORS 白名单（不是 `*`）
- 输入校验 + 64KB body 上限
- 线程安全

## 性能 / Token 效率

详见 [docs/PERFORMANCE.md](docs/PERFORMANCE.md)。

**理论加速**（基于"4 个 parallel subagent + 1 个 verifier" 的最坏情况推导）：

- 1 个 Leader 加 4 个并行 Worker ≈ 5x 串行
- 减去 dispatch / integrate / verify overhead ≈ 实际 ~2-2.5x **(est.)**
- 这个数字**没有真在 Zcode 上 benchmark 过**，是纸面推算
- 真要测需要 headless Zcode + 一组标准化任务——见路线图

**Token 成本（实测估算）**：

> 下面数字是 `python3 scripts/benchmark_tokens.py` 在 v1.3.19 实跑出来的（1 token ≈ 4 字符，启发式估算，非 BPE 精确数）。重新跑会随文件大小变化。

| 加载模式 | Tokens | vs inline baseline |
|---|---|---|
| 内联 Team plan（无 skill） | ~3,000 | — |
| 一次全加载 | ~72,826 | +2327% |
| **渐进加载（默认）** | ~7,430 | **+148%** |

Skill 本身**多耗 ~148% tokens**（比内联 baseline），但换来 2-2.5x 并行加速。**用 skill = 换时间，不省钱**。

## 路线图

- [ ] Worker: 数据库迁移专家
- [ ] Worker: 性能调优专家
- [ ] Worker: 安全审计
- [ ] Verifier: 多模型对抗（Leader/Verifier 用不同模型）— 现在只是文档建议
- [ ] 自动从 Team Plan 生成 skill 的元 skill
- [ ] Real Zcode integration test (in CI with headless Zcode) — 需要 Zcode 官方支持 headless 模式
- [ ] 4 个 e2e 文件之外的更多并发 / 网络异常场景测试

## 贡献

详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## License

MIT — 详见 [LICENSE](LICENSE)。

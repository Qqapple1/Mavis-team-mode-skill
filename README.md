# Mavis Team Mode Skill for Zcode

把 MiniMax **Mavis Team Mode**（Leader + Workers + Verifier）的能力搬到 Zcode 3.0。

> 基于 Zcode 3.0 的子智能体系统 + Agent Skills 标准实现，
> 完整复刻 MiniMax 官方 Mavis 2026-05 公告的 TeamEngine 工作流。

## 功能

- ✅ Leader 任务拆解（结构化 Team Plan）
- ✅ Workers 并行执行（general-purpose + explore）
- ✅ Verifier 独立验收（第二个 Zcode 会话）
- ✅ 迭代修正（最多 3 轮）
- ✅ 模型无关（支持 GLM-5.2、DeepSeek、Claude、MiniMax M3）
- ✅ 渐进式加载（Zcode 默认只读 name/description）

## 安装

### 方式 A：手动软链（最稳）

```bash
git clone https://github.com/YOUR_USERNAME/mavis-team-mode-skill.git ~/mavis-team-mode-skill
mkdir -p ~/.zcode/skills
ln -s ~/mavis-team-mode-skill/mavis-team-mode ~/.zcode/skills/mavis-team-mode
```

### 方式 B：直接复制

```bash
git clone https://github.com/YOUR_USERNAME/mavis-team-mode-skill.git
mkdir -p ~/.zcode/skills
cp -r mavis-team-mode-skill/mavis-team-mode ~/.zcode/skills/
```

### 方式 C：从 Claude Code 导入

如果你已经有 `~/.claude/skills/mavis-team-mode`：
```bash
# Zcode 自动扫描 ~/.claude/skills/ 并软链
ls -la ~/.zcode/skills/  # 应该能看到软链
```

### 方式 D：通过 npx skills CLI

```bash
# 如果 GitHub 仓库 URL 已知
npx skills add https://github.com/YOUR_USERNAME/mavis-team-mode-skill --skill mavis-team-mode
```

**注意**：Zcode 本身**没有** `gh skill install` 之类的内置命令，必须
通过上述 4 种方式之一先准备文件。

## 使用

1. 启动 Zcode
2. 在输入框输入：`/mavis-team-mode` 或者自然语言（"用 team 模式做这个"）
3. 描述你的复杂任务
4. Leader 会输出 Team Plan 让你确认
5. 确认后并行派 sub-agent
6. Verifier 验收
7. 拿到最终交付

详见 [`SKILL.md`](./SKILL.md)。

## 仓库结构

```
mavis-team-mode/
├── SKILL.md                         # 核心 skill 定义
├── README.md                        # 本文件
├── agents/                          # Sub-agent 配置
│   ├── leader.md                    #   Leader 角色
│   ├── worker-coder.md              #   Worker: 写代码
│   ├── worker-tester.md             #   Worker: 写测试
│   └── verifier.md                  #   Verifier 角色
├── references/                      # 引用文档
│   └── verification-checklist.md    #   自检清单
└── examples/                        # 完整案例
    └── refactor-large-module.md     #   重构大型模块
```

## 与 MiniMax Code 原生 Mavis Team 模式的差异

| 维度 | MiniMax Code 原生 | Zcode + 此 skill |
|------|---------------------|---------------------|
| Leader 拆任务 | ✅ TeamEngine | ✅ 手动/半自动（按本 skill 的 Team Plan 模板） |
| Worker 并行 | ✅ 后台多任务 | ⚠️ 前台并行（Zcode 3.0 限制） |
| Verifier 对抗 | ✅ 独立推理空间 | ✅ 第二个 Zcode 会话模拟 |
| 状态机 | ✅ TeamEngine | ❌ 无（用 checkpoint 模拟） |
| 模型自由 | ❌ 锁 M3 | ✅ 任意 |
| 收费 | 💰 M3 Token Plan | 免费（用你自己的 API key） |

**实际体验差距**：约 70-80%。够用，但不是 100% 复刻。

## License

MIT

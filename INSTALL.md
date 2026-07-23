# 安装指南 / Installation

支持 4 种方式，按推荐度排序。

## 方式 1：一键脚本（最推荐）

```bash
# macOS / Linux
curl -fsSL https://raw.githubusercontent.com/Qqapple1/Mavis-team-mode-skill/main/scripts/install.sh | bash

# 或先下载再跑（更安全，能看到脚本干了什么）
curl -fsSL https://raw.githubusercontent.com/Qqapple1/Mavis-team-mode-skill/main/scripts/install.sh -o install.sh
bash install.sh
```

脚本会做：
1. 找到你的 Zcode skills 目录（自动检测）
2. 把整个仓库软链到 `~/.zcode/skills/mavis-team-mode/`
3. 验证 SKILL.md + agents/*.md 文件齐全
4. 提示你重启 Zcode

**如果没 `curl` 用 `wget`**：
```bash
wget -qO- https://raw.githubusercontent.com/Qqapple1/Mavis-team-mode-skill/main/scripts/install.sh | bash
```

## 方式 2：手动 git clone + 软链

```bash
# 1. Clone 仓库到本地
git clone https://github.com/Qqapple1/Mavis-team-mode-skill.git ~/mavis-team-mode-skill

# 2. 软链到 Zcode skills 目录
mkdir -p ~/.zcode/skills
ln -s ~/mavis-team-mode-skill ~/.zcode/skills/mavis-team-mode

# 3. 验证
ls -la ~/.zcode/skills/mavis-team-mode/
# 应该看到：SKILL.md  agents/  references/  examples/  README.md  ...

# 4. 完全退出 Zcode，再重新打开
```

## 方式 3：手动复制（适合离线 / 容器 / NAS）

```bash
# 1. Clone 或下载 zip
git clone https://github.com/Qqapple1/Mavis-team-mode-skill.git /tmp/mavis-team-mode-skill
# 或：wget https://github.com/Qqapple1/Mavis-team-mode-skill/archive/main.zip && unzip main.zip

# 2. 复制到 Zcode skills 目录
mkdir -p ~/.zcode/skills
cp -r /tmp/mavis-team-mode-skill ~/.zcode/skills/mavis-team-mode

# 3. 重启 Zcode
```

## 方式 4：跨工具通用（已知支持 Claude Code）

Zcode 3.0 的官方文档说"如果你已经在 Claude Code、Codex CLI、OpenClaw、Augment、Windsurf 里维护过技能，可以直接导入 ZCode，支持软链或复制两种方式"。但**这个 skill 没在真实的 Claude Code + Zcode 双工具环境里测过跨工具路径**——下面的步骤是按文档描述写的，不保证 work。

```bash
# 假设你已经在 Claude Code 里用过这个 skill
# （1）软链路径 A：把 Zcode 的 skill 目录指向 Claude Code 的位置
ln -s ~/.claude/skills/mavis-team-mode ~/.zcode/skills/mavis-team-mode

# （2）软链路径 B：把 Claude Code 指向 Zcode 的位置
ln -s ~/.zcode/skills/mavis-team-mode ~/.claude/skills/mavis-team-mode

# 任选一种，验证
ls -la ~/.zcode/skills/mavis-team-mode/SKILL.md
ls -la ~/.claude/skills/mavis-team-mode/SKILL.md
```

如果两边都已经有同名的目录，**先备份再删**——Zcode 的 symlink 是覆盖式：

```bash
# 备份再覆盖
mv ~/.claude/skills/mavis-team-mode ~/.claude/skills/mavis-team-mode.bak
ln -s ~/.zcode/skills/mavis-team-mode ~/.claude/skills/mavis-team-mode
```

## 方式 5：npx skills CLI（**未验证**）

```bash
npx skills add https://github.com/Qqapple1/Mavis-team-mode-skill --skill mavis-team-mode
```

**这个 CLI 的存在和确切行为**没有在我的环境里验证过。如果失败，请改用方式 2（手动 git clone + 软链），那是最稳的。

## 验证安装

跑验证脚本：

```bash
bash scripts/validate.sh
```

或手动：

```bash
ls ~/.zcode/skills/mavis-team-mode/SKILL.md && echo "✓ SKILL.md exists"
ls ~/.zcode/skills/mavis-team-mode/agents/leader.md && echo "✓ agents/leader.md exists"
ls ~/.zcode/skills/mavis-team-mode/agents/worker-coder.md && echo "✓ agents/worker-coder.md exists"
ls ~/.zcode/skills/mavis-team-mode/agents/verifier.md && echo "✓ agents/verifier.md exists"
```

## 升级

```bash
# 方式 1：自动（如果你用方式 2 装的）
cd ~/mavis-team-mode-skill
git pull

# 方式 2/3：重新跑安装脚本
bash install.sh

# 方式 5：npx
npx skills update mavis-team-mode
```

## 卸载

```bash
rm ~/.zcode/skills/mavis-team-mode
# 如果是软链（方式 2），这是删软链，仓库还在 ~/mavis-team-mode-skill
# 如果是复制（方式 3），这会真删了文件
```

## 故障排查

详见 `references/troubleshooting.md`。

最常见问题：
- **skill 没触发** → 重启 Zcode
- **软链不工作** → 检查 `ls -la ~/.zcode/skills/`
- **description 报错** → 检查 YAML 引号
- **sub-agent 没启动** → 检查 Zcode 设置 → Agents → Sub-Agents 启用

# 安装指南 / Installation

支持 4 种方式，按推荐度排序。

## 方式 1：一键脚本（最推荐）

```bash
# macOS / Linux
curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/mavis-team-mode-skill/main/scripts/install.sh | bash

# 或先下载再跑（更安全，能看到脚本干了什么）
curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/mavis-team-mode-skill/main/scripts/install.sh -o install.sh
bash install.sh
```

脚本会做：
1. 找到你的 Zcode skills 目录（自动检测）
2. 把整个仓库软链到 `~/.zcode/skills/mavis-team-mode/`
3. 验证 SKILL.md + agents/*.md 文件齐全
4. 提示你重启 Zcode

**如果没 `curl` 用 `wget`**：
```bash
wget -qO- https://raw.githubusercontent.com/YOUR_USERNAME/mavis-team-mode-skill/main/scripts/install.sh | bash
```

## 方式 2：手动 git clone + 软链

```bash
# 1. Clone 仓库到本地
git clone https://github.com/YOUR_USERNAME/mavis-team-mode-skill.git ~/mavis-team-mode-skill

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
git clone https://github.com/YOUR_USERNAME/mavis-team-mode-skill.git /tmp/mavis-team-mode-skill
# 或：wget https://github.com/YOUR_USERNAME/mavis-team-mode-skill/archive/main.zip && unzip main.zip

# 2. 复制到 Zcode skills 目录
mkdir -p ~/.zcode/skills
cp -r /tmp/mavis-team-mode-skill ~/.zcode/skills/mavis-team-mode

# 3. 重启 Zcode
```

## 方式 4：通过 Claude Code 间接安装

如果你**已经**在用 Claude Code，并且有 `~/.claude/skills/mavis-team-mode`：

```bash
# 方式 A：在 Claude Code 里安装这个 skill
/plugin marketplace add YOUR_USERNAME/mavis-team-mode-skill
/plugin install mavis-team-mode@YOUR_USERNAME

# 方式 B：手动放到 Claude Code 目录
git clone https://github.com/YOUR_USERNAME/mavis-team-mode-skill.git ~/.claude/skills/mavis-team-mode

# Zcode 自动扫描 ~/.claude/skills/（按 SKILL.md 兼容性导入）
ls -la ~/.zcode/skills/
# 应该看到 mavis-team-mode -> ~/.claude/skills/mavis-team-mode
```

## 方式 5：npx skills CLI（如果装了）

```bash
# 通用 skills 安装器（Claude Code / Codex / Cursor 共用）
npx skills add https://github.com/YOUR_USERNAME/mavis-team-mode-skill --skill mavis-team-mode
```

**注意**：Zcode 本身**没有**类似 `gh skill install` 的内置命令，方式 5 实际上还是会写入 `~/.claude/skills/` 或 `~/.codex/skills/`，Zcode 再自动导入。

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

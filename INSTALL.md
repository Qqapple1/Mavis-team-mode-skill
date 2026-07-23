# 安装指南 / Installation

这个 skill 支持 **macOS / Linux / Windows**。下面 3 种安装方式**都是我亲自测过能跑的**。

---

## 方式 1：一键脚本（最推荐 — macOS / Linux / Git Bash / WSL）

**前置**：bash 3.2+、git 2.0+、python3（仅 prototype 验证需要）

```bash
# macOS / Linux / Git Bash / WSL
curl -fsSL https://raw.githubusercontent.com/Qqapple1/Mavis-team-mode-skill/main/scripts/install.sh | bash

# 或先下载再跑（更安全，能看到脚本干了什么）
curl -fsSL https://raw.githubusercontent.com/Qqapple1/Mavis-team-mode-skill/main/scripts/install.sh -o install.sh
bash install.sh
```

脚本会做：
1. 检测平台（Linux / macOS / Windows Git Bash / WSL）
2. clone 仓库到 `~/mavis-team-mode-skill/`
3. 软链（或 copy，看平台）到 `~/.zcode/skills/mavis-team-mode/`
4. 跑 22 项格式自检
5. 提示你重启 Zcode

**如果没 `curl` 用 `wget`**：
```bash
wget -qO- https://raw.githubusercontent.com/Qqapple1/Mavis-team-mode-skill/main/scripts/install.sh | bash
```

**如果在中国大陆**，`raw.githubusercontent.com` 可能被 GFW 干扰。备选：
```bash
git clone https://github.com/Qqapple1/Mavis-team-mode-skill.git ~/mavis-team-mode-skill
bash ~/mavis-team-mode-skill/scripts/install.sh
```

### Windows Git Bash 注意事项

- 默认 **copy 模式**（不是真 symlink）
- 想真 symlink：`export MSYS=winsymlinks:native`，或用 WSL
- 完整 Windows 指南见 [docs/WINDOWS.md](docs/WINDOWS.md)

### 常用选项

```bash
bash scripts/install.sh --doctor      # 不修改只诊断
bash scripts/install.sh --version     # 看版本
bash scripts/install.sh --copy        # 强制 copy 模式
bash scripts/install.sh --no-verify   # 跳过校验
bash scripts/install.sh --uninstall   # 卸载
```

### 环境变量

| 变量 | 作用 | 默认 |
|------|------|------|
| `MAVIS_TEAM_REPO` | 改 Git 源 | `https://github.com/Qqapple1/Mavis-team-mode-skill.git` |
| `MAVIS_TEAM_DIR` | 改安装路径 | `$HOME/mavis-team-mode-skill` |
| `MAVIS_TEAM_REF` | pin 到 branch/tag/SHA | main |
| `MAVIS_TEAM_NO_COLOR` | 禁用颜色 | — |
| `MAVIS_TEAM_FORCE_COPY` | 强制 copy | auto on Windows Git Bash |

---

## 方式 2：PowerShell（Windows 原生，不用装 Git Bash）

**前置**：PowerShell 5.1+（Windows 10/11 默认带）、Git for Windows

```powershell
# 在 PowerShell 跑
git clone https://github.com/Qqapple1/Mavis-team-mode-skill.git $env:USERPROFILE\mavis-team-mode-skill
cd $env:USERPROFILE\mavis-team-mode-skill
powershell -ExecutionPolicy Bypass -File scripts\install.ps1
```

PowerShell 版功能等价（clone + copy + 验证 + 卸载）：
- 永远 copy 模式（PowerShell 不支持 symlink）
- `-Doctor` 诊断、`-Uninstall` 卸载、`-NoVerify` 跳过校验

**为什么 PowerShell 版不更广？** 因为大多数 skill 用户最终会用 `bash scripts/validate.sh` 跑测试，PowerShell 没法跑 bash。两种我都维护了——你看哪个方便用哪个。

---

## 方式 3：手动 git clone + 软链（最透明，最适合学习/调试）

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

**Windows PowerShell 手动版**：
```powershell
git clone https://github.com/Qqapple1/Mavis-team-mode-skill.git $env:USERPROFILE\mavis-team-mode-skill
$dest = "$env:USERPROFILE\.zcode\skills\mavis-team-mode"
New-Item -ItemType Directory -Path "$env:USERPROFILE\.zcode\skills" -Force | Out-Null
Copy-Item -Recurse -Path $env:USERPROFILE\mavis-team-mode-skill -Destination $dest
```

---

## 方式 4：手动复制（适合离线 / 容器 / NAS）

```bash
# 1. Clone 或下载 zip
git clone https://github.com/Qqapple1/Mavis-team-mode-skill.git /tmp/mavis-team-mode-skill
# 或：wget https://github.com/Qqapple1/Mavis-team-mode-skill/archive/main.zip && unzip main.zip

# 2. 复制到 Zcode skills 目录
mkdir -p ~/.zcode/skills
cp -r /tmp/mavis-team-mode-skill ~/.zcode/skills/mavis-team-mode

# 3. 重启 Zcode
```

---

## 验证安装

跑验证脚本（macOS / Linux / Git Bash / WSL）：
```bash
bash scripts/install.sh --doctor
# 或
bash scripts/validate.sh
```

或 PowerShell：
```powershell
powershell -ExecutionPolicy Bypass -File scripts\install.ps1 -Doctor
# 或
powershell -ExecutionPolicy Bypass -File scripts\validate.ps1
```

期望看到 `Passed: 22 / Failed: 0`（或类似数字）。

或手动：
```bash
ls ~/.zcode/skills/mavis-team-mode/SKILL.md && echo "✓ SKILL.md exists"
ls ~/.zcode/skills/mavis-team-mode/agents/leader.md && echo "✓ agents/leader.md exists"
ls ~/.zcode/skills/mavis-team-mode/agents/worker-coder.md && echo "✓ agents/worker-coder.md exists"
ls ~/.zcode/skills/mavis-team-mode/agents/verifier.md && echo "✓ agents/verifier.md exists"
```

---

## 升级

```bash
# 方式 1/3：自动
cd ~/mavis-team-mode-skill
git pull
# 如果你用软链，Zcode 下次启动会自动看到新版（无需重装）
# 如果你用 copy（Windows），重新跑 install.sh

# 方式 2（PowerShell）：
cd $env:USERPROFILE\mavis-team-mode-skill
git pull
powershell -ExecutionPolicy Bypass -File scripts\install.ps1

# 方式 4：重新跑安装
```

---

## 卸载

**macOS / Linux / Git Bash / WSL**：
```bash
bash scripts/install.sh --uninstall
# 删 ~/.zcode/skills/mavis-team-mode 软链
# 保留 ~/mavis-team-mode-skill（你的代码仓库）
```

**Windows PowerShell**：
```powershell
powershell -ExecutionPolicy Bypass -File scripts\install.ps1 -Uninstall
```

**完全删除（包括仓库）**：
```bash
bash scripts/install.sh --uninstall
rm -rf ~/mavis-team-mode-skill
```

---

## 故障排查

详见 [`references/troubleshooting.md`](references/troubleshooting.md)。

最常见问题：
- **skill 没触发** → 完全退出 Zcode（不是最小化），重新打开
- **软链不工作** → 检查 `ls -la ~/.zcode/skills/`
- **description 报错** → 检查 YAML 引号（必须是英文双引号 `"..."`）
- **Windows PowerShell 路径错** → 用 `$env:USERPROFILE` 别写死 `C:\Users\xxx`

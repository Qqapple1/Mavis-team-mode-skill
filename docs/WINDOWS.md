# Windows 安装指南

**TL;DR**: 3 个选项，**都支持**：

- **WSL2 (Ubuntu)** — 真 symlink，最完整，但需要重启一次
- **Git Bash** — 最简单，install.sh 默认 copy 模式
- **PowerShell** — Windows 原生，用 `install.ps1`

选哪个看你哪个舒服。下面有详细对比。

---

## 方案 A：WSL2 (Ubuntu) — 推荐用于生产/长期使用

最完整的方案 — 真 symlink + Linux 文件权限 + Zcode 官方支持。

### 1. 装 WSL2

```powershell
# 在 PowerShell 管理员模式跑（一次）
wsl --install
# 重启电脑
# 默认装 Ubuntu
```

### 2. 在 WSL 里装依赖

```bash
# 打开 Ubuntu terminal
sudo apt update
sudo apt install -y python3 git bash
```

### 3. 在 WSL 里 clone + install

```bash
# 在 WSL 里的 Linux 文件系统（不要用 /mnt/c/，权限会乱）
git clone https://github.com/Qqapple1/Mavis-team-mode-skill.git ~/mavis-team-mode-skill
cd ~/mavis-team-mode-skill
bash scripts/install.sh
```

### 4. 在 Windows 上的 Zcode 客户端里用

Zcode 的 Windows 客户端能读 WSL 的文件。在 Zcode 里打开：
```
\\wsl$\Ubuntu\home\<your-username>\mavis-team-mode-skill
```

或在 WSL 终端里：
```bash
explorer.exe .
# 会打开 Windows 资源管理器
```

---

## 方案 B：Git Bash — 最简单（最常被推荐）

如果你不想用 WSL，Git Bash 也能跑：

1. 装 [Git for Windows](https://git-scm.com/download/win)
2. 装 [Python 3.8+ for Windows](https://www.python.org/downloads/windows/)（**关键**：勾 "Add Python to PATH"）
3. 装 [Zcode Windows 版](https://zcode-ai.com) (3.4.2+)
4. 打开 **Git Bash**（不是 PowerShell / CMD），跑：
```bash
git clone https://github.com/Qqapple1/Mavis-team-mode-skill.git ~/mavis-team-mode-skill
cd ~/mavis-team-mode-skill
bash scripts/install.sh
```

**已知坑**：
- 默认 **copy 模式**（不是真 NTFS symlink）
- 想真 symlink：`export MSYS=winsymlinks:native`（需要 Win 10+ 开发者模式），或用 WSL
- Git Bash 的 `~/` 是 `C:\Users\<you>\`，跟 Zcode Windows 客户端读的路径**可能不一致** — 如果不对，去 Zcode 设置里改 skills 目录

---

## 方案 C：PowerShell — Windows 原生（不用装 Git Bash）

如果你不想装 Git Bash，直接用 PowerShell：

```powershell
# 1. 装 Python (勾 "Add Python to PATH")
# https://www.python.org/downloads/windows/

# 2. 装 Git for Windows (PowerShell 用 git 命令)
# https://git-scm.com/download/win

# 3. 装 Zcode Windows 版
# https://zcode-ai.com (3.4.2+)

# 4. 在 PowerShell 跑:
git clone https://github.com/Qqapple1/Mavis-team-mode-skill.git $env:USERPROFILE\mavis-team-mode-skill
cd $env:USERPROFILE\mavis-team-mode-skill
powershell -ExecutionPolicy Bypass -File scripts\install.ps1
```

PowerShell 版**功能等价**（clone + copy + 验证 + 卸载），只是永远 copy 模式（PowerShell 不支持 symlink）。

**PowerShell 参数**：
- `-Doctor` 诊断（不改）
- `-Uninstall` 卸载
- `-NoVerify` 跳过验证
- `-InstallDir <path>` 自定义安装路径
- `-RepoUrl <url>` 自定义 Git 源

---

## 3 个方案对比

| 方案 | Symlink | PowerShell 原生 | 难度 | 适用场景 |
|---|---|---|---|---|
| **WSL2** | ✅ 真 symlink | ❌（bash 替代） | ⭐⭐⭐ | 长期使用、Linux 重度用户 |
| **Git Bash** | ⚠️ copy（默认）/ 真 symlink（设 MSYS env） | ❌ | ⭐ | 临时使用、不想重启 |
| **PowerShell** | ❌ 永远 copy | ✅ | ⭐⭐ | 不装 Git Bash、纯 Windows |

---

## 验证装好没

**WSL / Git Bash**：
```bash
bash scripts/install.sh --doctor
# 或
bash scripts/validate.sh
```

**PowerShell**：
```powershell
powershell -ExecutionPolicy Bypass -File scripts\install.ps1 -Doctor
# 或
powershell -ExecutionPolicy Bypass -File scripts\validate.ps1
```

期望看到 `Passed: 23`（bash）或 `Passed: 24`（PowerShell 验证项比 bash 多一些）。

---

## 跑 prototype server (Todo App)

**任何方案**：
```bash
cd examples/prototype-todo-app   # 或 PowerShell: cd examples\prototype-todo-app
python3 server/server.py         # 或 PowerShell: py server\server.py
```

然后在 Windows 浏览器打开：
- WSL2: `http://127.0.0.1:8765/api/health` （WSL2 自动转发到 Windows）
- Git Bash / PowerShell: 同样 URL

期望看到 JSON `{"status":"ok","ts":"..."}`。

---

## 跑 e2e tests

**任何方案**：
```bash
# 一个 terminal 跑 server
cd examples/prototype-todo-app
python3 server/server.py &

# 另一个 terminal 跑 tests
python3 test_e2e.py
python3 test_e2e_extended.py
python3 test_e2e_advanced.py
```

**PowerShell 简化版**（一个 terminal 全跑）：
```powershell
cd examples\prototype-todo-app
powershell -ExecutionPolicy Bypass -File .\run_e2e.ps1
```

期望看到：
```
ALL TESTS PASSED  (20/20)
ALL EXTENDED TESTS PASSED  (23/23)
Passed: 5, Failed: 0  (advanced)
```

---

## 我没在真 Windows 上测过的部分

- Zcode Windows 客户端**是否能识别**这个 skill（**在 GitHub Actions Windows runner 上跑过 PowerShell install + server 启动 + e2e**，但**没在真 Windows 用户的 Zcode 客户端里试过**）
- 软链在 Git Bash 下的行为（不是真 NTFS symlink）
- prototype server 跑在 WSL + Zcode 在 Windows 的 file watcher 行为

**欢迎 Windows 用户提 issue 反馈**：
https://github.com/Qqapple1/Mavis-team-mode-skill/issues

或者直接编辑本文件 (`docs/WINDOWS.md`) 提 PR。

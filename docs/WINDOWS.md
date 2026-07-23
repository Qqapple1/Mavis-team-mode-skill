# Windows 安装指南

**TL;DR**: 用 **WSL2 (Ubuntu)**，别用 Git Bash 或 PowerShell。

---

## 推荐：WSL2 (Ubuntu)

最干净的方案。Zcode 官方下载页对 Windows + WSL 用户都支持。

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

## 备选 1：Git Bash

如果你不想用 WSL，Git Bash 也能跑（但我没在真 Windows 上测过）：

1. 装 [Git for Windows](https://git-scm.com/download/win)
2. 装 [Python 3.8+ for Windows](https://www.python.org/downloads/windows/)（**关键**：勾 "Add Python to PATH"）
3. 打开 **Git Bash**（不是 PowerShell / CMD）
4. 跑：
```bash
git clone https://github.com/Qqapple1/Mavis-team-mode-skill.git ~/mavis-team-mode-skill
cd ~/mavis-team-mode-skill
bash scripts/install.sh
```

**已知坑**：
- `ln -s` 在 Windows 上**不**真做软链（Git Bash 假装做了，但 Windows 资源管理器看不见）—— 这影响 prototype server 的 `--doctor` 诊断
- Zcode 客户端需要看 `~/.zcode/skills/` —— Git Bash 的 `~/` 是 `C:\Users\<you>\`，和 Zcode Windows 客户端读的路径**可能不一致**

---

## 备选 2：PowerShell

**不推荐**。我们的 `install.sh` 是 bash 脚本，PowerShell 跑不了。

如果你坚持用 PowerShell，要**手动**做：
1. clone 仓库
2. 在 `C:\Users\<you>\.zcode\skills\` 创 `mavis-team-mode` 目录
3. 把 clone 出的所有文件 copy 过去

或者写个 PowerShell 版的 install.sh——欢迎 PR，但**这个 repo 不维护 PS 版**。

---

## 验证装好没

在 WSL 或 Git Bash 里跑：
```bash
bash scripts/install.sh --doctor
```

期望看到：
- ✓ Zcode skills dir exists
- ✓ Symlink: ~/.zcode/skills/mavis-team-mode -> /path/to/your/clone
- ✓ Clone exists
- ✓ SKILL.md present
- ✓ agents/leader.md present
- ✓ agents/verifier.md present
- ✓ agents/worker-coder.md present
- ✓ README.md present

---

## 跑 prototype server (Todo App)

在 WSL 或 Git Bash：
```bash
cd examples/prototype-todo-app
python3 server/server.py
```

然后在 Windows 浏览器打开：
- 如果 WSL: `http://127.0.0.1:8765/api/health` （WSL2 自动转发）
- 如果 Git Bash: 同样

期望看到 JSON `{"status":"ok","ts":"..."}`。

---

## 跑 e2e tests

在 WSL 或 Git Bash：
```bash
# 一个 terminal 跑 server
cd examples/prototype-todo-app
python3 server/server.py &

# 另一个 terminal 跑 tests
python3 examples/prototype-todo-app/test_e2e.py
python3 examples/prototype-todo-app/test_e2e_extended.py
python3 examples/prototype-todo-app/test_e2e_advanced.py
```

期望看到：
```
ALL TESTS PASSED  (20/20)
ALL EXTENDED TESTS PASSED  (23/23)
Passed: 5, Failed: 0  (advanced)
```

---

## 我没在真 Windows 上测过的部分

- Zcode Windows 客户端**是否能识别**这个 skill（应该能，但没真测）
- 软链在 Git Bash 下的行为（不是真 NTFS symlink）
- prototype server 跑在 WSL + Zcode 在 Windows 的 file watcher 行为

**欢迎 Windows 用户提 issue 反馈**：
https://github.com/Qqapple1/Mavis-team-mode-skill/issues

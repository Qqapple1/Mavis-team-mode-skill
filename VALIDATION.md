# Validation Guide

怎么验证这个 skill 装好、跑得对。

## 1. 文件结构验证（30 秒）

```bash
# 必需文件全部存在
for f in SKILL.md agents/leader.md agents/verifier.md agents/worker-coder.md; do
  test -f ~/.zcode/skills/mavis-team-mode/$f && echo "✓ $f" || echo "✗ MISSING $f"
done
```

## 2. 格式验证（10 秒）

```bash
bash scripts/validate.sh
```

期望输出：`Passed: 23, Failed: 0`（23 项格式自检）。

## 3. YAML frontmatter 验证（10 秒）

```bash
# 解析所有 .md 的 frontmatter
python3 -c "
import yaml, glob
for f in glob.glob('**/*.md', recursive=True):
    with open(f) as fp: c = fp.read()
    if not c.startswith('---'): continue
    end = c.find('---', 3)
    if end == -1: print(f'  ✗ {f}: unclosed'); continue
    try:
        yaml.safe_load(c[3:end])
        print(f'  ✓ {f}')
    except Exception as e:
        print(f'  ✗ {f}: {e}')
"
```

## 4. 真实可运行验证（2 分钟）

跑 prototype + 3 个 e2e 测试（48 个测试 = 20 + 23 + 5）：

```bash
cd examples/prototype-todo-app
python3 server/server.py &
sleep 2
python3 test_e2e.py           # 期望: ALL TESTS PASSED (20/20)
python3 test_e2e_extended.py  # 期望: ALL EXTENDED TESTS PASSED (23/23)
python3 test_e2e_advanced.py  # 期望: Passed: 5, Failed: 0
kill %1
```

或 Windows PowerShell 简化版（一个 terminal 全跑）：
```powershell
cd examples\prototype-todo-app
powershell -ExecutionPolicy Bypass -File .\run_e2e.ps1
```

## 5. Zcode 加载验证（需要 Zcode）

启动 Zcode，输入框输入：

```
用 mavis team mode 帮我 …
```

或自然语言：

```
拆开来做
用 team 模式跑一下
用多智能体协作处理
```

**Zcode 技能触发机制**：Agent Skills 标准下，技能是 **description 匹配触发**，不是 `/skill-name` 命令。Zcode 在用户输入时扫描所有可用 skill 的 `description` 字段，匹配后才加载完整 `SKILL.md`。

**期望反应**：
- Zcode 加载 SKILL.md，Leader 身份接管
- Leader 输出 Team Plan 模板，问你“具体什么任务”

**如果没反应**：
- 检查 Zcode 是否有这个 skill：`bash scripts/install.sh --doctor`
- 试试更明确的触发词：“team mode”、“用 team 模式”、“拆成子任务”
- 完全退出 Zcode 重开
- 看 Zcode 日志（设置 → Logs）
- 重跑 `bash scripts/validate.sh`

## 6. 端到端工作流验证（5 分钟）

在 Zcode 输入：

```
用 mavis team mode 帮我给这个项目加一个 README（如果还没有）
```

**期望反应**：
- Leader 输出 Team Plan（带 2-3 个 Sub-task）
- 派 sub-agent 执行
- 返回整合后的结果
- 问你要不要开第二个 Zcode 会话当 Verifier

**如果 Verifier 步骤失败**：
- 看 `references/troubleshooting.md` 的 "Verifier 没找到问题" 部分

## 7. 卸载验证（30 秒）

```bash
bash scripts/install.sh --uninstall
ls ~/.zcode/skills/mavis-team-mode 2>/dev/null && echo "✗ still there" || echo "✓ removed"
```

## 8. CI 验证（推送 GitHub 后）

```bash
git remote add origin https://github.com/Qqapple1/Mavis-team-mode-skill.git
git push -u origin main
```

GitHub Actions 应该跑通：
- ✓ Stats
- ✓ Windows install (PowerShell) — install + server startup + e2e
- ✓ Lint (ubuntu) / Lint (macos) / Lint (windows) — bash + python syntax
- ✓ Python 3.8 / 3.9 / 3.10 / 3.11 / 3.12
- ✓ Integration test (Linux) — install + validate + 48 e2e + benchmark

实际有 12 个 jobs / job groups（lint x3 + py x5 + win + integration + stats + package），详见 `.github/workflows/validate-skill.yml`。

## 全部 8 步通过 = skill 装好且能跑

| Step | 工具 | 时间 | 跳过风险 |
|------|------|------|----------|
| 1. 文件结构 | bash | 30s | 低（CI 会查）|
| 2. 格式验证 | validate.sh | 10s | 低 |
| 3. YAML 验证 | python | 10s | 低 |
| 4. prototype | python | 2min | 中（需要 server 端口空闲）|
| 5. Zcode 加载 | Zcode | 1min | 高（依赖 Zcode 版本）|
| 6. 端到端 | Zcode | 5min | 中（依赖模型）|
| 7. 卸载 | bash | 30s | 极低 |
| 8. CI | GitHub | 1min | 极低（无外部依赖）|

## 失败排查

- **Step 1-3 失败** → 看 `references/troubleshooting.md`
- **Step 4 失败** → 端口 8765 被占用？改 `PORT=xxxx python3 server/server.py` 和 `test_e2e.py` 里的 `PORT`
- **Step 5-6 失败** → 检查 Zcode 版本（要 3.0+），Agent Skills 标准支持
- **Step 8 失败** → 看 GitHub Actions 日志

---
name: reference-troubleshooting
description: "Common issues when installing or running Mavis Team Mode skill in Zcode, with diagnostic steps and fixes. Reference document, not a triggerable skill."
type: reference
category: troubleshooting
---

# Troubleshooting

## Skill 没被 Zcode 识别

**症状**：输入 "用 mavis team mode" 之类没反应，或自然语言没触发

**排查步骤**：

1. **检查文件位置**
   ```bash
   ls -la ~/.zcode/skills/mavis-team-mode/
   # 应该看到：SKILL.md, agents/, references/, examples/
   ```

2. **检查文件名**（大小写敏感）
   - ✅ `SKILL.md`（全大写）
   - ❌ `skill.md`

3. **检查 frontmatter 格式**
   ```bash
   head -20 ~/.zcode/skills/mavis-team-mode/SKILL.md
   # 第一行必须是 ---
   # name 和 description 必填
   ```

4. **重启 Zcode**
   - 完全退出（不是最小化）
   - 重新打开
   - Zcode 启动时扫描 skills 目录

5. **看 Zcode 日志**
   - 设置 → Logs → 找 "skill" 相关 error

## Sub-agent 没启动

**症状**：Leader 输出 Team Plan 后，没派 sub-agent

**原因**：
- Zcode 3.x 子智能体在某些版本下需要手动启用（**未在每个 Zcode 3.x minor 版本实测**，以下是基于一般 Zcode 行为推断）
- 某些任务类型不满足触发条件
- Leader 没在 Team Plan 模板里指定 `type: general-purpose | explore`

**解决**：
- 检查 Zcode 设置 → Agents → 确认 Sub-Agents 启用
- 确认任务描述里有"用 team 模式"或"mavis team"触发词
- 在 Team Plan 里明确每个 Sub-task 的 `type: general-purpose`（写文件）或 `type: explore`（只读）

## Verifier 没找到问题

**症状**：Verifier 给了 PASS，但用户实际发现 bug

**原因**：Verifier 是"软"独立——第二个 Zcode 会话，模型可能跟 Leader 一样（**没有强制要求 Zcode 切换模型**）

**解决**：
- 在 Zcode 里手动给 Verifier 会话换不同模型（**不保证 Zcode 3.x 一定支持热切换**）
- 加更严格的 acceptance criteria
- 让 Verifier 独立跑测试，不只是看代码

## Team Plan 太长 / 太短

**症状 A**：Plan 有 50 个 Sub-task，调度不过来了

**原因**：Leader 没控制粒度

**解决**：
- 每个 Sub-task 应该 5-30 分钟独立工作
- 超过 30 分钟的 Sub-task 继续拆
- 最多 5-7 个 Sub-task（多了协调成本爆炸）

**症状 B**：Plan 只有 2 个 Sub-task，不值得用 Team

**解决**：
- < 3 个 Sub-task 的任务直接干
- Team 模式只对"复杂多步 + 需要验收"的任务

## 软链没生效

**症状**：`ln -s` 后 Zcode 找不到 skill

**排查**：
```bash
ls -la ~/.zcode/skills/
# 看到 mavis-team-mode -> /path/to/repo

# 检查软链目标是否存在
ls -la /path/to/repo/

# 软链可以跨文件系统（包括外接硬盘/NAS）；
# 硬链接（hard link）才不能跨设备。软链问题通常是目标路径错了。
```

**解决**：
- 检查软链目标路径是否对（绝对路径，不是相对路径）
- 如果是 broken symlink，删除再重建：`rm ~/.zcode/skills/mavis-team-mode && ln -s <正确路径> ~/.zcode/skills/`
- 软链权限问题：跑 `chmod +x <目标目录>/SKILL.md`（某些 Zcode 版本需要）

---

# 非 ASCII 文本相关

## 1. 中文/emoji 搜索返回 0 结果,但 list / add 都正常

**症状**(v1.3.14 用户反馈):
```
$ mnote search "技术"
No matches
# 但 mnote list 里有"技术备忘"这条记录
```

**根因**: 代码用了 `json.dumps(value)` 写盘,Python 默认
`ensure_ascii=True`,中文被转义为 `\u4e2d\u6587` 存入文件。搜索时用
原始中文关键词"技术",匹配不到 ASCII 转义字符。

**诊断**:
```bash
# 看 001.md 文件实际内容（是中文还是转义）
cat 001.md
# 如果看到 "\u4e2d\u6587" 这种转义,中招了
# 如果看到 "中文",是别的 bug
```

**修复**:
```python
# WRONG
lines.append(f"{key}: {json.dumps(value)}")
# RIGHT
lines.append(f"{key}: {json.dumps(value, ensure_ascii=False)}")
```

**预防**:
- Worker-Coder 写文件前,如果有非 ASCII 处理,必须 `ensure_ascii=False`
- Tester 必须有 1 个非 ASCII 关键词的测试用例
- Leader 在 CONTRACT.md 里明言"非 ASCII 文本必须保留原字符,不得转义"

## 2. 读文件乱码

**症状**: 读出来是 `b'\\xe4\\xb8\\xad\\xe6\\x96\\x87'` 或 `\u4e2d\u6587`

**根因**: 用了 `open(path).read()` 没指定 `encoding="utf-8"`,系统默认
编码是 GBK / Latin-1

**修复**:
```python
# WRONG
content = open(path).read()
# RIGHT
content = open(path, encoding="utf-8").read()
```

---

# Windows

## 1. `python3` 命令找不到

**症状**: worker 跑 `python3 script.py` 报 `'python3' is not recognized as an internal or external command`

**排查**:
```powershell
# 依次试
python --version
py --version
where python
where py
```

**解决**:
- 优先用 `py`(Windows Python launcher,官方推荐)
- 如果 Zcode 捆绑了 Python(常见于 `codex-runtime/python/python.exe`),在 install 时加到 PATH
- 或者让 Leader prompt 里 worker 调 `py` 而非 `python3`

## 2. Shell glob 不展开(`*.txt` 原样传给工具)

**症状**: `frename *.txt` 在 Windows bash 里把字面字符串 `*.txt` 传给 frename,不是展开后的文件列表

**排查**:
```powershell
# bash 里试
echo *.txt
# 如果输出 `*.txt` 而不是文件列表,说明没展开
```

**解决**:
- 在 Worker prompt 里要求显式文件列表(不要依赖 glob)
- 或者跑 `frename $(ls *.txt)` 强制展开
- PowerShell 原生不支持 Unix glob;用 `Get-ChildItem *.txt | %{ frename $_.Name }`

## 3. 路径分隔符(`\` vs `/`)

**症状**: worker prompt 里写了 `D:\Z code\frename\xxx.py`,但代码里是 `D:/Z code/frename/xxx.py`,不一致

**解决**:
- Leader prompt 里统一用**正斜杠** `/`,大多数 Python/PowerShell 都接受
- 或者 Leader prompt 里明确说"用 Windows 原生反斜杠,但 worker 写文件时统一用正斜杠"
- 不要混用,会出 substring 匹配不到的隐性 bug

## 4. `~/.zcode/` 不展开

**症状**: PowerShell 里 `~/.zcode/skills/...` 字面不展开,~ 不是 PowerShell 的 home 缩写

**解决**:
- 用 `$env:USERPROFILE` 代替 `~`
- 或用 `Resolve-Path ~` 拿到完整路径再传

## 5. Worker 产出的文档与实际代码不一致

**症状**: Doc-Writer 写的 README 参数表(`--number --name --filter...`)跟 Coder 实现的 CLI(`--prefix --suffix --replace...`)对不上

**根因**: 4 个 Worker 完全隔离,没有共享接口契约,各自为政

**解决**:
- 在 SKILL.md Step 2.5 里 Leader 必须**先**写 `CONTRACT.md`(CLI 参数、函数签名、文件格式)再派发 Worker
- 简单任务(< 50 行)也至少在 Leader prompt 里写明完整接口
- 详见 SKILL.md Step 2.5

## 6. Worker 调研了但没写文件到磁盘

**症状**: Researcher 报告说"已经调研完成",但下游 Worker / 你自己看不到 `RESEARCH.md`

**根因**: Researcher 被派了 Zcode 内置的 `Explore` agent(只读),但任务要求写文件。Explore 不会写。

**解决**:
- 如果要写文件,Leader 必须派 `general-purpose`,不是 `Explore`
- 详见 `agents/worker-researcher.md` 里的 Mode selection 表
- 如果已经派错了,让 Researcher 重跑成 `general-purpose`

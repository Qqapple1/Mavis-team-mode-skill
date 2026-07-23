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
- Zcode 3.0 子智能体还是 Beta，可能需要手动启用
- 某些任务类型不满足触发条件

**解决**：
- 检查 Zcode 设置 → Agents → 确认 Sub-Agents 启用
- 确认任务描述里有"用 team 模式"或"mavis team"触发词

## Verifier 没找到问题

**症状**：Verifier 给了 PASS，但用户实际发现 bug

**原因**：Verifier 是"软"独立——第二个 Zcode 会话，模型可能跟 Leader 一样

**解决**：
- 用不同模型（Leader 用 GLM-5.2，Verifier 用 DeepSeek）
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

# 软链不能跨设备（symbolic link 不能链到外接硬盘/NAS）
```

**解决**：
- 软链目标必须是同一文件系统
- 跨设备用 `cp -r` 复制

# 多模型验证配置 (Multi-Model Verification Setup)

## 为什么需要多模型验证

TeamForge 的对抗式验证（Checker + Skeptic + Judge）能有效降低同模型偏见，但模型底层的逻辑盲区无法通过 Prompt 完全消除。

**终极解决方案**：让 Verifier 使用与 Worker 不同的模型。

## Method E: 外部 API 验证（高级用法）

如果 Zcode 支持多提供商配置，Leader 可以通过以下方式实现跨模型验证：

### 方案 1: Zcode 多提供商（推荐）

在 Zcode 配置中同时接入多个模型提供商（如 DeepSeek + MiMo + GPT），Leader 在派发 Verifier 时指定使用不同的模型：

```
VERIFIER MODEL: deepseek-v4-pro   # 如果 Worker 用的是 MiMo
```

### 方案 2: 外部 API 调用（高级）

如果 Zcode 不支持子 Agent 切换模型，Leader 可以通过 Bash 工具调用外部 API：

```bash
# 将验证任务发送给另一个模型
curl -X POST https://api.deepseek.com/v1/chat/completions \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-v4-pro",
    "messages": [
      {"role": "system", "content": "你是独立验证者..."},
      {"role": "user", "content": "请验证以下交付物..."}
    ]
  }'
```

### 方案 3: 对抗式 Prompt 优化（最低成本）

如果无法使用多模型，通过 Prompt 强制 Checker 和 Skeptic 产生对立视角：

- **Checker Prompt**: "你是宽松的检查者，假设代码是正确的，只检查明显错误"
- **Skeptic Prompt**: "你是极度悲观的攻击者，假设代码有 bug，全力寻找问题"

这种 Prompt 级别的对立，即使在同一模型下，也能产生有价值的对抗效果。

## 适用场景

| 方法 | 适用场景 | 效果 |
|------|----------|------|
| Method A | 手动开第二个 Zcode 会话 | 高（完全独立） |
| Method D | 自动派发 Verifier sub-agent | 中（同模型） |
| **Method E** | **外部 API 验证** | **最高（跨模型）** |
| 对抗式 Prompt | 无多模型配置 | 中高（Prompt 对立） |

## 配置示例

在 Zcode 中配置多提供商后，Leader 可以在 Team Plan 中指定：

```markdown
## 验证配置
- Worker 模型: mimo-v2.5-pro
- Verifier 模型: deepseek-v4-pro
- 验证模式: adversarial
```

## 快速配置指南

### 步骤 1: 配置多提供商
在 Zcode 配置中添加至少两个不同的模型提供商：
- 提供商 A: DeepSeek (api.deepseek.com)
- 提供商 B: MiMo (api.xiaomimimo.com)
- 或其他 OpenAI 兼容的 API

### 步骤 2: 在 Team Plan 中指定验证模型
```markdown
## 验证配置
- Worker 模型: mimo-v2.5-pro
- Verifier 模型: deepseek-v4-pro
- 验证模式: adversarial
```

### 步骤 3: Leader 自动切换
Leader 在派发 Verifier 时，通过环境变量或 API 参数指定使用不同的模型。

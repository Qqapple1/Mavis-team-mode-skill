---
name: reference-deepseek-setup
description: "How to configure Zcode to use DeepSeek as the LLM provider, with API setup and model selection guidance. Reference document, not a triggerable skill."
type: reference
category: setup
---

# DeepSeek + Zcode Setup

> **Honest framing**: This doc tells you how to connect Zcode to DeepSeek
> at the provider level. It does **not** test that DeepSeek + this skill
> actually produces good Team Mode output. Model behavior in multi-agent
> workflows depends on each model's tool-use reliability, which DeepSeek
> has not officially documented for Zcode 3.x as of 2026-07-23. The
> "model selection" table below is general DeepSeek knowledge, not
> measured in this repo.

把 Zcode 接到 DeepSeek API。

## 1. 拿到 DeepSeek API Key

访问 https://platform.deepseek.com/
- 注册/登录
- 左侧栏 `API Keys` → `Create new key`
- 复制 key（格式：`sk-xxxxxxxxxx`）
- **充值**（DeepSeek 现在新用户必须先充值才能用 API）

## 2. 在 Zcode 里加 DeepSeek Provider

打开 Zcode → 左下角设置 → Models → Add custom provider

**方案 A：Anthropic 协议（推荐）**

| 字段 | 值 |
|------|-----|
| Name | `DeepSeek` |
| Anthropic-compatible URL | `https://api.deepseek.com/anthropic` |
| OpenAI-compatible URL | `https://api.deepseek.com/v1` |
| API Key | `sk-xxxxxxxxxx` |
| Model | `deepseek-chat` 或 `deepseek-reasoner` |

**说明：**
- `deepseek-chat` — DeepSeek V3 系列，对标 GPT-4o（按 DeepSeek 官方文档，2026-07 检索）
- `deepseek-reasoner` — DeepSeek R1 系列，强推理但慢（同上）

## 3. 验证连通

回到主界面，发送一条消息：

> "用一句话介绍你自己"

如果 DeepSeek 答了 = 通了。

## 4. 跑 Mavis Team Mode

跟 Zcode 说（描述匹配触发）：

```
用 mavis team mode 加 deepseek 模型，帮我 [你的复杂任务]
```

## 5. 模型选择建议

| 任务类型 | 推荐模型 |
|----------|----------|
| 写代码、改 bug | `deepseek-chat` |
| 复杂调研、长任务 | `deepseek-reasoner` |
| 测试/Review | `deepseek-chat`（快）|
| 大型重构 | `deepseek-reasoner`（深） |

## 6. 已知限制

**DeepSeek 在 Zcode 上的 trade-off**（**这些只是常识 + 一般经验，不是我测出来的 Zcode 实际行为**）：
- ❌ 失去 Zcode 对原生 GLM 模型路径的默认调优 — **未验证**
- ❌ DeepSeek 工具调用格式跟 Anthropic 有差异 — **未在 Zcode 实测**
- ✅ 价格便宜（按 DeepSeek 官网公开定价，2026-07）
- ✅ 上下文长度（V3: 64K / R1: 64K 推理 + 8K 输出 — **不是 1M**，以 DeepSeek 官方为准）
- ✅ 推理能力强（R1 系列 — 公开基准）
- ✅ 开源（如果你想本地部署，可以跳过 API）

## 7. 国内访问

DeepSeek API 域名是 `api.deepseek.com`，国内直连，无需梯子。

---
name: example-research-then-implement
description: "Worked example: research WebSocket libraries then build a demo with mock server using Mavis Team Mode. Reference document, not a triggerable skill."
type: example
category: research
---

# Example: Research → Implement Pattern

**User task**: "我们公司想用 WebSocket 替代轮询。给我一个 demo，连接公司 mock server，接收实时消息。"

## Phase 1: Leader Plan

```markdown
# Team Plan

## 目标
写一个 WebSocket demo，连接公司 mock server，接收实时消息，UI 显示消息流。

## 子任务清单

### Subtask 1: 调研 WebSocket 库选型
- **type**: explore
- **tools**: [read_file, grep, glob, web_search, web_fetch]
- **prompt**: 调研：
  1. Node.js 主流 WebSocket 库对比（ws / socket.io / uWebSockets.js）
  2. 浏览器原生 WebSocket API 现状
  3. 重连、心跳、断线处理方案
  4. mock server 怎么写（mock-socket 库等）
  输出：选型建议 + 推荐方案的代码骨架。
- **acceptance**:
  - [ ] 对比至少 3 个库
  - [ ] 推荐方案有理由
  - [ ] 有可运行的最小 demo 代码
- **dependency**: none
- **estimated_minutes**: 15

### Subtask 2: 写 mock server
- **type**: general-purpose
- **prompt**: 基于 Subtask 1 的选型，写一个 mock server：
  1. 监听 8080
  2. 每 2 秒推送一条假消息
  3. 支持多客户端
  4. 有启停脚本
- **acceptance**:
  - [ ] server 能启动
  - [ ] 客户端连上能收到消息
  - [ ] 启停脚本能用
- **dependency**: depends-on-subtask-1
- **estimated_minutes**: 20

### Subtask 3: 写客户端
- **type**: general-purpose
- **prompt**: 写浏览器端 demo：
  1. 连接 mock server
  2. 显示消息流（带时间戳）
  3. 心跳 + 自动重连
  4. 断开时显示状态
- **acceptance**:
  - [ ] 浏览器打开能自动连
  - [ ] 实时显示消息
  - [ ] 手动 kill server 再启动，客户端能重连
- **dependency**: depends-on-subtask-1
- **estimated_minutes**: 25

### Subtask 4: 写 README
- **type**: general-purpose
- **prompt**: 写 README：
  1. 5 分钟跑起来
  2. 架构图（ASCII）
  3. 扩展点说明
- **acceptance**:
  - [ ] 新人 5 分钟能跑通
  - [ ] 有架构图
- **dependency**: depends-on-subtask-2, depends-on-subtask-3
- **estimated_minutes**: 10

## 验收标准
- [ ] mock server 能跑
- [ ] 客户端能连、能收消息、能重连
- [ ] README 5 分钟跑通指南可用

## 风险
- 公司 mock server 协议特殊 → fallback: 先用通用 WebSocket，公司协议后期再适配
- 浏览器跨域 → 列出 CORS 配置
```

## Phase 2: Dispatch

```
Subtask 1 (Research) ──→ Subtask 2 (Server) ──┐
                  ├──→ Subtask 3 (Client) ──┤
                                                └──→ Subtask 4 (README)
```

## Phase 3: Integration

Leader 把 server + client + README 整合成一个项目结构：

```
websocket-demo/
├── server/
│   ├── index.js
│   └── package.json
├── client/
│   ├── index.html
│   └── app.js
└── README.md
```

## Phase 4: Verification

Verifier 端到端测试：
1. 跑 `npm start` 启 server
2. 打开 client，确认 2 秒一条消息
3. `Ctrl+C` kill server
4. 5 秒后 client 显示"disconnected"
5. 重启 server
6. client 自动重连，消息继续

## Result

✅ 完整 demo
✅ 端到端可用
✅ 文档齐全

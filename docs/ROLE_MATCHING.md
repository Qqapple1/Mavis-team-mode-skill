# 角色匹配机制 (Role Matching)

## 概述

TeamForge 使用 `agents/ROLE_INDEX.yaml` 进行智能角色匹配，替代人工遍历决策树。

## 匹配算法

**关键词交集法（Jaccard 相似度）**：

1. Leader 从任务描述中提取关键词
2. 与 ROLE_INDEX.yaml 中每个角色的 keywords 列表取交集
3. 匹配度 = 交集大小 / 角色关键词总数
4. 返回匹配度最高的 3 个角色

**调用方式**：
```bash
python scripts/teamforge_utils.py --match-role "实现 FastAPI 后端 API"
# 输出:
# [{'role': 'worker-backend-architect', 'score': 0.67, 'matched': ['fastapi', '后端', 'api']}]
```

## ROLE_INDEX.yaml 格式

```yaml
worker-backend-architect:
  keywords: [后端, api, fastapi, django, flask, 数据库, 服务端, restful, graphql]
  desc: 后端架构设计
```

每个角色包含：
- `keywords`: 关键词列表（中英文均可）
- `desc`: 角色简短描述

## 如何新增角色

1. 在 `agents/` 目录创建 `worker-<name>.md` 角色文件
2. 在 `agents/ROLE_INDEX.yaml` 添加条目：
   ```yaml
   worker-<name>:
     keywords: [关键词1, 关键词2, ...]
     desc: 角色描述
   ```
3. 运行 `python scripts/teamforge_utils.py --self-check` 验证

## 匹配度阈值

- **> 60%**: 自动选择该角色
- **30-60%**: Leader 推荐但需用户确认
- **< 30%**: 回退到 `worker-team-member`

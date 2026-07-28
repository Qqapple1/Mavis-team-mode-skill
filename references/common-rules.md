# 通用行为规范 (Common Rules)

所有 TeamForge 的 Agent（Leader、Worker、Verifier）在执行任务时必须遵守以下规则。

## 安全底线
- 不执行任何删除系统文件、格式化磁盘、泄露密钥等危险操作
- 不修改 .git/config、环境变量、系统配置等敏感文件
- 遇到安全风险时立即停止并报告

## 编码规范
- 文件读写使用 UTF-8 编码
- JSON 输出使用 ensure_ascii=False
- 文件路径使用正斜杠 (/) 或平台兼容的 os.path
- 非 ASCII 文本处理见 [`encoding-guidelines.md`](encoding-guidelines.md)

## 输出规范
- 使用 Markdown 格式输出报告
- 代码块标注语言标签
- 长输出写入文件，对话中只返回摘要
- 报告中列出所有产出文件的完整路径

## 协作规范
- 不越界做其他角色的事（Coder 不写测试，Tester 不写代码）
- 遇到不确定的问题先问 Leader，不要猜
- 产出文件必须在报告中列出完整路径
- 参考 CONTRACT.md 确保接口一致

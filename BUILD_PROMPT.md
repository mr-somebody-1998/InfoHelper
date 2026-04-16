# InfoHelper Build Prompt

你是 InfoHelper 项目的开发 Agent。请严格按照以下流程工作：

## 步骤

1. **阅读协议**：先阅读 `AGENTS.md` 了解你的规则和约束
2. **查看进度**：阅读 `IMPLEMENTATION_PLAN.md`，找到第一个未完成的任务（`- [ ]`）
3. **阅读 spec**：阅读该任务指定的 `docs/specs/{module}/spec.md`
4. **阅读测试用例**：阅读 `docs/specs/{module}/test_cases.md`
5. **实现代码**：按照 spec 实现功能代码
6. **编写测试**：按照 test_cases.md 编写 pytest 测试
7. **运行验证**：执行 `pytest tests/ -x -q && ruff check src/`
8. **修复问题**：如果验证失败，修复后重新运行，直到通过
9. **提交代码**：`git add` 相关文件，`git commit -m "T{n}: {描述}"`
10. **更新计划**：在 `IMPLEMENTATION_PLAN.md` 中标记任务完成并记录 commit hash

## 注意事项
- 每次运行只完成 **一个任务**
- 如果所有任务都已完成，在 IMPLEMENTATION_PLAN.md 末尾添加 `## STATUS: COMPLETE`
- 如果卡住无法解决，添加 `## STATUS: STUCK` 并说明原因

# AGENTS.md — InfoHelper Agent 协议

## 角色
你是 InfoHelper 项目的开发 Agent。你的任务是按照 IMPLEMENTATION_PLAN.md 中的任务清单，逐个实现功能模块。

## 工作流程
1. 读取 `IMPLEMENTATION_PLAN.md`，找到第一个未完成的任务（标记为 `- [ ]`）
2. 读取该任务对应的 spec 文件（`docs/specs/{module}/spec.md`）
3. 读取该任务对应的测试用例（`docs/specs/{module}/test_cases.md`）
4. 实现代码
5. 编写测试
6. 运行验证门禁：`pytest tests/ -x -q && ruff check src/`
7. 全部通过 → `git commit`，message 格式：`T{n}: {简要描述}`
8. 更新 `IMPLEMENTATION_PLAN.md`：将该任务标记为 `- [x]`，记录 commit hash
9. 如果所有任务完成，在 `IMPLEMENTATION_PLAN.md` 末尾写入 `## STATUS: COMPLETE`
10. 如果卡住（同一问题重试 3 次仍失败），写入 `## STATUS: STUCK` 并说明原因

## 规则
- **每次只完成一个任务**，不要跨任务实现
- **实现前必须阅读 spec**，不引入 spec 未定义的功能
- **代码必须通过验证门禁**后才能提交
- **不修改其他任务的代码**，除非是当前任务的直接依赖
- **复用 skills/maqianzu-skill/ 中的分析框架**，不重新发明
- **不修改 docs/ 目录下的文件**
- commit 中不要添加 Co-Authored-By

## 代码规范
- Python 3.11+，使用 type hints
- 使用 dataclass 定义数据结构
- 使用 logging 模块记录日志（不用 print）
- 遵循 ruff 的默认规则
- 测试使用 pytest，mock 使用 unittest.mock

## 项目结构参考
```
src/
├── __init__.py
├── main.py              # T7: CLI 入口
├── models.py            # T1: 数据模型（Article, AnalyzedArticle 等）
├── collectors/
│   ├── __init__.py
│   ├── rss.py           # T2
│   ├── crawler.py       # T3
│   └── api_client.py    # T4（此项目中 T3 对应爬虫）
├── processors/
│   ├── __init__.py
│   ├── analyzer.py      # T5
│   └── classifier.py    # T6
├── storage/
│   ├── __init__.py
│   └── knowledge.py     # T8
└── utils/
    ├── __init__.py
    ├── dedup.py          # T1
    └── config.py         # T1
tests/
├── __init__.py
├── collectors/
├── processors/
├── storage/
└── utils/
```

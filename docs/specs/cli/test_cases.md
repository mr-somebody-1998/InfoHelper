# CLI 接口 — 测试用例

## 测试文件路径
`tests/test_main.py`

## 说明
CLI 测试使用 `subprocess` 或 `unittest.mock` 调用，Python API 测试直接实例化 InfoHelper 类。采集器和 Claude API 使用 mock。

---

## run 命令

### TC-CLI-001: 完整流程 — 默认参数
- **输入**：`python -m src.main run`
- **预期**：依次运行 RSS + 爬虫 + API 采集、分析、存储
- **验证**：stdout 输出 JSON，含 collected/analyzed/saved 字段

### TC-CLI-002: 指定采集器
- **输入**：`python -m src.main run --sources rss`
- **预期**：仅运行 RSS 采集器
- **验证**：爬虫和 API 采集器未被调用

### TC-CLI-003: 指定分类
- **输入**：`python -m src.main run --category ai`
- **预期**：仅采集 category=ai 的信息源

### TC-CLI-004: 无新文章
- **输入**：所有文章都已处理过
- **预期**：`{"collected": 0, "analyzed": 0, "saved": 0}`

### TC-CLI-005: 部分采集器失败
- **输入**：RSS 成功，爬虫失败
- **预期**：退出码 0，结果包含 RSS 采集的文章

---

## fetch 命令

### TC-CLI-101: 获取未读文章
- **输入**：`python -m src.main fetch --unread`
- **预期**：stdout 输出 JSON 数组，仅含未读文章

### TC-CLI-102: 按日期筛选
- **输入**：`python -m src.main fetch --date 2026-04-16`
- **预期**：仅返回该日期的文章

### TC-CLI-103: 按分类筛选
- **输入**：`python -m src.main fetch --category ai`
- **预期**：仅返回 AI 分类文章

### TC-CLI-104: 组合筛选
- **输入**：`python -m src.main fetch --unread --category economics --importance high`
- **预期**：返回同时满足三个条件的文章

### TC-CLI-105: limit 参数
- **输入**：`python -m src.main fetch --limit 5`
- **预期**：最多返回 5 条

### TC-CLI-106: text 格式输出
- **输入**：`python -m src.main fetch --format text`
- **预期**：输出人类可读的文本

### TC-CLI-107: 无匹配结果
- **输入**：筛选条件无匹配
- **预期**：输出 `[]`

---

## mark-read 命令

### TC-CLI-201: 标记指定 ID
- **输入**：`python -m src.main mark-read --id abc123 --id def456`
- **预期**：输出 `{"marked": 2}`

### TC-CLI-202: 标记全部已读
- **输入**：`python -m src.main mark-read --all`
- **预期**：所有未读文章标记为已读

### TC-CLI-203: 无效 ID
- **输入**：`python -m src.main mark-read --id nonexistent`
- **预期**：输出 `{"marked": 0}`

---

## status 命令

### TC-CLI-301: 查看状态
- **输入**：`python -m src.main status`
- **预期**：输出包含 total_articles、unread、by_category 等字段

### TC-CLI-302: 空数据库状态
- **输入**：首次运行，无历史数据
- **预期**：total_articles=0, unread=0

---

## Python API

### TC-API-401: InfoHelper 初始化
- **输入**：有效 config_path
- **预期**：成功实例化，各模块已初始化

### TC-API-402: InfoHelper 配置文件不存在
- **输入**：不存在的 config_path
- **预期**：抛出 FileNotFoundError 或 ConfigError

### TC-API-403: fetch_unread 快捷方法
- **预期**：等价于 fetch(unread=True)

### TC-API-404: run 返回统计
- **预期**：返回字典包含 collected/analyzed/saved

---

## 错误处理

### TC-CLI-501: 配置文件不存在
- **输入**：config.yaml 不存在
- **预期**：退出码 1，stderr 输出错误信息

### TC-CLI-502: 无效命令
- **输入**：`python -m src.main invalid_cmd`
- **预期**：输出 usage 帮助信息

### TC-CLI-503: 所有采集器失败
- **输入**：所有采集器 mock 为失败
- **预期**：退出码 2

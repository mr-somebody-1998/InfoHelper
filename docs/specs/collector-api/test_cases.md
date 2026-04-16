# API 客户端 — 测试用例

## 测试文件路径
`tests/collectors/test_api_client.py`

---

## arXiv 客户端

### TC-API-001: 成功获取 arXiv 论文
- **输入**：query="cat:cs.AI"，API 返回 3 篇论文
- **预期**：返回 3 个 Article，title/url/content/published_at 正确

### TC-API-002: arXiv 增量采集
- **输入**：API 返回 5 篇论文，2 篇已在 dedup 中
- **预期**：返回 3 篇新论文

### TC-API-003: arXiv 查询无结果
- **输入**：API 返回空结果集
- **预期**：返回空列表

### TC-API-004: arXiv API 超时
- **输入**：模拟请求超时
- **预期**：返回空列表，记录 error

### TC-API-005: arXiv 论文无 summary
- **输入**：某篇论文无 summary 字段
- **预期**：Article.content 为空字符串

---

## YouTube 客户端

### TC-API-101: 成功获取频道最新视频
- **输入**：channel_id 有效，返回 2 个视频
- **预期**：返回 2 个 Article，url 为 YouTube 视频链接

### TC-API-102: YouTube 增量采集
- **输入**：返回 3 个视频，1 个已在 dedup 中
- **预期**：返回 2 个新视频

### TC-API-103: YouTube API key 未配置
- **输入**：环境变量 YOUTUBE_API_KEY 未设置
- **预期**：跳过所有 youtube 源，记录 warning

### TC-API-104: YouTube 频道无新视频
- **输入**：API 返回空列表
- **预期**：返回空列表

### TC-API-105: YouTube API 429 限流
- **输入**：API 返回 429 状态码
- **预期**：返回空列表，记录 error

---

## APICollector 整体

### TC-API-201: 未知 API type
- **输入**：type 为 "unknown_api"
- **预期**：跳过该源，记录 error

### TC-API-202: 混合 API 源采集
- **输入**：配置含 1 个 arxiv + 1 个 youtube
- **预期**：返回两个源的文章合集

### TC-API-203: 配置为空
- **输入**：apis 为 `[]`
- **预期**：返回空列表

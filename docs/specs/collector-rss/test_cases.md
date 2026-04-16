# RSS 采集器 — 测试用例

## 测试文件路径
`tests/collectors/test_rss.py`

## Fixtures

```python
SAMPLE_RSS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Test Feed</title>
    <item>
      <title>Article 1</title>
      <link>https://example.com/article-1</link>
      <description>Summary of article 1</description>
      <pubDate>Wed, 16 Apr 2026 10:00:00 GMT</pubDate>
    </item>
    <item>
      <title>Article 2</title>
      <link>https://example.com/article-2</link>
      <description>Summary of article 2</description>
      <pubDate>Wed, 16 Apr 2026 11:00:00 GMT</pubDate>
    </item>
  </channel>
</rss>"""

SAMPLE_SOURCE_CONFIG = {
    "name": "Test Feed",
    "url": "https://example.com/feed.xml",
    "category": "ai",
    "priority": "high"
}
```

---

## 正常路径

### TC-RSS-001: 成功采集单个 RSS 源
- **输入**：有效 RSS 源，包含 2 篇新文章
- **预期**：返回 2 个 Article 对象，字段正确填充
- **验证**：title、url、source、category、priority、published_at 均正确

### TC-RSS-002: 成功采集多个 RSS 源
- **输入**：配置 3 个 RSS 源，各有 1-3 篇文章
- **预期**：返回所有源的文章合集
- **验证**：总数 = 各源文章数之和

### TC-RSS-003: 增量采集 — 跳过已处理文章
- **输入**：RSS 源有 3 篇文章，其中 1 篇 URL 已在 dedup 中
- **预期**：返回 2 篇新文章
- **验证**：已处理的 URL 不在结果中

### TC-RSS-004: 解析 Atom 格式 feed
- **输入**：Atom 格式的 feed XML
- **预期**：正确解析为 Article 对象
- **验证**：feedparser 兼容 Atom，字段正确映射

### TC-RSS-005: priority 字段默认值
- **输入**：源配置中未设置 priority
- **预期**：Article.priority 为 "normal"

### TC-RSS-006: 正确解析发布时间
- **输入**：entry 含 published_parsed 字段
- **预期**：Article.published_at 为对应的 datetime 对象

---

## 异常路径

### TC-RSS-101: 网络超时
- **输入**：模拟请求超时
- **预期**：该源返回空列表，记录 error 日志，不影响其他源

### TC-RSS-102: HTTP 4xx/5xx 响应
- **输入**：模拟 RSS 源返回 404
- **预期**：该源返回空列表，记录 error 日志

### TC-RSS-103: RSS 源返回空 feed
- **输入**：有效 XML 但无 entry
- **预期**：返回空列表，记录 warning

### TC-RSS-104: entry 缺少 title
- **输入**：entry 无 title 字段
- **预期**：跳过该条目，记录 warning

### TC-RSS-105: entry 缺少 link
- **输入**：entry 无 link 字段
- **预期**：跳过该条目，记录 warning

### TC-RSS-106: entry 无 content 和 summary
- **输入**：entry 仅有 title 和 link
- **预期**：Article.content 为空字符串，不跳过

### TC-RSS-107: entry 无发布时间
- **输入**：entry 无 published_parsed 和 updated_parsed
- **预期**：Article.published_at 使用当前时间

### TC-RSS-108: 配置为空列表
- **输入**：sources.yaml 中 rss 为空列表
- **预期**：返回空列表，无报错

### TC-RSS-109: 单条 entry 解析失败不影响其他
- **输入**：3 条 entry，第 2 条数据异常
- **预期**：返回第 1、3 条，第 2 条跳过并记录日志

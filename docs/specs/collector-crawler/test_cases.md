# 网页爬虫 — 测试用例

## 测试文件路径
`tests/collectors/test_crawler.py`

## Fixtures

```python
SAMPLE_LIST_HTML = """
<div class="article-list">
  <a href="/article/1"><h2>Article Title 1</h2></a>
  <a href="/article/2"><h2>Article Title 2</h2></a>
</div>
"""

SAMPLE_ARTICLE_HTML = """
<article>
  <h1>Article Title 1</h1>
  <div class="content"><p>Article body content here.</p></div>
</article>
"""

SAMPLE_CRAWLER_CONFIG = {
    "name": "Test Site",
    "url": "https://example.com/articles",
    "parser": "test_parser",
    "category": "economics",
    "access": "public"
}
```

---

## 正常路径

### TC-CRW-001: 成功采集单个爬虫源
- **输入**：有效网站，列表页含 2 篇文章
- **预期**：返回 2 个 Article 对象，正文已提取

### TC-CRW-002: 增量采集 — 跳过已处理文章
- **输入**：列表页含 3 篇文章，1 篇已在 dedup 中
- **预期**：返回 2 篇新文章

### TC-CRW-003: 多爬虫源并行采集
- **输入**：配置 3 个爬虫源
- **预期**：返回所有源的文章合集

### TC-CRW-004: Parser 正确分发
- **输入**：两个源使用不同 parser 名称
- **预期**：各源使用对应的 Parser 类解析

### TC-CRW-005: 请求间隔控制
- **输入**：同一站点有多篇文章需要抓取详情页
- **预期**：相邻请求间隔 >= 2s

---

## 异常路径

### TC-CRW-101: 网络超时
- **输入**：模拟请求超时
- **预期**：该源返回空列表，记录 error，其他源不受影响

### TC-CRW-102: HTTP 404 响应
- **输入**：列表页返回 404
- **预期**：该源返回空列表，记录 error

### TC-CRW-103: 未知 parser 名称
- **输入**：sources.yaml 中 parser 值不匹配任何 Parser 类
- **预期**：跳过该源，记录 error

### TC-CRW-104: 列表页解析失败
- **输入**：HTML 结构与 Parser 预期不匹配
- **预期**：返回空列表，记录 error

### TC-CRW-105: 详情页获取失败
- **输入**：列表页正常，某篇文章详情页 500
- **预期**：跳过该文章，其他文章正常返回

### TC-CRW-106: auth_required 源自动跳过
- **输入**：access 为 auth_required 的源
- **预期**：跳过该源，记录 info 日志

### TC-CRW-107: 登录重定向检测
- **输入**：详情页 302 重定向到登录页
- **预期**：跳过该文章，记录 warning

### TC-CRW-108: 正文提取为空
- **输入**：详情页存在但正文区域为空
- **预期**：Article.content 为空字符串，不跳过

### TC-CRW-109: 配置为空列表
- **输入**：crawlers 为 `[]`
- **预期**：返回空列表，无报错

---

## BaseParser 基类测试

### TC-CRW-201: 子类未实现 parse_list_page
- **预期**：调用时抛出 NotImplementedError

### TC-CRW-202: 子类未实现 parse_article_page
- **预期**：调用时抛出 NotImplementedError

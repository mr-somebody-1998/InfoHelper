# Claude 分析器 — 测试用例

## 测试文件路径
`tests/processors/test_analyzer.py`

## 说明
Claude API 调用使用 mock，不发送真实请求。测试重点在于：prompt 构建、响应解析、错误处理。

## Fixtures

```python
SAMPLE_ARTICLE = Article(
    title="Fed Holds Rates Steady",
    url="https://example.com/fed-rates",
    content="The Federal Reserve held interest rates steady at 5.25%...",
    source="Morgan Stanley Ideas",
    category="economics",
    priority="high",
    published_at=datetime(2026, 4, 16, 10, 0),
    raw_html=None
)

SAMPLE_CLAUDE_RESPONSE = """
## 核心摘要
美联储维持利率不变在 5.25%，符合市场预期。

## 关键数据
- 联邦基金利率：5.25%
- 通胀率：2.8%

## 结构化分析
从货币政策周期来看...

## 关联背景
上月 CPI 数据显示通胀有所回落...

## 重要程度
高
"""
```

---

## 正常路径

### TC-ANL-001: 成功分析单篇文章
- **输入**：1 篇有效 Article
- **预期**：返回 AnalyzedArticle，各字段正确填充
- **验证**：summary、key_data、analysis、importance 均非空

### TC-ANL-002: 批量分析多篇文章
- **输入**：3 篇 Article
- **预期**：返回 3 个 AnalyzedArticle
- **验证**：Claude API 被调用 3 次

### TC-ANL-003: system prompt 正确加载 maqianzu-skill
- **输入**：skills/maqianzu-skill/ 文件存在
- **预期**：system prompt 包含 SOUL.md 和 SKILL.md 内容
- **验证**：mock Claude API 调用时检查 system 参数

### TC-ANL-004: 响应解析 — 完整格式
- **输入**：Claude 返回标准格式的 Markdown
- **预期**：各字段正确提取到 AnalyzedArticle 对应属性

### TC-ANL-005: ID 生成
- **输入**：Article.url = "https://example.com/test"
- **预期**：AnalyzedArticle.id 为 URL 的确定性 hash
- **验证**：相同 URL 生成相同 ID

### TC-ANL-006: processed_at 时间戳
- **输入**：分析完成
- **预期**：processed_at 为分析时的当前时间

---

## 异常路径

### TC-ANL-101: API key 未配置
- **输入**：config 中无 api_key 且环境变量未设置
- **预期**：抛出 ConfigError

### TC-ANL-102: API 调用失败 — 网络错误
- **输入**：mock API 抛出连接异常
- **预期**：重试 2 次后跳过该文章，记录 error
- **验证**：API 共调用 3 次（1 + 2 重试）

### TC-ANL-103: API 限流 429
- **输入**：mock API 返回 429
- **预期**：等待后重试

### TC-ANL-104: 响应解析失败
- **输入**：Claude 返回非预期格式的文本
- **预期**：整个响应作为 analysis 字段，summary/key_data 为空

### TC-ANL-105: maqianzu-skill 文件不存在
- **输入**：skills/maqianzu-skill/ 目录不存在
- **预期**：使用 fallback prompt，记录 warning，分析仍正常

### TC-ANL-106: 文章 content 为空
- **输入**：Article.content = ""
- **预期**：基于 title 分析，记录 warning

### TC-ANL-107: 输入空列表
- **输入**：articles = []
- **预期**：返回空列表，不调用 API

### TC-ANL-108: 超长文章内容
- **输入**：content 长度 > 100K 字符
- **预期**：截断后发送，不报错

---

## 响应解析专项

### TC-ANL-201: 解析 — 重要程度为中文
- **输入**：响应中 "## 重要程度\n高"
- **预期**：importance = "high"

### TC-ANL-202: 解析 — 关键数据为列表
- **输入**：响应中含 bullet list
- **预期**：key_data 为字符串列表

### TC-ANL-203: 解析 — 缺少某个段落
- **输入**：响应中无"关联背景"段落
- **预期**：related_context 为空字符串，其他字段正常

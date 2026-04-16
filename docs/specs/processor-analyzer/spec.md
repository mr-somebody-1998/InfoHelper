# Claude 分析器 — 需求规格

## 模块路径
`src/processors/analyzer.py`

## 功能描述
接收采集到的 Article 列表，调用 Claude API 并加载 maqianzu-skill 分析框架，对每篇文章进行结构化摘要与深度分析，输出 AnalyzedArticle。

## 依赖
- `anthropic` — Anthropic Python SDK
- `skills/maqianzu-skill/` — 分析框架（SOUL.md、SKILL.md、prompts/）
- `src/utils/config.py` — 读取 config.yaml 中的 claude 配置
- `config/prompts/summary.txt` — 摘要分析 Prompt 模板

## 输入
`list[Article]` — 采集器输出的文章列表

## 输出
`list[AnalyzedArticle]`：

```python
@dataclass
class AnalyzedArticle:
    # 继承 Article 所有字段
    title: str
    url: str
    content: str
    source: str
    category: str
    priority: str
    published_at: datetime
    raw_html: str | None
    # 分析结果字段
    id: str                 # 唯一 ID（基于 URL 的 hash）
    summary: str            # 核心摘要（2-3 句）
    key_data: list[str]     # 关键数据点
    analysis: str           # 结构化分析
    related_context: str    # 关联背景
    importance: str         # 重要程度：high / medium / low
    processed_at: datetime  # 处理时间
```

## 核心逻辑

### 1. 加载分析框架
启动时一次性加载 maqianzu-skill 相关文件：
- `skills/maqianzu-skill/SOUL.md`
- `skills/maqianzu-skill/SKILL.md`
- `skills/maqianzu-skill/prompts/` 下的分析 prompt（如有）

拼接为 system prompt。若 maqianzu-skill 文件不存在，使用内置的 fallback system prompt。

### 2. 逐篇分析
对每篇 Article：
1. 构造 messages：将 summary prompt 模板 + article.content 作为 user message
2. 调用 `client.messages.create()`，传入 system prompt + messages
3. 解析 Claude 返回的结构化 Markdown，提取各字段
4. 构造 AnalyzedArticle

### 3. 响应解析
Claude 返回的 Markdown 需解析为结构化字段：
- 使用正则或 Markdown 标题匹配提取各段落
- 若解析失败，将整个响应作为 `analysis` 字段，其他字段留空

### 4. 并发控制
- 默认串行处理（避免 API 限流）
- 可配置并发数（默认 1）
- 两次 API 调用间隔 >= 1s

## 公开接口

```python
class Analyzer:
    def __init__(self, config: dict):
        """
        config 为 config.yaml 中的 claude 部分
        自动加载 maqianzu-skill 分析框架
        """

    def analyze(self, articles: list[Article]) -> list[AnalyzedArticle]:
        """批量分析文章"""

    def analyze_one(self, article: Article) -> AnalyzedArticle:
        """分析单篇文章"""

    def _build_system_prompt(self) -> str:
        """构建 system prompt（maqianzu-skill + 自定义）"""

    def _parse_response(self, response_text: str) -> dict:
        """解析 Claude 响应为结构化字段"""
```

## 配置项（config.yaml）
```yaml
claude:
  api_key: ${CLAUDE_API_KEY}
  model: claude-sonnet-4-20250514
  max_tokens: 2048
```

## 错误处理
- API key 无效/未配置：启动时抛出 ConfigError
- API 调用失败（网络/5xx）：重试 2 次，仍失败则跳过该文章，记录 error
- API 限流（429）：等待 retry-after 时间后重试
- Claude 返回内容无法解析：整个响应作为 analysis，其他字段为空字符串/空列表
- maqianzu-skill 文件不存在：使用 fallback prompt，记录 warning
- 文章 content 为空：仅基于 title 分析，记录 warning

## 边界条件
- 输入空列表：返回空列表
- 文章内容超长（> 100K 字符）：截断至模型上下文限制
- 非中文内容（英文文章）：Claude 自动适应语言

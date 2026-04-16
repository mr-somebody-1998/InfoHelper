# RSS 采集器 — 需求规格

## 模块路径
`src/collectors/rss.py`

## 功能描述
从配置的 RSS/Atom 订阅源中获取最新文章，解析为标准化的 Article 数据结构，支持增量采集（跳过已处理的文章）。

## 依赖
- `feedparser` — RSS/Atom 解析
- `src/utils/config.py` — 读取 sources.yaml 中的 rss 配置
- `src/utils/dedup.py` — 去重判断

## 输入
- `sources.yaml` 中 `rss` 列表，每项包含：
  - `name: str` — 源名称
  - `url: str` — RSS 订阅地址
  - `category: str` — 分类（ai / economics）
  - `priority: str` — 优先级（high / normal），可选，默认 normal

## 输出
`list[Article]`，每个 Article 包含：

```python
@dataclass
class Article:
    title: str              # 文章标题
    url: str                # 原文链接
    content: str            # 正文内容（或摘要）
    source: str             # 来源名称
    category: str           # 分类
    priority: str           # 优先级
    published_at: datetime  # 发布时间
    raw_html: str | None    # 原始 HTML（如有）
```

## 核心逻辑

### 1. 加载配置
从 `sources.yaml` 读取所有 `rss` 类型的信息源。

### 2. 逐源采集
对每个 RSS 源：
1. 使用 `feedparser.parse(url)` 解析
2. 遍历 `feed.entries`，提取 title、link、summary/content、published
3. 调用 `dedup.is_duplicate(url)` 判断是否已处理
4. 未处理的条目构造为 `Article` 对象

### 3. 错误处理
- 网络超时：单个源超时（默认 30s）后跳过，记录日志，不影响其他源
- 解析失败：单条 entry 解析失败时跳过，记录日志
- 空 feed：返回空列表，记录 warning

### 4. 发布时间解析
- 优先使用 `entry.published_parsed`
- 若缺失，使用 `entry.updated_parsed`
- 若都缺失，使用当前时间作为 fallback

## 公开接口

```python
class RSSCollector:
    def __init__(self, config: dict):
        """config 为 sources.yaml 中的 rss 列表"""

    def collect(self) -> list[Article]:
        """采集所有 RSS 源，返回去重后的新文章列表"""

    def collect_source(self, source: dict) -> list[Article]:
        """采集单个 RSS 源"""
```

## 边界条件
- RSS 源返回 HTTP 4xx/5xx：跳过该源，记录错误
- RSS 源返回空内容：返回空列表
- entry 缺少 title 或 link：跳过该条目
- entry.content 和 entry.summary 都为空：保留该条目但 content 为空字符串
- 配置中无 rss 项：返回空列表，不报错
- URL 包含特殊字符或编码：feedparser 内部处理

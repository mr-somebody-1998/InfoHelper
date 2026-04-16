# API 客户端 — 需求规格

## 模块路径
`src/collectors/api_client.py`

## 功能描述
对接提供开放 API 的数据源（arXiv、YouTube Data API），通过 API 请求获取最新内容并转化为标准 Article 数据结构。

## 依赖
- `requests` — HTTP 请求
- `src/utils/config.py` — 读取 sources.yaml 中的 apis 配置
- `src/utils/dedup.py` — 去重判断

## 输入
`sources.yaml` 中 `apis` 列表，每项包含：
- `name: str` — 源名称
- `type: str` — API 类型（arxiv / youtube）
- `category: str` — 分类
- `priority: str` — 优先级，可选，默认 normal
- 类型特有字段：
  - arxiv: `query: str` — 搜索查询（如 "cat:cs.AI"）
  - youtube: `channel_id: str` — YouTube 频道 ID

## 输出
`list[Article]` — 标准 Article 数据结构

## 核心设计

### API 客户端基类

```python
class BaseAPIClient:
    """API 客户端基类"""

    def fetch(self, config: dict) -> list[Article]:
        """获取文章列表"""
        raise NotImplementedError
```

### arXiv 客户端

```python
class ArxivClient(BaseAPIClient):
    """arXiv API 客户端"""
    BASE_URL = "http://export.arxiv.org/api/query"

    def fetch(self, config: dict) -> list[Article]:
        """
        调用 arXiv API，参数：
        - search_query: config["query"]
        - sortBy: lastUpdatedDate
        - max_results: 20（可配置）
        解析 Atom XML 响应，提取 title、link、summary、published
        """
```

### YouTube 客户端

```python
class YouTubeClient(BaseAPIClient):
    """YouTube Data API v3 客户端"""
    BASE_URL = "https://www.googleapis.com/youtube/v3"

    def fetch(self, config: dict) -> list[Article]:
        """
        1. 调用 search.list 获取频道最新视频
           - channelId: config["channel_id"]
           - order: date
           - maxResults: 10
        2. 调用 videos.list 获取视频详情（description）
        3. Article.content = 视频描述
        4. Article.url = https://youtube.com/watch?v={videoId}
        """
```

### APICollector 类

```python
class APICollector:
    def __init__(self, config: list[dict]):
        """config 为 sources.yaml 中的 apis 列表"""

    def collect(self) -> list[Article]:
        """采集所有 API 源"""

    def _get_client(self, api_type: str) -> BaseAPIClient:
        """根据 type 字段返回对应客户端"""
```

## 错误处理
- API 请求失败（网络/超时）：跳过该源，记录 error
- API 返回错误码（403 / 429 rate limit）：跳过该源，记录 error
- 响应格式异常：跳过该源，记录 error
- YouTube API key 未配置：跳过 youtube 类型源，记录 warning
- 未知 API type：跳过，记录 error

## 边界条件
- arXiv 查询无结果：返回空列表
- YouTube 频道无新视频：返回空列表
- 配置中 apis 为空：返回空列表
- arXiv 返回的论文无 summary：content 为空字符串

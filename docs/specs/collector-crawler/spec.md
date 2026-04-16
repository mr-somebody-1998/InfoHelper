# 网页爬虫 — 需求规格

## 模块路径
`src/collectors/crawler.py`

## 功能描述
针对无 RSS 输出的网站，通过 HTTP 请求抓取网页内容，使用站点特定的解析器（Parser）提取文章信息。每个目标站点有独立的 Parser 类，统一继承基类。

## 依赖
- `requests` — HTTP 请求
- `beautifulsoup4` — HTML 解析
- `src/utils/config.py` — 读取 sources.yaml 中的 crawlers 配置
- `src/utils/dedup.py` — 去重判断

## 输入
`sources.yaml` 中 `crawlers` 列表，每项包含：
- `name: str` — 源名称
- `url: str` — 目标网站 URL
- `parser: str` — 解析器名称（对应 Parser 类）
- `category: str` — 分类
- `access: str` — 访问级别（public / auth_required / partial）

## 输出
`list[Article]` — 与 RSS 采集器相同的 Article 数据结构

## 核心设计

### Parser 基类

```python
class BaseParser:
    """所有站点解析器的基类"""

    name: str  # 解析器名称，与 sources.yaml 中 parser 字段匹配

    def parse_list_page(self, html: str) -> list[dict]:
        """解析列表页，返回文章元数据列表 [{title, url, published_at}]"""
        raise NotImplementedError

    def parse_article_page(self, html: str) -> str:
        """解析文章详情页，返回正文文本"""
        raise NotImplementedError
```

### 站点解析器（首批实现）

| Parser 类 | 对应站点 | parser 名称 |
|-----------|---------|------------|
| MorganStanleyParser | morganstanley.com/ideas | morgan_stanley |
| GoldmanSachsParser | goldmansachs.com/insights | goldman_sachs |
| NomuraParser | nicmr.com/en/report.html | nomura |
| CitiParser | citigroup.com/global/insights | citi |
| UBSParser | ubs.com/.../global-research | ubs |
| BarclaysParser | ib.barclays/research | barclays |
| CF40Parser | cf40.org.cn | cf40 |
| RhodiumParser | rhg.com/research | rhodium |
| WallstreetcnParser | wallstreetcn.com | wallstreetcn |
| CaixinParser | caixin.com | caixin |

### CrawlerCollector 类

```python
class CrawlerCollector:
    def __init__(self, config: list[dict]):
        """config 为 sources.yaml 中的 crawlers 列表"""

    def collect(self) -> list[Article]:
        """采集所有爬虫源，返回去重后的新文章列表"""

    def collect_source(self, source: dict) -> list[Article]:
        """采集单个爬虫源"""

    def _get_parser(self, parser_name: str) -> BaseParser:
        """根据 parser 名称查找对应的 Parser 类"""

    def _fetch_page(self, url: str) -> str:
        """发起 HTTP 请求，返回 HTML 文本"""
```

### 采集流程
1. 根据 `parser` 名称查找对应的 Parser 类
2. `_fetch_page(url)` 获取列表页 HTML
3. `parser.parse_list_page(html)` 提取文章元数据列表
4. 对每篇文章：调用 `dedup.is_duplicate(url)` 去重
5. 新文章：`_fetch_page(article_url)` 获取详情页 → `parser.parse_article_page(html)` 提取正文
6. 构造 Article 对象返回

## HTTP 请求策略
- 超时：30s
- 请求间隔：同一站点请求间隔 >= 2s
- User-Agent：从预设列表中随机选取
- 遵守 robots.txt：首次访问站点时检查
- access 为 `auth_required` 的源：跳过采集，记录 info 日志（未来支持登录凭证）

## 错误处理
- 网络错误/超时：跳过该源，记录 error，不影响其他源
- HTTP 4xx/5xx：跳过该源，记录 error
- 解析失败（HTML 结构变化）：跳过该条目，记录 error
- 未知 parser 名称：跳过该源，记录 error
- 正文提取为空：保留该条目但 content 为空字符串

## 边界条件
- 列表页无文章：返回空列表
- 详情页跳转到登录页：检测到登录重定向时跳过，记录 warning
- 站点临时不可用：跳过，记录 error
- 配置中 crawlers 为空：返回空列表

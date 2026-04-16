# 知识存储模块 — 需求规格

## 模块路径
`src/storage/knowledge.py`

## 功能描述
将分析完成的 AnalyzedArticle 持久化存储到两个介质：
1. **SQLite** — 结构化索引，支持查询、去重、状态管理
2. **Markdown 文件** — 按日期和主题归档到 knowledge/ 目录，便于人工浏览

## 依赖
- `sqlite3` — 标准库
- `src/utils/config.py` — 读取 storage 配置

## 输入
`list[AnalyzedArticle]` — 分析器输出

## 数据库设计

### articles 表

```sql
CREATE TABLE IF NOT EXISTS articles (
    id TEXT PRIMARY KEY,            -- URL hash
    title TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    source TEXT NOT NULL,
    category TEXT NOT NULL,
    subcategory TEXT DEFAULT '',
    priority TEXT DEFAULT 'normal',
    importance TEXT DEFAULT 'medium',
    summary TEXT DEFAULT '',
    key_data TEXT DEFAULT '[]',     -- JSON 数组
    analysis TEXT DEFAULT '',
    related_context TEXT DEFAULT '',
    content TEXT DEFAULT '',
    published_at TEXT NOT NULL,     -- ISO 8601
    processed_at TEXT NOT NULL,     -- ISO 8601
    read INTEGER DEFAULT 0,         -- 0=未读, 1=已读
    created_at TEXT NOT NULL        -- 入库时间
);

CREATE INDEX idx_category ON articles(category);
CREATE INDEX idx_published ON articles(published_at);
CREATE INDEX idx_read ON articles(read);
CREATE INDEX idx_importance ON articles(importance);
```

## Markdown 归档结构

```
knowledge/
├── daily/
│   └── 2026-04-16.md       # 当日所有文章摘要
├── topics/
│   ├── economics/
│   │   └── macro.md         # 追加模式
│   └── ai/
│       └── models.md        # 追加模式
├── catalog.json             # 全量索引
└── index.md                 # 导航页（自动生成）
```

### daily/{date}.md 格式

```markdown
# 2026-04-16 信息汇总

## [high] Fed Holds Rates Steady
- **来源**: Morgan Stanley Ideas
- **分类**: economics / macro
- **摘要**: 美联储维持利率不变...
- **关键数据**: 联邦基金利率 5.25%, 通胀率 2.8%
- **分析**: 从货币政策周期来看...
- [原文链接](https://...)

---

## [medium] New GPT-5 Details
...
```

### topics/{category}/{subcategory}.md 格式
追加写入模式，每次新增文章追加到文件末尾：

```markdown
# AI 模型

## 2026-04-16 | GPT-5 Training Details
- **来源**: Karpathy Blog
- **摘要**: ...
- [原文链接](https://...)

## 2026-04-15 | Claude 4 Benchmark Results
...
```

### catalog.json 格式

```json
[
    {
        "id": "a1b2c3",
        "title": "文章标题",
        "category": "economics",
        "subcategory": "macro",
        "date": "2026-04-16",
        "daily_file": "daily/2026-04-16.md",
        "topic_file": "topics/economics/macro.md"
    }
]
```

## 公开接口

```python
class KnowledgeStore:
    def __init__(self, config: dict):
        """
        config 为 config.yaml 中的 storage 部分
        初始化 SQLite 连接，确保表存在
        确保 knowledge/ 目录结构存在
        """

    def save(self, articles: list[AnalyzedArticle]) -> int:
        """
        保存文章：写入 SQLite + 生成 Markdown
        返回实际新增数量（跳过已存在的）
        """

    def query(self,
              category: str | None = None,
              subcategory: str | None = None,
              date: str | None = None,
              priority: str | None = None,
              importance: str | None = None,
              unread_only: bool = False,
              limit: int = 50) -> list[dict]:
        """查询文章，返回字典列表"""

    def mark_read(self, article_ids: list[str]) -> int:
        """标记已读，返回实际更新数量"""

    def get_by_id(self, article_id: str) -> dict | None:
        """按 ID 获取单篇文章"""

    def _write_daily_markdown(self, article: AnalyzedArticle) -> None:
        """写入 daily/{date}.md"""

    def _write_topic_markdown(self, article: AnalyzedArticle) -> None:
        """追加写入 topics/{category}/{subcategory}.md"""

    def _update_catalog(self, article: AnalyzedArticle) -> None:
        """更新 catalog.json"""

    def _generate_index(self) -> None:
        """重新生成 index.md 导航页"""
```

## 错误处理
- SQLite 文件不存在：自动创建
- 文章 ID 重复（已存在）：跳过，记录 debug
- Markdown 目录不存在：自动创建
- catalog.json 损坏：备份后重新从 SQLite 生成
- 磁盘空间不足：抛出异常，由调用方处理

## 边界条件
- 输入空列表：返回 0，不写入任何文件
- 同一文章重复保存：幂等，不产生重复记录
- 查询无结果：返回空列表
- mark_read 传入不存在的 ID：忽略，返回实际更新数
- 并发写入：SQLite 使用 WAL 模式，支持读写并发

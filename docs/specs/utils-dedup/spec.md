# 去重模块 — 需求规格

## 模块路径
`src/utils/dedup.py`

## 功能描述
基于 SQLite 存储已处理文章的指纹（URL），提供快速去重判断。支持 URL 精确匹配和标题相似度匹配两种策略。

## 依赖
- `sqlite3` — 标准库
- `hashlib` — URL hash 计算

## 数据库设计

```sql
CREATE TABLE IF NOT EXISTS fingerprints (
    url_hash TEXT PRIMARY KEY,      -- URL 的 SHA256 前 16 位
    url TEXT NOT NULL,
    title TEXT DEFAULT '',
    created_at TEXT NOT NULL         -- ISO 8601
);

CREATE INDEX idx_title ON fingerprints(title);
```

共用 `config.yaml` 中 `storage.db_path` 指定的 SQLite 文件。

## 公开接口

```python
class Deduplicator:
    def __init__(self, db_path: str):
        """连接 SQLite，确保 fingerprints 表存在"""

    def is_duplicate(self, url: str, title: str = "") -> bool:
        """
        判断是否重复：
        1. URL hash 精确匹配 → True
        2. title 非空且与已有记录相似度 > 0.85 → True
        3. 否则 → False
        """

    def register(self, url: str, title: str = "") -> None:
        """注册已处理的文章指纹"""

    def register_batch(self, items: list[tuple[str, str]]) -> None:
        """批量注册 [(url, title), ...]"""

    def _url_hash(self, url: str) -> str:
        """URL → SHA256 前 16 位"""

    def _title_similarity(self, a: str, b: str) -> float:
        """标题相似度计算（基于字符级别的序列匹配）"""
```

## 标题相似度
使用 `difflib.SequenceMatcher` 计算，阈值 0.85。仅在 URL 不匹配时作为补充检测。

## 错误处理
- SQLite 文件不存在：自动创建
- 重复 register 同一 URL：幂等，不报错（INSERT OR IGNORE）

## 边界条件
- url 为空字符串：返回 False（不算重复）
- title 为空：仅做 URL 去重
- URL 含 query 参数差异（如 utm_source）：按原始 URL 匹配，不做归一化

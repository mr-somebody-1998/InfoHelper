from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Article:
    """采集器输出的原始文章"""

    title: str
    url: str
    content: str
    source: str
    category: str
    priority: str = "normal"
    published_at: datetime = field(default_factory=datetime.now)
    raw_html: str | None = None


@dataclass
class AnalyzedArticle:
    """分析器输出的已分析文章"""

    # 原始文章字段
    title: str
    url: str
    content: str
    source: str
    category: str
    priority: str
    published_at: datetime
    raw_html: str | None
    # 分析结果字段
    id: str
    summary: str = ""
    key_data: list[str] = field(default_factory=list)
    analysis: str = ""
    related_context: str = ""
    importance: str = "medium"
    subcategory: str = ""
    processed_at: datetime = field(default_factory=datetime.now)
    read: bool = False


@dataclass
class ClassificationResult:
    """分类结果"""

    category: str
    subcategory: str

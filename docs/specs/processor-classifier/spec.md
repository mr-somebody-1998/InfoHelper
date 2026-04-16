# 分类器 — 需求规格

## 模块路径
`src/processors/classifier.py`

## 功能描述
对文章进行主分类和子分类，可通过 Claude API 调用实现，也可对简单场景使用规则匹配（基于来源和关键词）。

## 依赖
- `anthropic` — Anthropic Python SDK（LLM 分类时）
- `src/utils/config.py`
- `config/prompts/classify.txt` — 分类 Prompt 模板

## 输入
`Article` 或 `AnalyzedArticle`（至少包含 title、content、source、category）

## 输出
更新文章的分类字段：

```python
@dataclass
class ClassificationResult:
    category: str       # 主分类：economics / ai
    subcategory: str    # 子分类
```

### 分类体系

| 主分类 | 子分类 |
|--------|--------|
| economics | macro（宏观经济）|
| economics | policy（货币政策）|
| economics | industry（产业动态）|
| economics | earnings（公司财报）|
| ai | models（AI 模型）|
| ai | applications（AI 应用）|
| ai | policy（AI 政策）|
| ai | investment（AI 投融资）|

## 核心设计

### 两级分类策略

**Level 1：规则分类（快速，零成本）**
- 基于 `source` 的 `category` 配置确定主分类
- 基于关键词匹配确定子分类

```python
KEYWORD_MAP = {
    "macro": ["GDP", "通胀", "inflation", "PMI", "就业", "unemployment"],
    "policy": ["利率", "interest rate", "央行", "Fed", "货币政策"],
    "industry": ["产业", "行业", "市场份额", "supply chain"],
    "earnings": ["财报", "营收", "revenue", "profit", "earnings"],
    "models": ["GPT", "LLM", "模型", "transformer", "training"],
    "applications": ["应用", "deploy", "产品", "agent", "copilot"],
    "ai_policy": ["监管", "regulation", "AI安全", "alignment"],
    "investment": ["融资", "估值", "valuation", "funding", "IPO"],
}
```

**Level 2：LLM 分类（精确，需 API 调用）**
- 当规则分类置信度低（关键词命中 < 2）时，调用 Claude API
- 使用 `config/prompts/classify.txt` 模板

### Classifier 类

```python
class Classifier:
    def __init__(self, config: dict):
        """config 为 config.yaml 中的 claude 部分"""

    def classify(self, article: Article) -> ClassificationResult:
        """分类单篇文章"""

    def classify_batch(self, articles: list[Article]) -> list[ClassificationResult]:
        """批量分类"""

    def _rule_classify(self, article: Article) -> ClassificationResult | None:
        """规则分类，返回 None 表示置信度不足"""

    def _llm_classify(self, article: Article) -> ClassificationResult:
        """LLM 分类"""
```

## 错误处理
- LLM 返回不在预定义分类中的值：fallback 到 article 原始 category，subcategory 为 "other"
- LLM 调用失败：使用规则分类结果，若规则也无法判断则使用原始 category
- 文章 title 和 content 都为空：使用原始 category

## 边界条件
- 英文内容：关键词表包含中英文
- 跨领域文章（如 AI 投融资）：以主要内容判断
- 输入空列表：返回空列表

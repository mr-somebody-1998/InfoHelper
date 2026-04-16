# Implementation Plan

## Task List

- [ ] T1: 项目脚手架 — 数据模型 + 配置加载 + 去重模块
  - spec: `docs/specs/utils-config/spec.md`, `docs/specs/utils-dedup/spec.md`
  - 创建 `src/models.py`（Article, AnalyzedArticle, ClassificationResult 数据类）
  - 创建 `src/utils/config.py`（Config 类）
  - 创建 `src/utils/dedup.py`（Deduplicator 类）
  - 创建 `requirements.txt`
  - 创建 `config/config.yaml` 和 `config/sources.yaml` 模板
  - 创建 `config/prompts/summary.txt` 和 `config/prompts/classify.txt`
  - 测试: `tests/utils/test_config.py`, `tests/utils/test_dedup.py`

- [ ] T2: RSS 采集器
  - spec: `docs/specs/collector-rss/spec.md`
  - 创建 `src/collectors/rss.py`（RSSCollector 类）
  - 测试: `tests/collectors/test_rss.py`

- [ ] T3: 网页爬虫框架
  - spec: `docs/specs/collector-crawler/spec.md`
  - 创建 `src/collectors/crawler.py`（BaseParser + CrawlerCollector）
  - 首批实现 2-3 个 Parser（如 CF40、Rhodium、WallstreetCN）
  - 测试: `tests/collectors/test_crawler.py`

- [ ] T4: API 客户端
  - spec: `docs/specs/collector-api/spec.md`
  - 创建 `src/collectors/api_client.py`（ArxivClient + YouTubeClient + APICollector）
  - 测试: `tests/collectors/test_api_client.py`

- [ ] T5: Claude 分析器
  - spec: `docs/specs/processor-analyzer/spec.md`
  - 创建 `src/processors/analyzer.py`（Analyzer 类）
  - 集成 maqianzu-skill 分析框架
  - 测试: `tests/processors/test_analyzer.py`

- [ ] T6: 分类器
  - spec: `docs/specs/processor-classifier/spec.md`
  - 创建 `src/processors/classifier.py`（Classifier 类）
  - 测试: `tests/processors/test_classifier.py`

- [ ] T7: 知识存储模块
  - spec: `docs/specs/storage/spec.md`
  - 创建 `src/storage/knowledge.py`（KnowledgeStore 类）
  - 测试: `tests/storage/test_knowledge.py`

- [ ] T8: CLI 接口 + Python API
  - spec: `docs/specs/cli/spec.md`
  - 创建 `src/main.py`（InfoHelper 类 + CLI 命令）
  - 测试: `tests/test_main.py`

- [ ] T9: 端到端集成测试
  - 创建 `tests/test_integration.py`
  - 模拟完整流程：采集 → 分析 → 分类 → 存储 → 查询
  - 验证各模块串联正确

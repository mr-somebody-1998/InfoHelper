# InfoHelper 设计文档

## 1. 项目概述

### 1.1 项目定位
InfoHelper 是一个 AI 驱动的信息聚合与分析系统，自动采集经济和 AI 领域的高质量信息，通过大模型进行结构化摘要与分析，并以标准化格式存储到本地知识库，供外部程序定时调用和推送。

### 1.2 核心流程
```
信息源 (RSS/爬虫/API)
        ↓
    数据采集层
        ↓
    内容处理层 (Claude API 摘要+分析)
        ↓
    知识存储 (本地 Markdown 归档)
        ↓
    对外接口 (供外部程序调用读取)
```

### 1.3 技术栈
| 组件 | 技术选型 |
|------|---------|
| 开发语言 | Python 3.11+ |
| LLM | Claude API (Anthropic SDK) |
| RSS 解析 | feedparser |
| 网页爬虫 | requests + BeautifulSoup |
| 数据存储 | SQLite + Markdown |
| 配置管理 | YAML |
| 部署环境 | Mac Mini (本地运行) |

---

## 2. 系统架构

```
┌─────────────────────────────────────────────────┐
│                   InfoHelper                     │
├──────────────────┬──────────────────────────────┤
│    数据采集层     │       内容处理层              │
│                  │                              │
│  RSS Parser      │  Claude API                  │
│  Web Crawler     │  maqianzu-skill 分析框架      │
│  API Client      │  Classifier                  │
├──────────────────┴──────────────────────────────┤
│                 知识管理层                        │
│       (SQLite 索引 + Markdown 结构化存储)         │
├─────────────────────────────────────────────────┤
│                 对外接口层                        │
│    (CLI / Python API，供外部程序定时调用)          │
├─────────────────────────────────────────────────┤
│               配置管理 (YAML)                    │
└─────────────────────────────────────────────────┘
```

---

## 3. 数据采集模块

### 3.1 RSS 订阅源
使用 `feedparser` 解析 RSS/Atom 订阅源，定时轮询获取最新内容。

**预设信息源（可配置扩展）：**

#### AI 领域

| 来源 | 类型 | 获取方式 | 说明 |
|------|------|---------|------|
| Karpathy Blog | RSS | feedparser | karpathy.github.io + karpathy.bearblog.dev |
| Karpathy YouTube | API | YouTube Data API | AI 教程与深度讲解 (Zero to Hero 等) |
| Karpathy X/Twitter | 爬虫 | nitter/RSS bridge | 推文与短评，AI 前沿观点 |
| 机器之心 | RSS | feedparser | 中文 AI 资讯 |
| 量子位 | RSS | feedparser | 中文 AI 资讯 |
| Hacker News (AI) | RSS | feedparser | 英文技术社区 |
| arXiv cs.AI | API | arxiv API | AI 论文预印本 |

#### 经济/金融研报

| 来源 | 公开程度 | 获取方式 | 说明 |
|------|---------|---------|------|
| Morgan Stanley (大摩) | 部分公开 | RSS + 爬虫 | Ideas 页面有公开内容及 RSS，深度研报需机构账号 |
| Goldman Sachs (高盛) | 部分公开 | 爬虫 | gspublishing 有部分公开研究，深度需 Marquee 平台 |
| Nomura (野村) | 公开 | 爬虫 | 野村资本市场研究所报告免费公开 |
| Citi (花旗) | 部分公开 | RSS + 爬虫 | Citi Institute 公开，深度需 Citi Velocity |
| UBS (瑞银) | 部分公开 | RSS + 爬虫 | 有公开 Insights 和 RSS，深度需订阅 |
| Barclays (巴克莱) | 付费 | 爬虫 (需登录) | 需 Barclays Live 机构账号 |
| CF40 (中国金融四十人论坛) | 公开 | 爬虫 | 官网及公众号有公开研究内容 |
| Foreign Policy | 大部分公开 | RSS | 有 RSS 订阅，部分内容需订阅 |
| Cognizant | 公开 | RSS | 洞察报告免费公开，有 RSS |
| Rhodium Group (荣鼎) | 公开 | 爬虫 | 研究报告免费，ClimateDeck 需注册 |

#### 财经综合

| 来源 | 类型 | 获取方式 | 说明 |
|------|------|---------|------|
| 36氪 | RSS | feedparser | 中文科技财经 |
| 华尔街见闻 | 爬虫 | requests+BS4 | 中文财经资讯 |
| 财新 | 爬虫 | requests+BS4 | 中文深度财经 |

> **注意**：大摩、高盛、花旗、瑞银、巴克莱的深度研报受付费墙保护。系统优先采集其公开可获取的 Insights/Ideas 内容；如用户有机构账号，可配置登录凭证以获取完整研报。

### 3.2 网页爬虫
针对无 RSS 输出的网站，使用 `requests + BeautifulSoup` 进行内容抓取。

**设计要点：**
- 每个目标站点编写独立的解析器（Parser）
- 遵守 robots.txt，设置合理的请求间隔
- User-Agent 轮换，避免被封禁
- 提取标题、正文、发布时间、来源 URL

### 3.3 API 客户端
对接提供开放 API 的数据源（如 NewsAPI、arXiv API）。

### 3.4 去重机制
- 基于 URL 去重（精确匹配）
- 基于标题相似度去重（防止同一事件的不同报道重复推送）
- 使用 SQLite 存储已处理文章的指纹

---

## 4. 内容处理模块

### 4.1 maqianzu-skill 分析框架集成

内容分析的核心能力基于 [maqianzu-skill](https://github.com/4thfever/maqianzu-skill) 项目。该项目提供了一套可复现的结构化分析框架，包含：

- **SOUL.md** — 分析人格与稳定倾向定义
- **AGENTS.md** — 顶层执行协议
- **SKILL.md** — 内部分析模式入口
- **knowledge/** — 分层知识库（topics → episodes）
- **prompts/** — 分析框架、响应策略、检索工作流

**集成方式：**
将 maqianzu-skill 作为 Git submodule 引入项目，Claude API 调用时加载其 SOUL、SKILL 和 prompts 作为系统提示词，使分析输出具备结构化分析路径而非简单摘要。

```
InfoHelper/
├── skills/
│   └── maqianzu-skill/      # Git submodule → github.com/4thfever/maqianzu-skill
│       ├── SOUL.md
│       ├── AGENTS.md
│       ├── SKILL.md
│       ├── knowledge/
│       └── prompts/
```

### 4.2 Claude API 集成

使用 Anthropic Python SDK 调用 Claude API，结合 maqianzu-skill 的分析框架对采集内容进行深度处理。

```python
# 示意代码
from anthropic import Anthropic

client = Anthropic(api_key=config.claude_api_key)

# 加载 maqianzu-skill 分析框架
soul = load_file("skills/maqianzu-skill/SOUL.md")
skill = load_file("skills/maqianzu-skill/SKILL.md")
analysis_prompt = load_file("skills/maqianzu-skill/prompts/analysis.md")

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=2048,
    system=f"{soul}\n\n{skill}\n\n{analysis_prompt}",
    messages=[{
        "role": "user",
        "content": f"请对以下文章进行结构化分析：\n\n{article_content}"
    }]
)
```

### 4.3 Prompt 模板

在 maqianzu-skill 分析框架基础上，叠加 InfoHelper 自身的处理需求：

**摘要分析 Prompt（补充层）：**
```
基于你的分析框架，对以下文章进行处理，输出需包含：

1. **核心摘要**：用 2-3 句话概括关键信息
2. **关键数据**：提取文中的重要数据和指标
3. **结构化分析**：运用你的分析方法论，给出深层解读
4. **关联背景**：与近期相关事件的关联（如有）
5. **重要程度**：评估为 高/中/低

输出格式为结构化 Markdown。
```

**分类 Prompt：**
```
将以下文章归类到最匹配的类别：
- 宏观经济 / 货币政策 / 产业动态 / 公司财报
- AI 模型 / AI 应用 / AI 政策 / AI 投融资
返回主分类和子分类。
```

### 4.4 处理流程
```
原始文章 → 内容清洗 → 加载 maqianzu-skill 分析框架 → Claude 结构化分析 → Claude 分类 → 格式化输出 → 存储
```

---

## 5. 对外接口

InfoHelper 本身不负责推送，而是提供标准化的接口供外部程序（如 OpenClaw + 飞书）定时调用读取。

### 5.1 CLI 接口
```bash
# 执行一次完整的采集 + 分析 + 存储流程
python -m src.main run

# 仅获取最新未读的分析结果（JSON 格式输出）
python -m src.main fetch --unread

# 获取指定日期的分析结果
python -m src.main fetch --date 2026-04-16

# 按分类获取
python -m src.main fetch --category ai
python -m src.main fetch --category economics

# 标记已读
python -m src.main mark-read --id <article_id>
```

### 5.2 Python API
```python
from src.main import InfoHelper

helper = InfoHelper(config_path="config/config.yaml")

# 执行采集分析
helper.run()

# 获取未读结果
articles = helper.fetch_unread()

# 按条件查询
articles = helper.fetch(category="ai", date="2026-04-16", priority="high")

# 标记已读
helper.mark_read(article_ids=[...])
```

### 5.3 输出格式
每条分析结果以统一的 JSON 结构输出，便于外部程序解析：

```json
{
  "id": "a1b2c3",
  "title": "文章标题",
  "source": "Morgan Stanley Ideas",
  "category": "economics",
  "subcategory": "macro",
  "priority": "high",
  "url": "https://...",
  "published_at": "2026-04-16T10:30:00Z",
  "processed_at": "2026-04-16T10:35:00Z",
  "summary": "核心摘要...",
  "key_data": ["数据点1", "数据点2"],
  "analysis": "结构化分析内容...",
  "related_context": "关联背景...",
  "read": false
}
```

---

## 6. 知识存储结构

采集和分析后的内容以 Markdown 文件归档到本地，便于检索和回溯。

```
knowledge/
├── topics/                  # 按主题分类索引
│   ├── economics/
│   │   ├── macro.md         # 宏观经济
│   │   ├── policy.md        # 货币政策
│   │   └── industry.md      # 产业动态
│   └── ai/
│       ├── models.md        # AI 模型
│       ├── applications.md  # AI 应用
│       └── investment.md    # AI 投融资
├── daily/                   # 按日期归档
│   ├── 2026-04-16.md
│   └── 2026-04-17.md
├── catalog.json             # 文章索引（标题、分类、日期、路径）
└── index.md                 # 导航页
```

---

## 7. 项目目录结构

```
InfoHelper/
├── docs/
│   └── design.md            # 本设计文档
├── skills/
│   └── maqianzu-skill/      # Git submodule: 结构化分析框架
│       ├── SOUL.md           #   分析人格定义
│       ├── AGENTS.md         #   执行协议
│       ├── SKILL.md          #   分析模式入口
│       ├── knowledge/        #   分层知识库
│       ├── prompts/          #   分析框架与策略
│       └── tools/            #   语料工具
├── src/
│   ├── __init__.py
│   ├── main.py              # 入口，调度管理
│   ├── collectors/          # 数据采集模块
│   │   ├── __init__.py
│   │   ├── rss.py           # RSS 采集器
│   │   ├── crawler.py       # 网页爬虫
│   │   └── api_client.py    # API 客户端
│   ├── processors/          # 内容处理模块
│   │   ├── __init__.py
│   │   ├── analyzer.py      # Claude API 摘要分析
│   │   └── classifier.py    # 内容分类
│   ├── storage/             # 知识存储模块
│   │   ├── __init__.py
│   │   └── knowledge.py     # Markdown 归档管理
│   └── utils/               # 工具函数
│       ├── __init__.py
│       ├── dedup.py          # 去重
│       └── config.py         # 配置加载
├── config/
│   ├── config.yaml          # 主配置文件
│   ├── sources.yaml         # 信息源配置
│   └── prompts/             # Prompt 模板
│       ├── summary.txt
│       └── classify.txt
├── knowledge/               # 知识存储目录
├── requirements.txt
└── README.md
```

---

## 8. 配置管理

主配置文件 `config/config.yaml` 示例：

```yaml
# Claude API 配置
claude:
  api_key: ${CLAUDE_API_KEY}    # 通过环境变量注入
  model: claude-sonnet-4-20250514
  max_tokens: 2048

# 存储配置
storage:
  knowledge_dir: ./knowledge
  db_path: ./data/infohelper.db  # SQLite 去重数据库
```

信息源配置 `config/sources.yaml` 示例：

```yaml
# --- AI 领域 ---
rss:
  # Karpathy
  - name: Karpathy Blog (GitHub)
    url: https://karpathy.github.io/feed.xml
    category: ai
    priority: high
  - name: Karpathy Blog (Bear)
    url: https://karpathy.bearblog.dev/feed/
    category: ai
    priority: high
  # 综合
  - name: 机器之心
    url: https://www.jiqizhixin.com/rss
    category: ai
  - name: 量子位
    url: https://www.qbitai.com/feed
    category: ai
  - name: Hacker News AI
    url: https://hnrss.org/newest?q=AI+LLM
    category: ai
  - name: Foreign Policy
    url: https://foreignpolicy.com/feed
    category: economics
  - name: Cognizant Insights
    url: https://news.cognizant.com/rss
    category: economics
  - name: 36氪
    url: https://36kr.com/feed
    category: economics

apis:
  - name: arXiv AI
    type: arxiv
    query: "cat:cs.AI"
    category: ai
  - name: Karpathy YouTube
    type: youtube
    channel_id: UCNJB0_oMTVAyPtmMMAQpidg    # Andrej Karpathy
    category: ai
    priority: high

# --- Karpathy X/Twitter ---
twitter:
  - name: Karpathy
    handle: karpathy
    category: ai
    priority: high
    method: rss_bridge          # 通过 nitter 或 RSS Bridge 获取

# --- 金融研报（公开内容） ---
crawlers:
  # 投行研报
  - name: Morgan Stanley Ideas
    url: https://www.morganstanley.com/ideas
    parser: morgan_stanley
    category: economics
    access: public
  - name: Goldman Sachs Insights
    url: https://www.goldmansachs.com/insights
    parser: goldman_sachs
    category: economics
    access: public
  - name: Nomura Research
    url: https://www.nicmr.com/en/report.html
    parser: nomura
    category: economics
    access: public
  - name: Citi Institute
    url: https://www.citigroup.com/global/insights/citi-institute
    parser: citi
    category: economics
    access: public
  - name: UBS Insights
    url: https://www.ubs.com/global/en/investment-bank/insights-and-data.html
    parser: ubs
    category: economics
    access: public
  - name: Barclays Research
    url: https://www.ib.barclays/research.html
    parser: barclays
    category: economics
    access: auth_required     # 需机构账号
  # 智库/研究机构
  - name: CF40
    url: https://www.cf40.org.cn/
    parser: cf40
    category: economics
    access: public
  - name: Rhodium Group
    url: https://rhg.com/research/
    parser: rhodium
    category: economics
    access: public
  # 财经综合
  - name: 华尔街见闻
    url: https://wallstreetcn.com
    parser: wallstreetcn
    category: economics
    access: public
  - name: 财新
    url: https://www.caixin.com
    parser: caixin
    category: economics
    access: partial           # 部分付费
```

---

## 9. 开发方法论：Harness Engineering + Ralph Loop

本项目采用 [Harness Engineering](https://martinfowler.com/articles/harness-engineering.html) 理念，结合 [Ralph Loop](https://github.com/nitodeco/ralph) 迭代模式，以 AI Agent 驱动开发。

### 9.1 核心理念

**Harness Engineering** — 围绕 AI Agent 构建完整的约束体系（harness），包含：
- **Guides（前馈控制）**：规格文档、架构定义、编码规范 → 在 Agent 动手前引导方向
- **Sensors（反馈控制）**：测试、类型检查、Lint → 在 Agent 产出后验证质量

**Ralph Loop** — 确定性的迭代开发循环：
```
while 未完成:
    1. 评估当前进度（读 specs + 代码状态）
    2. 选择下一个未完成任务
    3. 实现该任务
    4. 运行验证门禁（tests / lint / type check）
    5. 通过则提交，失败则修复
    6. 记录进度，进入下一轮
```

### 9.2 项目文件结构（Ralph 规范）

```
InfoHelper/
├── AGENTS.md                    # Agent 执行协议（角色、规则、约束）
├── BUILD_PROMPT.md              # 构建循环的注入 Prompt
├── IMPLEMENTATION_PLAN.md       # 任务清单 + 完成状态 + commit hash
├── specs/                       # 规格文档目录
│   ├── collector-rss/           # RSS 采集器规格
│   │   ├── spec.md
│   │   └── test_cases.md
│   ├── collector-crawler/       # 爬虫采集器规格
│   │   ├── spec.md
│   │   └── test_cases.md
│   ├── processor-analyzer/      # Claude 分析器规格
│   │   ├── spec.md
│   │   └── test_cases.md
│   ├── storage/                 # 存储模块规格
│   │   ├── spec.md
│   │   └── test_cases.md
│   └── cli/                     # CLI 接口规格
│       ├── spec.md
│       └── test_cases.md
├── docs/
│   └── design.md                # 本设计文档
├── skills/
│   └── maqianzu-skill/          # Git submodule
├── src/                         # 源代码
├── tests/                       # 测试用例
├── config/
├── knowledge/
├── ralph.sh                     # Ralph 循环执行脚本
├── requirements.txt
└── README.md
```

### 9.3 三阶段开发流程

#### Phase 1: 需求定义（Spec Phase）
与 AI 对话 30+ 分钟，充分探索需求，输出结构化规格文档到 `specs/` 目录。

**每个 spec 包含：**
- 功能描述与边界条件
- 输入/输出格式定义
- 测试用例（含正常路径和异常路径）
- 依赖关系

#### Phase 2: 规划循环（Plan Loop）
Agent 分析 specs 与现有代码的差距，生成 `IMPLEMENTATION_PLAN.md`：

```markdown
# Implementation Plan

## Task List
- [ ] T1: 项目脚手架搭建（config 加载、目录结构）
- [ ] T2: RSS 采集器实现（feedparser + 去重）
- [ ] T3: 网页爬虫框架（基类 + 大摩/高盛解析器）
- [ ] T4: Claude 分析器（Anthropic SDK + maqianzu-skill 集成）
- [ ] T5: 分类器实现
- [ ] T6: 知识存储模块（SQLite + Markdown 归档）
- [ ] T7: CLI 接口（run / fetch / mark-read）
- [ ] T8: 端到端集成测试
```

此阶段 **不产生代码提交**，只迭代计划直到完整连贯。

#### Phase 3: 构建循环（Build Loop）
每轮迭代 **只做一个任务**：

```bash
#!/bin/bash
# ralph.sh
while :; do
    cat BUILD_PROMPT.md | claude-code
    # Agent 内部流程：
    #   1. 读取 IMPLEMENTATION_PLAN.md 找到下一个未完成任务
    #   2. 读取对应 specs/xxx/spec.md
    #   3. 实现代码
    #   4. 运行 pytest + mypy + ruff
    #   5. 全部通过 → git commit → 更新 PLAN 标记完成
    #   6. 失败 → 修复 → 重试
    #   7. 全部任务完成 → 写入 COMPLETE 标记 → 退出
done
```

### 9.4 验证门禁（Sensors）

| 门禁 | 工具 | 触发时机 |
|------|------|---------|
| 单元测试 | pytest | 每次提交前 |
| 类型检查 | mypy | 每次提交前 |
| 代码风格 | ruff | 每次提交前 |
| 集成测试 | pytest + fixtures | 模块完成时 |

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: pytest
        name: Run tests
        entry: pytest tests/ -x -q
        language: system
        pass_filenames: false
      - id: mypy
        name: Type check
        entry: mypy src/
        language: system
        pass_filenames: false
      - id: ruff
        name: Lint
        entry: ruff check src/
        language: system
        pass_filenames: false
```

### 9.5 AGENTS.md 示例

```markdown
# AGENTS.md — InfoHelper Agent 协议

## 角色
你是 InfoHelper 项目的开发 Agent。

## 规则
1. 每次只完成 IMPLEMENTATION_PLAN.md 中的一个任务
2. 实现前先阅读对应的 specs/xxx/spec.md
3. 所有代码必须通过 pytest + mypy + ruff
4. 每个任务完成后执行 git commit，message 格式：`T{n}: {简要描述}`
5. 更新 IMPLEMENTATION_PLAN.md 标记任务完成并记录 commit hash
6. 如果所有任务完成，写入 COMPLETE 标记
7. 如果卡住超过 3 次重试，写入 STUCK 标记并说明原因

## 约束
- 不引入未在 specs 中定义的功能
- 不修改其他任务的代码（除非是当前任务的依赖）
- 复用 skills/maqianzu-skill/ 中的分析框架，不重新发明
```

---

## 10. 部署方案

### 10.1 环境要求
- Mac Mini (Apple Silicon)
- Python 3.11+

### 10.2 安装与运行
```bash
# 安装依赖
pip install -r requirements.txt

# 设置环境变量
export CLAUDE_API_KEY=your_api_key

# 执行一次采集分析
python -m src.main run

# 获取未读结果（供外部程序调用）
python -m src.main fetch --unread
```

### 10.3 外部调用示例
外部程序（如 OpenClaw）定时调用 InfoHelper 获取分析结果并推送：
```bash
# crontab 或 launchd 定时执行
# 1. 先采集分析
python -m src.main run
# 2. 获取未读结果，传递给推送程序
python -m src.main fetch --unread --format json | your_push_program
```

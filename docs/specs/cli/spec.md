# CLI 接口 — 需求规格

## 模块路径
`src/main.py`

## 功能描述
InfoHelper 的入口模块，提供 CLI 命令和 Python API。外部程序通过 CLI 命令触发采集分析流程或读取结果。

## 依赖
- `argparse` — 命令行参数解析（标准库）
- `src/collectors/` — 三个采集器
- `src/processors/` — 分析器 + 分类器
- `src/storage/` — 存储模块
- `src/utils/config.py` — 配置加载

## CLI 命令

### `run` — 执行采集分析

```bash
python -m src.main run [--sources rss,crawler,api] [--category ai|economics]
```

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--sources` | 指定采集器类型，逗号分隔 | 全部（rss,crawler,api） |
| `--category` | 仅采集指定分类的源 | 全部 |

**执行流程：**
1. 加载配置
2. 依次运行采集器 → 合并 Article 列表
3. 分析器处理 → 分类器分类
4. 存储到 SQLite + Markdown
5. 输出到 stdout：`{"collected": N, "analyzed": N, "saved": N}`

### `fetch` — 获取分析结果

```bash
python -m src.main fetch [--unread] [--date YYYY-MM-DD] [--category ai|economics] [--priority high|normal] [--importance high|medium|low] [--limit N] [--format json|text]
```

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--unread` | 仅返回未读文章 | false |
| `--date` | 筛选日期 | 无（全部） |
| `--category` | 筛选分类 | 无（全部） |
| `--priority` | 筛选优先级 | 无（全部） |
| `--importance` | 筛选重要程度 | 无（全部） |
| `--limit` | 最大返回条数 | 50 |
| `--format` | 输出格式 | json |

**输出：**
- `json`：JSON 数组输出到 stdout
- `text`：人类可读的文本格式

### `mark-read` — 标记已读

```bash
python -m src.main mark-read --id <id1> [--id <id2> ...]
python -m src.main mark-read --all
```

| 参数 | 说明 |
|------|------|
| `--id` | 指定文章 ID，可多次使用 |
| `--all` | 标记所有未读为已读 |

**输出：** `{"marked": N}`

### `status` — 查看系统状态

```bash
python -m src.main status
```

**输出：**
```json
{
  "total_articles": 150,
  "unread": 23,
  "by_category": {"ai": 80, "economics": 70},
  "by_importance": {"high": 15, "medium": 85, "low": 50},
  "last_run": "2026-04-16T10:35:00Z"
}
```

## Python API

```python
class InfoHelper:
    def __init__(self, config_path: str = "config/config.yaml"):
        """加载配置，初始化各模块"""

    def run(self, sources: list[str] | None = None,
            category: str | None = None) -> dict:
        """
        执行采集分析流程
        返回 {"collected": N, "analyzed": N, "saved": N}
        """

    def fetch(self, unread: bool = False,
              date: str | None = None,
              category: str | None = None,
              priority: str | None = None,
              importance: str | None = None,
              limit: int = 50) -> list[dict]:
        """查询文章"""

    def fetch_unread(self) -> list[dict]:
        """获取所有未读文章（fetch(unread=True) 的快捷方式）"""

    def mark_read(self, article_ids: list[str]) -> int:
        """标记已读，返回实际更新数量"""

    def mark_all_read(self) -> int:
        """标记所有未读为已读"""

    def status(self) -> dict:
        """返回系统状态统计"""
```

## 退出码
| 退出码 | 含义 |
|--------|------|
| 0 | 成功 |
| 1 | 配置错误（缺少必要配置） |
| 2 | 运行时错误（所有采集器都失败等） |

## 错误处理
- 配置文件不存在：退出码 1，输出错误信息到 stderr
- 所有采集器都失败：退出码 2，仍尝试输出已有结果
- 部分采集器失败：正常退出（0），在 stdout 结果中标注失败的源
- 无效参数：argparse 自动处理，输出 usage

## 边界条件
- 首次运行无历史数据：run 正常执行，fetch 返回空列表
- fetch 无匹配结果：输出空 JSON 数组 `[]`
- mark-read 传入全部无效 ID：输出 `{"marked": 0}`

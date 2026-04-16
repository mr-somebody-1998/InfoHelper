# 配置加载模块 — 需求规格

## 模块路径
`src/utils/config.py`

## 功能描述
加载并验证 YAML 配置文件（config.yaml + sources.yaml），支持环境变量替换，提供统一的配置访问接口。

## 依赖
- `pyyaml` — YAML 解析
- `os` — 环境变量

## 配置文件

### config.yaml — 主配置
```yaml
claude:
  api_key: ${CLAUDE_API_KEY}      # 环境变量替换
  model: claude-sonnet-4-20250514
  max_tokens: 2048

storage:
  knowledge_dir: ./knowledge
  db_path: ./data/infohelper.db
```

### sources.yaml — 信息源配置
```yaml
rss:
  - name: str
    url: str
    category: str
    priority: str         # 可选
apis:
  - name: str
    type: str
    ...
twitter:
  - name: str
    handle: str
    ...
crawlers:
  - name: str
    url: str
    parser: str
    category: str
    access: str
```

## 公开接口

```python
class Config:
    def __init__(self, config_path: str = "config/config.yaml",
                 sources_path: str = "config/sources.yaml"):
        """加载并验证两个配置文件"""

    @property
    def claude(self) -> dict:
        """Claude API 配置"""

    @property
    def storage(self) -> dict:
        """存储配置"""

    @property
    def rss_sources(self) -> list[dict]:
        """RSS 信息源列表"""

    @property
    def crawler_sources(self) -> list[dict]:
        """爬虫信息源列表"""

    @property
    def api_sources(self) -> list[dict]:
        """API 信息源列表"""

    @property
    def twitter_sources(self) -> list[dict]:
        """Twitter 信息源列表"""

    def get(self, key_path: str, default=None):
        """点号分隔的路径访问，如 config.get("claude.model")"""
```

## 环境变量替换
配置值中的 `${VAR_NAME}` 会被替换为对应环境变量的值。

- `${VAR_NAME}` 存在 → 替换为值
- `${VAR_NAME}` 不存在 → 保留原始字符串，记录 warning

## 验证规则
- `claude.api_key`：必须存在且非空（替换后）
- `claude.model`：必须存在
- `storage.db_path`：必须存在
- `rss` 中每项必须有 `name` 和 `url`
- `crawlers` 中每项必须有 `name`、`url`、`parser`

验证失败抛出 `ConfigError`。

## 错误处理
- 配置文件不存在：抛出 FileNotFoundError
- YAML 格式错误：抛出 ConfigError
- 必要字段缺失：抛出 ConfigError
- 环境变量未设置：记录 warning，不抛异常（由使用方判断）

## 边界条件
- sources.yaml 中某个类别为空列表：正常返回空列表
- sources.yaml 不存在：所有 sources 属性返回空列表，记录 warning
- 配置值为非字符串类型：不做环境变量替换

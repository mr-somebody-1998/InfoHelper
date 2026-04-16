# 配置加载模块 — 测试用例

## 测试文件路径
`tests/utils/test_config.py`

## Fixtures
- 临时目录中创建 config.yaml 和 sources.yaml

---

## 配置加载

### TC-CFG-001: 成功加载完整配置
- **输入**：有效 config.yaml + sources.yaml
- **预期**：Config 实例化成功，各属性可访问

### TC-CFG-002: 环境变量替换
- **输入**：config.yaml 含 `${TEST_KEY}`，设置环境变量 TEST_KEY=abc
- **预期**：config.claude["api_key"] == "abc"

### TC-CFG-003: 环境变量未设置
- **输入**：`${MISSING_VAR}` 未设置
- **预期**：值保留为 "${MISSING_VAR}"，记录 warning

### TC-CFG-004: 点号路径访问
- **输入**：config.get("claude.model")
- **预期**：返回对应值

### TC-CFG-005: 点号路径默认值
- **输入**：config.get("nonexistent.key", "default")
- **预期**：返回 "default"

---

## 信息源配置

### TC-CFG-101: 获取 RSS 源列表
- **输入**：sources.yaml 含 3 个 rss 项
- **预期**：rss_sources 返回 3 项列表

### TC-CFG-102: 获取爬虫源列表
- **预期**：crawler_sources 返回配置的爬虫列表

### TC-CFG-103: 获取 API 源列表
- **预期**：api_sources 返回配置的 API 列表

### TC-CFG-104: 获取 Twitter 源列表
- **预期**：twitter_sources 返回配置的 Twitter 列表

### TC-CFG-105: 某类别为空
- **输入**：sources.yaml 中 rss 为 `[]`
- **预期**：rss_sources 返回空列表

### TC-CFG-106: 某类别不存在
- **输入**：sources.yaml 中无 twitter 键
- **预期**：twitter_sources 返回空列表

---

## 验证

### TC-CFG-201: 缺少 claude.api_key
- **输入**：config.yaml 无 api_key 字段
- **预期**：抛出 ConfigError

### TC-CFG-202: 缺少 claude.model
- **预期**：抛出 ConfigError

### TC-CFG-203: RSS 源缺少 name
- **输入**：某 rss 项无 name
- **预期**：抛出 ConfigError

### TC-CFG-204: 爬虫源缺少 parser
- **输入**：某 crawler 项无 parser
- **预期**：抛出 ConfigError

---

## 错误处理

### TC-CFG-301: config.yaml 不存在
- **输入**：不存在的路径
- **预期**：抛出 FileNotFoundError

### TC-CFG-302: YAML 格式错误
- **输入**：无效 YAML 内容
- **预期**：抛出 ConfigError

### TC-CFG-303: sources.yaml 不存在
- **输入**：config.yaml 有效，sources.yaml 不存在
- **预期**：所有 sources 属性返回空列表，记录 warning

---

## 边界条件

### TC-CFG-401: 配置值为数字
- **输入**：max_tokens: 2048（非字符串）
- **预期**：不做环境变量替换，值保持为 int

### TC-CFG-402: 嵌套环境变量
- **输入**：值为 "prefix_${VAR}_suffix"
- **预期**：仅替换 ${VAR} 部分

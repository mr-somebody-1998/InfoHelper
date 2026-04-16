# 去重模块 — 测试用例

## 测试文件路径
`tests/utils/test_dedup.py`

## Fixtures
- 使用内存 SQLite（`:memory:`）

---

## URL 去重

### TC-DDP-001: 新 URL 不重复
- **输入**：is_duplicate("https://example.com/new")
- **预期**：返回 False

### TC-DDP-002: 已注册 URL 判定重复
- **输入**：先 register("https://example.com/a")，再 is_duplicate("https://example.com/a")
- **预期**：返回 True

### TC-DDP-003: 不同 URL 不重复
- **输入**：register URL-A，is_duplicate URL-B
- **预期**：返回 False

### TC-DDP-004: URL hash 确定性
- **输入**：同一 URL 多次计算 hash
- **预期**：结果一致

---

## 标题去重

### TC-DDP-101: 标题高度相似
- **输入**：已注册 title="美联储维持利率不变"，检查 title="美联储维持利率不变，符合预期"
- **预期**：相似度 > 0.85，返回 True

### TC-DDP-102: 标题不相似
- **输入**：已注册 title="美联储维持利率"，检查 title="GPT-5 发布"
- **预期**：相似度 < 0.85，返回 False

### TC-DDP-103: 标题为空时跳过标题匹配
- **输入**：is_duplicate(url="new_url", title="")
- **预期**：仅做 URL 匹配

### TC-DDP-104: URL 不同但标题相似
- **输入**：不同 URL，相似标题
- **预期**：标题相似度 > 0.85 时返回 True

---

## 注册

### TC-DDP-201: 注册单条
- **输入**：register("https://example.com/a", "Title A")
- **预期**：后续 is_duplicate 返回 True

### TC-DDP-202: 批量注册
- **输入**：register_batch 5 条记录
- **预期**：所有 5 条都可检测到

### TC-DDP-203: 重复注册幂等
- **输入**：同一 URL 注册两次
- **预期**：不报错，数据库中仅 1 条记录

---

## 边界条件

### TC-DDP-301: URL 为空字符串
- **输入**：is_duplicate("")
- **预期**：返回 False

### TC-DDP-302: 自动建表
- **输入**：全新 SQLite 文件
- **预期**：fingerprints 表自动创建

### TC-DDP-303: 大量数据性能
- **输入**：注册 10000 条，查询 1 条
- **预期**：查询时间 < 10ms

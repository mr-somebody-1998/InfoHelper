# 知识存储模块 — 测试用例

## 测试文件路径
`tests/storage/test_knowledge.py`

## Fixtures
- 使用临时目录作为 knowledge_dir
- 使用内存 SQLite（`:memory:`）或临时文件

---

## SQLite 存储

### TC-STO-001: 保存单篇文章
- **输入**：1 个 AnalyzedArticle
- **预期**：SQLite 中新增 1 条记录，字段正确
- **验证**：query 可查到该文章

### TC-STO-002: 保存多篇文章
- **输入**：3 个 AnalyzedArticle
- **预期**：SQLite 新增 3 条记录
- **验证**：save 返回 3

### TC-STO-003: 幂等 — 重复保存
- **输入**：同一篇文章保存两次
- **预期**：第二次跳过，save 返回 0
- **验证**：数据库中仅 1 条记录

### TC-STO-004: 自动建表
- **输入**：全新的 SQLite 文件
- **预期**：articles 表和索引自动创建

---

## 查询

### TC-STO-101: 按 category 查询
- **输入**：3 篇文章（2 economics, 1 ai），查询 category="ai"
- **预期**：返回 1 篇

### TC-STO-102: 按 date 查询
- **输入**：不同日期的文章，查询特定日期
- **预期**：仅返回该日期的文章

### TC-STO-103: 按 unread_only 查询
- **输入**：3 篇文章，1 篇已读
- **预期**：unread_only=True 返回 2 篇

### TC-STO-104: 组合查询
- **输入**：category="ai" + unread_only=True
- **预期**：返回符合两个条件的文章

### TC-STO-105: limit 参数
- **输入**：10 篇文章，limit=3
- **预期**：返回 3 篇

### TC-STO-106: 查询无结果
- **输入**：查询不存在的 category
- **预期**：返回空列表

### TC-STO-107: get_by_id 有效 ID
- **输入**：已存在的文章 ID
- **预期**：返回该文章的字典

### TC-STO-108: get_by_id 无效 ID
- **输入**：不存在的 ID
- **预期**：返回 None

---

## 已读标记

### TC-STO-201: 标记已读
- **输入**：2 个文章 ID
- **预期**：mark_read 返回 2，查询确认 read=1

### TC-STO-202: 标记不存在的 ID
- **输入**：1 个有效 ID + 1 个无效 ID
- **预期**：mark_read 返回 1

---

## Markdown 归档

### TC-STO-301: 生成 daily markdown
- **输入**：保存 1 篇 2026-04-16 的文章
- **预期**：knowledge/daily/2026-04-16.md 存在，内容包含文章标题和摘要

### TC-STO-302: daily markdown 追加
- **输入**：同一天保存 2 篇文章（分两次调用）
- **预期**：同一个 daily 文件包含 2 篇文章

### TC-STO-303: 生成 topic markdown
- **输入**：category=ai, subcategory=models
- **预期**：knowledge/topics/ai/models.md 存在，包含文章内容

### TC-STO-304: topic markdown 追加
- **输入**：同一 topic 保存多篇文章
- **预期**：追加到同一文件

### TC-STO-305: 自动创建目录
- **输入**：topics/ai/ 目录不存在
- **预期**：自动创建后写入文件

### TC-STO-306: 更新 catalog.json
- **输入**：保存 2 篇文章
- **预期**：catalog.json 包含 2 条索引记录

### TC-STO-307: 生成 index.md
- **输入**：保存多篇不同分类的文章
- **预期**：index.md 包含 daily 和 topics 的导航链接

---

## 边界条件

### TC-STO-401: 输入空列表
- **预期**：save 返回 0，不修改任何文件

### TC-STO-402: key_data JSON 序列化
- **输入**：key_data = ["GDP 4.5%", "通胀 2.8%"]
- **预期**：SQLite 中存储为 JSON 字符串，查询时还原为列表

### TC-STO-403: 特殊字符处理
- **输入**：title 含引号、Markdown 特殊字符
- **预期**：正确存储和写入 Markdown，不破坏格式

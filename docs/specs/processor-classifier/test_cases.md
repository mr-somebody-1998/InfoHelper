# 分类器 — 测试用例

## 测试文件路径
`tests/processors/test_classifier.py`

---

## 规则分类

### TC-CLS-001: 关键词命中 — 宏观经济
- **输入**：title="GDP增速放缓至4.5%"，category="economics"
- **预期**：category="economics"，subcategory="macro"

### TC-CLS-002: 关键词命中 — 货币政策
- **输入**：title="Fed Holds Interest Rate at 5.25%"
- **预期**：category="economics"，subcategory="policy"

### TC-CLS-003: 关键词命中 — AI 模型
- **输入**：title="GPT-5 Training Details Revealed"
- **预期**：category="ai"，subcategory="models"

### TC-CLS-004: 关键词命中 — AI 应用
- **输入**：title="新版 Copilot 支持多 Agent 协作"
- **预期**：category="ai"，subcategory="applications"

### TC-CLS-005: 多关键词命中 — 取最高匹配
- **输入**：content 中 "利率" 出现 3 次，"GDP" 出现 1 次
- **预期**：subcategory="policy"（命中更多）

### TC-CLS-006: 关键词不足 — 回退到 LLM
- **输入**：title 和 content 中无关键词命中
- **预期**：调用 LLM 分类

---

## LLM 分类

### TC-CLS-101: LLM 返回有效分类
- **输入**：mock Claude 返回 "economics / macro"
- **预期**：category="economics"，subcategory="macro"

### TC-CLS-102: LLM 返回无效分类
- **输入**：mock Claude 返回 "technology / hardware"
- **预期**：fallback 到原始 category，subcategory="other"

### TC-CLS-103: LLM 调用失败
- **输入**：mock API 抛出异常
- **预期**：使用规则分类结果

---

## 批量分类

### TC-CLS-201: 混合分类 — 部分规则部分 LLM
- **输入**：3 篇文章，2 篇可规则分类，1 篇需 LLM
- **预期**：LLM 仅被调用 1 次

### TC-CLS-202: 空列表
- **输入**：articles = []
- **预期**：返回空列表

---

## 边界条件

### TC-CLS-301: 英文内容分类
- **输入**：全英文文章含 "inflation" 和 "unemployment"
- **预期**：正确分类为 economics/macro

### TC-CLS-302: 中英混合内容
- **输入**：中文标题 + 英文正文
- **预期**：关键词表兼容两种语言

### TC-CLS-303: 文章无 content
- **输入**：content 为空，仅有 title
- **预期**：基于 title 分类

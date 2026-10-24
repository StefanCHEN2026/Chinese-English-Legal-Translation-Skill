# 法律术语中英互译 Skill

[![Code License: MIT](https://img.shields.io/badge/Code%20License-MIT-yellow.svg)](LICENSE)
[![Data License: CC BY-NC 4.0](https://img.shields.io/badge/Data%20License-CC%20BY--NC%204.0-lightgrey.svg)](LICENSE-DATA)
[![Terms: 34,000+](https://img.shields.io/badge/Terms-34,000+-blue.svg)](references/glossary.csv)

面向中国大陆法律实务的中英双语法律术语翻译工具。基于香港律政司(DOJ)双语法律词汇表清洗整理的 ~34,000 条通用法律术语，加上 ~950 条中国大陆法律体系特色术语、472 条英-德对照法律术语（威斯康星州法院）以及美国法院术语英文释义（加州萨克拉门托县高等法院）。

## ✨ 特色

- 📚 **34,000+ 通用法律术语** — 涵盖民法、刑法、商法、诉讼法、宪法行政法、国际法
- 🇨🇳 **950+ 大陆特色术语** — PRC 民法典、刑法、公司法等核心法律官方英译
- 🇩🇪 **472 条英-德对照** — 威斯康星州法院《英德法律词汇表》，含英文释义，支持德文查询
- 🇺🇸 **美国法院术语释义** — 萨克拉门托县高等法院《English Legal Glossary》，英文术语+权威英文释义
- 🏛️ **拉丁法律术语** — ~430 条拉丁术语均附双语注释
- 🔍 **智能搜索** — 精确匹配 → 子串搜索 → 模糊匹配，自动路由（中/英/德三语字段）
- 🏷️ **领域分类** — 六大法律领域标注，支持按领域筛选
- 📄 **多格式输出** — 文本、JSON、CSV 三种输出格式
- 🔄 **可复现清洗** — 从原始 DOJ 数据到清洗结果的完整 pipeline

## 📦 安装

### 方式一：ZCode Skill（推荐）

```bash
# 复制到 ZCode skill 目录
cp -r legal-translation/ ~/.agents/skills/legal-translation/

# 或在项目中使用
cp -r legal-translation/ your-project/.agents/skills/legal-translation/
```

ZCode 会自动发现并加载该 skill，当你询问法律术语翻译时自动触发。

### 方式二：独立脚本

也可以直接使用脚本（无需 ZCode）：

```bash
git clone https://github.com/StefanCHEN2026/Chinese-English-Legal-Translation-Skill.git
cd Chinese-English-Legal-Translation-Skill
pip install -r requirements.txt  # 无需额外依赖，仅需 Python 3.8+
```

## 🚀 快速使用

### 基本查询

```bash
# 中文 → 英文
python scripts/lookup.py -q "不可抗力"

# 英文 → 中文
python scripts/lookup.py -q "force majeure"

# JSON 格式输出（方便程序调用）
python scripts/lookup.py -q "tort" --format json
```

### 高级查询

```bash
# 模糊搜索
python scripts/lookup.py -q "合同违约" --fuzzy -n 10

# 按领域筛选
python scripts/lookup.py -q "证据" --domain 诉讼法

# 精确匹配
python scripts/lookup.py -q "物权" --exact

# 查询大陆法律术语
python scripts/lookup.py -q "用益物权" -g references/mainland_terms.csv

# 限制返回数量
python scripts/lookup.py -q "party" -n 5

# 英-德对照查询（威斯康星州法院词汇表）
python scripts/lookup.py -q "witness"   # 英文 → 中文翻译 + 德文对照
python scripts/lookup.py -q "Zeuge"     # 德文 → 英文
```

### 中国大陆法律特有概念

```bash
# 大陆特色术语已在 mainland_terms.csv 中
python scripts/lookup.py -q "善意取得"
python scripts/lookup.py -q "人民调解"
python scripts/lookup.py -q "审判委员会"
python scripts/lookup.py -q "指导性案例"
```

## 📊 数据规模

| 文件 | 条目数 | 内容 |
|------|--------|------|
| `glossary.csv` | 33,996 | 通用法律术语（清洗自 DOJ 双语词汇表） |
| `mainland_terms.csv` | 951 | 中国大陆法律体系特色术语 |
| `german_legal_glossary.csv` | 472 | 英-德对照法律术语（威斯康星州法院） |
| `us_legal_definitions.csv` | 整理中 | 美国法院术语英文释义（萨克拉门托县高等法院），见 [source-guide](references/source-guide.md) |

### 领域分布

| 领域 | 条目数 | 占比 |
|------|--------|------|
| 通用 | ~31,000 | 90% |
| 诉讼法 | ~960 | 2.8% |
| 刑法 | ~630 | 1.9% |
| 商法 | ~600 | 1.8% |
| 民法 | ~560 | 1.6% |
| 宪法行政法 | ~285 | 0.8% |
| 国际法 | ~263 | 0.8% |

> 注：大部分通用术语适用于多个领域，标记为"通用"。

## 🛠️ 数据清洗

`glossary.csv` 由原始 DOJ CSV（78,912 行）清洗而来。清洗脚本本地维护、未随仓库分发，清洗策略如下（可据此复现）：

清洗策略（温和）：
- ✅ 保留通用法律词典和大陆法律来源
- ❌ 移除香港独有机构/角色/概念
- ❌ 移除报告/咨询文件来源
- ❌ 移除模板占位符条目
- 🔄 去重：来源优先级 词典 > 条例 > 其他

## 🔗 配合 PKULaw MCP 工具

本 Skill 与北大法宝 MCP 工具配合使用效果更佳：

1. **术语查询** → 使用本 Skill 查找中英对应
2. **法条验证** → 使用 `mcp__pkulaw-law-search` 验证术语在法条中的实际用法
3. **案例参考** → 使用 `mcp__pkulaw-case-search` 查看术语在判决中的使用

## 📖 数据来源

| 来源 | 用途 | 链接 |
|------|------|------|
| **香港律政司双语法律词汇表** | 英文法律词汇的主要来源（已清洗去香港专属内容） | https://www.doj.gov.hk/en/publications/glossary.html |
| **威斯康星州法院《Glossary of Legal Terminology – English–German》** | 472 条英-德对照 + 英文释义 | https://www.wicourts.gov/services/interpreter/docs/germanglossary.pdf |
| **加州萨克拉门托县高等法院《English Legal Glossary》**（康特拉科斯塔县高等法院网站托管） | 美国法院术语 + 英文释义 | https://contracosta.courts.ca.gov/system/files/general/english-legal-glossary.pdf |
| **中华人民共和国民法典 / 刑法 / 公司法等 NPC 官方英译本** | 大陆法律术语 | — |

> 检索/收录日期：2026-10-24。详细来源说明与数据处理方法见 [references/source-guide.md](references/source-guide.md)

## ⚠️ 使用注意事项

1. **普通法 vs 大陆法**：主体术语库源自香港普通法体系，部分翻译风格偏向英式 / common law 表达
2. **大陆法律翻译**：中国大陆法律特有概念请优先使用 `mainland_terms.csv`
3. **翻译一致性**：同一中文术语在不同语境下可能有不同英文对应，本工具列出所有选项
4. **非官方翻译**：除 mainland_terms.csv 中标注为官方翻译的术语外，其他翻译仅供参考

## 🗺️ 路线图

- [x] v1.0 — 数据清洗 + 大陆术语精选 + ZCode Skill
- [x] v1.1 — 新增英-德对照词汇表（威斯康星州法院）与美国法院术语释义（萨克拉门托）
- [ ] v1.2 — 改进领域分类算法（降低"通用"占比）
- [ ] v1.3 — 在线抓取 NPC/CLT 最新术语
- [ ] v2.0 — 接入 pkulaw MCP 做实时法条验证
- [ ] v2.1 — LLM 辅助的上下文翻译建议
- [ ] v3.0 — Web 界面、社区贡献机制

## 📄 许可（双许可）

| 部分 | 许可 | 商用 | 文件 |
|------|------|------|------|
| 代码与文档（`scripts/`、`SKILL.md` 等） | **MIT License** | ✅ 允许 | [LICENSE](LICENSE) |
| 术语数据（`references/*.csv`） | **CC BY-NC 4.0** | ❌ 禁止 | [LICENSE-DATA](LICENSE-DATA) |

> ⚠️ 术语数据的原始来源（香港律政司、威斯康星州法院、加州萨克拉门托县高等法院、NPC 等）各有其使用条款，请在使用时自行确认合规性，并保留来源署名。原始 PDF 不随仓库分发，仅提供来源链接。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！特别是：

- 补充大陆法律术语
- 改进领域分类
- 报告翻译错误
- 添加更多数据来源

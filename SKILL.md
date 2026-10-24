---
name: legal-translation
description: >
  Chinese-English legal terminology translation using a curated glossary
  of 34,000+ legal terms. Use when the user asks about Chinese legal
  term translation, English legal equivalents, PRC law terminology,
  legal vocabulary lookup, or needs to find how specific legal concepts
  are expressed in Chinese or English. Covers general legal vocabulary
  plus dedicated PRC Civil Code, Criminal Law, Company Law, and
  procedural law terminology. Also supports English-German legal term
  lookup (Wisconsin Courts glossary) and US court legal term
  definitions (Sacramento Superior Court glossary).
---

# Legal Translation Skill — 法律术语中英互译

## Overview

This skill provides authoritative Chinese-English legal terminology lookup based on:

| Data Source | Entries | Coverage |
|------------|---------|----------|
| `glossary.csv` | ~34,000 | General legal terms (cleaned from HK DOJ bilingual glossary) |
| `mainland_terms.csv` | ~950 | PRC-specific legal concepts (Civil Code, Criminal Law, Company Law, etc.) |
| `german_legal_glossary.csv` | 472 | English-German legal terms + English explanations (Wisconsin Courts) |
| `us_legal_definitions.csv` | ~1,300 | US court legal terms with plain-English definitions (Sacramento Superior Court; CN equivalents backfilled) |

**Coverage**: Civil law, criminal law, commercial law, procedural law, constitutional/administrative law, international law, plus Latin legal terms. English-German bilingual lookup and US court terminology as supplementary sources.

**Limitations**: The general glossary leans toward common law terminology (Hong Kong origin). For PRC-specific socialist legal system concepts, supplement with `mainland_terms.csv`. The German glossary is English-German only (no Chinese); US definitions are English-only with Chinese equivalents backfilled from the existing glossaries.

---

## 信息来源 / Information Sources

### 通用法律术语 (glossary.csv ~34,000条)

| 来源 | 说明 |
|------|------|
| **香港律政司 (DoJ) 双语法律词汇表** | 原始78,912条，经温和清洗后保留33,996条 |
| 英汉民商事法律词汇 | 通用英汉法律词典，质量最高的子来源 |
| 刑事诉讼词汇集 | 刑事程序专门词汇 |
| 香港法例中的通用术语 | 去除香港独有机构/概念后保留 |

> 清洗策略与解析方法完整说明见 `references/source-guide.md`（数据准备脚本本地维护，未随仓库分发）

### 中国大陆法律术语 (mainland_terms.csv ~950条)

| 来源 | 条目 | 说明 |
|------|------|------|
| **《中华人民共和国民法典》** NPC官方英译本 | ~290 | 全7编定义条款与核心概念 |
| **《人民法院组织机构、职务名称、工作场所英译文》** 法〔2021〕184号 | ~90 | 最高人民法院发布的法院系统英译权威标准 |
| **《中华人民共和国刑法》** NPC官方英译本 | ~135 | 总则+分则重点罪名+刑罚体系 |
| **《中华人民共和国公司法》(2023修订)** 等商法 | ~155 | 公司/破产/证券/保险/知识产权等 |
| **三大诉讼法** NPC官方英译本 | ~145 | 民事/刑事/行政诉讼+仲裁+调解 |
| **《中华人民共和国宪法》+行政法** NPC官方英译本 | ~95 | 国家机构+行政许可/处罚/强制/复议 |
| **国际法相关法律法规** | ~35 | 对外贸易/引渡/涉外法律适用 |

### 英德法律术语 (german_legal_glossary.csv 472条)

| 来源 | 说明 |
|------|------|
| **威斯康星州法院《Glossary of Legal Terminology – English–German》** | 472 词，英→德对照 + 英文释义。编译：Dustin DeGrande（Dagmar Grimm 修订），威斯康星州法院系统法庭口译服务发布 |

> 来源: https://www.wicourts.gov/services/interpreter/docs/germanglossary.pdf

### 美国法院术语释义 (us_legal_definitions.csv)

| 来源 | 说明 |
|------|------|
| **加州萨克拉门托县高等法院《English Legal Glossary》**（由康特拉科斯塔县高等法院网站托管） | 英文术语 + 英文释义；中文对照由既有词表按英文精确匹配回填 |

> 来源: https://contracosta.courts.ca.gov/system/files/general/english-legal-glossary.pdf
> 注意：`us_legal_definitions.csv` 的「中文对照」列是按英文精确匹配从 `glossary.csv` / `mainland_terms.csv` 回填的，并非来源文件自带，引用时请知悉。

### 核验方式

- **北大法宝 (PKULaw) MCP 工具** — 逐条核验中文术语在现行法条原文中的存在性
- 英文翻译基于 **全国人大 (NPC)** 官方公布的英文译本
- 法院系统术语依据 **最高人民法院法〔2021〕184号通知**

---

## Quick Start

### Basic Lookup
```bash
# Chinese → English
python "$SKILL_DIR/scripts/lookup.py" -q "不可抗力"

# English → Chinese
python "$SKILL_DIR/scripts/lookup.py" -q "force majeure"
```

### Fuzzy Search
```bash
python "$SKILL_DIR/scripts/lookup.py" -q "合同违约" --fuzzy
```

### Domain Filtering
```bash
python "$SKILL_DIR/scripts/lookup.py" -q "证据" --domain 诉讼法 -n 10
```

### 英德对照查询 (EN-DE, Wisconsin Courts)
```bash
# 英文 → 中文 + 德文对照
python "$SKILL_DIR/scripts/lookup.py" -q "witness"

# 德文 → 英文
python "$SKILL_DIR/scripts/lookup.py" -q "Zeuge"
```

### JSON Output (for programmatic use)
```bash
python "$SKILL_DIR/scripts/lookup.py" -q "tort" --format json
```

---

## Lookup Workflow

When a user requests legal terminology translation, follow this priority:

### 1. Determine Query Direction
- **Chinese query** → Search `cn` field → return English equivalents
- **English query** → Search `en` field → return Chinese equivalents (plus German where available)
- **German query** → Search `de` field → return English (and explanation)
- **Mixed or uncertain** → Search all fields

### 2. Search Strategy (in order)
```
Exact match → Substring match → Fuzzy match
```

1. **Exact match first**: `lookup.py -q "term" --exact`
2. **If no result**: `lookup.py -q "term"` (substring mode, the default)
3. **If still no result**: `lookup.py -q "term" --fuzzy`
4. **For domain-specific queries**: Add `--domain` filter

### 3. When to Use Domain Filtering
User mentions specific legal area → use `--domain` flag:
- `民法` → Civil law (contracts, torts, property, family, succession)
- `刑法` → Criminal law
- `商法` → Commercial law (companies, securities, insurance, IP)
- `诉讼法` → Procedural law (litigation, arbitration, evidence)
- `宪法行政法` → Constitutional & administrative law
- `国际法` → International law (treaties, maritime, extradition)

### 4. For Mainland PRC Law
When users work with PRC law specifically, load both glossaries:
```bash
python "$SKILL_DIR/scripts/lookup.py" -q "物权" -g "$SKILL_DIR/references/mainland_terms.csv"
```

The mainland terms cover PRC-specific concepts NOT found in the general HK-sourced glossary:
- 物权 (Real Rights), 用益物权 (Usufructuary Rights)
- 人民调解 (People's Mediation), 行政复议 (Administrative Reconsideration)
- 审判委员会 (Judicial Committee), 指导性案例 (Guiding Case)
- Socialist legal system concepts unique to PRC

---

## Output Format

### Standard Text Output
```
查询: "tort"
找到 3 条结果:
------------------------------------------------------------

[1] 侵权法
    EN: tort
    来源: HK Ordinance
    标签: 民法, 单词

[2] 侵权行为
    EN: tort
    来源: HK Ordinance
    标签: 民法, 单词

[3] 侵权（行为）
    EN: tort
    来源: 英汉民商事法律词汇
    标签: 民法, 短语
```

### Presenting Results to Users
When relaying results back to the user:
1. **Single exact match**: Present directly with source and domain
2. **Multiple matches**: List all, noting differences in context/usage
3. **Partial/fuzzy matches**: Clearly indicate match quality
4. **No match found**: Suggest trying broader terms or alternative expressions

---

## Important Translation Conventions

### PRC Legal English vs HK Legal English
The same Chinese term may have different English translations in different contexts:

| Chinese | HK/Common Law | PRC/Mainland |
|---------|---------------|--------------|
| 物权 | property right | real right |
| 法定代表人 | (no direct equivalent) | legal representative |
| 司法解释 | (no direct equivalent) | judicial interpretation |
| 调解 | mediation | mediation / conciliation |
| 审判委员会 | (no direct equivalent) | judicial committee / adjudication committee |

### Latin Legal Terms
The glossary includes ~430 Latin legal terms with bilingual annotations. These are marked as type `拉丁术语`. Example:
```
CN: 不可抗力
EN: vis major ["superior violence"]
CN: 不可抗力
EN: force majeure ["superior strength"]
```

### Dual Translations
Some terms have multiple valid translations — present all options when relevant and note the context.

---

## Integration with PKULaw MCP Tools

This skill complements the PKULaw MCP tools already configured. For legal research tasks:

1. **Term lookup first**: Use this skill to find English equivalents
2. **Statutory verification**: Use `mcp__pkulaw-law-search__search_article` to verify the term's usage in actual statutes
3. **Citation validation**: Use `mcp__pkulaw-citation-validator__adjust_provisions` to check legal references
4. **Case reference**: Use `mcp__pkulaw-case-search__search_case` for how terms appear in judicial decisions

Example workflow:
```
User: "How do you say 善意取得 in English?"
1. lookup.py -q "善意取得" → "Bona Fide Acquisition / Good Faith Acquisition"
2. (Optional) mcp__pkulaw-law-search__search_article → verify in Civil Code Art. 311
```

---

## Reference Files

| File | Description |
|------|-------------|
| `references/glossary.csv` | Main terminology database (33,996 entries) |
| `references/mainland_terms.csv` | PRC-specific legal terms (951 entries) |
| `references/german_legal_glossary.csv` | English-German legal terms (472 entries, Wisconsin Courts) |
| `references/us_legal_definitions.csv` | US court legal terms with English definitions (Sacramento Superior Court) |
| `references/source-guide.md` | Source column explanation and data provenance |
| `references/legal-domains.md` | Legal domain classification taxonomy |

## Scripts

| Script | Description |
|--------|-------------|
| `scripts/lookup.py` | Query tool (exact/fuzzy/substring, domain filter, JSON/text output) |

> 数据准备脚本（DOJ 清洗、大陆术语抓取）本地维护、未随仓库分发；清洗与解析策略已在 `references/source-guide.md` 完整说明，可按其复现。

---

## Data Cleaning (Reproducible)

The cleaning script is maintained locally and not distributed with the repository, but the pipeline is fully documented for reproducibility:

The cleaning pipeline:
1. Filters out Hong Kong-specific institutions, roles, and concepts
2. Removes report/consultation paper sources
3. Filters template/placeholder patterns
4. Deduplicates by (CN, EN) with source priority
5. Classifies by legal domain and term type
6. Outputs `references/glossary.csv`

Source priority for deduplication: 英汉民商事法律词汇 > 刑事诉讼词汇集 > PRC Law > HK Ordinance > Other

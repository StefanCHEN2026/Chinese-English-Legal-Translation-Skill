# 数据来源说明 (Source Guide)

## 术语库来源

### glossary.csv (~34,000 条)

原始数据来自 **香港律政司 (Department of Justice, Hong Kong)** 双语法律词汇表。

| 原始来源 | 占比 | 说明 |
|---------|------|------|
| 英汉民商事法律词汇 | ~38% | 通用英汉法律词典，非香港独有，质量最高 |
| 香港法例（第XX章） | ~40% | 香港条例中引用的通用法律术语 |
| 刑事诉讼词汇集 | ~7% | 刑事程序专门词汇 |
| 中国大陆法律 | ~1% | 宪法、民法典等大陆法律引用 |
| 其他 | ~14% | 条约、基本法、其他来源 |

**清洗标准（温和策略）：**
- ✅ 保留：通用法律词典来源、刑事诉讼词汇、大陆法律来源
- ✅ 保留：香港条例中不包含香港独有机构的通用术语
- ❌ 移除：纯报告/咨询文件来源
- ❌ 移除：包含香港独有机构（立法会、律政司等）、角色（大律师等）、概念（新界、乡事等）
- ❌ 移除：模板/占位符条目（......所衍生、......所附带）

**去重策略**：按 `(中文词语, 英文词语)` 去重，来源优先级：英汉民商事法律词汇 > 刑事诉讼词汇集 > 中国大陆法律 > 香港条例 > 其他

**注意**：
- 该数据源自香港普通法体系，部分翻译风格偏向英式/common law 表达
- 对于中国大陆法律体系中的特色概念，请参考 `mainland_terms.csv`
- 拉丁术语以双语格式保留（如 `force majeure ["superior strength"]`）

### mainland_terms.csv (~950 条)

精选中国大陆法律体系特色术语，来源包括：

1. **中华人民共和国民法典** (Civil Code of the PRC, 2021)
2. **中华人民共和国刑法** (Criminal Law of the PRC)
3. **中华人民共和国公司法** (Company Law of the PRC)
4. **中华人民共和国宪法** (Constitution of the PRC)
5. **三大诉讼法** (Civil/Criminal/Administrative Procedure Laws)
6. **最高人民法院司法解释**

**特点**：
- 覆盖 PRC 社会主义法律体系的独特概念
- 使用中国大陆官方翻译标准（如 NPC 英文版用语）
- 与 glossary.csv 互补：glossary.csv 偏 common law，mainland_terms.csv 偏 PRC civil law

### german_legal_glossary.csv (472 条)

| 项目 | 说明 |
|------|------|
| **来源** | 威斯康星州法院系统（Wisconsin Court System）法庭口译服务发布的《Glossary of Legal Terminology – English–German》 |
| **编者** | 编译 Dustin DeGrande（German Translator），Dagmar Grimm 修订 |
| **URL** | https://www.wicourts.gov/services/interpreter/docs/germanglossary.pdf |
| **收录日期** | 2026-10-24 |
| **内容** | 472 条英→德对照法律术语，每条附英文释义（括号内）与词性（n./v./adj.） |
| **文件结构** | `英文词语, 德文词语, 英文释义, 词性, 来源, 领域, 类型` |
| **处理方式** | 从原 PDF 提取文本（pymupdf），按空行分块、以 `- n./v./adj.` 词性标记切分英德字段；保留原文德语变体（如 `/` 分隔的多种译法）与英文释义 |

**注意**：
- 该表为英-德对照，**不含中文**。查询英文术语时可同时返回中文翻译（来自其他词表）与德文对照
- 12 条无词性标记的条目（如 motion granted / objection overruled）已按 `)- 分隔` 模式解析，词性留空

### us_legal_definitions.csv (~1,300 条)

| 项目 | 说明 |
|------|------|
| **内容来源** | 加州萨克拉门托县高等法院（Superior Court of California, County of Sacramento）《English Legal Glossary》 |
| **发布页面** | 由康特拉科斯塔县高等法院（Superior Court of California, County of Contra Costa）网站托管 |
| **URL** | https://contracosta.courts.ca.gov/system/files/general/english-legal-glossary.pdf |
| **收录日期** | 2026-10-24 |
| **内容** | 英文法律术语 + 面向公众的英文释义（美国加州法院实务用语，约 65 页） |
| **文件结构** | `英文词语, 英文释义, 中文对照, 来源, 领域, 类型` |
| **中文对照** | **回填字段**：按英文词语（含单复数变体）精确匹配 `glossary.csv` / `mainland_terms.csv` 得到，最多保留 3 个中文对应词；并非来源文件自带，引用时请注意区分 |

**注意**：
- 该词汇表为纯英文（术语+释义），中文对照为回填所得
- 术语为美国加州法院用语，部分概念（如 PC 1203.4 MOTION、W&I Code 相关条目）带有加州成文法特色，与香港/大陆法系术语体系不完全对应

---

## 使用许可

### 香港 DOJ 数据
香港律政司双语词汇表为政府公开数据。使用前请查阅香港政府数据使用条款：
- https://www.doj.gov.hk/en/publications/glossary.html

### 美国法院词汇表
- **威斯康星州法院《英德法律词汇表》**：威斯康星州法院系统公开发布的口译服务资料，版权归原发布机构所有，转载请注明来源
- **萨克拉门托县高等法院《English Legal Glossary》**：加州法院面向公众发布的语言辅助资料，版权归原发布机构所有，转载请注明来源

两者均为美国州法院公开资料，收录时已注明来源与日期；再分发请保留署名并遵循原发布机构的使用条款。

### 大陆法律术语
中国大陆法律术语翻译基于 NPC 官方翻译和公开学术资料。

本仓库采用**双许可**：代码与文档（scripts/、SKILL.md 及 .md 文档）采用 **MIT**；术语数据（references/*.csv）采用 **CC BY-NC 4.0（署名-非商业性使用）**。各数据来源的许可信息在具体使用场景中请自行核实。

---

## 数据质量说明

| 质量维度 | 评级 | 说明 |
|---------|------|------|
| 翻译准确性 | ⭐⭐⭐⭐ | 基于 DOJ 专业双语法律翻译 |
| 大陆适用性 | ⭐⭐⭐ | 主体为 common law 体系，大陆术语需用 mainland_terms.csv 补充 |
| 覆盖全面性 | ⭐⭐⭐⭐ | 33,000+ 通用术语 + 950+ 大陆特色术语 + 472 英德对照 + 美国法院释义 |
| 分类准确性 | ⭐⭐⭐ | 领域分类基于关键词匹配，约 90% 标注为「通用」，v1.2 将改进 |
| 去重完整性 | ⭐⭐⭐⭐⭐ | 按 (CN, EN) 严格去重，保留最优来源 |

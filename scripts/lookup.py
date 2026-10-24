#!/usr/bin/env python3
"""
法律术语查询工具（中英互译 + 英德对照 + 美国法院术语释义）
支持精确匹配、子串搜索、模糊匹配，以及按领域/来源筛选。

用法：
    # 精确查询
    python lookup.py -q "不可抗力"
    python lookup.py -q "force majeure"

    # 模糊查询
    python lookup.py -q "合同违约" --fuzzy

    # 子串搜索
    python lookup.py -q "仲裁" --substring

    # 按领域筛选
    python lookup.py -q "证据" --domain 诉讼法

    # 英德对照（自动查询 german_legal_glossary.csv）
    python lookup.py -q "witness"

    # JSON 输出
    python lookup.py -q "tort" --format json

    # 限制结果数
    python lookup.py -q "party" --limit 10
"""

import csv
import argparse
import json
import os
import sys
from difflib import SequenceMatcher

# ========== 配置 ==========

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF_DIR = os.path.join(SKILL_DIR, 'references')

# 按优先级加载的默认术语库（存在即加载）
DEFAULT_FILES = [
    'glossary.csv',               # 通用法律术语（香港律政司 DOJ 清洗版）
    'mainland_terms.csv',         # 中国大陆法律术语
    'german_legal_glossary.csv',  # 英德法律术语（威斯康星州法院）
    'us_legal_definitions.csv',   # 美国法院术语释义（加州萨克拉门托）
]


def load_glossary(path):
    """加载术语库CSV（自动识别表头结构）"""
    entries = []
    if not os.path.exists(path):
        return entries

    with open(path, 'r', encoding='utf-8-sig', errors='replace') as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header is None:
            return entries
        cols = [h.strip() for h in header]

        def idx(name):
            return cols.index(name) if name in cols else None

        if '德文词语' in cols:
            # 英德对照结构: 英文词语,德文词语,英文释义,词性,来源,领域,类型
            i_en, i_de, i_def = idx('英文词语'), idx('德文词语'), idx('英文释义')
            i_pos, i_src, i_dom, i_typ = idx('词性'), idx('来源'), idx('领域'), idx('类型')
            for row in reader:
                if len(row) <= i_de:
                    continue
                entries.append({
                    'cn': '', 'en': row[i_en].strip(), 'de': row[i_de].strip(),
                    'definition': row[i_def].strip() if i_def is not None else '',
                    'pos': row[i_pos].strip() if i_pos is not None else '',
                    'source': row[i_src].strip() if i_src is not None else '',
                    'domain': row[i_dom].strip() if i_dom is not None else '通用',
                    'type': row[i_typ].strip() if i_typ is not None else '',
                })
        elif '英文释义' in cols:
            # 美国法院释义结构: 英文词语,英文释义,中文对照,来源,领域,类型
            i_en, i_def, i_cn = idx('英文词语'), idx('英文释义'), idx('中文对照')
            i_src, i_dom, i_typ = idx('来源'), idx('领域'), idx('类型')
            for row in reader:
                if len(row) <= i_def:
                    continue
                entries.append({
                    'cn': row[i_cn].strip() if i_cn is not None else '',
                    'en': row[i_en].strip(), 'de': '',
                    'definition': row[i_def].strip(),
                    'pos': '',
                    'source': row[i_src].strip() if i_src is not None else '',
                    'domain': row[i_dom].strip() if i_dom is not None else '通用',
                    'type': row[i_typ].strip() if i_typ is not None else '',
                })
        else:
            # 经典结构: 中文词语,英文词语,来源,领域,类型
            for row in reader:
                if len(row) >= 2:
                    entries.append({
                        'cn': row[0].strip(),
                        'en': row[1].strip(),
                        'de': '',
                        'definition': '',
                        'pos': '',
                        'source': row[2].strip() if len(row) > 2 else '',
                        'domain': row[3].strip() if len(row) > 3 else '通用',
                        'type': row[4].strip() if len(row) > 4 else '',
                    })
    return entries


def similarity(a, b):
    """计算两个字符串的相似度 (0-1)"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def search_exact(entries, query):
    """精确匹配：中文、英文或德文完全相等"""
    results = []
    q_lower = query.lower().strip()

    for entry in entries:
        if (entry['cn'].lower() == q_lower or entry['en'].lower() == q_lower
                or entry['de'].lower() == q_lower):
            results.append((entry, 1.0))
    return results


def _field_score(q_lower, value, q_words):
    """单个字段的子串匹配打分（与既有英文打分规则一致）"""
    if not value or q_lower not in value.lower():
        return 0
    score = len(q_lower) / max(len(value), 1)
    words = value.lower().split()
    if any(qw in words for qw in q_words):
        score += 0.3
    return min(score, 1.0)


def search_substring(entries, query):
    """子串匹配：中文、英文或德文包含查询词"""
    results = []
    q_lower = query.lower().strip()
    q_words = q_lower.split()

    for entry in entries:
        score = max(
            _field_score(q_lower, entry['cn'], q_words),
            _field_score(q_lower, entry['en'], q_words),
            _field_score(q_lower, entry['de'], q_words),
        )
        if score > 0:
            results.append((entry, score))
    return results


def search_fuzzy(entries, query, threshold=0.4):
    """模糊匹配：计算相似度"""
    results = []
    q_lower = query.lower().strip()

    for entry in entries:
        sims = [similarity(v, q_lower)
                for v in (entry['cn'], entry['en'], entry['de']) if v]
        for v in (entry['cn'], entry['en'], entry['de']):
            if v and q_lower in v.lower():
                sims.append(0.7 + 0.3 * len(q_lower) / max(len(v), 1))
        best = max(sims) if sims else 0
        if best >= threshold:
            results.append((entry, best))

    return results


def filter_by_domain(results, domain):
    """按法律领域筛选"""
    return [(e, s) for e, s in results if e['domain'] == domain]


def _entry_title(entry):
    """结果标题：优先中文，无中文（纯英文释义条目）用英文"""
    return entry['cn'] or entry['en']


def format_text(results, query, show_source=True):
    """文本格式输出"""
    if not results:
        return f"未找到与 \"{query}\" 匹配的术语。"

    lines = []
    lines.append(f"查询: \"{query}\"")
    lines.append(f"找到 {len(results)} 条结果:")
    lines.append("-" * 60)

    for i, (entry, score) in enumerate(results, 1):
        title = _entry_title(entry)
        lines.append(f"\n[{i}] {title}")
        if entry['en'] and entry['en'] != title:
            lines.append(f"    EN: {entry['en']}")
        if entry['de']:
            lines.append(f"    DE: {entry['de']}")
        if entry['definition']:
            lines.append(f"    释义: {entry['definition']}")
        if show_source and entry['source']:
            lines.append(f"    来源: {entry['source']}")
        meta = [m for m in (entry['pos'], entry['type']) if m]
        if entry['domain'] and entry['domain'] != '通用':
            meta.insert(0, entry['domain'])
        if meta:
            lines.append(f"    标签: {', '.join(meta)}")
        if score < 1.0:
            lines.append(f"    匹配度: {score:.0%}")

    return '\n'.join(lines)


def format_json(results, query):
    """JSON 格式输出"""
    output = {
        'query': query,
        'count': len(results),
        'results': []
    }
    for entry, score in results:
        item = {
            'cn': entry['cn'],
            'en': entry['en'],
            'source': entry['source'],
            'domain': entry['domain'],
            'type': entry['type'],
            'score': round(score, 3),
        }
        if entry['de']:
            item['de'] = entry['de']
        if entry['definition']:
            item['definition'] = entry['definition']
        if entry['pos']:
            item['pos'] = entry['pos']
        output['results'].append(item)
    return json.dumps(output, ensure_ascii=False, indent=2)


def format_csv_output(results, query):
    """CSV 格式输出"""
    lines = ['中文词语,英文词语,德文词语,来源,领域,类型,匹配度']
    for entry, score in results:
        lines.append(f'"{entry["cn"]}","{entry["en"]}","{entry["de"]}",'
                     f'"{entry["source"]}","{entry["domain"]}","{entry["type"]}",{score:.3f}')
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='法律术语查询工具（中英互译 + 英德对照 + 美国法院术语释义）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python lookup.py -q "不可抗力"
  python lookup.py -q "negligence" --fuzzy
  python lookup.py -q "仲裁" --substring --domain 诉讼法
  python lookup.py -q "witness"            # 英德对照 + 中文翻译一起返回
  python lookup.py -q "Zeuge"              # 德文查询
  python lookup.py -q "tort" --format json
        """
    )
    parser.add_argument('-q', '--query', required=True, help='查询词（中文/英文/德文）')
    parser.add_argument('--fuzzy', action='store_true', help='启用模糊匹配')
    parser.add_argument('--substring', '-s', action='store_true', help='子串搜索模式（默认）')
    parser.add_argument('--exact', '-e', action='store_true', help='仅精确匹配')
    parser.add_argument('--domain', '-d', default=None, help='按法律领域筛选')
    parser.add_argument('--source', default=None, help='按来源筛选')
    parser.add_argument('--limit', '-n', type=int, default=20, help='最大返回结果数 (默认: 20)')
    parser.add_argument('--format', '-f', default='text', choices=['text', 'json', 'csv'],
                        help='输出格式 (默认: text)')
    parser.add_argument('--glossary', '-g', default=None, help='指定术语库CSV路径')
    parser.add_argument('--no-source', action='store_true', help='不显示来源信息')

    args = parser.parse_args()

    # 加载术语库
    paths = []
    if args.glossary:
        paths.append(args.glossary)
    else:
        for name in DEFAULT_FILES:
            p = os.path.join(REF_DIR, name)
            if os.path.exists(p):
                paths.append(p)

    entries = []
    for path in paths:
        loaded = load_glossary(path)
        entries.extend(loaded)
        if loaded:
            print(f"已加载 {os.path.basename(path)}: {len(loaded)} 条", file=sys.stderr)

    if not entries:
        print("错误: 未找到任何术语库文件", file=sys.stderr)
        return 1

    # 去重（保留先加载的；德文/来源字段参与键值）
    seen = set()
    unique_entries = []
    for e in entries:
        key = (e['cn'], e['en'], e['de'], e['source'])
        if key not in seen:
            seen.add(key)
            unique_entries.append(e)
    entries = unique_entries

    # 搜索
    query = args.query.strip()

    if args.exact:
        results = search_exact(entries, query)
    elif args.fuzzy:
        results = search_fuzzy(entries, query)
    else:
        # 先精确匹配
        results = search_exact(entries, query)
        if not results:
            # 再子串匹配
            results = search_substring(entries, query)

    # 按来源筛选
    if args.source:
        results = [(e, s) for e, s in results if args.source in e['source']]

    # 排序（按匹配度降序）
    results.sort(key=lambda x: x[1], reverse=True)

    # 按领域筛选
    if args.domain:
        results = filter_by_domain(results, args.domain)

    # 限制数量
    results = results[:args.limit]

    # 输出
    show_source = not args.no_source
    if args.format == 'json':
        print(format_json(results, query))
    elif args.format == 'csv':
        print(format_csv_output(results, query))
    else:
        print(format_text(results, query, show_source))

    return 0


if __name__ == '__main__':
    exit(main())

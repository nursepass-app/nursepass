#!/usr/bin/env python3
"""
questions.json を field ごとに分割し questions/ ディレクトリに保存。
questions_index.json を生成する。
"""
import json, os, re
from collections import defaultdict, Counter

SRC = 'questions.json'
OUT_DIR = 'questions'
INDEX_FILE = 'questions_index.json'


def to_filename(field: str) -> str:
    name = re.sub(r'[・/\\:*?"<>|＊]', '_', field)
    return name.strip('_') or 'unknown'


def main():
    with open(SRC, encoding='utf-8') as f:
        data = json.load(f)

    groups: dict[str, list] = defaultdict(list)
    for q in data:
        groups[q['field']].append(q)

    os.makedirs(OUT_DIR, exist_ok=True)

    subjects = []
    for idx, field in enumerate(sorted(groups.keys()), 1):
        qs = groups[field]
        fname = f'questions_{idx:02d}_{to_filename(field)}.json'
        path = f'{OUT_DIR}/{fname}'

        stars_dist = dict(sorted(Counter(q['stars'] for q in qs).items()))
        cat_dist   = dict(sorted(Counter(q['category'] for q in qs).items()))

        with open(path, 'w', encoding='utf-8') as f:
            json.dump({'field': field, 'questions': qs}, f, ensure_ascii=False)

        subjects.append({
            'field':      field,
            'path':       path,
            'count':      len(qs),
            'categories': cat_dist,
            'stars':      {str(k): v for k, v in stars_dist.items()},
        })
        print(f'  [{idx:02d}] {field}: {len(qs)}問 → {path}')

    index = {
        'total':    len(data),
        'version':  '1.0',
        'subjects': subjects,
    }
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    print(f'\n✅ {len(subjects)}科目を生成。合計{len(data)}問。')
    print(f'   {INDEX_FILE} を出力しました。')


if __name__ == '__main__':
    main()

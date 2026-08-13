"""查 screening 结果批次分布与 bg_45 对应. 用法: python3 extract_candidates.py <json_path>"""
import json
import sys

path = sys.argv[1] if len(sys.argv) > 1 else '/mnt/d/nature reproduction/mattergen/screening_extended_result.json'
with open(path, encoding='utf-8') as f:
    data = json.load(f)

from collections import Counter
batches = Counter(r['batch'] for r in data['results'])
print('批次分布:', dict(batches))
print('bg_45 数量:', batches.get('bg_45', 0))
hits = [r for r in data['results'] if r.get('formula') == 'BaF6Si']
for r in hits:
    print('BaF6Si:', r.get('batch'), r.get('index'), r.get('n_atoms'))

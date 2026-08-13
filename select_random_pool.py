"""确认随机抽样候选的 batch/index/Ef"""
import json

path = '/mnt/d/nature reproduction/mattergen/screening_extended_result.json'
with open(path, encoding='utf-8') as f:
    data = json.load(f)
results = data['results']

targets = ['C2N2', 'O5', 'H4Na2', 'C2Li6N4', 'F2O2', 'Hg2O8S2', 'Cl3LiPb']
for t in targets:
    hits = [r for r in results if r.get('formula') == t]
    print(f'\n{t} ({len(hits)} 条):')
    for r in hits:
        el = ''.join(r.get('elements', {}).keys())
        print(f"  batch={r.get('batch')} idx={r.get('index')} n={r.get('n_atoms')} "
              f"Ef={r.get('formation_energy'):+.3f} 元素={el}")

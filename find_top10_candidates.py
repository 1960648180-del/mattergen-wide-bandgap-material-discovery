"""从 screening_extended_result.json 查目标候选的 batch/index"""
import json

with open(r'd:\nature reproduction\mattergen\screening_extended_result.json', encoding='utf-8') as f:
    data = json.load(f)

targets = ['F3Sc', 'F3La', 'BaF6Si', 'BaF6Si2']
print('target formula → batch/index 列表:')
for t in targets:
    hits = [r for r in data['results'] if r.get('formula') == t]
    print(f'\n{t} ({len(hits)} 条):')
    for r in hits[:10]:
        print(f"  batch={r.get('batch')} index={r.get('index')} n_atoms={r.get('n_atoms')} "
              f"Ef={r.get('formation_energy', 0):.3f} elements={r.get('elements')}")

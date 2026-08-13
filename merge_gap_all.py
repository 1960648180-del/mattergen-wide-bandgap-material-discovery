"""
补救完成后: 合并主表 + 补救结果 -> gap_all_merged.json + 三层统计
用法: python3 merge_gap_all.py
- 首次完成: 主表 gap_all.json (source 保留原始来源)
- 补救完成: gap_remedy_results/*.json (标 remedy='补救', 同口径4×4×4)
- 仍未收敛: 195 - 总完成数
- 覆盖率: 完成数/195
"""
import json
from pathlib import Path
from collections import Counter

TOTAL = 195
MAIN = Path('/mnt/d/nature reproduction/mattergen/gap_all.json')
META = Path('/mnt/d/nature reproduction/mattergen/candidates_meta.json')
REMEDY = Path('/home/isaac/p1_dft/gap_remedy_results')
OUT = Path('/mnt/d/nature reproduction/mattergen/gap_all_merged.json')

main = json.loads(MAIN.read_text(encoding='utf-8'))
meta = json.loads(META.read_text(encoding='utf-8')) if META.exists() else {}
main_forms = {r['formula'] for r in main}

def classify(form, m):
    has_F = m.get('has_F', ('F' in form))
    has_O = ('O' in form)
    if has_F and has_O:
        return '氧氟'
    elif has_F:
        return '氟'
    return '非氟'

remedy_rows = []
for jf in sorted(REMEDY.glob('*.json')):
    try:
        d = json.loads(jf.read_text(encoding='utf-8'))
        if not d or d[0].get('pbe_bandgap') is None:
            continue
        r = d[0]
        form = r['formula']
        if form in main_forms:
            continue
        m = meta.get(form, {})
        gap = r['pbe_bandgap']
        remedy_rows.append({
            'formula': form, 'bandgap_eV': gap, 'category': classify(form, m),
            'near_metal': gap < 0.2, 'has_f': m.get('has_f', False),
            'n_atoms': r['n_atoms'], 'energy_per_atom': r['energy_per_atom'],
            'mag_uB': r.get('mag_moment_uB'), 'source': m.get('source', ''),
            'chgnet_E': m.get('chgnet_E'), 'homo': r.get('homo'),
            'lumo': r.get('lumo'), 'kpts': r.get('kpts'),
            'remedy': '补救',
        })
    except Exception:
        continue

for r in main:
    r['remedy'] = '首次'

merged = main + remedy_rows
merged.sort(key=lambda x: -x['bandgap_eV'])
OUT.write_text(json.dumps(merged, indent=2, ensure_ascii=False), encoding='utf-8')

n_main = len(main)
n_remedy = len(remedy_rows)
n_total = n_main + n_remedy
n_missing = TOTAL - n_total
print('=== 三层统计 ===')
print(f'首次完成: {n_main}')
print(f'补救完成: {n_remedy}')
print(f'仍未收敛: {n_missing}')
print(f'总完成:   {n_total} / {TOTAL}  覆盖率 {n_total/TOTAL*100:.1f}%')
print('\n体系分布(合并后):', dict(Counter(r['category'] for r in merged)))
print('近金属(gap<0.2):', sum(1 for r in merged if r['near_metal']))
print('含f:', sum(1 for r in merged if r['has_f']))
print('\nTop 12 (合并后):')
for r in merged[:12]:
    print(f"  {r['formula']:<14} gap={r['bandgap_eV']:.3f} | {r['category']} | "
          f"{r['remedy']} | f={'Y' if r['has_f'] else 'N'} | n={r['n_atoms']}")
print(f'\n输出: {OUT}')

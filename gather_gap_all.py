"""
汇总全量带隙结果 -> gap_all.json (带类别列)
用法: python3 gather_gap_all.py [gap_results_dir] [meta_json] [out_json]
- 类别: 体系(氟/非氟/氧氟)  近金属标记(gap<0.2)  含f标记(has_f)
"""
import json, sys
from pathlib import Path

WSL_DIR = Path('/home/isaac/p1_dft/gap_all_results')
META = Path('/mnt/d/nature reproduction/mattergen/candidates_meta.json')
OUT = Path('/mnt/d/nature reproduction/mattergen/gap_all.json')

if len(sys.argv) > 1: WSL_DIR = Path(sys.argv[1])
if len(sys.argv) > 2: META = Path(sys.argv[2])
if len(sys.argv) > 3: OUT = Path(sys.argv[3])

meta = json.loads(META.read_text(encoding='utf-8')) if META.exists() else {}

rows = []
for jf in sorted(WSL_DIR.glob('*.json')):
    try:
        data = json.loads(jf.read_text(encoding='utf-8'))
    except Exception:
        continue
    if not data:  # 空列表 = 失败
        continue
    r = data[0]
    form = r['formula']
    gap = r['pbe_bandgap']
    m = meta.get(form, {})
    has_F = m.get('has_F', ('F' in form))
    has_O = ('O' in form)
    # 体系分类
    if has_F and has_O:
        cat = '氧氟'
    elif has_F:
        cat = '氟'
    else:
        cat = '非氟'
    rows.append({
        'formula': form,
        'bandgap_eV': gap,
        'category': cat,          # 体系: 氟/非氟/氧氟
        'near_metal': gap < 0.2,  # 近金属标记
        'has_f': m.get('has_f', False),  # 含f(镧系/锕系)标记
        'n_atoms': r['n_atoms'],
        'energy_per_atom': r['energy_per_atom'],
        'mag_uB': r.get('mag_moment_uB'),
        'source': m.get('source', ''),
        'chgnet_E': m.get('chgnet_E'),
        'homo': r.get('homo'),
        'lumo': r.get('lumo'),
        'kpts': r.get('kpts'),
    })

rows.sort(key=lambda x: -x['bandgap_eV'])
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding='utf-8')

# 汇总
from collections import Counter
print(f'总候选: {len(rows)}')
print('按体系:', dict(Counter(r["category"] for r in rows)))
print('近金属(gap<0.2):', sum(1 for r in rows if r['near_metal']))
print('含f元素:', sum(1 for r in rows if r['has_f']))
print('\nTop 12 带隙:')
for r in rows[:12]:
    print(f"  {r['formula']:<14} gap={r['bandgap_eV']:.3f} | {r['category']} | "
          f"{'近金属' if r['near_metal'] else '   '} | f={'Y' if r['has_f'] else 'N'} | "
          f"n={r['n_atoms']} | {r['source']}")
print(f'\n输出: {OUT}')

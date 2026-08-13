"""深入分析: 氟化物偏差分布 + 近金属构成, 确认结论走向"""
import json, re
from pathlib import Path

GAP = Path('/mnt/d/nature reproduction/mattergen/gap_all.json')
REMEDY = Path('/home/isaac/p1_dft/gap_remedy_results')
META = Path('/mnt/d/nature reproduction/mattergen/candidates_meta.json')

def target_from_source(src):
    m = re.search(r'bg_(\d+)', src or '')
    return int(m.group(1)) / 10.0 if m else None

meta = json.loads(META.read_text(encoding='utf-8'))
rows = []
main_forms = set()
for r in json.loads(GAP.read_text(encoding='utf-8')):
    r['remedy'] = '首次'; rows.append(r); main_forms.add(r['formula'])
for jf in sorted(REMEDY.glob('*.json')):
    try:
        d = json.loads(jf.read_text(encoding='utf-8'))
        if not d or d[0].get('pbe_bandgap') is None: continue
        r = d[0]; form = r['formula']
        if form in main_forms: continue
        m = meta.get(form, {})
        gap = r['pbe_bandgap']
        has_F = m.get('has_F', 'F' in form)
        has_O = 'O' in form
        rows.append({'formula': form, 'bandgap_eV': gap,
                     'category': '氧氟' if (has_F and has_O) else ('氟' if has_F else '非氟'),
                     'near_metal': gap < 0.2, 'has_f': m.get('has_f', False),
                     'source': m.get('source', ''), 'remedy': '补救'})
    except Exception: continue

for r in rows:
    r['target'] = target_from_source(r.get('source', ''))
    r['dev'] = r['bandgap_eV'] - r['target'] if r['target'] is not None else None

print(f'有带隙总数: {len(rows)}, 近金属(gap<0.2): {sum(1 for r in rows if r["near_metal"])}\n')

# 氟化物完整偏差列表 (有目标的)
print('=== 氟化物偏差明细 (有目标) ===')
fl = [r for r in rows if r['category'] == '氟' and r['target'] is not None]
for r in sorted(fl, key=lambda x: x['dev']):
    mark = '近金属' if r['near_metal'] else '     '
    print(f"  {r['formula']:<12} 目标={r['target']:.1f} 实测={r['bandgap_eV']:.3f} 偏差={r['dev']:+.2f} {mark} ({r['remedy']})")

# 近金属的体系分布
print('\n=== 近金属(gap<0.2) 体系构成 ===')
nm = [r for r in rows if r['near_metal']]
from collections import Counter
print(dict(Counter(r['category'] for r in nm)))
print('近金属中含f:', sum(1 for r in nm if r['has_f']), '/', len(nm))

# 非氟负偏差主因: 近金属拉低?
print('\n=== 非氟(有目标)分 gap 区间 ===')
nf = [r for r in rows if r['category'] == '非氟' and r['target'] is not None]
lo = [r for r in nf if r['bandgap_eV'] < 0.2]
hi = [r for r in nf if r['bandgap_eV'] >= 0.2]
print(f'非氟总数: {len(nf)}, 其中近金属(<0.2): {len(lo)}, 非近金属: {len(hi)}')
if lo:
    devs = [r['dev'] for r in lo]
    print(f'近金属非氟偏差均值: {sum(devs)/len(devs):+.2f} (n={len(lo)})')
if hi:
    devs = [r['dev'] for r in hi]
    print(f'非近金属非氟偏差均值: {sum(devs)/len(devs):+.2f} (n={len(hi)})')

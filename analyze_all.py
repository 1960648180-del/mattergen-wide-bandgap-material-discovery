"""
确定补救样本的目标归属 + 基于全部样本计算大体趋势
- 补救成功61个: 分 条件生成(有target) / 开放生成(无target)
- 全部样本趋势: 条件生成池偏差 + 无目标样本分布 + 整体
"""
import json, re
from pathlib import Path
from collections import Counter

GAP = Path('/mnt/d/nature reproduction/mattergen/gap_all.json')
REMEDY = Path('/home/isaac/p1_dft/gap_remedy_results')
META = Path('/mnt/d/nature reproduction/mattergen/candidates_meta.json')

def target_from_source(src):
    src = src or ''
    m = re.search(r'bg_(\d+)', src)
    if m:
        return int(m.group(1)) / 10.0
    m2 = re.search(r'bandgap_(\d+)', src)
    if m2:
        return int(m2.group(1)) / 10.0
    return None

meta = json.loads(META.read_text(encoding='utf-8'))

def classify(form, m):
    has_F = m.get('has_F', 'F' in form)
    has_O = 'O' in form
    return '氧氟' if (has_F and has_O) else ('氟' if has_F else '非氟')

# ---- 补救样本分析 ----
print('=== 补救成功样本 (61) 的目标归属 ===')
remedy_cf, remedy_oe = [], []
for jf in sorted(REMEDY.glob('*.json')):
    try:
        d = json.loads(jf.read_text(encoding='utf-8'))
        if not d or d[0].get('pbe_bandgap') is None:
            continue
        form = d[0]['formula']
        src = meta.get(form, {}).get('source', '')
        t = target_from_source(src)
        gap = d[0]['pbe_bandgap']
        if t is not None:
            remedy_cf.append((form, t, gap, src))
        else:
            remedy_oe.append((form, gap, src))
    except Exception:
        continue

print(f'补救中条件生成(有目标): {len(remedy_cf)}')
for form, t, gap, src in sorted(remedy_cf, key=lambda x: x[2]):
    print(f'  {form:<12} 目标={t:.1f} 实测={gap:.3f} 偏差={gap-t:+.2f} ({src})')
print(f'补救中开放生成(无目标): {len(remedy_oe)}')
for form, gap, src in sorted(remedy_oe, key=lambda x: -x[1]):
    print(f'  {form:<12} 实测={gap:.3f} ({src})')

# ---- 全部样本趋势 ----
print('\n=== 全部样本 (首轮124 + 补救61 = 185) ===')
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
        rows.append({'formula': form, 'bandgap_eV': gap,
                     'category': classify(form, m), 'near_metal': gap < 0.2,
                     'has_f': m.get('has_f', False), 'source': m.get('source', ''),
                     'remedy': '补救'})
    except Exception: continue

for r in rows:
    r['target'] = target_from_source(r.get('source', ''))
    r['dev'] = r['bandgap_eV'] - r['target'] if r['target'] is not None else None

cf = [r for r in rows if r['target'] is not None]
oe = [r for r in rows if r['target'] is None]
print(f'条件生成(有目标): {len(cf)}, 开放生成(无目标): {len(oe)}')
print(f'近金属(gap<0.2): {sum(1 for r in rows if r["near_metal"])} / {len(rows)} = {sum(1 for r in rows if r["near_metal"])/len(rows)*100:.0f}%')

# 条件生成偏差(主统计)
print('\n--- 条件生成池偏差 (主统计) ---')
for cat in ['氟', '非氟', '氧氟']:
    g = [r for r in cf if r['category'] == cat]
    if not g: continue
    devs = [r['dev'] for r in g]
    n = len(devs)
    nm = sum(1 for r in g if r['near_metal'])
    print(f"{cat:<4} n={n:>3} 偏差均值={sum(devs)/n:>+7.2f} MAE={sum(abs(d) for d in devs)/n:>6.2f} "
          f"正偏={sum(1 for d in devs if d>0)/n*100:>4.0f}% 近金属={nm} [{min(devs):+.1f},{max(devs):+.1f}]")
if cf:
    devs = [r['dev'] for r in cf]
    n = len(devs)
    print(f"全部 n={n:>3} 偏差均值={sum(devs)/n:>+7.2f} MAE={sum(abs(d) for d in devs)/n:>6.2f} "
          f"正偏={sum(1 for d in devs if d>0)/n*100:>4.0f}% 近金属={sum(1 for r in cf if r['near_metal'])}")

# 无目标样本分布
print('\n--- 开放生成(无目标) 带隙分布 ---')
oe_gaps = [r['bandgap_eV'] for r in oe]
oe_nm = sum(1 for r in oe if r['near_metal'])
print(f'n={len(oe_gaps)}, 中位={sorted(oe_gaps)[len(oe_gaps)//2]:.2f}, 近金属={oe_nm} ({oe_nm/len(oe_gaps)*100:.0f}%)')
print('体系:', dict(Counter(r['category'] for r in oe)))
print('带隙范围:', f'[{min(oe_gaps):.2f}, {max(oe_gaps):.2f}]')

# 整体趋势总结
print('\n=== 整体趋势 ===')
print(f'全池 {len(rows)}: 条件生成 {len(cf)}, 开放生成 {len(oe)}')
print(f'近金属占 {sum(1 for r in rows if r["near_metal"])/len(rows)*100:.0f}%')

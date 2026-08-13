"""
用当前全量数据(首轮+补救)重新验证核心结论: 氟化物系统性正偏差
- 从 source 映射目标带隙 (bg_25->2.5, bg_30->3.0 ...)
- 分组统计: 氟/非氟/氧氟 的偏差均值/MAE/正偏差比例
用法: python3 analyze_bias.py
"""
import json, re
from pathlib import Path
from collections import defaultdict

GAP = Path('/mnt/d/nature reproduction/mattergen/gap_all.json')
REMEDY = Path('/home/isaac/p1_dft/gap_remedy_results')
META = Path('/mnt/d/nature reproduction/mattergen/candidates_meta.json')

def target_from_source(src):
    m = re.search(r'bg_(\d+)', src or '')
    if m:
        return int(m.group(1)) / 10.0
    return None  # results/widegap/bulk_150 无明确目标带隙

meta = json.loads(META.read_text(encoding='utf-8')) if META.exists() else {}

def classify(form, m):
    has_F = m.get('has_F', 'F' in form)
    has_O = 'O' in form
    return '氧氟' if (has_F and has_O) else ('氟' if has_F else '非氟')

# 合并: 主表 + 补救
rows = []
main_forms = set()
for r in json.loads(GAP.read_text(encoding='utf-8')):
    r['remedy'] = '首次'
    rows.append(r)
    main_forms.add(r['formula'])
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
        rows.append({'formula': form, 'bandgap_eV': gap, 'category': classify(form, m),
                     'near_metal': gap < 0.2, 'has_f': m.get('has_f', False),
                     'n_atoms': r['n_atoms'], 'energy_per_atom': r['energy_per_atom'],
                     'mag_uB': r.get('mag_moment_uB'), 'source': m.get('source', ''),
                     'homo': r.get('homo'), 'lumo': r.get('lumo'),
                     'remedy': '补救'})
    except Exception:
        continue

# 加目标带隙
for r in rows:
    r['target'] = target_from_source(r.get('source', ''))
    if r['target'] is not None:
        r['dev'] = r['bandgap_eV'] - r['target']

print(f'总候选(有带隙): {len(rows)}')
print(f'有明确目标带隙(可算偏差): {sum(1 for r in rows if r["target"] is not None)}')
print(f'开放生成无目标(results系): {sum(1 for r in rows if r["target"] is None)}\n')

# 分组统计(仅对有目标的)
groups = defaultdict(list)
for r in rows:
    if r['target'] is not None:
        groups[r['category']].append(r)

print('=== 偏差统计 (DFT实测 - 目标带隙, 单位 eV) ===')
print(f"{'体系':<6}{'n':>4}{'偏差均值':>10}{'偏差中位':>10}{'MAE':>8}{'正偏%':>8}{'范围':>16}")
for cat in ['氟', '非氟', '氧氟']:
    g = groups[cat]
    if not g:
        continue
    devs = [r['dev'] for r in g]
    n = len(devs)
    mean = sum(devs) / n
    mae = sum(abs(d) for d in devs) / n
    pos = sum(1 for d in devs if d > 0) / n * 100
    med = sorted(devs)[n // 2]
    print(f"{cat:<6}{n:>4}{mean:>10.2f}{med:>10.2f}{mae:>8.2f}{pos:>8.0f}%"
          f"[{min(devs):.1f}, {max(devs):.1f}]")

allg = [r for r in rows if r['target'] is not None]
if allg:
    devs = [r['dev'] for r in allg]
    n = len(devs)
    print(f"{'全部':<6}{n:>4}{sum(devs)/n:>10.2f}{sorted(devs)[n//2]:>10.2f}"
          f"{sum(abs(d) for d in devs)/n:>8.2f}{sum(1 for d in devs if d>0)/n*100:>8.0f}%"
          f"[{min(devs):.1f}, {max(devs):.1f}]")

# 近金属(补救后)
print(f'\n近金属(gap<0.2): {sum(1 for r in rows if r["near_metal"])}')
print(f'含f: {sum(1 for r in rows if r["has_f"])}')

# 氟化物宽带隙 Top (验证 3-4eV 超出)
print('\n=== 氟化物 Top 8 (目标 vs 实测) ===')
fl = sorted([r for r in rows if r['category'] == '氟' and r['target'] is not None],
            key=lambda x: -x['bandgap_eV'])[:8]
for r in fl:
    print(f"  {r['formula']:<12} 目标={r['target']:.1f} 实测={r['bandgap_eV']:.3f} 偏差={r['dev']:+.2f} ({r['remedy']})")

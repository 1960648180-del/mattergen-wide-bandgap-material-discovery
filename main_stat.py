"""
主统计: 仅保留条件生成样本(有明确目标带隙), 输出 gap_main.json + 分组偏差
- 条件生成池: extended_pool/bg_25-45 (100) + pool_bandgap_25/35/40 (48) = 148
- 无目标(开放生成 results/widegap/bulk_150) 移出主统计, 放附录
用法: python3 main_stat.py
"""
import json, re
from pathlib import Path
from collections import Counter

GAP = Path('/mnt/d/nature reproduction/mattergen/gap_all.json')
REMEDY = Path('/home/isaac/p1_dft/gap_remedy_results')
META = Path('/mnt/d/nature reproduction/mattergen/candidates_meta.json')
OUT = Path('/mnt/d/nature reproduction/mattergen/gap_main.json')

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
        has_F = m.get('has_F', 'F' in form)
        has_O = 'O' in form
        rows.append({'formula': form, 'bandgap_eV': gap,
                     'category': '氧氟' if (has_F and has_O) else ('氟' if has_F else '非氟'),
                     'near_metal': gap < 0.2, 'has_f': m.get('has_f', False),
                     'n_atoms': r['n_atoms'], 'energy_per_atom': r['energy_per_atom'],
                     'mag_uB': r.get('mag_moment_uB'), 'source': m.get('source', ''),
                     'homo': r.get('homo'), 'lumo': r.get('lumo'),
                     'remedy': '补救'})
    except Exception:
        continue

# 主统计: 只保留有目标带隙的条件生成样本
main_rows = []
for r in rows:
    t = target_from_source(r.get('source', ''))
    if t is not None:
        r['target'] = t
        r['dev'] = r['bandgap_eV'] - t
        main_rows.append(r)

main_rows.sort(key=lambda x: -x['bandgap_eV'])
OUT.write_text(json.dumps(main_rows, indent=2, ensure_ascii=False), encoding='utf-8')

# 条件生成池总数
cond_pool = 148  # extended 100 + pool_bandgap 48
n_ok = len(main_rows)
print(f'条件生成池: {cond_pool}, 当前有带隙: {n_ok}, 主统计覆盖率: {n_ok}/{cond_pool} = {n_ok/cond_pool*100:.1f}%')
print(f'无目标(开放生成)排除: {len(rows) - n_ok}\n')

print('=== 主统计分组偏差 (DFT实测 - 目标带隙, eV) ===')
groups = Counter()
stats = {}
for cat in ['氟', '非氟', '氧氟']:
    g = [r for r in main_rows if r['category'] == cat]
    if not g:
        continue
    devs = [r['dev'] for r in g]
    n = len(devs)
    mean = sum(devs) / n
    mae = sum(abs(d) for d in devs) / n
    med = sorted(devs)[n // 2]
    pos = sum(1 for d in devs if d > 0) / n * 100
    nm = sum(1 for r in g if r['near_metal'])
    print(f"{cat:<4} n={n:>3} 偏差均值={mean:>+7.2f} 中位={med:>+7.2f} MAE={mae:>6.2f} "
          f"正偏={pos:>4.0f}% 近金属={nm} [{min(devs):+.1f},{max(devs):+.1f}]")

allg = main_rows
devs = [r['dev'] for r in allg]
n = len(devs)
print(f"{'全部':<4} n={n:>3} 偏差均值={sum(devs)/n:>+7.2f} 中位={sorted(devs)[n//2]:>+7.2f} "
      f"MAE={sum(abs(d) for d in devs)/n:>6.2f} 正偏={sum(1 for d in devs if d>0)/n*100:>4.0f}% "
      f"近金属={sum(1 for r in allg if r['near_metal'])}")

# 非金属 vs 金属分开(排除近金属后的偏差, 反映'成功生成'的保真度)
print('\n=== 仅非金属样本(gap>=0.2) 偏差 ===')
for cat in ['氟', '非氟', '氧氟']:
    g = [r for r in main_rows if r['category'] == cat and not r['near_metal']]
    if not g:
        continue
    devs = [r['dev'] for r in g]
    n = len(devs)
    print(f"{cat:<4} n={n:>3} 偏差均值={sum(devs)/n:>+7.2f} MAE={sum(abs(d) for d in devs)/n:>6.2f} "
          f"正偏={sum(1 for d in devs if d>0)/n*100:>4.0f}% [{min(devs):+.1f},{max(devs):+.1f}]")

print(f'\n输出: {OUT} ({len(main_rows)} 条, 含 target/dev/remedy)')

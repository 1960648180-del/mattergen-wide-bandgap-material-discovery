"""
系统性负偏差分析 (条件生成 141 样本, gap_main.json)
- 按目标带隙档位分析偏差 (MatterGen 是否目标越高越难达到)
- 负偏差构成 (金属/窄带隙/中等)
- 达成率 (实测在目标±0.5 内)
- 输出论文可用统计表
"""
import json
from pathlib import Path
from collections import Counter, defaultdict

MAIN = Path('/mnt/d/nature reproduction/mattergen/gap_main.json')
rows = json.loads(MAIN.read_text(encoding='utf-8'))
print(f'条件生成样本: {len(rows)}\n')

# 1. 按目标档位
print('=== 按目标带隙档位 ===')
print(f"{'目标(eV)':>8}{'n':>4}{'偏差均值':>9}{'中位':>8}{'MAE':>7}{'正偏%':>7}{'近金属':>7}{'达成±0.5%':>10}")
by_t = defaultdict(list)
for r in rows:
    by_t[r['target']].append(r)
for t in sorted(by_t):
    g = by_t[t]
    devs = [r['dev'] for r in g]
    n = len(devs)
    mean = sum(devs) / n
    med = sorted(devs)[n // 2]
    mae = sum(abs(d) for d in devs) / n
    pos = sum(1 for d in devs if d > 0) / n * 100
    nm = sum(1 for r in g if r['near_metal'])
    hit = sum(1 for r in g if abs(r['dev']) <= 0.5) / n * 100
    print(f"{t:>8.1f}{n:>4}{mean:>+9.2f}{med:>+8.2f}{mae:>7.2f}{pos:>7.0f}%{nm:>7}{hit:>10.0f}%")

# 2. 偏差方向构成
print('\n=== 全部样本偏差方向 ===')
devs = [r['dev'] for r in rows]
n = len(devs)
neg = sum(1 for d in devs if d < 0)
pos = sum(1 for d in devs if d > 0)
zero = n - neg - pos
print(f'负偏差(实测<目标): {neg} ({neg/n*100:.0f}%)')
print(f'正偏差(实测>目标): {pos} ({pos/n*100:.0f}%)')
print(f'接近(偏差=0±0.1): {zero}')

# 3. 负偏差样本的实测 gap 构成
print('\n=== 负偏差样本 (dev<0) 的实测带隙构成 ===')
neg_rows = [r for r in rows if r['dev'] < 0]
bins = Counter()
for r in neg_rows:
    g = r['bandgap_eV']
    if g < 0.2: bins['金属(<0.2)'] += 1
    elif g < 1.0: bins['窄带隙(0.2-1)'] += 1
    elif g < 2.0: bins['中带隙(1-2)'] += 1
    else: bins['宽(>2)'] += 1
for k, v in bins.items():
    print(f'  {k}: {v} ({v/len(neg_rows)*100:.0f}%)')

# 4. 达成率
print('\n=== 达成率 (实测在目标±0.5eV) ===')
for cat in ['氟', '非氟', '氧氟']:
    g = [r for r in rows if r['category'] == cat]
    if not g: continue
    hit = sum(1 for r in g if abs(r['dev']) <= 0.5) / len(g) * 100
    nm = sum(1 for r in g if r['near_metal'])
    print(f'  {cat:<4} n={len(g):>3} 达成率={hit:>5.1f}% 近金属={nm}')
hit_all = sum(1 for r in rows if abs(r['dev']) <= 0.5) / len(rows) * 100
print(f'  全部 n={len(rows)} 达成率={hit_all:.1f}%')

# 5. 相关系数 (目标 vs 实测) - 简单线性
print('\n=== 目标 vs 实测 线性趋势 ===')
xs = [r['target'] for r in rows]
ys = [r['bandgap_eV'] for r in rows]
mx = sum(xs) / n; my = sum(ys) / n
cov = sum((x-mx)*(y-my) for x, y in zip(xs, ys)) / n
vx = sum((x-mx)**2 for x in xs) / n
vy = sum((y-my)**2 for y in ys) / n
slope = cov / vx if vx else 0
r_pearson = cov / (vx*vy)**0.5 if vx and vy else 0
print(f'斜率(目标→实测): {slope:.3f} (理想=1)')
print(f'Pearson r: {r_pearson:.3f}')
print(f'均值: 目标={mx:.2f}, 实测={my:.2f}')

# 6. 体系×档位 关键表 (论文主表)
print('\n=== 体系 × 目标档位 偏差均值 (论文主表) ===')
cats = ['氟', '非氟', '氧氟']
targets = sorted(by_t.keys())
hdr = '体系'.ljust(6) + ''.join(f'{t:>9.1f}' for t in targets) + f"{'全档':>9}"
print(hdr)
for cat in cats:
    line = cat.ljust(6)
    for t in targets:
        g = [r for r in rows if r['category'] == cat and r['target'] == t]
        if g:
            line += f'{sum(r["dev"] for r in g)/len(g):>+9.2f}'
        else:
            line += f'{"—":>9}'
    gg = [r for r in rows if r['category'] == cat]
    line += f'{sum(r["dev"] for r in gg)/len(gg):>+9.2f}'
    print(line)

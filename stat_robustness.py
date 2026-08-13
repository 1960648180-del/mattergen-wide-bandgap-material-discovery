"""统计强度补充: bootstrap CI + 敏感性分析 (数据可支撑性)
1) 关键数字的 95% bootstrap CI: 总偏差均值 / MAE / 近金属占比 / 达成率 / r
2) 敏感性: 主表alone vs 合并补救; 近金属阈值 0.1/0.2/0.3
输出: 控制台 + mattergen/stat_robustness.txt
用法: python3 stat_robustness.py
"""
import json
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parent
d = json.loads((ROOT / 'gap_main.json').read_text(encoding='utf-8'))

rng = np.random.default_rng(42)

def bootstrap_ci(values, stat_fn, n_boot=2000, ci=95):
    vals = np.asarray(values, dtype=float)
    boots = []
    for _ in range(n_boot):
        s = rng.choice(vals, size=len(vals), replace=True)
        boots.append(stat_fn(s))
    lo = (100 - ci) / 2
    hi = 100 - lo
    return np.percentile(boots, [lo, hi])

def mean_fn(x): return x.mean()
def mae_fn(x): return np.abs(x).mean()
def frac_fn(x): return (x).mean()

devs = np.array([r['dev'] for r in d])
gaps = np.array([r['bandgap_eV'] for r in d])
tgts = np.array([r['target'] for r in d])
near = np.array([1.0 if r['near_metal'] else 0.0 for r in d])
ach = np.array([1.0 if abs(r['dev']) <= 0.5 else 0.0 for r in d])

out = []
def log(s):
    print(s)
    out.append(s)

log('=' * 60)
log('统计强度: bootstrap 95% CI (n_boot=2000)')
log('=' * 60)
log(f'n = {len(d)}')
for name, vals, fn in [
    ('总偏差均值 (eV)', devs, mean_fn),
    ('MAE (eV)', devs, mae_fn),
    ('近金属占比', near, frac_fn),
    ('达成率 (±0.5 eV)', ach, frac_fn),
]:
    lo, hi = bootstrap_ci(vals, fn)
    point = fn(vals)
    log(f'  {name:<16} = {point:.3f}   [95% CI: {lo:.3f} ~ {hi:.3f}]')

# r 的 bootstrap CI
r_boots = []
for _ in range(2000):
    idx = rng.choice(len(d), size=len(d), replace=True)
    r_boots.append(np.corrcoef(tgts[idx], gaps[idx])[0, 1])
log(f'  {"Pearson r":<16} = {np.corrcoef(tgts, gaps)[0,1]:.3f}   [95% CI: {np.percentile(r_boots,[2.5,97.5])[0]:.3f} ~ {np.percentile(r_boots,[2.5,97.5])[1]:.3f}]')

log('')
log('=' * 60)
log('敏感性 1: 近金属阈值')
log('=' * 60)
for thr in [0.1, 0.2, 0.3]:
    f = float(np.mean([1.0 if r['bandgap_eV'] < thr else 0.0 for r in d]))
    log(f'  gap < {thr} eV: {100*f:.1f}%')

log('')
log('=' * 60)
log('敏感性 2: 补救样本是否改变结论方向')
log('=' * 60)
remedy = [r for r in d if r.get('remedy') == '补救']
first = [r for r in d if r.get('remedy') == '首次']
for name, rows in [('首次', first), ('补救', remedy), ('全部', d)]:
    if not rows:
        continue
    ds = np.array([r['dev'] for r in rows])
    nm = float(np.mean([1.0 if r['near_metal'] else 0.0 for r in rows]))
    log(f'  {name:<4}: n={len(rows):<4} 偏差均值={ds.mean():+.2f}  近金属={100*nm:.0f}%')

log('')
log('=' * 60)
log('敏感性 3: 氟化物非金属子集 (n 小, 报告 CI)')
log('=' * 60)
fl_nm = [r['dev'] for r in d if r['category'] == '氟' and not r['near_metal']]
if fl_nm:
    arr = np.array(fl_nm)
    lo, hi = bootstrap_ci(arr, mean_fn)
    log(f'  非金属氟 n={len(arr)}: 偏差均值={arr.mean():+.2f}  [95% CI: {lo:+.2f} ~ {hi:+.2f}] 正偏占比={100*np.mean(arr>0):.0f}%')

(ROOT / 'stat_robustness.txt').write_text('\n'.join(out), encoding='utf-8')
log('')
log('写入 stat_robustness.txt')

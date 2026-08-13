"""
随机抽样 DFT 形成能统计: CHGNet vs DFT
计算 DFT 形成能 (DFT 总能 - 元素 DFT 参考) / 原子数, 与 CHGNet 形成能对比
输出 MAE、符号一致率、逐样本表
"""
import json

# ===== 候选 DFT 总能 (pos-relaxed, eV) =====
totals = {
    'C2N2':    -29.6220,   # n=4
    'O5':      -16.0922,   # n=5
    'C2Li6N4': -60.5353,   # n=12
    'F2O2':     -8.6889,   # n=4
    'Hg2O8S2': -48.6832,   # n=12
    'Cl3LiPb': -17.7240,   # n=5
}
comps = {
    'C2N2':    {'C': 2, 'N': 2},
    'O5':      {'O': 5},
    'C2Li6N4': {'C': 2, 'Li': 6, 'N': 4},
    'F2O2':    {'F': 2, 'O': 2},
    'Hg2O8S2': {'Hg': 2, 'O': 8, 'S': 2},
    'Cl3LiPb': {'Cl': 3, 'Li': 1, 'Pb': 1},
}

# ===== 元素 DFT 参考 (eV/atom, 自旋 PBE) =====
ref = {
    'F':  -1.297253 / 2, 'O': -6.7838 / 2, 'Rb': -0.9095,
    'Hf': -14.9873 / 2, 'Y': -9.4076 / 2, 'Re': -23.2410 / 2,
    'Li': -1.8997, 'Tb': -15.1274 / 2, 'Sc': -9.3611 / 2,
    'Lu': -7.8018 / 2, 'Nd': -9.530170 / 2, 'P': -3.1626,
    'Ho': -7.9362 / 2,
}
# 新算 DFT 参考
import os
refpath = '/home/isaac/p1_dft/dft_ref_energies.json'
if os.path.exists(refpath):
    with open(refpath, encoding='utf-8') as f:
        ref.update(json.load(f))
    print('已加载新算参考:', list(json.load(open(refpath, encoding='utf-8')).keys()))
else:
    print('⚠️ 未找到 dft_ref_energies.json (参考计算未完成), 用 CHGNet 近似')
    with open('/mnt/d/nature reproduction/mattergen/elemental_ref_energies.json', encoding='utf-8') as f:
        chg = json.load(f)
    for el in ['C', 'N', 'H', 'Na', 'Cl', 'Pb', 'Hg', 'S']:
        ref[el] = chg[el]

# ===== CHGNet 形成能 (from screening json) =====
with open('/mnt/d/nature reproduction/mattergen/screening_extended_result.json', encoding='utf-8') as f:
    screen = json.load(f)
chgnet_ef = {}
for r in screen['results']:
    if r['formula'] in totals and r['formula'] not in chgnet_ef:
        chgnet_ef[r['formula']] = r['formation_energy']

# ===== 计算 =====
print('\n===== CHGNet vs DFT 形成能 =====')
print(f"{'候选':<10} {'原子':>4} {'DFT总能':>10} {'DFT Ef':>8} {'CHGNet Ef':>9} {'Δ(Ef)':>8}")
rows = []
for name in totals:
    c = comps[name]
    n = sum(c.values())
    e_total = totals[name]
    ref_sum = sum(n_el * ref[el] for el, n_el in c.items())
    dft_ef = (e_total - ref_sum) / n
    chg = chgnet_ef.get(name)
    rows.append((name, n, dft_ef, chg))
    print(f"{name:<10} {n:>4} {e_total:>10.3f} {dft_ef:>+8.3f} {chg:>+9.3f} "
          f"{'—' if chg is None else f'{dft_ef-chg:+.3f}'}")

# 统计 (仅 CHGNet 有值的)
valid = [(n, d, c) for n, _, d, c in rows if c is not None]
if valid:
    mae = sum(abs(d - c) for _, d, c in valid) / len(valid)
    sign_ok = sum(1 for _, d, c in valid if (d > 0) == (c > 0))
    print(f'\n统计 ({len(valid)} 样本):')
    print(f'  MAE = {mae:.3f} eV/atom')
    print(f'  符号一致率 = {sign_ok}/{len(valid)} ({sign_ok/len(valid)*100:.0f}%)')
    for n, d, c in valid:
        print(f'    {n:<10} CHGNet {c:+.2f} → DFT {d:+.2f}  一致={ (d>0)==(c>0) }')

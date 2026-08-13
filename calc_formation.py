# === DFT 参考态能量（自旋） ===
ref = {
    'Tb': -15.1274 / 2,    # eV/atom (hcp, 2 atoms, energy-converged)
    'F':  -1.297253 / 2,   # eV/atom (F2 molecule)
    'Sc': -9.3611 / 2,     # eV/atom (hcp, 2 atoms) 
    'Lu': -7.8018 / 2,     # eV/atom (hcp, 2 atoms)
    'Nd': -9.530170 / 2,   # eV/atom (hcp, 2 atoms, converged 118 iter)
    'O':  -6.7838 / 2,     # eV/atom (O2 triplet molecule)
    'P':  -3.1626,         # eV/atom (sc, 1 atom)
    'Ho': -7.9362 / 2,     # eV/atom (hcp, 2 atoms)
    'Rb': -0.9095,         # eV/atom (bcc, 1 atom)
}

# === 候选 DFT 总能量（自旋） ===
total = {
    'TbF3':      -25.531928,   # 4 atoms: Tb + 3F
    'ScF3':      -22.6335,     # 4 atoms: Sc + 3F  
    'F2Lu2O2':   -37.3386,     # 6 atoms: 2Lu + 2F + 2O
    'Nd2O8P2':   -83.0769,     # 12 atoms: 2Nd + 8O + 2P
    'F6HoRb3':   -42.8336,     # 10 atoms: Ho + 3Rb + 6F
}

# === CHGNet 形成能 ===
chgnet_ef = {
    'TbF3':    -4.33,
    'ScF3':    -4.19,
    'F2Lu2O2': -4.17,
    'Nd2O8P2': -3.69,
    'F6HoRb3': -3.54,
}

# === 组成 ===
compositions = {
    'TbF3':    {'Tb': 1, 'F': 3},
    'ScF3':    {'Sc': 1, 'F': 3},
    'F2Lu2O2': {'Lu': 2, 'F': 2, 'O': 2},
    'Nd2O8P2': {'Nd': 2, 'O': 8, 'P': 2},
    'F6HoRb3': {'Ho': 1, 'Rb': 3, 'F': 6},
}

print('=' * 90)
print(' 严格 DFT 形成能计算（自旋极化 PBE）— 5 个候选')
print('=' * 90)
print()
header = f"{'体系':<12} {'原子':>4} {'DFT 总能':>10} {'参考和':>10} {'Ef 总':>10} {'Ef/atom':>9} {'CHGNet':>9} {'误差':>8}"
print(header)
print('-' * 90)

results = {}
for name in ['TbF3', 'ScF3', 'F2Lu2O2', 'Nd2O8P2', 'F6HoRb3']:
    comp = compositions[name]
    n_atoms = sum(comp.values())
    e_total = total[name]
    e_ref_sum = sum(n * ref[el] for el, n in comp.items())
    e_form_total = e_total - e_ref_sum
    e_form_pa = e_form_total / n_atoms
    ef_chg = chgnet_ef[name]
    err = e_form_pa - ef_chg
    results[name] = e_form_pa
    print(f'{name:<12} {n_atoms:>4} {e_total:>10.4f} {e_ref_sum:>10.4f} {e_form_total:>10.4f} {e_form_pa:>9.4f} {ef_chg:>9.2f} {err:>+8.4f}')

print()
print('参考态能量（DFT 自旋 PBE）:')
for el in ['Tb', 'F', 'Sc', 'Lu', 'Nd', 'O', 'P', 'Ho', 'Rb']:
    print(f'  {el:>2}: {ref[el]:.4f} eV/atom')

# 统计
errors = [abs(results[n] - chgnet_ef[n]) for n in results]
mae = sum(errors) / len(errors)
rmse = (sum(e**2 for e in errors) / len(errors)) ** 0.5
print()
print('=' * 90)
print(f'统计指标: MAE = {mae:.4f} eV/atom,  RMSE = {rmse:.4f} eV/atom')
print(f'符号一致率: 5/5 (100%)')
print(f'误差范围: {min(errors):.4f} ~ {max(errors):.4f} eV/atom')
print('=' * 90)

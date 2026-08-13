"""
P1 三个候选的 DFT 形成能计算
"""
import json

# === DFT 参考态能量（自旋 PBE, eV/atom）===
ref = {
    'F':  -1.297253 / 2,   # F2 molecule
    'O':  -6.7838 / 2,     # O2 triplet
    'Rb': -0.9095,         # bcc
    'Hf': -14.9873 / 2,    # hcp, 2 atoms
    'Y':  -9.4076 / 2,     # hcp, 2 atoms
    'Re': -23.2410 / 2,    # hcp, 2 atoms
    'Li': -1.8997,         # bcc
}

# === P1 候选 DFT 总能量（自旋）===
total = {
    'F9Hf3O3Y': -102.2695,   # 16 atoms
    'F6Rb3Y':   -44.3108,    # 10 atoms
    'LiO11Re3': -97.9687,    # 15 atoms
}

# === 组成 ===
comp = {
    'F9Hf3O3Y': {'F': 9, 'Hf': 3, 'O': 3, 'Y': 1},
    'F6Rb3Y':   {'F': 6, 'Rb': 3, 'Y': 1},
    'LiO11Re3': {'Li': 1, 'O': 11, 'Re': 3},
}

# === CHGNet 形成能 ===
chgnet_ef = {
    'F9Hf3O3Y': -6.333,
    'F6Rb3Y':   -4.125,
    'LiO11Re3': -4.712,
}

print("=" * 80)
print(" P1 候选 DFT 形成能计算")
print("=" * 80)
print()
print(f"{'候选':<12} {'原子':>4} {'DFT 总能':>10} {'Ef 总':>10} {'Ef/atom':>9} {'CHGNet':>9} {'误差':>8}")
print("-" * 80)

for name in ['F9Hf3O3Y', 'F6Rb3Y', 'LiO11Re3']:
    c = comp[name]
    n_atoms = sum(c.values())
    e_total = total[name]
    e_ref_sum = sum(n * ref[el] for el, n in c.items())
    e_form_total = e_total - e_ref_sum
    e_form_pa = e_form_total / n_atoms
    ef_chg = chgnet_ef[name]
    err = e_form_pa - ef_chg
    print(f"{name:<12} {n_atoms:>4} {e_total:>10.4f} {e_form_total:>10.4f} {e_form_pa:>9.4f} {ef_chg:>9.3f} {err:>+8.3f}")

print()
print("参考态能量 (eV/atom):")
for el in ['F', 'O', 'Rb', 'Hf', 'Y', 'Re', 'Li']:
    print(f"  {el}: {ref[el]:.4f}")

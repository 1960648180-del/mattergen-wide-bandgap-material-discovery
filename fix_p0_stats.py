# 修正 P0 统计：MAE、平均偏差、F6Rb3Y 形成能重算
# 用精确 DFT 参考能量
ref = {
    'F':  -1.297253 / 2,   # F2 molecule
    'Rb': -0.9095,         # bcc
    'Y':  -9.4076 / 2,     # hcp 2 atoms
}

# ============ 带隙数据 ============
# (候选, PBE带隙, 目标带隙)
gaps = [
    ('F9Hf3O3Y', 4.1691, 3.0),
    ('F6Rb3Y',   5.8558, 4.0),
    ('LiO11Re3', 1.6424, 2.5),
]

print('=== 带隙偏差统计 ===')
devs = []
for name, g, t in gaps:
    d = g - t
    devs.append(d)
    print(f'  {name:<10} gap={g:.3f} 目标={t:.1f} 偏差={d:+.3f}')

mae = sum(abs(d) for d in devs) / len(devs)
mean_dev = sum(devs) / len(devs)
print(f'  MAE = {mae:.3f} eV')
print(f'  平均偏差 = {mean_dev:+.3f} eV')
print(f'  偏差: {[f"{d:+.2f}" for d in devs]}')

# ============ F6Rb3Y 形成能重算 ============
print('\n=== F6Rb3Y 形成能重算 (新总能 -44.3416) ===')
comp = {'F': 6, 'Rb': 3, 'Y': 1}
n = sum(comp.values())
E_new = -44.3416  # f6rb3y_posrelaxed_new.cif, kpts 4x4x4
ref_sum = 6 * ref['F'] + 3 * ref['Rb'] + 1 * ref['Y']
ef_new = (E_new - ref_sum) / n
print(f'  组成: {comp}, 原子数={n}')
print(f'  新总能: {E_new:.4f} eV')
print(f'  参考和: {ref_sum:.4f} eV')
print(f'  新形成能: {ef_new:.4f} eV/atom')

# 旧值对比
print('\n=== 新旧 F6Rb3Y 形成能对比 ===')
E_old = -36.9151  # 旧全晶胞弛豫 (体积-38.8% 脏数据)
ef_old = (E_old - ref_sum) / n
print(f'  旧总能: {E_old:.4f} eV → 旧形成能: {ef_old:.4f} eV/atom')
print(f'  新总能: {E_new:.4f} eV → 新形成能: {ef_new:.4f} eV/atom')
print(f'  能量差: {E_new - E_old:.4f} eV (新结构低 {abs(E_new-E_old):.1f} eV!)')
print(f'  形成能差: {ef_new - ef_old:+.4f} eV/atom')

# === P1 三个候选 DFT 弛豫统一汇总 ===
# 计算: 原始结构/CHGNet relax/DFT relax 的能量对比
#       形成能 (DFT), 晶格参数变化, 磁矩
import os
os.environ['GPAW_SETUP_PATH'] = '/usr/local/lib/python3.12/dist-packages/gpaw_data/setups'
import numpy as np
from ase.io import read
from ase.io.cif import write_cif
import json

# ============ 输入数据 ============
# DFT 参考单质能量 (eV/atom) — 来自 WSL 单质 DFT 计算
ref = {
    'F':  -0.6486,
    'O':  -3.3919,
    'Rb': -0.9095,
    'Hf': -7.4936,
    'Y':  -4.7038,
    'Re': -11.6205,
    'Li': -1.8997,
}

compositions = {
    'F9Hf3O3Y': {'F': 9, 'Hf': 3, 'O': 3, 'Y': 1},
    'F6Rb3Y':   {'F': 6, 'Rb': 3, 'Y': 1},
    'LiO11Re3': {'Li': 1, 'O': 11, 'Re': 3},
}

# CHGNet 结果 (relax 前后能量, 从 chgnet_prepare.py 输出)
chgnet = {
    'F9Hf3O3Y': {'raw': -133.895, 'relaxed': -134.001},
    'F6Rb3Y':   {'raw': None,     'relaxed': None},
    'LiO11Re3': {'raw': -125.150, 'relaxed': -125.568},
}

# CHGNet 形成能 (修正后) eV/atom
chgnet_ef = {
    'F6Rb3Y': -3.48,
    'F9Hf3O3Y': -4.07,
    'LiO11Re3': -2.22,
}

# CHGNet relaxed CIF 路径 (弛豫起点)
chgnet_cif = {
    'F9Hf3O3Y': '/home/isaac/p1_dft/chgnet_relaxed_F9Hf3O3Y.cif',
    'F6Rb3Y':   '/home/isaac/p1_dft/chgnet_relaxed_F6Rb3Y.cif',
    'LiO11Re3': '/home/isaac/p1_dft/chgnet_relaxed_LiO11Re3.cif',
}

# DFT relax 输出 CIF (位置需在 WSL 运行后确认)
dft_cif = {
    'F9Hf3O3Y': '/home/isaac/p1_dft/f9hf3o3y_posrelaxed.cif',
    'F6Rb3Y':   '/home/isaac/p1_dft/f6rb3y_relaxed.cif',
    'LiO11Re3': '/home/isaac/p1_dft/li_o11re3_posrelaxed.cif',
}

# DFT relax 能量 (eV) — 需要从 relax 输出中手动填入
# F6Rb3Y: -36.9151 (full-cell, 100步, fmax=0.287)
# F9Hf3O3Y: -102.3844 (pos-only, 40步, fmax=0.037 ✓ 收敛)
# LiO11Re3: -98.8612 (pos-only, 59步, fmax=0.0345 ✓ 收敛)
dft_energy = {
    'F6Rb3Y': -36.9151,
    'F9Hf3O3Y': -102.3844,
    'LiO11Re3': -98.8612,
}

# MatterGen 原始 CIF (用于对比晶格)
raw_cif = {
    'F9Hf3O3Y': '/home/isaac/p1_dft/raw_F9Hf3O3Y.cif',
    'F6Rb3Y':   '/home/isaac/p1_dft/raw_F6Rb3Y.cif',
    'LiO11Re3': '/home/isaac/p1_dft/raw_LiO11Re3.cif',
}

def cell_str(cell):
    return f"[{cell[0][0]:.4f}, {cell[1][1]:.4f}, {cell[2][2]:.4f}]"

print('=' * 100)
print(' P1 三个候选 DFT 弛豫统一汇总')
print('=' * 100)

for name in ['F9Hf3O3Y', 'F6Rb3Y', 'LiO11Re3']:
    comp = compositions[name]
    n = sum(comp.values())
    print(f'\n--- {name} ({n} atoms) ---')
    print(f'  组成: {comp}')

    # 读取 DFT relaxed CIF
    if os.path.exists(dft_cif[name]):
        a = read(dft_cif[name])
        print(f'  DFT relaxed cell: {cell_str(a.cell)}')
        print(f'  DFT relaxed 体积: {a.get_volume():.4f} Å³')

    # 读取 CHGNet relaxed CIF
    if os.path.exists(chgnet_cif[name]):
        c = read(chgnet_cif[name])
        print(f'  CHGNet relaxed cell: {cell_str(c.cell)}')

    # DFT 能量
    if name in dft_energy:
        e = dft_energy[name]
        print(f'  DFT relax 能量: {e:.4f} eV  ({e/n:.4f} eV/atom)')
        # 形成能
        ref_sum = sum(ref[el] * nn for el, nn in comp.items())
        ef_total = e - ref_sum
        ef_pa = ef_total / n
        print(f'  参考和: {ref_sum:.4f} eV')
        print(f'  DFT 形成能: {ef_total:.4f} eV  ({ef_pa:.4f} eV/atom)')
        print(f'  CHGNet 形成能: {chgnet_ef[name]:.4f} eV/atom')
        print(f'  差值 (DFT-CHGNet): {ef_pa - chgnet_ef[name]:+.4f} eV/atom')
    else:
        print(f'  DFT 能量: 未完成 (需补充 dft_energy[{name}])')

print('\n' + '=' * 100)
print('说明: 本脚本需在 WSL (/home/isaac/p1_dft) 运行, 待 F9Hf3O3Y 和 LiO11Re3 弛豫完成后')
print('补充 dft_energy 值后即可输出完整汇总。')
print('=' * 100)

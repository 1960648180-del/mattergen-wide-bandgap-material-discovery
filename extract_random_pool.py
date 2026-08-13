"""从 extended_pool 提取随机抽样候选结构"""
import os, warnings
warnings.filterwarnings('ignore')
from ase.io import read, write

base = '/mnt/d/nature reproduction/mattergen'

# (公式, batch, index, 备注)
targets = [
    ('C2N2',    'bg_30', 4,  '负对照 Ef=+0.189'),
    ('O5',      'bg_25', 7,  '负对照 Ef=+0.180'),
    ('H4Na2',   'bg_40', 4,  '边界 Ef=-0.134'),
    ('C2Li6N4', 'bg_30', 15, '边界 Ef=-0.688'),
    ('F2O2',    'bg_45', 1,  '边界 Ef=-0.378'),
    ('Hg2O8S2', 'bg_25', 1,  '非F稳定 Ef=-1.775'),
    ('Cl3LiPb', 'bg_25', 9,  '非F稳定 Ef=-1.727'),
]

for formula, batch, idx, note in targets:
    p = os.path.join(base, f'extended_pool/{batch}/generated_crystals.extxyz')
    frames = read(p, index=':')
    at = frames[idx]
    got = at.get_chemical_formula()
    if got != formula:
        print(f'⚠️ {batch} idx{idx} 是 {got}, 期望 {formula}, 跳过')
        continue
    out = os.path.join(base, f'rand_{formula}.cif')
    write(out, at)
    print(f'✅ {formula} ({batch} idx{idx}, n={len(at)}) → {os.path.basename(out)}  [{note}]')
print('完成')

"""从 extended_pool 提取非氟对照候选结构"""
import os, warnings
warnings.filterwarnings('ignore')
from ase.io import read, write

base = '/mnt/d/nature reproduction/mattergen'
# (公式, batch, index)
targets = [
    ('BeO2Zn',  'bg_30', 9),
    ('Cl2CsK',  'bg_30', 10),
    ('CaO3Zr',  'bg_35', 17),
    ('O2Rb4',   'bg_35', 15),
    ('Al3O5',   'bg_40', 15),
    ('Br2Cs2',  'bg_40', 8),
    ('CaClKO',  'bg_45', 9),
    ('H2Cs2S2', 'bg_45', 19),
]
for formula, batch, idx in targets:
    p = f'{base}/extended_pool/{batch}/generated_crystals.extxyz'
    frames = read(p, index=':')
    at = frames[idx]
    got = at.get_chemical_formula()
    if got != formula:
        print(f'⚠️ {batch} idx{idx} 是 {got}, 期望 {formula}, 跳过')
        continue
    out = f'{base}/nonf_{formula}.cif'
    write(out, at)
    print(f'✅ {formula} ({batch} idx{idx}, n={len(at)}) → {os.path.basename(out)}')
print('完成')

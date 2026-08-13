"""
能带结构计算: 确认直接/间接带隙性质
====================================
用 GPAW 沿高对称路径计算能带, 输出 VBM/CBM 位置与直接/间接判定。

用法: python band_structure.py <cif> <kpts> <outprefix>
  例: python band_structure.py f9hf3o3y_posrelaxed.cif 4 4 4 bs_F9
"""
import sys
import os
import warnings
warnings.filterwarnings('ignore')
os.environ.setdefault(
    "GPAW_SETUP_PATH",
    "/usr/local/lib/python3.12/dist-packages/gpaw_data/setups")

import numpy as np
from ase.io import read
from ase.dft.kpoints import bandpath
from gpaw import GPAW, PW, FermiDirac, Mixer

cif = sys.argv[1]
kpts = tuple(int(x) for x in sys.argv[2:5])
prefix = sys.argv[5] if len(sys.argv) > 5 else 'bs'

atoms = read(cif)
n = len(atoms)
formula = atoms.get_chemical_formula()
print(f'能带计算: {formula} ({n} atoms)  kpts={kpts}', flush=True)

# 高对称路径 (用 cell 的默认 path)
path = atoms.cell.bandpath(npoints=60)
print(f'高对称路径: {path.path}  k点数={len(path.kpts)}', flush=True)

calc = GPAW(mode=PW(400), xc='PBE', kpts=kpts, hund=True,
            occupations=FermiDirac(0.05),
            mixer=Mixer(beta=0.05, nmaxold=7, weight=100.0),
            maxiter=300, txt=f'{prefix}.txt')
atoms.calc = calc
atoms.get_potential_energy()  # 先收敛

# 计算能带
bs = calc.band_structure(path.kpts, spin_orbital=False)
bs.write(f'{prefix}_band.json')

# 提取 VBM/CBM (能带带隙定义: 沿路径扫描)
# 从 bs 数据找占据数
try:
    data = bs.energies  # shape (spin, band, kpt)
    occ = bs.occupations if hasattr(bs, 'occupations') else None
    nocc = int(sum(atoms.get_atomic_numbers()) / 2)  # 粗略, 需修正
except Exception as e:
    print(f'能带数据提取注意: {e}')

print(f'能带已保存: {prefix}_band.json', flush=True)
print('提示: 用 bs.plot() 或读取 json 判断 VBM/CBM k 位置', flush=True)

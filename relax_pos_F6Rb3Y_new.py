"""
F6Rb3Y 新方案 DFT 仅位置弛豫 (P0 批次)
======================================
参数调整 (相对首轮):
  - 起点: CHGNet relaxed 结构 (chgnet_relaxed_F6Rb3Y.cif)
  - 仅位置弛豫 (固定晶胞, FIRE 直接优化原子)
  - Mixer(beta=0.1) 加速 SCF (非 f 电子体系可用)
  - 初始磁矩设为 0 (Y/Rb/F 抗磁性)
  - fmax=0.05 保持 (带隙候选收敛标准)
  - kpts=3x3x3 保持 (不降 k 点)
"""
import warnings; warnings.filterwarnings('ignore')
from ase.io import read, write
from ase.optimize import FIRE
from gpaw import GPAW, PW, FermiDirac, Mixer
import numpy as np
import os; os.environ['GPAW_SETUP_PATH'] = '/usr/local/lib/python3.12/dist-packages/gpaw_data/setups'

atoms = read('/home/isaac/p1_dft/chgnet_relaxed_F6Rb3Y.cif')
n = len(atoms)
print(f'F6Rb3Y new-scheme pos-relax: {n} atoms, cell={atoms.cell.lengths()}')

# 初始磁矩设为 0
atoms.set_initial_magnetic_moments(np.zeros(n))

calc = GPAW(mode=PW(400), xc='PBE', kpts=(3,3,3),
            hund=True, occupations=FermiDirac(0.3),
            mixer=Mixer(beta=0.1, nmaxold=7, weight=100.0),
            maxiter=500, txt='/home/isaac/p1_dft/f6rb3y_posrelax_new.txt')
atoms.calc = calc

opt = FIRE(atoms)
opt.run(fmax=0.05, steps=100)

energy = atoms.get_potential_energy()
mag = atoms.get_magnetic_moment()
print(f'F6Rb3Y new-scheme pos-relaxed: DFT={energy:.4f} eV  {energy/n:.4f} eV/atom  mag={mag:.2f} uB')
write('/home/isaac/p1_dft/f6rb3y_posrelaxed_new.cif', atoms)

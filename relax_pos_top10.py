"""
扩 Top10: DFT 仅位置弛豫 (P0 新方案)
====================================
起点: CHGNet relaxed 结构; 仅位置弛豫; Mixer 0.1; 磁矩 0; fmax=0.05; kpts 3×3×3
处理: F3La, BaF6Si (F3Sc 已有首轮 DFT 结构 dft_F3Sc.cif)
"""
import warnings; warnings.filterwarnings('ignore')
from ase.io import read, write
from ase.optimize import FIRE
from gpaw import GPAW, PW, FermiDirac, Mixer
import numpy as np
import os; os.environ['GPAW_SETUP_PATH'] = '/usr/local/lib/python3.12/dist-packages/gpaw_data/setups'

names = ['F3La', 'BaF6Si']
for name in names:
    atoms = read(f'/home/isaac/p1_dft/chgnet_relaxed_{name}.cif')
    n = len(atoms)
    atoms.set_initial_magnetic_moments(np.zeros(n))
    calc = GPAW(mode=PW(400), xc='PBE', kpts=(3, 3, 3),
                hund=True, occupations=FermiDirac(0.3),
                mixer=Mixer(beta=0.1, nmaxold=7, weight=100.0),
                maxiter=500, txt=f'/home/isaac/p1_dft/{name.lower()}_posrelax.txt')
    atoms.calc = calc
    opt = FIRE(atoms)
    opt.run(fmax=0.05, steps=100)
    energy = atoms.get_potential_energy()
    mag = atoms.get_magnetic_moment()
    print(f'{name} pos-relaxed: DFT={energy:.4f} eV  {energy/n:.4f} eV/atom  mag={mag:.2f} uB')
    write(f'/home/isaac/p1_dft/{name.lower()}_posrelaxed.cif', atoms)
    print(f'已保存 {name.lower()}_posrelaxed.cif')
print('全部完成')

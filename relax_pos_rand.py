"""
随机抽样: DFT 仅位置弛豫 (P0 新方案参数)
起点: CHGNet relaxed; 仅位置; Mixer 0.1; 磁矩 0; fmax 0.05; kpts 3×3×3
候选: C2N2, O5, H4Na2, C2Li6N4, F2O2, Hg2O8S2, Cl3LiPb
"""
import warnings; warnings.filterwarnings('ignore')
from ase.io import read, write
from ase.optimize import FIRE
from gpaw import GPAW, PW, FermiDirac, Mixer
import numpy as np
import os; os.environ['GPAW_SETUP_PATH'] = '/usr/local/lib/python3.12/dist-packages/gpaw_data/setups'

names = ['C2N2', 'O5', 'H4Na2', 'C2Li6N4', 'F2O2', 'Hg2O8S2', 'Cl3LiPb']
for name in names:
    atoms = read(f'/home/isaac/p1_dft/chgnet_relaxed_rand_{name}.cif')
    n = len(atoms)
    atoms.set_initial_magnetic_moments(np.zeros(n))
    calc = GPAW(mode=PW(400), xc='PBE', kpts=(3, 3, 3),
                hund=True, occupations=FermiDirac(0.3),
                mixer=Mixer(beta=0.1, nmaxold=7, weight=100.0),
                maxiter=500, txt=f'/home/isaac/p1_dft/rand_{name}_relax.txt')
    atoms.calc = calc
    opt = FIRE(atoms)
    try:
        opt.run(fmax=0.05, steps=100)
        energy = atoms.get_potential_energy()
        mag = atoms.get_magnetic_moment()
        print(f'{name} pos-relaxed: DFT={energy:.4f} eV  {energy/n:.4f} eV/atom  mag={mag:.2f} uB', flush=True)
        write(f'/home/isaac/p1_dft/rand_{name}_posrelaxed.cif', atoms)
    except Exception as e:
        print(f'{name} 失败/未收敛: {e}', flush=True)
print('全部完成', flush=True)

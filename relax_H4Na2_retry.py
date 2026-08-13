"""
H4Na2 重试: 保守 Mixer + 初始磁矩 0 (NaH 应非磁)
上次 SCF 不收敛 (iter 500, 磁矩振荡到 +3.2)
用 beta=0.05 保守混合 + 固定磁矩 0
"""
import warnings; warnings.filterwarnings('ignore')
from ase.io import read, write
from ase.optimize import FIRE
from gpaw import GPAW, PW, FermiDirac, Mixer
import numpy as np
import os; os.environ['GPAW_SETUP_PATH'] = '/usr/local/lib/python3.12/dist-packages/gpaw_data/setups'

name = 'H4Na2'
atoms = read(f'/home/isaac/p1_dft/chgnet_relaxed_rand_{name}.cif')
n = len(atoms)
atoms.set_initial_magnetic_moments(np.zeros(n))
calc = GPAW(mode=PW(400), xc='PBE', kpts=(3, 3, 3),
            hund=True, occupations=FermiDirac(0.3),
            mixer=Mixer(beta=0.05, nmaxold=9, weight=100.0),
            maxiter=500, txt=f'/home/isaac/p1_dft/rand_{name}_retry.txt')
atoms.calc = calc
opt = FIRE(atoms)
try:
    opt.run(fmax=0.05, steps=100)
    energy = atoms.get_potential_energy()
    mag = atoms.get_magnetic_moment()
    print(f'{name} retry pos-relaxed: DFT={energy:.4f} eV  {energy/n:.4f} eV/atom  mag={mag:.2f} uB', flush=True)
    write(f'/home/isaac/p1_dft/rand_{name}_posrelaxed.cif', atoms)
except Exception as e:
    print(f'{name} retry 失败/未收敛: {e}', flush=True)
print('完成', flush=True)

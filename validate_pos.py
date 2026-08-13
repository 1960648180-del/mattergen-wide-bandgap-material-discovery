"""
结构近似验证: DFT 位置弛豫 (第③档结构)
候选: BeO2Zn, CaO3Zr (非氟, 从 CHGNet 结构); KO2Pr, DyKO2 (含f, 从 CHGNet 结构)
fmax=0.05, P0 参数 (含f用保守 Mixer 0.05)
"""
import warnings; warnings.filterwarnings('ignore')
from ase.io import read, write
from ase.optimize import FIRE
from gpaw import GPAW, PW, FermiDirac, Mixer
import numpy as np
import os; os.environ['GPAW_SETUP_PATH'] = '/usr/local/lib/python3.12/dist-packages/gpaw_data/setups'

# (name, 输入CIF, 输出CIF, Mixer beta)
jobs = [
    ('BeO2Zn', 'chgnet_relaxed_nonf_BeO2Zn.cif', 'validate_BeO2Zn.cif', 0.1),
    ('CaO3Zr', 'chgnet_relaxed_nonf_CaO3Zr.cif', 'validate_CaO3Zr.cif', 0.1),
    ('KO2Pr',  'chgnet_relaxed_fe_KO2Pr.cif',   'validate_KO2Pr.cif',  0.05),
    ('DyKO2',  'chgnet_relaxed_fe_DyKO2.cif',   'validate_DyKO2.cif',  0.05),
]
for name, src, out, beta in jobs:
    atoms = read(f'/home/isaac/p1_dft/{src}')
    n = len(atoms)
    atoms.set_initial_magnetic_moments(np.zeros(n))
    calc = GPAW(mode=PW(400), xc='PBE', kpts=(3, 3, 3),
                hund=True, occupations=FermiDirac(0.3),
                mixer=Mixer(beta=beta, nmaxold=7, weight=100.0),
                maxiter=500, txt=f'/home/isaac/p1_dft/validate_{name}_relax.txt')
    atoms.calc = calc
    opt = FIRE(atoms)
    try:
        opt.run(fmax=0.05, steps=100)
        energy = atoms.get_potential_energy()
        mag = atoms.get_magnetic_moment()
        print(f'{name} pos-relaxed: DFT={energy:.4f} eV  {energy/n:.4f} eV/atom  mag={mag:.2f} uB', flush=True)
        write(f'/home/isaac/p1_dft/{out}', atoms)
    except Exception as e:
        print(f'{name} 失败/未收敛: {e}', flush=True)
print('全部完成', flush=True)

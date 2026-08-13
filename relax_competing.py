"""
第二级 DFT 复核: F9Hf3O3Y 最近竞争相
====================================
DFT 位置弛豫 YHfF7, HfF4, HfO2 (P0 参数) → 总能 → 复核 Ehull
分解: F9Hf3O3Y = 1·YHfF7 + 0.5·HfF4 + 1.5·HfO2
"""
import warnings; warnings.filterwarnings('ignore')
from ase.io import read, write
from ase.optimize import FIRE
from gpaw import GPAW, PW, FermiDirac, Mixer
import numpy as np
import json
import os; os.environ['GPAW_SETUP_PATH'] = '/usr/local/lib/python3.12/dist-packages/gpaw_data/setups'

phases = ['YHfF7', 'HfF4', 'HfO2']
energies = {}
for name in phases:
    atoms = read(f'/home/isaac/p1_dft/compet_{name}.cif')
    n = len(atoms)
    atoms.set_initial_magnetic_moments(np.zeros(n))
    calc = GPAW(mode=PW(400), xc='PBE', kpts=(3, 3, 3),
                hund=True, occupations=FermiDirac(0.3),
                mixer=Mixer(beta=0.1, nmaxold=7, weight=100.0),
                maxiter=500, txt=f'/home/isaac/p1_dft/compet_{name}_relax.txt')
    atoms.calc = calc
    opt = FIRE(atoms)
    try:
        opt.run(fmax=0.05, steps=100)
        e = atoms.get_potential_energy()
        mag = atoms.get_magnetic_moment()
        energies[name] = e
        print(f'{name}: DFT={e:.4f} eV  {e/n:.4f} eV/atom  mag={mag:.2f} uB  n={n}', flush=True)
        write(f'/home/isaac/p1_dft/compet_{name}_relaxed.cif', atoms)
    except Exception as ex:
        print(f'{name} 失败: {ex}', flush=True)

# 复核 Ehull
if len(energies) == 3:
    E_F9 = -102.4052  # f9hf3o3y_posrelaxed.cif 4x4x4 总能
    E_decomp = (1 * energies['YHfF7'] + 0.5 * energies['HfF4']
                + 1.5 * energies['HfO2'])
    ehull_total = E_F9 - E_decomp   # >0: F9 高于凸包(不稳定); <0: 稳定
    ehull_per_atom = ehull_total / 16
    print(f'\n===== DFT 复核 (第二级) =====', flush=True)
    print(f'E(F9)        = {E_F9:.4f} eV', flush=True)
    print(f'E(YHfF7)     = {energies["YHfF7"]:.4f} eV', flush=True)
    print(f'E(HfF4)      = {energies["HfF4"]:.4f} eV', flush=True)
    print(f'E(HfO2)      = {energies["HfO2"]:.4f} eV', flush=True)
    print(f'E(分解组合)   = {E_decomp:.4f} eV', flush=True)
    print(f'DFT Ehull    = {ehull_total:.4f} eV (总)  {ehull_per_atom:.4f} eV/atom', flush=True)
    if ehull_per_atom < 0.001:
        print('-> 稳定 (在凸包上)', flush=True)
    elif ehull_per_atom < 0.1:
        print('-> 亚稳态', flush=True)
    else:
        print('-> 不稳定', flush=True)
    out = {'E_F9': E_F9, 'E_phases': energies, 'E_decomp': E_decomp,
           'ehull_total': ehull_total, 'ehull_per_atom': ehull_per_atom}
    with open('/home/isaac/p1_dft/dft_ehull_F9.json', 'w') as f:
        json.dump(out, f, indent=2)
    print('已保存 dft_ehull_F9.json', flush=True)
print('完成', flush=True)

"""
补算 DFT 单质参考能量 (自旋 PBE, PW400, 与候选同参数)
- C: 金刚石 (2 原子), N2/H2/Cl2: 分子(真空box), Na: bcc, Pb: fcc
- Hg/S: 液体/分子晶体难算, 用 CHGNet 参考近似 (标注)
输出: dft_ref_energies.json
"""
import warnings; warnings.filterwarnings('ignore')
from ase.build import bulk, molecule
from ase.optimize import FIRE
from ase.filters import ExpCellFilter
from gpaw import GPAW, PW, FermiDirac, Mixer
import numpy as np
import json
import os; os.environ['GPAW_SETUP_PATH'] = '/usr/local/lib/python3.12/dist-packages/gpaw_data/setups'

def calc_e(atoms, kpts, name, relax_cell=False):
    atoms.calc = GPAW(mode=PW(400), xc='PBE', kpts=kpts,
                      hund=True, occupations=FermiDirac(0.1),
                      mixer=Mixer(beta=0.1, nmaxold=7, weight=100.0),
                      maxiter=500, txt=f'/home/isaac/p1_dft/{name}.txt')
    if relax_cell:
        opt = FIRE(ExpCellFilter(atoms))
    else:
        opt = FIRE(atoms)
    opt.run(fmax=0.03, steps=200)
    return atoms.get_potential_energy()

refs = {}
# 1. C 金刚石
C = bulk('C', 'diamond', a=3.57, cubic=True)
refs['C'] = calc_e(C, (4,4,4), 'ref_C') / len(C)
print(f'C(diamond) = {refs["C"]:.4f} eV/atom', flush=True)

# 2. N2 分子
N2 = molecule('N2')
N2.center(vacuum=6.0)
refs['N'] = calc_e(N2, (1,1,1), 'ref_N2') / 2
print(f'N(N2) = {refs["N"]:.4f} eV/atom', flush=True)

# 3. H2 分子
H2 = molecule('H2')
H2.center(vacuum=6.0)
refs['H'] = calc_e(H2, (1,1,1), 'ref_H2') / 2
print(f'H(H2) = {refs["H"]:.4f} eV/atom', flush=True)

# 4. Na bcc
Na = bulk('Na', 'bcc', a=4.23, cubic=True)
refs['Na'] = calc_e(Na, (4,4,4), 'ref_Na', relax_cell=True) / len(Na)
print(f'Na(bcc) = {refs["Na"]:.4f} eV/atom', flush=True)

# 5. Cl2 分子
Cl2 = molecule('Cl2')
Cl2.center(vacuum=6.0)
refs['Cl'] = calc_e(Cl2, (1,1,1), 'ref_Cl2') / 2
print(f'Cl(Cl2) = {refs["Cl"]:.4f} eV/atom', flush=True)

# 6. Pb fcc
Pb = bulk('Pb', 'fcc', a=4.95, cubic=True)
refs['Pb'] = calc_e(Pb, (4,4,4), 'ref_Pb', relax_cell=True) / len(Pb)
print(f'Pb(fcc) = {refs["Pb"]:.4f} eV/atom', flush=True)

# 7/8. Hg, S: 从 CHGNet 参考 (近似, 标注)
import sys
chgnet_path = '/mnt/d/nature reproduction/mattergen/elemental_ref_energies.json'
with open(chgnet_path, encoding='utf-8') as f:
    chg = json.load(f)
refs['Hg'] = chg['Hg']  # 近似 (液体难算)
refs['S'] = chg['S']    # 近似
print(f'Hg(approx) = {refs["Hg"]:.4f}, S(approx) = {refs["S"]:.4f}  [CHGNet 近似]', flush=True)

with open('/home/isaac/p1_dft/dft_ref_energies.json', 'w') as f:
    json.dump(refs, f, indent=2)
print('已保存 dft_ref_energies.json', flush=True)

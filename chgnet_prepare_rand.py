"""
CHGNet 预弛豫: 随机抽样 7 候选 (C2N2, O5, H4Na2, C2Li6N4, F2O2, Hg2O8S2, Cl3LiPb)
输入: rand_{formula}.cif → 输出: chgnet_relaxed_rand_{formula}.cif
"""
import warnings
warnings.filterwarnings("ignore")
from ase.io import read, write
from ase.optimize import FIRE
from ase.filters import ExpCellFilter
from chgnet.model import CHGNet
from chgnet.model.dynamics import CHGNetCalculator
from pathlib import Path

ROOT = Path(__file__).parent
names = ['C2N2', 'O5', 'H4Na2', 'C2Li6N4', 'F2O2', 'Hg2O8S2', 'Cl3LiPb']

model = CHGNet.load()
print('CHGNet 加载完成')

for name in names:
    src = ROOT / f'rand_{name}.cif'
    if not src.exists():
        print(f'跳过 {name}: 缺 {src.name}')
        continue
    atoms = read(str(src))
    n = len(atoms)
    print(f'\n=== {name} ({n} 原子) ===')
    atoms.calc = CHGNetCalculator(model=model)
    ef = ExpCellFilter(atoms)
    opt = FIRE(ef)
    opt.run(fmax=0.05, steps=300)
    energy = atoms.get_potential_energy()
    print(f'  CHGNet relax: E={energy:.4f} eV  {energy/n:.4f} eV/atom')
    write(str(ROOT / f'chgnet_relaxed_rand_{name}.cif'), atoms)
    print(f'  已保存 chgnet_relaxed_rand_{name}.cif')
print('\n全部完成')

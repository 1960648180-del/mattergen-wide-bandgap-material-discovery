"""提取含f候选 + CHGNet 预弛豫: KO2Pr, DyKO2"""
import warnings
warnings.filterwarnings("ignore")
from ase.io import read, write
from ase.optimize import FIRE
from ase.filters import ExpCellFilter
from chgnet.model import CHGNet
from chgnet.model.dynamics import CHGNetCalculator
from pathlib import Path

ROOT = Path(__file__).parent
# (formula, batch, index)
targets = [('KO2Pr', 'bg_30', 6), ('DyKO2', 'bg_40', 9)]

model = CHGNet.load()
for formula, batch, idx in targets:
    p = f'{ROOT}/extended_pool/{batch}/generated_crystals.extxyz'
    frames = read(p, index=':')
    at = frames[idx]
    got = at.get_chemical_formula()
    if got != formula:
        print(f'⚠️ {batch} idx{idx} 是 {got}, 期望 {formula}, 跳过')
        continue
    src = ROOT / f'felec_{formula}.cif'
    write(str(src), at)
    n = len(at)
    print(f'\n=== {formula} ({n} 原子) 提取自 {batch} idx{idx} ===')
    at.calc = CHGNetCalculator(model=model)
    ef = ExpCellFilter(at)
    opt = FIRE(ef)
    opt.run(fmax=0.05, steps=300)
    energy = at.get_potential_energy()
    print(f'  CHGNet relax: E={energy:.4f} eV  {energy/n:.4f} eV/atom')
    write(str(ROOT / f'chgnet_relaxed_fe_{formula}.cif'), at)
    print(f'  已保存 chgnet_relaxed_fe_{formula}.cif')
print('\n全部完成')

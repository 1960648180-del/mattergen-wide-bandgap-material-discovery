"""
计算 11 个缺失元素的 CHGNet 参考能量
元素: Be, Bi, Dy, Gd, Hf, Hg, Mo, Pb, Re, Tl, Y
方法: ASE 构建单质结构 → CHGNet 弛豫 → 每原子能量
"""
import warnings
warnings.filterwarnings("ignore")

import json
import numpy as np
from pathlib import Path

from ase.build import bulk
from ase.io import read, write
from ase.optimize import FIRE
from ase.constraints import ExpCellFilter
from chgnet.model import CHGNet
from chgnet.model.dynamics import CHGNetCalculator

ROOT = Path(__file__).parent

# 单质结构 (元素: (晶体结构, 晶格参数))
ELEMENT_STRUCTURES = {
    'Be': ('hcp', dict(a=2.29, c=3.58)),
    'Bi': ('rhombohedral', dict(a=4.75, alpha=57.35)),  # A7 结构
    'Dy': ('hcp', dict(a=3.59, c=5.65)),
    'Gd': ('hcp', dict(a=3.64, c=5.78)),
    'Hf': ('hcp', dict(a=3.19, c=5.05)),
    'Hg': ('rhombohedral', dict(a=3.47, alpha=70.5)),   # 体心三角
    'Mo': ('bcc', dict(a=3.15)),
    'Pb': ('fcc', dict(a=4.95)),
    'Re': ('hcp', dict(a=2.76, c=4.46)),
    'Tl': ('hcp', dict(a=3.46, c=5.52)),
    'Y':  ('hcp', dict(a=3.65, c=5.73)),
}

def main():
    model = CHGNet.load()
    print(f"CHGNet 加载完成")
    
    ref_energies = {}
    for element, (crystal, params) in ELEMENT_STRUCTURES.items():
        try:
            atoms = bulk(element, crystalstructure=crystal, **params)
            n = len(atoms)
            atoms.calc = CHGNetCalculator(model=model)
            
            # 弛豫
            filter = ExpCellFilter(atoms)
            opt = FIRE(filter)
            opt.run(fmax=0.05, steps=200)
            
            energy = atoms.get_potential_energy()
            energy_per_atom = energy / n
            ref_energies[element] = energy_per_atom
            print(f"  {element}: {crystal} {n}原子  E/atom={energy_per_atom:.6f} eV")
        except Exception as e:
            print(f"  {element}: 失败 - {e}")
    
    # 保存
    out_file = ROOT / "chgnet_missing_refs.json"
    with open(out_file, 'w') as f:
        json.dump(ref_energies, f, indent=2)
    print(f"\n已保存 {len(ref_energies)} 个参考能量: {out_file}")
    
    return ref_energies

if __name__ == "__main__":
    main()

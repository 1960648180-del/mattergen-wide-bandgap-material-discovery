"""
CHGNet 预弛豫: F6Rb3Y 原始结构 → CHGNet relaxed CIF + 能量
作为 F6Rb3Y 新方案 DFT relax 的起点 (Mixer 0.1 + 磁矩 0 + fmax 0.05)
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

def main():
    model = CHGNet.load()
    print(f"CHGNet 加载完成")

    name = "F6Rb3Y"
    raw_cif = ROOT / f"dft_{name}.cif"
    atoms = read(str(raw_cif))
    n = len(atoms)
    print(f"\n=== {name} ({n} 原子) ===")
    print(f"  原始晶胞: {atoms.cell.lengths()}")

    atoms.calc = CHGNetCalculator(model=model)
    ef = ExpCellFilter(atoms)
    opt = FIRE(ef)
    opt.run(fmax=0.05, steps=300)

    energy = atoms.get_potential_energy()
    print(f"  CHGNet relax: E={energy:.4f} eV  {energy/n:.4f} eV/atom")
    print(f"  晶胞: {atoms.cell.lengths()}")

    out_cif = ROOT / f"chgnet_relaxed_{name}.cif"
    write(str(out_cif), atoms)
    print(f"  已保存: {out_cif}")

if __name__ == "__main__":
    main()

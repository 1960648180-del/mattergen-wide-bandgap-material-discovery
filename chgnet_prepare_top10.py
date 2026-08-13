"""
CHGNet 预弛豫: 扩 Top10 三候选 (F3Sc, F3La, BaF6Si)
输入: F3La.cif, BaF6Si.cif, dft_F3Sc.cif (Windows venv 跑, GPU)
输出: chgnet_relaxed_{name}.cif
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

def relax(name, raw_cif):
    model = CHGNet.load()
    atoms = read(str(raw_cif))
    n = len(atoms)
    print(f"\n=== {name} ({n} 原子) ===")
    print(f"  原始晶胞: {[round(x,3) for x in atoms.cell.lengths()]}")

    atoms.calc = CHGNetCalculator(model=model)
    ef = ExpCellFilter(atoms)
    opt = FIRE(ef)
    opt.run(fmax=0.05, steps=300)

    energy = atoms.get_potential_energy()
    print(f"  CHGNet relax: E={energy:.4f} eV  {energy/n:.4f} eV/atom")
    print(f"  晶胞: {[round(x,3) for x in atoms.cell.lengths()]}")

    out_cif = ROOT / f"chgnet_relaxed_{name}.cif"
    write(str(out_cif), atoms)
    print(f"  已保存: {out_cif}")

if __name__ == "__main__":
    for name, cif in [("F3Sc", "dft_F3Sc.cif"),
                      ("F3La", "F3La.cif"),
                      ("BaF6Si", "BaF6Si.cif")]:
        p = ROOT / cif
        if not p.exists():
            print(f"跳过 {name}: 缺少 {cif}")
            continue
        relax(name, p)
    print("\n全部完成")

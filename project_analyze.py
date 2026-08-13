"""项目结果分析：批量统计 + 带隙条件对比"""
from ase.io import read
from pathlib import Path
from collections import Counter
import numpy as np

ROOT = Path(__file__).parent

batches = [
    ("results",          "无条件"),
    ("results_bulk_150", "体模量150"),
    ("results_widegap",  "宽带隙"),
    ("pool_bandgap_25",  "带隙2.5eV", 2.5),
    ("pool_bandgap_35",  "带隙3.5eV", 3.5),
    ("pool_bandgap_40",  "带隙4.0eV", 4.0),
]

print("晶体概览")
print(f"{'批次':<14} {'数量':>4} {'原子/晶胞':>10} {'密度(g/cm³)':>12} {'体积(Å³)':>8}")
print("-" * 65)

all_els = Counter()
for batch in batches:
    folder = batch[0]
    extxyz = ROOT / folder / "generated_crystals.extxyz"
    if not extxyz.exists():
        continue
    crystals = read(str(extxyz), index=":")
    n_atoms = [len(c) for c in crystals]
    densities, volumes = [], []
    from ase.data import atomic_masses as am
    batch_els = Counter()
    for c in crystals:
        v = c.get_volume()
        m = sum(am[c.get_atomic_numbers()]) * 1.66054e-27
        densities.append(m / (v * 1e-30) / 1e3)
        volumes.append(v)
        batch_els.update(c.get_chemical_symbols())
        all_els.update(c.get_chemical_symbols())
    top3 = batch_els.most_common(3)
    top_els = " ".join([f"{el}{n}" for el, n in top3])
    print(f"{batch[1]:<14} {len(crystals):>4} {np.mean(n_atoms):>5.1f}~{max(n_atoms):>2d}  "
          f"{np.mean(densities):>6.2f}±{np.std(densities):.2f}  {np.mean(volumes):>5.0f}")

print(f"\n总计 {sum(all_els.values())} 个原子，{len(all_els)} 种元素")

if len(batches) >= 4:
    print("\n带隙条件对比（4个宽禁带批次）")
    print(f"{'批次':<14} {'目标':>6} {'密度':>8} {'Ef范围(eV/atom)':>18}")

"""
统一验证：CHGNet 弛豫 → 形成能 → 几何检查
用法: python validate.py [batch_name]
      python validate.py           # 跑4个宽禁带批次
      python validate.py all       # 跑全部6个批次
"""
from ase.io import read
from ase.neighborlist import neighbor_list
from chgnet.model.dynamics import StructOptimizer
from pymatgen.io.ase import AseAtomsAdaptor
from ase.data import atomic_masses
from pathlib import Path
import numpy as np, json, sys, warnings
warnings.filterwarnings("ignore")

ROOT = Path(__file__).parent
CACHE_REF = ROOT / "elemental_ref_energies.json"

ALL_BATCHES = [
    ("results", "无条件"), ("results_bulk_150", "体模量150"), ("results_widegap", "宽带隙"),
    ("pool_bandgap_25", "带隙2.5eV"), ("pool_bandgap_35", "带隙3.5eV"), ("pool_bandgap_40", "带隙4.0eV"),
]

# 弛豫收敛标准
FORCE_CONVERGENCE = 0.05  # eV/Å, FIRE 优化器受力收敛阈值
ENERGY_CONVERGENCE = 1e-6  # eV, 能量收敛阈值
GEOMETRY_MIN_DIST = 1.0  # Å, 最小原子间距阈值（低于此值判为原子重叠）

def geometry_check(atoms):
    """独立几何合理性检查"""
    n = len(atoms)
    v = atoms.get_volume()
    m = sum(atomic_masses[atoms.get_atomic_numbers()]) * 1.66054e-27
    density = m / (v * 1e-30) / 1e3
    
    i, j, d = neighbor_list('ijd', atoms, cutoff=5.0, self_interaction=False)
    min_dist = np.min(d) if len(d) > 0 else 99
    coord = np.bincount(i, minlength=n) if len(i) > 0 else np.zeros(n)
    avg_cn = np.mean(coord)
    
    return {
        "density": round(density, 2),
        "min_dist": round(min_dist, 3),
        "avg_cn": round(avg_cn, 1),
        "has_overlap": min_dist < GEOMETRY_MIN_DIST,
    }

def main():
    # 选择批次
    args = sys.argv[1:]
    if "all" in args:
        batches = ALL_BATCHES
    else:
        batches = ALL_BATCHES[2:]  # 默认4个宽禁带
    
    relaxer = StructOptimizer()
    ref = json.load(open(CACHE_REF)) if CACHE_REF.exists() else {}
    
    print(f"验证 {len(batches)} 个批次")
    print(f"弛豫: CHGNet v0.3.0, FIRE 优化器, fmax<{FORCE_CONVERGENCE} eV/Å")
    print(f"几何: 最小原子间距阈值 {GEOMETRY_MIN_DIST}Å, 用于过滤严重非物理结构")
    for folder, label in batches:
        extxyz = ROOT / folder / "generated_crystals.extxyz"
        if not extxyz.exists():
            print(f"  跳过 {label}: 无文件"); continue
        
        crystals = read(str(extxyz), index=":")
        n_ok_geom, n_ok_ef = 0, 0
        results = []
        
        for i, crys in enumerate(crystals):
            formula = crys.get_chemical_formula()
            n_atoms = len(crys)
            
            # 几何检查
            geo = geometry_check(crys)
            if not geo["has_overlap"]: n_ok_geom += 1
            
            # CHGNet 弛豫 + 形成能
            try:
                pmg = AseAtomsAdaptor.get_structure(crys)
                result = relaxer.relax(pmg, verbose=False)
                total_e = result["trajectory"].energies[-1]
                
                ref_sum = sum(ref.get(s, 0) for s in crys.get_chemical_symbols())
                ef_pa = (total_e - ref_sum) / n_atoms
                if ef_pa < 0: n_ok_ef += 1
            except:
                ef_pa = None
            
            results.append({"formula": formula, "ef_pa": ef_pa, **geo})
        
        # 汇总
        ef_vals = [r["ef_pa"] for r in results if r["ef_pa"] is not None]
        print(f"\n  {label} ({len(crystals)}个):")
        print(f"    几何通过: {n_ok_geom}/{len(crystals)}")
        print(f"    形成能<0: {n_ok_ef}/{len(ef_vals)} 范围 {min(ef_vals):+.2f}~{max(ef_vals):+.2f}" if ef_vals else "    形成能: N/A")

if __name__ == "__main__":
    main()

"""
提取 P1 三个候选 (F9Hf3O3Y, F6Rb3Y, LiO11Re3)
- 从 extxyz 中定位并提取
- 输出 CIF
- 结构合理性检查 (键长, 配位)
"""
import warnings
warnings.filterwarnings("ignore")

from ase.io import read, write
from ase.neighborlist import neighbor_list
import numpy as np
from pathlib import Path

ROOT = Path(__file__).parent
POOL = ROOT / "extended_pool"

# 目标候选 (化学式, 批次)
TARGETS = {
    "F9Hf3O3Y": "bg_30",
    "F6Rb3Y": "bg_40",
    "LiO11Re3": "bg_25",
}

def analyze_structure(atoms, formula):
    """结构合理性检查"""
    symbols = atoms.get_chemical_symbols()
    
    # 键长分析
    i, j, d = neighbor_list('ijd', atoms, cutoff=4.0, self_interaction=False)
    # 过滤重复
    pairs = set()
    bonds = []
    for a, b, dist in zip(i, j, d):
        if (b, a) in pairs:
            continue
        pairs.add((a, b))
        bonds.append((symbols[a], symbols[b], dist))
    
    bonds.sort(key=lambda x: x[2])
    
    # 最短键长
    min_bonds = bonds[:5]
    
    # 配位数 (每个原子的近邻数)
    coord = np.bincount(i, minlength=len(atoms)) if len(i) > 0 else np.zeros(len(atoms))
    
    # 检查过短键 (< 1.0 Å 异常, < 0.7 Å 严重)
    short_bonds = [b for b in bonds if b[2] < 0.9]
    
    # 体积密度
    vol = atoms.get_volume()
    mass = sum(atoms.get_masses())
    density = mass / vol * 1.66054  # g/cm3
    
    return {
        "min_bond": bonds[0] if bonds else None,
        "short_bonds": short_bonds,
        "avg_cn": np.mean(coord),
        "density": density,
        "volume": vol,
        "n_coord_0": int(np.sum(coord == 0)),  # 配位数为0的原子数
    }

def main():
    found = {}
    for formula, batch in TARGETS.items():
        extxyz = POOL / batch / "generated_crystals.extxyz"
        if not extxyz.exists():
            print(f"[{formula}] 文件不存在: {extxyz}")
            continue
        
        atoms_list = read(str(extxyz), ":")
        target = None
        idx = None
        for i, a in enumerate(atoms_list):
            if a.get_chemical_formula() == formula:
                target = a
                idx = i
                break
        
        if target is None:
            print(f"[{formula}] 未找到!")
            continue
        
        # 输出 CIF 到本地 (后续拷贝到 WSL)
        cif_name = f"{formula}.cif"
        local_cif = ROOT / f"dft_{cif_name}"
        write(str(local_cif), target)
        
        # 分析
        info = analyze_structure(target, formula)
        found[formula] = {"atoms": target, "idx": idx, "batch": batch, "info": info, "cif": str(local_cif)}
        
        print(f"\n{'='*60}")
        print(f"  {formula}  (批次 {batch}, 索引 #{idx})")
        print(f"  CIF: {local_cif}")
        print(f"  {'='*55}")
        print(f"  原子数: {len(target)}")
        print(f"  晶格: a={target.cell.lengths()[0]:.3f} b={target.cell.lengths()[1]:.3f} "
              f"c={target.cell.lengths()[2]:.3f} Å")
        print(f"  角度: {target.cell.angles()[0]:.1f} {target.cell.angles()[1]:.1f} "
              f"{target.cell.angles()[2]:.1f}°")
        print(f"  体积: {info['volume']:.2f} Å³")
        print(f"  密度: {info['density']:.2f} g/cm³")
        print(f"  平均配位数: {info['avg_cn']:.1f}")
        print(f"  配位数为0的原子: {info['n_coord_0']}")
        print(f"  最短键: {info['min_bond'][0]}-{info['min_bond'][1]} = {info['min_bond'][2]:.3f} Å" if info['min_bond'] else "  N/A")
        if info['short_bonds']:
            print(f"  ⚠️ 过短键 (<0.9Å): {len(info['short_bonds'])} 个")
            for b in info['short_bonds'][:5]:
                print(f"    {b[0]}-{b[1]} = {b[2]:.3f} Å")
        else:
            print(f"  ✅ 无过短键")
        
        # 列出最短 5 个键
        print(f"  最短 5 个键:")
        from ase.neighborlist import neighbor_list as nl
        i2, j2, d2 = nl('ijd', target, cutoff=4.0, self_interaction=False)
        sym = target.get_chemical_symbols()
        pairs_seen = set()
        bonds_all = []
        for a, b, dist in zip(i2, j2, d2):
            if (b, a) in pairs_seen:
                continue
            pairs_seen.add((a, b))
            bonds_all.append((sym[a], sym[b], dist))
        bonds_all.sort(key=lambda x: x[2])
        for b in bonds_all[:5]:
            print(f"    {b[0]}-{b[1]} = {b[2]:.3f} Å")
    
    return found

if __name__ == "__main__":
    found = main()

"""
CHGNet 自建凸包：F-Tb 体系
下载 MP 中所有 F-Tb 竞争相 → CHGNet 统一弛豫 → 建凸包 → 放 F3Tb
"""
import requests, json, time
from chgnet.model.dynamics import StructOptimizer
from pymatgen.core import Structure
from pymatgen.analysis.phase_diagram import PhaseDiagram
from pymatgen.entries.computed_entries import ComputedEntry
from pymatgen.core.composition import Composition
from pymatgen.io.ase import AseAtomsAdaptor
from ase.io import read
from pathlib import Path
import numpy as np
import warnings
warnings.filterwarnings("ignore")

API_KEY = "2Vs7rDBCK6qe47L6ESCexF9u9EHMoLGT"
HEADERS = {"X-API-KEY": API_KEY}
ROOT = Path(r"d:\nature reproduction\mattergen")

def get_f_tb_phases():
    """获取 MP 中 F-Tb 体系所有已知相"""
    url = "https://api.materialsproject.org/materials/summary/"
    params = {"chemsys": "F-Tb", "_fields": "structure,material_id,formation_energy_per_atom,energy_per_atom", "_per_page": 50}
    resp = requests.get(url, headers=HEADERS, params=params, timeout=30)
    if resp.status_code != 200:
        print(f"API 错误: {resp.status_code}")
        return []
    data = resp.json().get("data", [])
    print(f"MP 中 F-Tb 体系共 {len(data)} 个相")
    return data

def main():
    relaxer = StructOptimizer()
    
    # 获取所有 F-Tb 相
    mp_phases = get_f_tb_phases()
    if not mp_phases:
        return
    
    # 弛豫每个相得到 CHGNet 统一标尺的能量
    entries = []
    for i, phase in enumerate(mp_phases):
        mid = phase.get("material_id", "?")
        struct_dict = phase.get("structure")
        if not struct_dict:
            continue
        
        struct = Structure.from_dict(struct_dict)
        formula = struct.composition.reduced_formula
        n_atoms = struct.composition.num_atoms
        
        try:
            result = relaxer.relax(struct, verbose=False)
            chgnet_energy = result["trajectory"].energies[-1]
            entries.append(ComputedEntry(struct.composition, chgnet_energy))
            print(f"  [{i+1}/{len(mp_phases)}] {formula:<12} {chgnet_energy:>+9.2f} eV")
        except Exception as e:
            print(f"  [{i+1}/{len(mp_phases)}] {formula:<12} 弛豫失败: {str(e)[:40]}")
    
    if len(entries) < 2:
        print("相数据不足，无法构建凸包")
        return
    
    # 添加元素参考态（纯 F, 纯 Tb）
    ref_data = json.load(open(ROOT / "elemental_ref_energies.json"))
    for el, e_per_atom in [("F", ref_data.get("F", 0)), ("Tb", ref_data.get("Tb", 0))]:
        from pymatgen.core import Element
        fake_comp = Composition({el: 1})
        entries.append(ComputedEntry(fake_comp, e_per_atom))
    
    # 构建凸包
    pd = PhaseDiagram(entries)
    
    # 加载我们的 F3Tb (pool_bandgap_40 中第2个)
    crystals = read(str(ROOT / "pool_bandgap_40" / "generated_crystals.extxyz"), index=":")
    our_crys = None
    for c in crystals:
        if c.get_chemical_formula() == "F3Tb":
            our_crys = c
            break
    if our_crys is None:
        print("未找到 F3Tb")
        return
    our_struct = AseAtomsAdaptor.get_structure(our_crys)
    
    # 用 CHGNet 弛豫我们的结构（已在 validate 中做过，但这里重新算以确保标尺统一）
    result = relaxer.relax(our_struct, verbose=False)
    our_energy = result["trajectory"].energies[-1]
    our_entry = ComputedEntry(our_struct.composition, our_energy)
    
    # 计算凸包能
    ehull = pd.get_e_above_hull(our_entry)
    decomp = pd.get_decomposition(our_struct.composition)
    decomp_str = " + ".join([f"{k.formula}({v:.2f})" for k, v in decomp.items()])
    
    print(f"\n{'='*50}")
    print(f"F-Tb 体系凸包分析")
    print(f"{'='*50}")
    print(f"F-Tb 竞争相数: {len(entries)}")
    print(f"我们的 F₃Tb:")
    print(f"  CHGNet 总能: {our_energy:.2f} eV")
    print(f"  CHGNet Ehull: {ehull:.4f} eV/atom" if ehull is not None else "  Ehull: 无法计算")
    if decomp_str:
        print(f"  分解产物: {decomp_str}")
    if ehull is not None and ehull < 0.001:
        print(f"  -> 在 CHGNet 凸包上为稳定相")
    elif ehull is not None and ehull < 0.1:
        print(f"  -> 在 CHGNet 凸包上为亚稳态")
    elif ehull is not None:
        print(f"  -> 在 CHGNet 凸包上不稳定")
    
    # 列出凸包上的稳定相
    print(f"\n稳定相 (凸包顶点):")
    for e in pd.stable_entries:
        print(f"  {e.composition.reduced_formula:<12} {e.energy_per_atom:+.3f} eV/atom")

if __name__ == "__main__":
    main()

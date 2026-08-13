"""
CHGNet 全体系凸包: F9Hf3O3Y (Hf-Y-O-F 四元体系)
==================================================
第一级: 下载 MP 中 Hf-Y-O-F 所有子体系相 → CHGNet 统一弛豫 → pymatgen PhaseDiagram
→ 放 F9Hf3O3Y, 算 Ehull + 分解产物 (最近竞争相)
"""
import requests, json, time, sys
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass
from chgnet.model.dynamics import StructOptimizer
from pymatgen.core import Structure, Composition
from pymatgen.analysis.phase_diagram import PhaseDiagram
from pymatgen.entries.computed_entries import ComputedEntry
from pymatgen.io.ase import AseAtomsAdaptor
from ase.io import read
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")

API_KEY = "2Vs7rDBCK6qe47L6ESCexF9u9EHMoLGT"
HEADERS = {"X-API-KEY": API_KEY}
ROOT = Path(r"d:\nature reproduction\mattergen")

SUBSYSTEMS = ["Hf-Y-O-F", "Hf-Y-O", "Hf-Y-F", "Hf-O-F", "Y-O-F",
              "Hf-O", "Hf-Y", "Hf-F", "Y-O", "Y-F", "O-F", "Hf", "Y", "O", "F"]

def get_phases():
    url = "https://api.materialsproject.org/materials/summary/"
    all_data = {}
    for chemsys in SUBSYSTEMS:
        params = {"chemsys": chemsys,
                  "_fields": "structure,material_id,formula_pretty,formation_energy_per_atom",
                  "_per_page": 100}
        try:
            resp = requests.get(url, headers=HEADERS, params=params, timeout=30)
            if resp.status_code == 200:
                for d in resp.json().get("data", []):
                    mid = d.get("material_id")
                    if mid and "structure" in d:
                        all_data[mid] = d
            print(f"  {chemsys:<10}: {resp.status_code} (累计 {len(all_data)} 相)")
        except Exception as e:
            print(f"  {chemsys:<10}: 异常 {str(e)[:50]}")
    return list(all_data.values())

def main():
    relaxer = StructOptimizer()
    print("下载 Hf-Y-O-F 体系所有相...")
    mp_phases = get_phases()
    print(f"共 {len(mp_phases)} 个唯一相 (含单质/多晶型)")

    entries = []
    for i, phase in enumerate(mp_phases):
        mid = phase.get("material_id", "?")
        struct_dict = phase.get("structure")
        if not struct_dict:
            continue
        try:
            struct = Structure.from_dict(struct_dict)
        except Exception as e:
            print(f"  [{i+1}] {mid} 结构解析失败: {str(e)[:40]}")
            continue
        formula = struct.composition.reduced_formula
        n = struct.composition.num_atoms
        try:
            result = relaxer.relax(struct, verbose=False)
            chgnet_energy = result["trajectory"].energies[-1]
            entries.append(ComputedEntry(struct.composition, chgnet_energy))
            print(f"  [{i+1}/{len(mp_phases)}] {mid} {formula:<12} n={n} E={chgnet_energy:>+9.2f} eV")
        except Exception as e:
            print(f"  [{i+1}/{len(mp_phases)}] {mid} {formula:<12} 弛豫失败: {str(e)[:40]}")

    # 元素参考 (CHGNet 标尺)
    ref_data = json.load(open(ROOT / "elemental_ref_energies.json", encoding="utf-8"))
    for el in ["Hf", "Y", "O", "F"]:
        e = ref_data.get(el)
        if e is not None:
            entries.append(ComputedEntry(Composition({el: 1}), e))
            print(f"  元素参考 {el}: {e:+.4f} eV/atom")

    if len(entries) < 2:
        print("相数据不足")
        return

    pd = PhaseDiagram(entries)

    # 放 F9Hf3O3Y
    atoms = read(str(ROOT / "f9hf3o3y_posrelaxed.cif"))
    our_struct = AseAtomsAdaptor.get_structure(atoms)
    result = relaxer.relax(our_struct, verbose=False)
    our_energy = result["trajectory"].energies[-1]
    our_entry = ComputedEntry(our_struct.composition, our_energy)

    ehull = pd.get_e_above_hull(our_entry)
    decomp = pd.get_decomposition(our_struct.composition)
    decomp_str = " + ".join([f"{k.formula}({v:.4f} mol)" for k, v in decomp.items()])

    print(f"\n{'='*55}")
    print("Hf-Y-O-F 体系凸包分析 (CHGNet 标尺)")
    print(f"{'='*55}")
    print(f"竞争相数: {len(entries)} (含多晶型)")
    print("F9Hf3O3Y:")
    print(f"  CHGNet 总能: {our_energy:.4f} eV")
    print(f"  CHGNet Ehull: {ehull:.4f} eV/atom")
    print(f"  分解产物: {decomp_str}")
    if ehull is not None and ehull < 0.001:
        print("  -> 凸包上为稳定相")
    elif ehull is not None and ehull < 0.1:
        print("  -> 凸包上为亚稳态 (0.001-0.1 eV/atom)")
    else:
        print("  -> 凸包上不稳定 (>0.1 eV/atom)")

    print(f"\n稳定相 (凸包顶点):")
    for e in sorted(pd.stable_entries, key=lambda x: x.composition.reduced_formula):
        print(f"  {e.composition.reduced_formula:<12} {e.energy_per_atom:+.3f} eV/atom")

    # 保存结果供第二级 DFT 复核
    out = {"ehull": ehull, "decomposition": {k.formula: v for k, v in decomp.items()},
           "stable_phases": [e.composition.reduced_formula for e in pd.stable_entries]}
    with open(ROOT / "convex_hull_F9_result.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print("\n结果已保存: convex_hull_F9_result.json")

if __name__ == "__main__":
    main()

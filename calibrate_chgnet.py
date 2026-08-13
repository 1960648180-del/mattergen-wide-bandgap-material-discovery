"""
CHGNet 形成能与 MP-DFT 数据对比
读取 extxyz, CHGNet 弛豫得形成能, 查 MP 相同组成对比
"""
import requests, json, time
from ase.io import read
from chgnet.model.dynamics import StructOptimizer
from pymatgen.io.ase import AseAtomsAdaptor
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")

API_KEY = "2Vs7rDBCK6qe47L6ESCexF9u9EHMoLGT"
HEADERS = {"X-API-KEY": API_KEY}
ROOT = Path(r"d:\nature reproduction\mattergen")
REF = json.load(open(ROOT / "elemental_ref_energies.json"))

BATCHES = [
    ("results_widegap", "宽带隙"),
    ("pool_bandgap_25", "带隙2.5eV"),
    ("pool_bandgap_35", "带隙3.5eV"),
    ("pool_bandgap_40", "带隙4.0eV"),
]

def query_mp(formula):
    url = "https://api.materialsproject.org/materials/thermo/"
    params = {"formula": formula, "_fields": "formation_energy_per_atom,material_id", "_per_page": 3}
    try:
        resp = requests.get(url, headers=HEADERS, params=params, timeout=15)
        if resp.status_code == 200:
            data = resp.json().get("data", [])
            if data:
                return data[0]["formation_energy_per_atom"], data[0].get("material_id", "?")
    except:
        pass
    return None, None

def main():
    relaxer = StructOptimizer()
    comparisons = []
    total = 0

    for folder, label in BATCHES:
        extxyz = ROOT / folder / "generated_crystals.extxyz"
        if not extxyz.exists():
            continue
        for crys in read(str(extxyz), index=":"):
            total += 1
            symbols = crys.get_chemical_symbols()
            formula = crys.get_chemical_formula()

            pmg = AseAtomsAdaptor.get_structure(crys)
            result = relaxer.relax(pmg, verbose=False)
            total_e = result["trajectory"].energies[-1]
            n = len(symbols)
            chgnet_ef = (total_e - sum(REF.get(s, 0) for s in symbols)) / n

            mp_ef, mp_id = query_mp(formula)
            if mp_ef is not None:
                comparisons.append({
                    "formula": formula, "batch": label,
                    "CHGNet_Ef": round(chgnet_ef, 4),
                    "MP_PBE_Ef": round(mp_ef, 4),
                    "diff": round(chgnet_ef - mp_ef, 4),
                    "mp_id": mp_id,
                })

            if total % 10 == 0:
                time.sleep(0.3)

    print(f"处理了 {total} 个晶体，找到 {len(comparisons)} 个 MP 匹配")
    if not comparisons:
        return

    print(f"\n{'化学式':<20} {'批次':<10} {'CHGNet Ef':>10} {'MP-PBE Ef':>10} {'差值':>8} {'MP ID':<12}")
    print("-" * 75)
    for c in sorted(comparisons, key=lambda x: abs(x["diff"]))[:20]:
        print(f"{c['formula']:<20} {c['batch']:<10} {c['CHGNet_Ef']:>+8.3f}  {c['MP_PBE_Ef']:>+8.3f}  {c['diff']:>+7.3f}  {c['mp_id']:<12}")

    diffs = [c["diff"] for c in comparisons]
    chgnet_ef = [c["CHGNet_Ef"] for c in comparisons]
    print(f"\n匹配数: {len(comparisons)}")
    print(f"MAE: {sum(abs(d) for d in diffs)/len(diffs):.3f} eV/atom")
    print(f"RMSE: {(sum(d**2 for d in diffs)/len(diffs))**0.5:.3f} eV/atom")
    print(f"系统偏差: {sum(diffs)/len(diffs):+.3f} eV/atom")
    print(f"符号一致率: {sum(1 for i in range(len(comparisons)) if (chgnet_ef[i]<0)==(mp_ef[i]<0))/len(comparisons)*100:.0f}%")

if __name__ == "__main__":
    main()

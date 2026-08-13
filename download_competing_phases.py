"""下载 F9Hf3O3Y 最近竞争相稳定结构: YHfF7, HfF4, HfO2"""
import requests, json
from pymatgen.core import Structure
from pymatgen.io.cif import CifWriter

API_KEY = "2Vs7rDBCK6qe47L6ESCexF9u9EHMoLGT"
HEADERS = {"X-API-KEY": API_KEY}
url = "https://api.materialsproject.org/materials/summary/"

targets = ["YHfF7", "HfF4", "HfO2"]
for comp in targets:
    params = {"formula": comp, "is_stable": True,
              "_fields": "structure,material_id,formation_energy_per_atom,energy_above_hull",
              "_per_page": 10}
    try:
        resp = requests.get(url, headers=HEADERS, params=params, timeout=30)
        data = resp.json().get("data", []) if resp.status_code == 200 else []
        print(f"{comp}: status={resp.status_code}, {len(data)} 个稳定相")
        if not data:
            continue
        # 选 e_above_hull 最低(最稳定)的
        best = min(data, key=lambda d: d.get("energy_above_hull", 9) or 9)
        mid = best.get("material_id")
        struct = Structure.from_dict(best["structure"])
        eah = best.get("energy_above_hull")
        print(f"  选 {mid} {struct.composition.reduced_formula} "
              f"e_above_hull={eah} n={struct.composition.num_atoms}")
        fname = f"compet_{comp}.cif"
        CifWriter(struct).write_file(fname)
        print(f"  已保存 {fname}")
    except Exception as e:
        print(f"{comp}: 异常 {str(e)[:80]}")

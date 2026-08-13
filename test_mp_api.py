"""测试 MP API: Hf-Y-O-F 体系相下载"""
import requests, json

API_KEY = "2Vs7rDBCK6qe47L6ESCexF9u9EHMoLGT"
HEADERS = {"X-API-KEY": API_KEY}
url = "https://api.materialsproject.org/materials/summary/"

for chemsys in ["Hf-Y-O-F", "Hf-Y-O", "Hf-O", "Y-F"]:
    params = {"chemsys": chemsys,
              "_fields": "material_id,formula_pretty,formation_energy_per_atom,is_stable",
              "_per_page": 50}
    try:
        resp = requests.get(url, headers=HEADERS, params=params, timeout=30)
        print(f"chemsys={chemsys}: status={resp.status_code}")
        if resp.status_code == 200:
            data = resp.json().get("data", [])
            print(f"  {len(data)} 个相")
            for d in data[:8]:
                print(f"    {d.get('material_id')} {d.get('formula_pretty'):<12} "
                      f"Ef={d.get('formation_energy_per_atom', 0):+.3f} stable={d.get('is_stable')}")
        else:
            print(f"  错误: {resp.text[:150]}")
    except Exception as e:
        print(f"chemsys={chemsys}: 异常 {str(e)[:80]}")

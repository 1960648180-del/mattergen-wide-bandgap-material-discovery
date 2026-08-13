"""
结构新颖性分析：64 个晶体 vs MP 已知结构
用 StructureMatcher 做全量比对，输出三类定量结果
"""
from ase.io import read
from pymatgen.analysis.structure_matcher import StructureMatcher
from pymatgen.io.ase import AseAtomsAdaptor
from pathlib import Path
import requests, json, time

API_KEY = "2Vs7rDBCK6qe47L6ESCexF9u9EHMoLGT"
HEADERS = {"X-API-KEY": API_KEY}
ROOT = Path(r"d:\nature reproduction\mattergen")

BATCHES = [
    ("results_widegap", "宽带隙"),
    ("pool_bandgap_25", "带隙2.5eV"),
    ("pool_bandgap_35", "带隙3.5eV"),
    ("pool_bandgap_40", "带隙4.0eV"),
]

# 缓存 MP 结构，避免重复请求
_mp_struct_cache = {}

def get_mp_structures(formula):
    if formula in _mp_struct_cache:
        return _mp_struct_cache[formula]
    # MP 使用标准元素顺序，ASE 的公式可能不匹配
    from pymatgen.core import Composition
    try:
        mp_formula = Composition(formula).reduced_formula
    except:
        mp_formula = formula
    url = "https://api.materialsproject.org/materials/summary/"
    params = {"formula": mp_formula, "_fields": "structure,material_id", "_per_page": 10}
    try:
        resp = requests.get(url, headers=HEADERS, params=params, timeout=30)
        if resp.status_code == 200:
            data = resp.json().get("data", [])
            structures = []
            for d in data:
                s = d.get("structure")
                mid = d.get("material_id", "?")
                if s and s.get("lattice"):
                    try:
                        from pymatgen.core import Structure as PMGStructure
                        struct = PMGStructure.from_dict(s)
                        structures.append((mid, struct))
                    except Exception as e:
                        pass
            _mp_struct_cache[formula] = structures
            return structures
    except:
        pass
    _mp_struct_cache[formula] = []
    return []

def main():
    matcher = StructureMatcher(
        ltol=0.2,   # 晶格参数容差
        stol=0.3,   # 原子位置容差
        angle_tol=5 # 角度容差
    )
    
    known = []        # 与 MP 同构
    new_polymorph = [] # 同组成不同构型
    new_stoich = []    # MP 无此组成
    
    total = 0
    for folder, label in BATCHES:
        extxyz = ROOT / folder / "generated_crystals.extxyz"
        if not extxyz.exists():
            continue
        for crys in read(str(extxyz), index=":"):
            total += 1
            formula = crys.get_chemical_formula()
            symbols = crys.get_chemical_symbols()
            
            # 转 pymatgen
            our_struct = AseAtomsAdaptor.get_structure(crys)
            
            # 查 MP
            mp_structs = get_mp_structures(formula)
            
            if not mp_structs:
                new_stoich.append((formula, label, None))
                continue
            
            # 比对
            matched = False
            for mid, mp_struct in mp_structs:
                if matcher.fit(our_struct, mp_struct):
                    known.append((formula, label, mid))
                    matched = True
                    break
            
            if not matched:
                new_polymorph.append((formula, label, [m[0] for m in mp_structs]))
    
    # 输出
    print(f"\n结构新颖性分析结果")
    print(f"{'='*50}")
    print(f"总样本: {total}")
    print(f"\n分类:")
    print(f"  已知结构 (与 MP 同构):      {len(known)}")
    print(f"  新晶型 (同组成不同结构):    {len(new_polymorph)}")
    print(f"  新化学计量比 (MP 未收录):   {len(new_stoich)}")
    print(f"\n已知结构 ({len(known)}):")
    for f, l, mid in known[:10]:
        print(f"  {f:<20} {l:<10} {mid}")
    print(f"\n新晶型 ({len(new_polymorph)}):")
    for f, l, mids in new_polymorph[:10]:
        print(f"  {f:<20} {l:<10} MP IDs: {', '.join(mids[:3])}")
    print(f"\n新化学计量比 ({len(new_stoich)}):")
    for f, l, _ in new_stoich[:10]:
        print(f"  {f:<20} {l}")

if __name__ == "__main__":
    main()

"""
MatterGen 扩展候选 CHGNet 批量筛选
==================================
输入: extended_pool/ 下各 batch 的 generated_crystals.extxyz
处理: CHGNet 弛豫 + 形成能计算
输出: 
  - screening_extended_result.json (完整结果)
  - 统计 (成功率/能量分布/元素分布/重复率)
  - Top 候选排名 + 推荐 10 个 DFT 验证

用法: python screening_extended.py
"""

import json
import warnings
import os
from pathlib import Path
from collections import Counter, defaultdict

warnings.filterwarnings("ignore")

import numpy as np
from ase.io import read
from ase.optimize import FIRE
from chgnet.model import CHGNet
from chgnet.model.dynamics import CHGNetCalculator
from ase.constraints import ExpCellFilter

# 项目根目录
PROJECT_ROOT = Path(__file__).parent
POOL_DIR = PROJECT_ROOT / "extended_pool"
OUTPUT_JSON = PROJECT_ROOT / "screening_extended_result.json"

# 元素参考能量 (CHGNet)
REF_PATH = PROJECT_ROOT / "elemental_ref_energies.json"


def load_reference_energies() -> dict:
    with open(REF_PATH) as f:
        return json.load(f)


def relax_with_chgnet(atoms):
    """CHGNet 弛豫 + 计算能量"""
    model = CHGNet.load()
    calc = CHGNetCalculator(model=model)
    atoms.calc = calc

    # 弛豫
    filter = ExpCellFilter(atoms)
    opt = FIRE(filter)
    opt.run(fmax=0.05, steps=500)

    energy = atoms.get_potential_energy()
    return atoms, energy


def compute_formation_energy(atoms, total_energy, ref_energies):
    """计算形成能 (eV/atom)"""
    symbols = atoms.get_chemical_symbols()
    n = len(symbols)
    ref_sum = sum(ref_energies.get(s, 0) for s in symbols)
    return (total_energy - ref_sum) / n


def main():
    print("=" * 60)
    print(" MatterGen 扩展候选 CHGNet 筛选")
    print("=" * 60)

    ref_energies = load_reference_energies()
    print(f"加载 {len(ref_energies)} 个元素参考能量")

    # 收集所有 extxyz (排除 test 目录)
    all_extxyz = sorted(
        p for p in POOL_DIR.glob("*/generated_crystals.extxyz")
        if not p.parent.name.startswith("test")
    )
    if not all_extxyz:
        print("未找到生成文件! 请先运行生成 pipeline")
        return

    # 加载 CHGNet 模型 (只加载一次)
    model = CHGNet.load()
    calc = CHGNetCalculator(model=model)

    results = []
    total_count = 0
    success_count = 0

    for extxyz in all_extxyz:
        batch_name = extxyz.parent.name
        try:
            atoms_list = read(str(extxyz), ":")
        except Exception as e:
            print(f"  [{batch_name}] 读取失败: {e}")
            continue

        for i, atoms in enumerate(atoms_list):
            total_count += 1
            formula = atoms.get_chemical_formula()
            try:
                atoms.calc = calc
                # 弛豫
                filter = ExpCellFilter(atoms)
                opt = FIRE(filter)
                opt.run(fmax=0.05, steps=300)

                energy = atoms.get_potential_energy()
                n_atoms = len(atoms)
                ef = compute_formation_energy(atoms, energy, ref_energies)
                symbols = atoms.get_chemical_symbols()
                element_counter = Counter(symbols)

                results.append({
                    "batch": batch_name,
                    "index": i,
                    "formula": formula,
                    "n_atoms": n_atoms,
                    "total_energy": energy,
                    "energy_per_atom": energy / n_atoms,
                    "formation_energy": ef,
                    "elements": dict(element_counter),
                })
                success_count += 1
                print(f"  [{batch_name} #{i}] {formula} ({n_atoms}原子) Ef={ef:.3f}")
            except Exception as e:
                print(f"  [{batch_name} #{i}] {formula} 失败: {e}")

    # ===== 统计 =====
    print()
    print("=" * 60)
    print(" 统计结果")
    print("=" * 60)

    # 成功率
    print(f"\n总候选: {total_count}")
    print(f"成功: {success_count} ({success_count/max(total_count,1)*100:.1f}%)")
    print(f"失败: {total_count - success_count}")

    if not results:
        print("无成功结果!")
        return

    # 能量分布
    efs = [r["formation_energy"] for r in results]
    print(f"\n形成能分布 (eV/atom):")
    print(f"  范围: {min(efs):.3f} ~ {max(efs):.3f}")
    print(f"  均值: {np.mean(efs):.3f}")
    print(f"  中位数: {np.median(efs):.3f}")
    print(f"  标准差: {np.std(efs):.3f}")
    print(f"  负形成能比例: {sum(1 for e in efs if e < 0)/len(efs)*100:.1f}%")

    # 元素分布
    element_counter = Counter()
    for r in results:
        for el, n in r["elements"].items():
            element_counter[el] += n
    print(f"\n元素分布 (Top 15):")
    for el, count in element_counter.most_common(15):
        print(f"  {el}: {count}")

    # 化学式重复率
    formula_counter = Counter(r["formula"] for r in results)
    dup_formulas = {f: c for f, c in formula_counter.items() if c > 1}
    print(f"\n化学式分布:")
    print(f"  唯一化学式: {len(formula_counter)} / {len(results)}")
    print(f"  重复化学式: {len(dup_formulas)} ({len(dup_formulas)/len(formula_counter)*100:.1f}%)")
    if dup_formulas:
        print(f"  重复列表: {list(dup_formulas.items())[:10]}")

    # ===== 筛选 Top 候选 =====
    print()
    print("=" * 60)
    print(" Top 候选 (形成能最低)")
    print("=" * 60)

    # 按形成能排序，去重化学式
    seen_formulas = set()
    unique_results = []
    for r in sorted(results, key=lambda x: x["formation_energy"]):
        if r["formula"] not in seen_formulas:
            seen_formulas.add(r["formula"])
            unique_results.append(r)

    top_n = min(10, len(unique_results))
    top_candidates = unique_results[:top_n]

    print(f"\n推荐 {top_n} 个 DFT 验证候选:")
    print(f"{'排名':<4} {'化学式':<14} {'原子数':>4} {'形成能':>8} {'批次':<10}")
    print("-" * 50)
    for rank, r in enumerate(top_candidates, 1):
        print(f"{rank:<4} {r['formula']:<14} {r['n_atoms']:>4} {r['formation_energy']:>8.3f} {r['batch']:<10}")

    # 多样性推荐 (不同元素组合)
    print("\n多样性推荐 (不同元素体系):")
    element_sets = {}
    for r in results:
        el_set = tuple(sorted(r["elements"].keys()))
        if el_set not in element_sets or r["formation_energy"] < element_sets[el_set]["formation_energy"]:
            element_sets[el_set] = r
    diverse = sorted(element_sets.values(), key=lambda x: x["formation_energy"])[:10]
    for rank, r in enumerate(diverse, 1):
        print(f"{rank:<4} {r['formula']:<14} {r['n_atoms']:>4} {r['formation_energy']:>8.3f} {r['batch']:<10}")

    # 保存结果
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump({
            "total": total_count,
            "success": success_count,
            "results": results,
            "top_candidates": top_candidates,
            "diverse_candidates": diverse,
        }, f, indent=2, ensure_ascii=False)
    print(f"\n结果已保存: {OUTPUT_JSON}")


if __name__ == "__main__":
    main()

"""
候选晶体 PBE 带隙验证脚本
=========================

对候选晶体结构做 GPAW-PBE 单点计算，提取 PBE 带隙（HOMO-LUMO gap），
用于检验 MatterGen 条件生成（dft_band_gap，PBE 标尺）的有效性。

标尺自洽说明
------------
MatterGen 以目标带隙（PBE 标尺）为条件生成 → 验证也应使用同一标尺 (PBE)，
否则"条件是否达成"的判定会失真。HSE06 等杂化泛函的绝对带隙系统性大于 PBE，
不宜直接与目标值比较，应作为后续单独报告的高精度确认。

计算参数（与项目 DFT 验证保持一致）
-----------------------------------
- 泛函: PBE（自旋极化, hund=True）
- 截断能: 400 eV（--pw 可覆盖）
- k 点: 默认 4×4×4（--kpts 可覆盖；正式结果建议做 k 点收敛测试）
- smearing: FermiDirac(0.05 eV) —— 带隙计算用小 smearing 更准确
- SCF: maxiter=200, Pulay Mixer

用法（在 WSL 的 GPAW 环境中运行）
--------------------------------
python bandgap_verify.py --cif chgnet_relaxed_F9Hf3O3Y.cif
python bandgap_verify.py --dir /home/isaac/p1_dft --pattern "chgnet_relaxed_*.cif" --kpts 3 3 3
python bandgap_verify.py --cif a.cif b.cif --out bandgap_results.json

输出
----
每个结构: PBE 带隙 (eV)、HOMO/LUMO、总能 (eV)、每原子能量 (eV/atom)、磁矩 (uB)
"""

import argparse
import json
import os
import warnings
from pathlib import Path

import numpy as np

warnings.filterwarnings("ignore")
os.environ.setdefault(
    "GPAW_SETUP_PATH",
    "/usr/local/lib/python3.12/dist-packages/gpaw_data/setups")

from ase.io import read  # noqa: E402
from gpaw import GPAW, PW, FermiDirac, Mixer  # noqa: E402


def compute_gap(cif_path: Path, kpts, pw, log):
    atoms = read(str(cif_path))
    n = len(atoms)
    formula = atoms.get_chemical_formula()

    calc = GPAW(
        mode=PW(pw), xc="PBE", kpts=kpts, hund=True,
        occupations=FermiDirac(0.05),
        mixer=Mixer(beta=0.05, nmaxold=7, weight=100.0),
        maxiter=200, txt=str(log),
    )
    atoms.calc = calc
    energy = atoms.get_potential_energy()

    # 手动计算自旋分辨带隙: gap = min(所有自旋 LUMO) - max(所有自旋 HOMO)
    hl = calc.get_homo_lumo()
    homo_arr = np.atleast_1d(hl[0])
    lumo_arr = np.atleast_1d(hl[1])
    homo = float(np.max(homo_arr))
    lumo = float(np.min(lumo_arr))
    gap = lumo - homo
    mag = atoms.get_magnetic_moment()

    return {
        "cif": str(cif_path),
        "formula": formula,
        "n_atoms": n,
        "total_energy": round(energy, 4),
        "energy_per_atom": round(energy / n, 4),
        "homo": round(homo, 4),
        "lumo": round(lumo, 4),
        "pbe_bandgap": round(gap, 4),
        "mag_moment_uB": round(mag, 3),
        "kpts": list(kpts),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cif", nargs="+", default=[], help="CIF 文件路径")
    ap.add_argument("--dir", default=None, help="目录")
    ap.add_argument("--pattern", default="*.cif", help="目录内匹配模式")
    ap.add_argument("--kpts", nargs=3, type=int, default=[4, 4, 4])
    ap.add_argument("--pw", type=float, default=400.0)
    ap.add_argument("--out", default=None, help="结果 JSON 输出路径")
    args = ap.parse_args()

    kpts = tuple(args.kpts)
    files = [Path(f) for f in args.cif]
    if args.dir:
        files += sorted(Path(args.dir).glob(args.pattern))
    files = [f for f in files if f.suffix.lower() == ".cif"]

    if not files:
        ap.error("未提供任何 CIF（用 --cif 或 --dir + --pattern）")

    results = []
    for f in files:
        log = f.with_suffix(".gap.txt")
        print(f"计算: {f.name}  kpts={kpts}  PW={args.pw:.0f}  (log: {log.name})")
        try:
            r = compute_gap(f, kpts, args.pw, log)
        except Exception as e:
            print(f"  ❌ 失败: {e}")
            continue
        print(f"  {r['formula']:<14} 带隙={r['pbe_bandgap']:.3f} eV | "
              f"E/atom={r['energy_per_atom']:.3f} | mag={r['mag_moment_uB']:.2f} uB")
        results.append(r)

    # 汇总
    print("\n=== PBE 带隙汇总 ===")
    for r in sorted(results, key=lambda x: x["pbe_bandgap"]):
        print(f"  {r['formula']:<14} gap={r['pbe_bandgap']:.3f} eV | "
              f"E/atom={r['energy_per_atom']:.3f} eV")

    if args.out:
        Path(args.out).write_text(
            json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"结果已保存: {args.out}")

    print("\n注意:")
    print(" - PBE 带隙与条件生成同标尺，用于检验条件控制是否有效")
    print(" - 绝对带隙建议后续用 HSE06 确认（PBE 会系统性低估）")
    print(" - 磁性/金属体系 gap≈0 属正常，需结合能带结构判断")


if __name__ == "__main__":
    main()

"""
CHGNet 元素参考能量库质量校验
================================

背景
----
`elemental_ref_energies.json` 用于 CHGNet 形成能计算。此前曾因缺失 11 种元素
参考（脚本用 `ref.get(s, 0)` 静默归零）导致形成能虚低、Top 排名错误。
本脚本用于防止此类问题再次发生，并检测参考能量中的离群值。

功能
----
1. 元素覆盖检查
   - 扫描所有生成批次 (pool_*/results*/extended_pool/*) 的 extxyz，
   - 找出候选实际用到、但参考库缺失的元素（一旦缺失，形成能即不可信）。
2. 离群值检测
   - 按 (周期, 区块) 分组（如 4f 稀土组），组内用 MAD 检测离群参考能量，
   - 例如 Gd = -14.05 eV/atom vs 相邻稀土 ~ -4.5，应被抓出。
3. 输出校验报告（控制台 + 可选 JSON）

用法
----
python check_ref_quality.py [--ref elemental_ref_energies.json] [--json out.json]

返回值
------
0 = 无问题；1 = 存在缺失参考或疑似离群值（便于接入 CI / 批处理脚本）
"""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from ase.io import read
from pymatgen.core import Element

ROOT = Path(__file__).resolve().parent
DEFAULT_REF = ROOT / "elemental_ref_energies.json"

# 所有可能含生成产物的目录（相对 ROOT）
POOL_DIRS = [
    "results", "results_bulk_150", "results_widegap",
    "pool_bandgap_25", "pool_bandgap_35", "pool_bandgap_40",
    "extended_pool",
]


def collect_used_elements(root: Path) -> dict:
    """扫描各批次的 generated_crystals.extxyz，返回 {元素: 计数}"""
    used = defaultdict(int)
    files = 0
    for d in POOL_DIRS:
        for extxyz in (root / d).glob("*/generated_crystals.extxyz"):
            files += 1
            try:
                for atoms in read(str(extxyz), index=":"):
                    for s in atoms.get_chemical_symbols():
                        used[s] += 1
            except Exception as e:
                print(f"  [warn] 读取失败 {extxyz}: {e}")
    print(f"扫描到 {files} 个 extxyz 文件")
    return dict(used)


def outlier_detection(ref: dict, mad_z: float = 4.0, abs_thresh: float = 1.5):
    """按 (row, block) 分组，组内 MAD 检测离群值。

    阈值说明（保守设计，避免误报）：
    - 组内 Z = |E - 中位数| / MAD > mad_z
    - 且绝对偏差 |E - 中位数| > abs_thresh (eV/atom)
    两者同时满足才标记。
    """
    groups = defaultdict(list)
    for el, e in ref.items():
        try:
            elem = Element(el)
            key = (elem.row, elem.block)
        except Exception:
            key = ("?", "?")
        groups[key].append((el, e))

    flags = []
    for key, items in sorted(groups.items(), key=lambda x: str(x[0])):
        if len(items) < 3:  # 组内样本太少不做统计
            continue
        vals = np.array([v for _, v in items], dtype=float)
        med = float(np.median(vals))
        mad = float(np.median(np.abs(vals - med)))
        if mad < 1e-9:
            mad = 1e-9
        for el, v in items:
            z = abs(v - med) / mad
            if z > mad_z and abs(v - med) > abs_thresh:
                flags.append({
                    "element": el,
                    "energy": v,
                    "group_median": med,
                    "deviation": v - med,
                    "z": round(z, 1),
                    "group": key,
                })
    return flags


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ref", default=str(DEFAULT_REF),
                    help="参考能量库路径")
    ap.add_argument("--json", default=None, help="输出报告到 JSON 文件")
    args = ap.parse_args()

    ref_path = Path(args.ref)
    if not ref_path.exists():
        print(f"参考库不存在: {ref_path}")
        return 1
    ref = json.load(open(ref_path, encoding="utf-8"))
    print(f"参考库元素数: {len(ref)}")

    # 1. 元素覆盖检查
    print("\n=== 1. 元素覆盖检查 ===")
    used = collect_used_elements(ROOT)
    missing = sorted(set(used) - set(ref))
    print(f"候选实际用到元素: {len(used)} 种")
    if missing:
        print(f"❌ 缺失参考的元素 ({len(missing)}): {missing}")
        print("   → 这些候选的形成能当前不可信（按 0 处理），必须补齐参考！")
    else:
        print("✅ 候选所用元素参考全部覆盖")

    # 2. 离群值检测
    print("\n=== 2. 离群值检测（按 周期+区块 分组, MAD）===")
    flags = outlier_detection(ref)
    if flags:
        print(f"⚠️ 发现 {len(flags)} 个疑似离群参考:")
        for f in flags:
            print(f"  {f['element']:<3} {f['energy']:>9.3f} eV/atom | "
                  f"同组中位 {f['group_median']:>7.3f} | "
                  f"偏差 {f['deviation']:>+7.3f} | Z={f['z']} | 组 {f['group']}")
        print("   → 需人工核对参考态结构/磁性状态，确认是否为真实参考")
    else:
        print("✅ 未发现明显离群值")

    # 3. 汇总输出
    report = {
        "n_elements": len(ref),
        "missing_in_candidates": missing,
        "outliers": flags,
    }
    if args.json:
        Path(args.json).write_text(
            json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\n报告已保存: {args.json}")

    # 返回码：有问题则非 0（便于自动化接入）
    return 1 if (missing or flags) else 0


if __name__ == "__main__":
    sys.exit(main())

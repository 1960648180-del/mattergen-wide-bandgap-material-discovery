"""14 样本带隙统计: 氟化物 vs 非氟 分组对比"""
# (候选, 体系, 目标, DFT带隙)
data = [
    # 氟化物/氧氟化物 (5)
    ("F9Hf3O3Y", "氟", 3.0, 4.169),
    ("F6Rb3Y",   "氟", 4.0, 5.856),
    ("F3Sc",     "氟", 3.5, 6.432),
    ("F3La",     "氟", 2.5, 6.682),
    ("BaF6Si",   "氟", 4.5, 7.868),
    # 非氟 (9)
    ("LiO11Re3", "非氟", 2.5, 1.642),
    ("BeO2Zn",   "非氟", 3.0, 3.108),
    ("Cl2CsK",   "非氟", 3.0, 5.229),
    ("CaO3Zr",   "非氟", 3.5, 3.997),
    ("O2Rb4",    "非氟", 3.5, 0.818),
    ("Al3O5",    "非氟", 4.0, 0.137),
    ("Br2Cs2",   "非氟", 4.0, 4.611),
    ("CaClKO",   "非氟", 4.5, 4.260),
    ("H2Cs2S2",  "非氟", 4.5, 3.663),
]

def stats(rows):
    devs = [dft - t for _, _, t, dft in rows]
    mae = sum(abs(d) for d in devs) / len(devs)
    mean = sum(devs) / len(devs)
    pos = sum(1 for d in devs if d > 0)
    neg = sum(1 for d in devs if d < 0)
    return mae, mean, pos, neg, devs

for label, group in [("氟化物 (5)", [r for r in data if r[1] == "氟"]),
                     ("非氟 (9)", [r for r in data if r[1] == "非氟"]),
                     ("全部 (14)", data)]:
    mae, mean, pos, neg, devs = stats(group)
    print(f"\n===== {label} =====")
    print(f"  MAE = {mae:.3f} eV")
    print(f"  平均偏差 = {mean:+.3f} eV")
    print(f"  正偏差 {pos} / 负偏差 {neg}")
    for name, grp, t, dft in group:
        print(f"    {name:<10} 目标={t:.1f} 实测={dft:.3f} 偏差={dft-t:+.3f}")

# 逐样本全表
print("\n===== 14 样本全表 =====")
for name, grp, t, dft in data:
    print(f"  {name:<10} [{grp}] 目标={t:.1f} 实测={dft:.3f} 偏差={dft-t:+.3f}")

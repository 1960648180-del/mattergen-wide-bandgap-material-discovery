"""重算 6 样本带隙统计 (P0 3 个 + 扩 Top10 3 个)"""
data = [
    # (候选, 目标, DFT带隙)  严格版 (DFT 弛豫结构)
    ("F9Hf3O3Y", 3.0, 4.169),
    ("F6Rb3Y", 4.0, 5.856),
    ("LiO11Re3", 2.5, 1.642),
    ("F3Sc", 3.5, 6.432),
    ("F3La", 2.5, 6.682),
    ("BaF6Si", 4.5, 7.868),
]

devs = [dft - t for _, t, dft in data]
mae = sum(abs(d) for d in devs) / len(devs)
mean_dev = sum(devs) / len(devs)
pos = sum(1 for d in devs if d > 0)

print("6 样本偏差统计:")
print(f"  样本数: {len(data)}")
print(f"  正偏差数: {pos}/{len(data)} ({pos/len(data)*100:.0f}%)")
print(f"  MAE: {mae:.3f} eV")
print(f"  平均偏差: {mean_dev:+.3f} eV")
print(f"  最大正偏差: {max(devs):+.3f} eV")
print(f"  最大负偏差: {min(devs):+.3f} eV")
print()
print("逐样本:")
for (c, t, dft), d in zip(data, devs):
    print(f"  {c:<10} 目标={t:.1f} DFT={dft:.3f} 偏差={d:+.3f}")

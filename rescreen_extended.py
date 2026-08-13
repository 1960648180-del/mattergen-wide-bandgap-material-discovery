"""
用补齐后的参考能量重新计算扩展候选的形成能并重新排名
(复用 screening_extended_result.json 中已存的总能量, 无需重跑 CHGNet 弛豫)
"""
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).parent

# 1. 合并参考能量
ref_path = ROOT / "elemental_ref_energies.json"
missing_path = ROOT / "chgnet_missing_refs.json"

ref = json.load(open(ref_path))
missing = json.load(open(missing_path))

# 备份原文件
shutil.copy(ref_path, ref_path.with_suffix(".json.bak"))

# 合并
added = {}
for el, val in missing.items():
    if el not in ref:
        ref[el] = val
        added[el] = val

# 保存合并后的
with open(ref_path, 'w') as f:
    json.dump(ref, f, indent=2)

print(f"参考能量库更新: 原 {len(ref)-len(added)} + 新增 {len(added)} = {len(ref)} 种元素")
print(f"新增: {list(added.keys())}")

# 2. 重新计算形成能
data = json.load(open(ROOT / "screening_extended_result.json"))

for r in data['results']:
    total_e = r['total_energy']
    symbols = []
    for el, n in r['elements'].items():
        symbols.extend([el] * n)
    ref_sum = sum(ref.get(s, 0) for s in symbols)
    n_atoms = r['n_atoms']
    r['formation_energy'] = (total_e - ref_sum) / n_atoms
    r['ref_valid'] = all(s in ref for s in r['elements'])

# 3. 重新排名 (仅用参考完整的候选, 否则不公平)
valid = [r for r in data['results'] if r['ref_valid']]
invalid = [r for r in data['results'] if not r['ref_valid']]
print(f"\n参考完整候选: {len(valid)} / 100")
print(f"仍缺参考候选: {len(invalid)}")

# Top 10 (去重化学式)
seen = set()
unique_valid = []
for r in sorted(valid, key=lambda x: x['formation_energy']):
    if r['formula'] not in seen:
        seen.add(r['formula'])
        unique_valid.append(r)

top10 = unique_valid[:10]
data['top_candidates'] = top10

print("\n" + "=" * 75)
print(" 修正后的 Top 10 候选 (仅参考完整)")
print("=" * 75)
print(f"{'排名':<4} {'化学式':<16} {'原子':>4} {'形成能':>8} {'批次':<10}")
print("-" * 75)
for rank, r in enumerate(top10, 1):
    print(f"{rank:<4} {r['formula']:<16} {r['n_atoms']:>4} {r['formation_energy']:>8.3f} {r['batch']:<10}")

# 保存
data['missing_ref_candidates'] = [r['formula'] for r in invalid]
with open(ROOT / "screening_extended_result.json", 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
print(f"\n结果已更新保存")

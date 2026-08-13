"""分析 screening 候选池: Ef 分布/负对照/边界/体系多样性"""
import json
from collections import Counter

path = '/mnt/d/nature reproduction/mattergen/screening_extended_result.json'
with open(path, encoding='utf-8') as f:
    data = json.load(f)

results = data['results']
print(f"total字段: {data.get('total')}, results数: {len(results)}")

# Ef 范围
efs = sorted(results, key=lambda r: r.get('formation_energy', 0))
print(f"\nEf 最大 3 个 (负对照候选):")
for r in efs[-3:]:
    print(f"  {r['formula']:<14} batch={r.get('batch')} idx={r.get('index')} "
          f"Ef={r.get('formation_energy'):+.3f} n={r.get('n_atoms')} el={r.get('elements')}")
print(f"\nEf 最小 3 个:")
for r in efs[:3]:
    print(f"  {r['formula']:<14} batch={r.get('batch')} idx={r.get('index')} "
          f"Ef={r.get('formation_energy'):+.3f} n={r.get('n_atoms')}")

# 边界 |Ef|<1.0
boundary = [r for r in results if abs(r.get('formation_energy', 0)) < 1.0]
print(f"\n边界候选 |Ef|<1.0: {len(boundary)} 个")
for r in boundary:
    print(f"  {r['formula']:<14} Ef={r.get('formation_energy'):+.3f} n={r.get('n_atoms')}")

# 体系多样性: 是否含 F
def is_fluoride(r):
    return 'F' in r.get('elements', {})
n_f = sum(1 for r in results if is_fluoride(r))
print(f"\n含 F 体系: {n_f}/{len(results)} ({n_f/len(results)*100:.0f}%)")
# 非 F 体系候选
nonf = [r for r in results if not is_fluoride(r)]
print(f"非 F 体系 {len(nonf)} 个, 示例 (前15):")
for r in nonf[:15]:
    print(f"  {r['formula']:<14} Ef={r.get('formation_energy'):+.3f} n={r.get('n_atoms')} batch={r.get('batch')} idx={r.get('index')}")

"""检查 CHGNet 参考能量缺失元素对扩展筛选的影响"""
import json
from collections import Counter

ref = json.load(open('elemental_ref_energies.json'))
data = json.load(open('screening_extended_result.json'))

# 统计所有出现的元素
all_elements = set()
for r in data['results']:
    all_elements.update(r['elements'].keys())

missing = sorted(el for el in all_elements if el not in ref)
present = sorted(el for el in all_elements if el in ref)
print(f"出现的元素总数: {len(all_elements)}")
print(f"有参考能量: {len(present)}")
print(f"缺参考能量: {len(missing)}")
print(f"\n缺失元素: {missing}")

# 统计受影响的候选
affected = [r for r in data['results'] if any(el in missing for el in r['elements'])]
unaffected = [r for r in data['results'] if not any(el in missing for el in r['elements'])]
print(f"\n受影响候选: {len(affected)}/{len(data['results'])} ({len(affected)/len(data['results'])*100:.0f}%)")
print(f"未受影响候选: {len(unaffected)}")

# 检查 Top 候选是否受影响
print("\nTop 10 候选受影响情况:")
for r in data['top_candidates']:
    has_missing = any(el in missing for el in r['elements'])
    miss_els = [el for el in r['elements'] if el in missing]
    status = f"❌ 受影响 (缺 {miss_els})" if has_missing else "✅ 有效"
    print(f"  {r['formula']:<16} Ef={r['formation_energy']:+.3f}  {status}")

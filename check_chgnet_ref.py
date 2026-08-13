import json
ref = json.load(open('elemental_ref_energies.json'))
print("CHGNet 元素参考能量 (eV/atom):")
for el in ['Hf', 'Y', 'Re', 'Li', 'Rb', 'F', 'O']:
    val = ref.get(el, 'N/A')
    print(f"  {el}: {val}")

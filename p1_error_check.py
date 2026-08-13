import json
data = json.load(open('screening_extended_result.json'))
targets = ['F9Hf3O3Y', 'F6Rb3Y', 'LiO11Re3']
dft_ef = {'F9Hf3O3Y': -3.6920, 'F6Rb3Y': -3.2987, 'LiO11Re3': -1.5931}

print("候选          CHGNet(修正)   DFT       误差")
print("-" * 45)
for r in data['results']:
    if r['formula'] in targets:
        chg = r['formation_energy']
        dft = dft_ef[r['formula']]
        err = dft - chg
        print(f"{r['formula']:<14} {chg:>10.3f}  {dft:>8.3f}  {err:>+7.3f}")

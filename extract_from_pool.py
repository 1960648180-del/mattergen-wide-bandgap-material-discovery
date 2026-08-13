"""从 extended_pool 提取目标候选结构"""
import os, warnings
warnings.filterwarnings('ignore')
from ase.io import read, write

base = '/mnt/d/nature reproduction/mattergen'

# F3La: screening 说 bg_25 idx0; BaF6Si: bg_45 idx16
targets = [
    ('extended_pool/bg_25/generated_crystals.extxyz', 0, 'F3La'),
    ('extended_pool/bg_45/generated_crystals.extxyz', 16, 'BaF6Si'),
]

for f, idx, expect in targets:
    p = os.path.join(base, f)
    print(f'=== {f} ===')
    try:
        frames = read(p, index=':')
        print(f'  总帧数: {len(frames)}')
        for i in range(max(0, idx-2), min(len(frames), idx+3)):
            form = frames[i].get_chemical_formula()
            print(f'  [{i}] {form} n={len(frames[i])}')
        at = frames[idx]
        form = at.get_chemical_formula()
        if form != expect:
            print(f'  ⚠️ idx{idx} 是 {form}, 期望 {expect}')
        else:
            print(f'  ✅ 找到 {form} idx{idx}')
            out = os.path.join(base, f'{expect}.cif')
            write(out, at)
            print(f'  已写入: {out}')
    except Exception as e:
        print(f'  出错: {e}')

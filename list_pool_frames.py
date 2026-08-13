"""列出各 extxyz 帧的 formula + 属性, 找 F3La/BaF6Si/bg_45"""
import os, warnings
warnings.filterwarnings('ignore')
from ase.io import read

base = '/mnt/d/nature reproduction/mattergen'
files = ['pool_bandgap_25/generated_crystals.extxyz',
         'pool_bandgap_35/generated_crystals.extxyz',
         'pool_bandgap_40/generated_crystals.extxyz',
         'results_widegap/generated_crystals.extxyz',
         'results/generated_crystals.extxyz']

for f in files:
    p = os.path.join(base, f)
    if not os.path.exists(p):
        print(f'{f}: 不存在')
        continue
    print(f'\n=== {f} ===')
    try:
        for i, at in enumerate(read(p, index=':')):
            form = at.get_chemical_formula()
            keys = list(at.info.keys())
            props = {k: at.info[k] for k in keys if k != 'key_value_pairs'}
            flag = ' <-- 目标' if form in ('F3La', 'BaF6Si') else ''
            print(f'  [{i}] {form} n={len(at)} info={props}{flag}')
    except Exception as e:
        print(f'  读取出错: {e}')

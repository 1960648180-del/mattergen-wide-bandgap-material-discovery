"""分析 extended_pool 非氟候选 (无F, 覆盖各档位, 小体系)"""
import os, warnings
warnings.filterwarnings('ignore')
from ase.io import read

base = '/mnt/d/nature reproduction/mattergen'
batches = ['bg_25', 'bg_30', 'bg_35', 'bg_40', 'bg_45']
# 常见 f 电子元素
f_elems = {'La', 'Lu', 'Tb', 'Nd', 'Ho', 'Tm', 'Dy', 'Gd', 'Sm', 'Eu', 'Pr', 'Ce', 'Er', 'Yb'}

for b in batches:
    p = f'{base}/extended_pool/{b}/generated_crystals.extxyz'
    if not os.path.exists(p):
        continue
    print(f'\n=== {b} (目标档 {b[3:]}.0) ===')
    frames = read(p, index=':')
    for i, at in enumerate(frames):
        syms = set(at.get_chemical_symbols())
        if 'F' in syms:
            continue  # 跳过氟化物
        formula = at.get_chemical_formula()
        n = len(at)
        has_f = bool(syms & f_elems)
        tag = ' [f电子]' if has_f else ''
        if n <= 16:  # 小体系优先
            print(f'  [{i}] {formula:<12} n={n}{tag}')

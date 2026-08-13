"""统计各 extxyz 文件的 batch 分布 (用 ASE 读取 info). 用法: python3 check_batches.py"""
import os, warnings
warnings.filterwarnings('ignore')
from ase.io import read

base = '/mnt/d/nature reproduction/mattergen'
files = ['pool_bandgap_25/generated_crystals.extxyz',
         'pool_bandgap_35/generated_crystals.extxyz',
         'pool_bandgap_40/generated_crystals.extxyz',
         'results/generated_crystals.extxyz',
         'results_bulk_150/generated_crystals.extxyz',
         'results_widegap/generated_crystals.extxyz']

for f in files:
    p = os.path.join(base, f)
    if not os.path.exists(p):
        print(f'{f}: 不存在')
        continue
    from collections import Counter
    batches = Counter()
    total = 0
    try:
        for at in read(p, index=':'):
            total += 1
            b = at.info.get('batch', '?')
            batches[b] += 1
            if total >= 4000:
                break
    except Exception as e:
        print(f'{f}: 读取出错 {e} (已读 {total})')
    print(f'{f}: 总 {total} 帧, batch分布={dict(batches)}')

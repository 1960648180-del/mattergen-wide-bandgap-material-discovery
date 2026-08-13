"""统计全量候选池: 各来源数量 + 去重总数"""
import os, warnings
warnings.filterwarnings('ignore')
from ase.io import read

base = '/mnt/d/nature reproduction/mattergen'
# 各生成结果文件
files = {
    'extended_pool/bg_25': 'extended_pool/bg_25/generated_crystals.extxyz',
    'extended_pool/bg_30': 'extended_pool/bg_30/generated_crystals.extxyz',
    'extended_pool/bg_35': 'extended_pool/bg_35/generated_crystals.extxyz',
    'extended_pool/bg_40': 'extended_pool/bg_40/generated_crystals.extxyz',
    'extended_pool/bg_45': 'extended_pool/bg_45/generated_crystals.extxyz',
    'pool_bandgap_25': 'pool_bandgap_25/generated_crystals.extxyz',
    'pool_bandgap_35': 'pool_bandgap_35/generated_crystals.extxyz',
    'pool_bandgap_40': 'pool_bandgap_40/generated_crystals.extxyz',
    'results': 'results/generated_crystals.extxyz',
    'results_widegap': 'results_widegap/generated_crystals.extxyz',
    'results_bulk_150': 'results_bulk_150/generated_crystals.extxyz',
}
seen = set()
for label, rel in files.items():
    p = os.path.join(base, rel)
    if not os.path.exists(p):
        print(f'{label}: 不存在')
        continue
    frames = read(p, index=':')
    n = len(frames)
    print(f'{label}: {n} 帧')
    for at in frames:
        seen.add(at.get_chemical_formula())
print(f'\n去重后候选总数: {len(seen)}')
# 列出去重公式
forms = sorted(seen)
print('公式列表:')
for f in forms:
    print(f'  {f}')

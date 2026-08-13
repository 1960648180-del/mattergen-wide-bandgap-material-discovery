"""WSL 端: 统计候选池原子数分布, 估算总耗时"""
import json, subprocess
from pathlib import Path
from ase.io import read

INP = Path('/home/isaac/p1_dft/gap_all_input')
cifs = sorted(INP.glob('*.cif'))
sizes = []
for c in cifs:
    try:
        at = read(str(c))
        sizes.append((c.stem, len(at)))
    except Exception as e:
        print(f'{c.name}: ERR {e}')

sizes.sort(key=lambda x: x[1])
import collections
bins = collections.Counter()
for name, n in sizes:
    if n <= 8: bins['<=8'] += 1
    elif n <= 12: bins['9-12'] += 1
    elif n <= 16: bins['13-16'] += 1
    elif n <= 20: bins['17-20'] += 1
    else: bins['>20'] += 1

print(f'总候选: {len(sizes)}')
print('原子数分布:', dict(bins))
print('\n小体系(n<=8):')
for name, n in sizes[:30]:
    print(f'  {name:<16} n={n}')
print('\n大体系(n>16) 前20:')
big = [(name, n) for name, n in sizes if n > 16]
for name, n in big[:20]:
    print(f'  {name:<16} n={n}')
print(f'\n大体系总数(n>16): {len(big)}')

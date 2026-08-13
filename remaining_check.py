"""WSL 端: 统计未完成候选的原子数与含f情况, 评估FAIL影响面"""
import json
from pathlib import Path
from ase.io import read

INP = Path('/home/isaac/p1_dft/gap_all_input')
RES = Path('/home/isaac/p1_dft/gap_all_results')

done = {f.stem for f in RES.glob('*.json')}
cifs = sorted(INP.glob('*.cif'))
F_EL = {'La','Ce','Pr','Nd','Pm','Sm','Eu','Gd','Tb','Dy','Ho','Er','Tm','Yb','Lu',
        'Ac','Th','Pa','U','Np','Pu','Am','Cm'}

remaining = []
for c in cifs:
    if c.stem in done:
        continue
    at = read(str(c))
    syms = set(at.get_chemical_symbols())
    has_f = bool(syms & F_EL)
    remaining.append((c.stem, len(at), has_f))

remaining.sort(key=lambda x: -x[1])
print(f'未完成: {len(remaining)}')
import collections
n_hi = sum(1 for _, n, f in remaining if n >= 13)
n_f_hi = sum(1 for _, n, f in remaining if f and n >= 13)
n_f = sum(1 for _, n, f in remaining if f)
print(f'n>=13 大体系: {n_hi},  其中含f: {n_f_hi}')
print(f'含f总数(任意大小): {n_f}')
print('\n剩余候选 (按原子数降序, [*]=含f):')
for name, n, f in remaining:
    mark = '*' if f else ' '
    print(f'  {mark} {name:<16} n={n:>3}')

"""WSL 端: 分析 FAIL 黑名单候选的元素构成与共性"""
import json
from pathlib import Path
from ase.io import read
from collections import Counter

INP = Path('/home/isaac/p1_dft/gap_all_input')
FAIL = Path('/home/isaac/p1_dft/gap_all_failed.txt')
DONE = Path('/home/isaac/p1_dft/gap_all_results')

failed = [l.strip() for l in FAIL.read_text().splitlines() if l.strip()]
done = {f.stem for f in DONE.glob('*.json')}

F_EL = {'La','Ce','Pr','Nd','Pm','Sm','Eu','Gd','Tb','Dy','Ho','Er','Tm','Yb','Lu',
        'Ac','Th','Pa','U','Np','Pu','Am','Cm'}
TM = {'Sc','Ti','V','Cr','Mn','Fe','Co','Ni','Cu','Zn','Y','Zr','Nb','Mo','Tc',
      'Ru','Rh','Pd','Ag','Cd','Hf','Ta','W','Re','Os','Ir','Pt','Au','Hg'}

rows = []
for name in failed:
    cif = INP / f'{name}.cif'
    if not cif.exists():
        rows.append((name, None, None, None, None, None))
        continue
    at = read(str(cif))
    syms = at.get_chemical_symbols()
    sset = set(syms)
    n = len(at)
    rows.append((name, n, sorted(sset), bool(sset & F_EL), bool(sset & TM), None))

print(f'FAIL 候选共 {len(failed)} 个\n')
for name, n, syms, has_f, has_tm, mag in sorted(rows, key=lambda x: -(x[1] or 0)):
    if n is None:
        print(f'  {name:<16} CIF缺失'); continue
    f_mark = 'f' if has_f else ' '
    tm_mark = 'TM' if has_tm else ' '
    print(f'  {name:<16} n={n:>3} {f_mark} {tm_mark} 元素: {"".join(syms)}')

print('\n=== 统计 ===')
nf = sum(1 for r in rows if r[2] and r[3])
ntm = sum(1 for r in rows if r[2] and r[4])
print(f'含f元素: {nf}/{len(failed)}')
print(f'含过渡金属: {ntm}/{len(failed)}')

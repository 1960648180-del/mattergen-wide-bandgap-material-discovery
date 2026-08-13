"""
能带结构分析: 定位 HOMO-LUMO 网格法 vs 能带带隙 的口径差异
================================================================
对候选做:
  1. SCF 收敛 (kpts 默认 4×4×4, 与报告一致)
  2. 高对称路径能带 (fixed_density 非自洽) → 路径带隙 + VBM/CBM 位置
  3. 密集均匀网格能带 (fixed_density 非自洽) → 密集网格带隙 (逼近能带带隙真值)

关键对比:
  HL_gap (4×4×4 HOMO-LUMO 网格法, 报告口径)  vs
  path_gap (高对称路径能带带隙)              vs
  dense_gap (密集均匀网格带隙, 逼近 MP 定义)
  若 dense/path << HL → 网格法高估 (口径是主因); 若相近 → 口径非主因。

注: 使用 GPAW 26.7 的 fixed_density() 方法做非自洽能带。
   高对称路径 k 点有重复 → symmetry='off';
   密集网格 (monkhorst_pack) 无重复 → 默认 symmetry (可约化加速)。

用法: python3 band_analysis.py <cif> [scf_k1 scf_k2 scf_k3] [dense_k1 dense_k2 dense_k3] [prefix]
  例: python3 band_analysis.py f9hf3o3y_posrelaxed.cif 4 4 4 8 8 8 bs_F9
"""
import sys
import os
import json
import time
import warnings
warnings.filterwarnings('ignore')
os.environ.setdefault(
    "GPAW_SETUP_PATH",
    "/usr/local/lib/python3.12/dist-packages/gpaw_data/setups")

import numpy as np
from ase.io import read
from ase.dft.kpoints import bandpath, monkhorst_pack
from gpaw import GPAW, PW, FermiDirac, Mixer

cif = sys.argv[1]
if len(sys.argv) >= 5:
    sk = tuple(int(x) for x in sys.argv[2:5])
else:
    sk = (4, 4, 4)
if len(sys.argv) >= 8:
    dk = tuple(int(x) for x in sys.argv[5:8])
else:
    dk = (8, 8, 8)
prefix = sys.argv[8] if len(sys.argv) > 8 else 'bs'

atoms = read(cif)
n = len(atoms)
formula = atoms.get_chemical_formula()
print(f'能带分析: {formula} ({n} atoms)  SCF kpts={sk}  dense={dk}', flush=True)

# 1) SCF 收敛
t0 = time.time()
calc = GPAW(mode=PW(400), xc='PBE', kpts=sk, hund=True,
            occupations=FermiDirac(0.05),
            mixer=Mixer(beta=0.05, nmaxold=7, weight=100.0),
            maxiter=300, txt=f'{prefix}.txt')
atoms.calc = calc
E = atoms.get_potential_energy()
hl = calc.get_homo_lumo()
homo_hl = float(np.max(np.atleast_1d(hl[0])))
lumo_hl = float(np.min(np.atleast_1d(hl[1])))
gap_hl = lumo_hl - homo_hl
nocc = int(round(calc.get_number_of_electrons() / 2))
print(f'SCF 完成 ({time.time()-t0:.0f}s): E={E:.4f} eV  HOMO={homo_hl:.4f} '
      f'LUMO={lumo_hl:.4f} gap(HL)={gap_hl:.4f} eV  占据带/自旋={nocc}', flush=True)

def fd_bands(kpts_arr, sym_off=False, label=''):
    """fixed_density 非自洽能带 → (vbm, cbm, gap, vbm_k, cbm_k, energies, kpts_list)"""
    t0 = time.time()
    kw = dict(symmetry='off') if sym_off else {}
    c2 = calc.fixed_density(kpts=kpts_arr, txt='-', **kw)
    bs = c2.band_structure()
    en = bs.energies  # (nspin, nkpts, nbands)
    ks = c2.get_ibz_k_points()
    vbm = float(en[:, :, :nocc].max())
    cbm = float(en[:, :, nocc:].min())
    vidx = np.unravel_index(np.argmax(en[:, :, :nocc]), en[:, :, :nocc].shape)
    cidx = np.unravel_index(np.argmin(en[:, :, nocc:]), en[:, :, nocc:].shape)
    vbm_k = ks[vidx[1]].tolist() if vidx[1] < len(ks) else None
    cbm_k = ks[cidx[1]].tolist() if cidx[1] < len(ks) else None
    print(f'  {label}: {time.time()-t0:.0f}s  k点数={en.shape[1]}  '
          f'VBM={vbm:.4f} CBM={cbm:.4f} gap={cbm-vbm:.4f}', flush=True)
    return vbm, cbm, cbm - vbm, vbm_k, cbm_k, en

result = {
    'cif': cif,
    'formula': formula,
    'n_atoms': n,
    'scf_kpts': list(sk),
    'dense_kpts': list(dk),
    'E_total': round(E, 4),
    'E_per_atom': round(E / n, 4),
    'HL_homo': round(homo_hl, 4),
    'HL_lumo': round(lumo_hl, 4),
    'HL_gap': round(gap_hl, 4),
}

# 2) 高对称路径能带
try:
    path = atoms.cell.bandpath(npoints=80)
    vbm, cbm, pg, vbk, cbk, en = fd_bands(path.kpts, sym_off=True, label='高对称路径')
    result['path_vbm'] = round(vbm, 4)
    result['path_cbm'] = round(cbm, 4)
    result['path_gap'] = round(pg, 4)
    result['path_vbm_k'] = [round(x, 3) for x in vbk] if vbk else None
    result['path_cbm_k'] = [round(x, 3) for x in cbk] if cbk else None
    np.savez(f'{prefix}_band_path.npz', energies=en, kpts=path.kpts)
    print('  已保存路径能带: %s_band_path.npz' % prefix, flush=True)
except Exception as ex:
    print(f'高对称路径能带失败: {ex}', flush=True)

# 3) 密集均匀网格能带
try:
    mp = monkhorst_pack(dk)
    vbm, cbm, dg, vbk, cbk, en = fd_bands(mp, sym_off=False, label='密集网格%s' % (str(dk)))
    result['dense_vbm'] = round(vbm, 4)
    result['dense_cbm'] = round(cbm, 4)
    result['dense_gap'] = round(dg, 4)
    result['dense_vbm_k'] = [round(x, 3) for x in vbk] if vbk else None
    result['dense_cbm_k'] = [round(x, 3) for x in cbk] if cbk else None
    np.savez(f'{prefix}_band_dense.npz', energies=en, kpts=mp)
    print('  已保存密集能带: %s_band_dense.npz' % prefix, flush=True)
except Exception as ex:
    print(f'密集网格能带失败: {ex}', flush=True)

with open(f'{prefix}_analysis.json', 'w') as f:
    json.dump(result, f, indent=2, ensure_ascii=False)
print('==== 汇总 ====', flush=True)
print(json.dumps(result, indent=2, ensure_ascii=False), flush=True)
print(f'完成. 分析JSON: {prefix}_analysis.json', flush=True)

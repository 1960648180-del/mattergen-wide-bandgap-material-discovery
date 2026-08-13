"""
F9 能带分析补跑: 只补 SCF 密度 + 密集网格 8×8×8
================================================
路径能带结果已保存在 {prefix}_band_path.npz (从 run.log 已知), 无需重跑。
本脚本: SCF 4×4×4 (重建密度) → 密集网格 8×8×8 (fixed_density) → 合并写出完整 JSON

用法: python3 band_analysis_resume.py <cif> <scf_k1> <scf_k2> <scf_k3> <dk1> <dk2> <dk3> <prefix> <path_npz>
  例: python3 band_analysis_resume.py f9hf3o3y_posrelaxed.cif 4 4 4 8 8 8 bs_F9 bs_F9_band_path.npz
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
from ase.dft.kpoints import monkhorst_pack
from gpaw import GPAW, PW, FermiDirac, Mixer

cif = sys.argv[1]
sk = tuple(int(x) for x in sys.argv[2:5])
dk = tuple(int(x) for x in sys.argv[5:8])
prefix = sys.argv[8]
path_npz = sys.argv[9]

atoms = read(cif)
n = len(atoms)
formula = atoms.get_chemical_formula()
print(f'补跑: {formula} ({n} atoms)  SCF={sk}  dense={dk}  路径npz={path_npz}', flush=True)

# 1) SCF 重建密度
t0 = time.time()
calc = GPAW(mode=PW(400), xc='PBE', kpts=sk, hund=True,
            occupations=FermiDirac(0.05),
            mixer=Mixer(beta=0.05, nmaxold=7, weight=100.0),
            maxiter=300, txt=f'{prefix}_resume.txt')
atoms.calc = calc
E = atoms.get_potential_energy()
hl = calc.get_homo_lumo()
homo_hl = float(np.max(np.atleast_1d(hl[0])))
lumo_hl = float(np.min(np.atleast_1d(hl[1])))
gap_hl = lumo_hl - homo_hl
nocc = int(round(calc.get_number_of_electrons() / 2))
print(f'SCF 完成 ({time.time()-t0:.0f}s): E={E:.4f}  HOMO={homo_hl:.4f} '
      f'LUMO={lumo_hl:.4f} gap(HL)={gap_hl:.4f}  占据带/自旋={nocc}', flush=True)

# 2) 密集网格
t0 = time.time()
mp = monkhorst_pack(dk)
c2 = calc.fixed_density(kpts=mp, txt='-')
bs = c2.band_structure()
en = bs.energies
ks = c2.get_ibz_k_points()
dvbm = float(en[:, :, :nocc].max())
dcbm = float(en[:, :, nocc:].min())
vidx = np.unravel_index(np.argmax(en[:, :, :nocc]), en[:, :, :nocc].shape)
cidx = np.unravel_index(np.argmin(en[:, :, nocc:]), en[:, :, nocc:].shape)
dvbm_k = ks[vidx[1]].tolist() if vidx[1] < len(ks) else None
dcbm_k = ks[cidx[1]].tolist() if cidx[1] < len(ks) else None
print(f'密集网格{str(dk)}: {time.time()-t0:.0f}s  k点数={en.shape[1]}  '
      f'VBM={dvbm:.4f} CBM={dcbm:.4f} gap={dcbm-dvbm:.4f}', flush=True)
np.savez(f'{prefix}_band_dense.npz', energies=en, kpts=mp)

# 3) 从 path npz 恢复路径结果
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
    'dense_vbm': round(dvbm, 4),
    'dense_cbm': round(dcbm, 4),
    'dense_gap': round(dcbm - dvbm, 4),
    'dense_vbm_k': [round(x, 3) for x in dvbm_k] if dvbm_k else None,
    'dense_cbm_k': [round(x, 3) for x in dcbm_k] if dcbm_k else None,
}
try:
    pd = np.load(path_npz)
    en_p = pd['energies']
    kp = pd['kpts']
    pvbm = float(en_p[:, :, :nocc].max())
    pcbm = float(en_p[:, :, nocc:].min())
    pvidx = np.unravel_index(np.argmax(en_p[:, :, :nocc]), en_p[:, :, :nocc].shape)
    pcidx = np.unravel_index(np.argmin(en_p[:, :, nocc:]), en_p[:, :, nocc:].shape)
    result['path_vbm'] = round(pvbm, 4)
    result['path_cbm'] = round(pcbm, 4)
    result['path_gap'] = round(pcbm - pvbm, 4)
    result['path_vbm_k'] = [round(x, 3) for x in kp[pvidx[1]]] if pvidx[1] < len(kp) else None
    result['path_cbm_k'] = [round(x, 3) for x in kp[pcidx[1]]] if pcidx[1] < len(kp) else None
    print(f'恢复路径能带: gap={pcbm-pvbm:.4f} (VBM={pvbm:.4f}, CBM={pcbm:.4f})', flush=True)
except Exception as ex:
    print(f'恢复路径能带失败: {ex}', flush=True)

with open(f'{prefix}_analysis.json', 'w') as f:
    json.dump(result, f, indent=2, ensure_ascii=False)
print('==== 汇总 ====', flush=True)
print(json.dumps(result, indent=2, ensure_ascii=False), flush=True)
print(f'完成. 分析JSON: {prefix}_analysis.json', flush=True)

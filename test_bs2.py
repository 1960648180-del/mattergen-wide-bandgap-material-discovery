"""GPAW 原生能带: restart 复用密度 + 任意 k 点提取本征值"""
import os, warnings, time
warnings.filterwarnings('ignore')
os.environ.setdefault("GPAW_SETUP_PATH", "/usr/local/lib/python3.12/dist-packages/gpaw_data/setups")
import numpy as np
from ase.io import read
from ase.dft.kpoints import bandpath, monkhorst_pack
from gpaw import GPAW, PW, FermiDirac, Mixer

atoms = read('f6rb3y_posrelaxed_new.cif')
calc = GPAW(mode=PW(400), xc='PBE', kpts=(2,2,2), hund=True,
            occupations=FermiDirac(0.05),
            mixer=Mixer(beta=0.05, nmaxold=7, weight=100.0),
            maxiter=200, txt='t2_scf.txt')
atoms.calc = calc
E = atoms.get_potential_energy()
calc.write('t2_scf.gpw')
print('SCF 完成 E=%.4f  已保存 gpw' % E, flush=True)
nocc = int(round(calc.get_number_of_electrons() / 2))
print('每自旋占据带 =', nocc, flush=True)

def extract_bands(gpwfile, kpts, label):
    t0 = time.time()
    c2 = GPAW(gpwfile, kpts=kpts)  # 复用密度, 非自洽
    ks = c2.get_ibz_k_points()
    nspin = c2.get_number_of_spins()
    en = []
    for s in range(nspin):
        en.append([c2.get_eigenvalues(kpt=k, spin=s) for k in range(len(ks))])
    en = np.array(en)  # (nspin, nkpts, nbands)
    vbm = en[:, :, :nocc].max()
    cbm = en[:, :, nocc:].min()
    vidx = np.unravel_index(np.argmax(en[:, :, :nocc]), en[:, :, :nocc].shape)
    cidx = np.unravel_index(np.argmin(en[:, :, nocc:]), en[:, :, nocc:].shape)
    print('%s: 耗时%.1fs  shape=%s' % (label, time.time()-t0, en.shape), flush=True)
    print('  VBM=%.4f CBM=%.4f gap=%.4f | VBM_k=%s CBM_k=%s' % (
        vbm, cbm, cbm-vbm, np.round(ks[vidx[1]],3), np.round(ks[cidx[1]],3)), flush=True)
    return vbm, cbm

# 1) 高对称路径
path = atoms.cell.bandpath(npoints=40)
v1, c1 = extract_bands('t2_scf.gpw', path.kpts, '高对称路径')
# 2) 密集网格
mp = monkhorst_pack((4,4,4))
v2, c2 = extract_bands('t2_scf.gpw', mp, '密集网格4x4x4')
print('路径gap=%.4f  密集gap=%.4f' % (c1-v1, c2-v2), flush=True)
print('测试完成', flush=True)

"""快速测试: band_structure API + 手动 VBM/CBM 提取 (小 k 点, 快速)"""
import os, warnings
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
            maxiter=200, txt='test_bs_scf.txt')
atoms.calc = calc
E = atoms.get_potential_energy()
print('SCF 完成 E=', round(E,4), flush=True)

nocc = int(round(calc.get_number_of_electrons() / 2))
print('电子数 =', calc.get_number_of_electrons(), ' 每自旋占据带 =', nocc, flush=True)

# 1) 高对称路径
import time
from ase.spectrum.band_structure import calculate_band_structure
from ase.dft.kpoints import BandPath
t0 = time.time()
path = atoms.cell.bandpath(npoints=40)
bs = calculate_band_structure(atoms, path=path, cell_tol=1e-3)
print('路径 calculate_band_structure 耗时 %.1fs' % (time.time()-t0), flush=True)
print('energies shape:', bs.energies.shape, flush=True)
Epath = bs.energies  # (nspins, nkpts, nbands)
vbm = Epath[:, :, :nocc].max()
cbm = Epath[:, :, nocc:].min()
print('路径: VBM=%.4f CBM=%.4f gap=%.4f' % (vbm, cbm, cbm-vbm), flush=True)
vidx = np.unravel_index(np.argmax(Epath[:, :, :nocc]), Epath[:, :, :nocc].shape)
cidx = np.unravel_index(np.argmin(Epath[:, :, nocc:]), Epath[:, :, nocc:].shape)
print('  VBM 位置 (spin,k):', vidx, ' kpt=', path.kpts[vidx[1]], flush=True)
print('  CBM 位置 (spin,k):', cidx, ' kpt=', path.kpts[cidx[1]], flush=True)

# 2) 密集均匀网格
t0 = time.time()
mp = monkhorst_pack((4,4,4))
bp_dense = BandPath(atoms.cell, kpts=mp)
bs_d = calculate_band_structure(atoms, path=bp_dense, cell_tol=1e-3)
print('密集网格 calculate_band_structure 耗时 %.1fs' % (time.time()-t0), flush=True)
print('dense energies shape:', bs_d.energies.shape, flush=True)
Ed = bs_d.energies
vd = Ed[:, :, :nocc].max()
cd = Ed[:, :, nocc:].min()
print('密集: VBM=%.4f CBM=%.4f gap=%.4f' % (vd, cd, cd-vd), flush=True)
print('测试完成', flush=True)

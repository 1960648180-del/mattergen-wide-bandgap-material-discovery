import warnings; warnings.filterwarnings('ignore')
from ase.io import read
import numpy as np

a = read('/home/isaac/p1_dft/chgnet_relaxed_F6Rb3Y.cif')
b = read('/home/isaac/p1_dft/f6rb3y_posrelaxed_new.cif')
print('原子数:', len(a), len(b))
print('CHGNet坐标[0]:', a.get_positions()[0])
print('DFT-new坐标[0]:', b.get_positions()[0])
disp = np.linalg.norm(b.get_positions() - a.get_positions(), axis=1)
print('最大原子位移: %.4f Angstrom' % np.max(disp))
print('平均原子位移: %.4f Angstrom' % np.mean(disp))
print('晶胞相同:', np.allclose(a.cell, b.cell, atol=1e-5))

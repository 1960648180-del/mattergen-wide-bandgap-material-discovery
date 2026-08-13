import warnings; warnings.filterwarnings('ignore')
from ase.io import read
import os

raw = {
    'F9Hf3O3Y': read('/home/isaac/p1_dft/dft_F9Hf3O3Y.cif') if os.path.exists('/home/isaac/p1_dft/dft_F9Hf3O3Y.cif') else None,
    'F6Rb3Y': read('/home/isaac/p1_dft/dft_F6Rb3Y.cif') if os.path.exists('/home/isaac/p1_dft/dft_F6Rb3Y.cif') else None,
    'LiO11Re3': read('/home/isaac/p1_dft/dft_LiO11Re3.cif') if os.path.exists('/home/isaac/p1_dft/dft_LiO11Re3.cif') else None,
}
rel = {
    'F9Hf3O3Y': read('/home/isaac/p1_dft/f9hf3o3y_posrelaxed.cif'),
    'F6Rb3Y': read('/home/isaac/p1_dft/f6rb3y_relaxed.cif'),
    'LiO11Re3': read('/home/isaac/p1_dft/li_o11re3_posrelaxed.cif'),
}
for name in ['F9Hf3O3Y', 'F6Rb3Y', 'LiO11Re3']:
    print(f'{name}:')
    if raw[name] is not None:
        r = raw[name]
        d = rel[name]
        print(f'  原始 体积: {r.get_volume():.2f} A3  晶胞: {[round(x,3) for x in r.cell.lengths()]}')
        print(f'  DFT  体积: {d.get_volume():.2f} A3  晶胞: {[round(x,3) for x in d.cell.lengths()]}')
        print(f'  体积变化: {(d.get_volume()-r.get_volume())/r.get_volume()*100:+.2f}%')
    else:
        print(f'  原始 CIF 缺失 (dft_{name}.cif 不在 /home/isaac/p1_dft/)')

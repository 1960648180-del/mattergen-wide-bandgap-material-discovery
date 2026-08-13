import warnings
warnings.filterwarnings('ignore')
from pymatgen.core import Structure
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer

for name in ['F9Hf3O3Y', 'F6Rb3Y', 'LiO11Re3']:
    s = Structure.from_file(f'dft_{name}.cif')
    sg = SpacegroupAnalyzer(s)
    d = sg.get_symmetry_dataset()
    print(f'{name}:')
    print(f'  空间群: {sg.get_space_group_symbol()} (#{sg.get_space_group_number()})')
    print(f'  晶体系统: {sg.get_crystal_system()}')
    print(f'  国际符号: {d["international"]}')
    print()

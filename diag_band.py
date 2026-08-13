import sys
print('python:', sys.version.split()[0])
try:
    import numpy as np
    print('numpy OK', np.__version__)
except Exception as e:
    print('numpy FAIL', e)
try:
    from ase.io import read
    print('ase OK')
except Exception as e:
    print('ase FAIL', e)
try:
    from ase.dft.kpoints import bandpath, monkhorst_pack
    print('kpoints import OK')
except Exception as e:
    print('kpoints FAIL', e)
try:
    from gpaw import GPAW, PW, FermiDirac, Mixer
    print('gpaw import OK')
except Exception as e:
    print('gpaw FAIL', e)
import ast
try:
    ast.parse(open('band_analysis.py').read())
    print('band_analysis.py 语法OK')
except Exception as e:
    print('band_analysis.py 语法FAIL', e)

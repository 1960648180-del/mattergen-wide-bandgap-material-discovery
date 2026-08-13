import warnings
warnings.filterwarnings('ignore')
try:
    import pymatgen
    print('pymatgen', pymatgen.__version__)
except Exception as e:
    print('pymatgen FAIL:', str(e)[:80])
from ase.build import bulk
tests = [('HfO2', 'fluorite', 5.08), ('HfO2', 'monoclinic', None),
         ('Y2O3', 'bixbyite', 10.60), ('YF3', None, None), ('HfF4', None, None)]
for name, cs, a in tests:
    try:
        kw = dict(a=a) if a else dict(a=5.0, cubic=True)
        if cs:
            at = bulk(name, crystalstructure=cs, **kw)
        else:
            at = bulk(name, **kw)
        print(f'{name} ({cs}) OK n={len(at)} formula={at.get_chemical_formula()}')
    except Exception as e:
        print(f'{name} ({cs}) FAIL: {str(e)[:70]}')

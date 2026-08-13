"""检查 GPAW 26.7 HSE06 支持与预估"""
import os, warnings
warnings.filterwarnings('ignore')
os.environ.setdefault("GPAW_SETUP_PATH", "/usr/local/lib/python3.12/dist-packages/gpaw_data/setups")
from gpaw import GPAW, PW, FermiDirac

try:
    calc = GPAW(mode=PW(400), xc='HSE06', kpts=(2, 2, 2),
                occupations=FermiDirac(0.05), txt='-')
    print('HSE06 构造成功: ', calc)
    print('XC:', calc.xc)
except Exception as e:
    print('HSE06 构造失败:', e)
# 列出可用 xc 名称
try:
    from gpaw.xc import XC
    names = ['HSE06', 'HSE03', 'PBE0', 'PBE']
    for n in names:
        try:
            x = XC(n)
            print(f'  XC {n}: OK ({x})')
        except Exception as e:
            print(f'  XC {n}: 失败 {e}')
except Exception as e:
    print('XC 模块导入失败:', e)

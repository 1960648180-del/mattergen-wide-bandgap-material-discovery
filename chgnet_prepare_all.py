"""
全量候选 CHGNet 预弛豫 (第②档结构)
====================================
遍历所有生成结果, 按 formula 去重, CHGNet 预弛豫每个候选
输出: chgnet_relaxed_all/{formula}.cif + candidates_meta.json (类别标注)
"""
import warnings, json
warnings.filterwarnings("ignore")
from ase.io import read, write
from ase.optimize import FIRE
from ase.filters import ExpCellFilter
from chgnet.model import CHGNet
from chgnet.model.dynamics import CHGNetCalculator
from pathlib import Path

ROOT = Path(__file__).parent
OUT_DIR = ROOT / 'chgnet_relaxed_all'
OUT_DIR.mkdir(exist_ok=True)

SOURCES = [
    ('extended_pool/bg_25', 'extended_pool/bg_25/generated_crystals.extxyz'),
    ('extended_pool/bg_30', 'extended_pool/bg_30/generated_crystals.extxyz'),
    ('extended_pool/bg_35', 'extended_pool/bg_35/generated_crystals.extxyz'),
    ('extended_pool/bg_40', 'extended_pool/bg_40/generated_crystals.extxyz'),
    ('extended_pool/bg_45', 'extended_pool/bg_45/generated_crystals.extxyz'),
    ('pool_bandgap_25', 'pool_bandgap_25/generated_crystals.extxyz'),
    ('pool_bandgap_35', 'pool_bandgap_35/generated_crystals.extxyz'),
    ('pool_bandgap_40', 'pool_bandgap_40/generated_crystals.extxyz'),
    ('results', 'results/generated_crystals.extxyz'),
    ('results_widegap', 'results_widegap/generated_crystals.extxyz'),
    ('results_bulk_150', 'results_bulk_150/generated_crystals.extxyz'),
]

# f 电子元素
F_EL = {'La','Lu','Tb','Nd','Ho','Tm','Dy','Gd','Sm','Eu','Pr','Ce','Er','Yb'}

def main():
    model = CHGNet.load()
    print('CHGNet 加载完成')

    # 按 formula 去重收集候选 (formula -> (atoms, source, idx))
    unique = {}
    for label, rel in SOURCES:
        p = ROOT / rel
        if not p.exists():
            print(f'跳过 {label}: 不存在')
            continue
        frames = read(str(p), index=':')
        for i, at in enumerate(frames):
            form = at.get_chemical_formula()
            if form not in unique:
                unique[form] = (at, label, i)
    print(f'唯一候选: {len(unique)}')

    meta = {}
    done = 0
    for form, (atoms, source, idx) in sorted(unique.items()):
        syms = set(atoms.get_chemical_symbols())
        has_F = 'F' in syms
        has_f = bool(syms & F_EL)
        n = len(atoms)
        out_cif = OUT_DIR / f'{form}.cif'
        if out_cif.exists():
            # 已有, 跳过弛豫但记录
            meta[form] = {'source': source, 'source_idx': idx, 'n_atoms': n,
                          'has_F': has_F, 'has_f': has_f, 'chgnet_E': None}
            print(f'[{done+1}/{len(unique)}] {form} 已存在, 跳过')
            done += 1
            continue
        try:
            atoms.calc = CHGNetCalculator(model=model)
            ef = ExpCellFilter(atoms)
            opt = FIRE(ef)
            opt.run(fmax=0.05, steps=300)
            e = atoms.get_potential_energy()
            write(str(out_cif), atoms)
            meta[form] = {'source': source, 'source_idx': idx, 'n_atoms': n,
                          'has_F': has_F, 'has_f': has_f, 'chgnet_E': e}
            print(f'[{done+1}/{len(unique)}] {form} n={n} E={e:.3f} eV  F={has_F} f={has_f}')
        except Exception as ex:
            meta[form] = {'source': source, 'source_idx': idx, 'n_atoms': n,
                          'has_F': has_F, 'has_f': has_f, 'chgnet_E': None, 'error': str(ex)[:60]}
            print(f'[{done+1}/{len(unique)}] {form} 弛豫失败: {str(ex)[:50]}')
        done += 1

    with open(ROOT / 'candidates_meta.json', 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    print(f'\n完成. {done} 个候选, 元数据: candidates_meta.json')

if __name__ == '__main__':
    main()

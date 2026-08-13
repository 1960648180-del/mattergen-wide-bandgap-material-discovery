"""WSL 端: 检查无效JSON + 确认FAIL验证样本存在"""
import json
from pathlib import Path

RES = Path('/home/isaac/p1_dft/gap_all_results')
INP = Path('/home/isaac/p1_dft/gap_all_input')

print('=== 无效/损坏 JSON 检查 ===')
bad = 0
for jf in sorted(RES.glob('*.json')):
    try:
        d = json.loads(jf.read_text(encoding='utf-8'))
        if not d or d[0].get('pbe_bandgap') is None:
            print(f'  {jf.name}: 空/无gap ({len(d)}项)'); bad += 1
    except Exception as e:
        print(f'  {jf.name}: 损坏 - {e}'); bad += 1
print(f'无效: {bad}')

print('\n=== FAIL 验证样本确认 ===')
for name in ['Al2F12Rb6', 'Al3B4DyO12']:
    cif = INP / f'{name}.cif'
    print(f'  {name}: CIF {"存在" if cif.exists() else "缺失"}')

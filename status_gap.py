"""WSL 端: 查看全量带隙进度 (无引号地狱)"""
import json, subprocess
from pathlib import Path

RES = Path('/home/isaac/p1_dft/gap_all_results')
INP = Path('/home/isaac/p1_dft/gap_all_input')
LOG = Path('/home/isaac/p1_dft/run_bandgap_all.log')

# 已完成
done = sorted(RES.glob('*.json'))
print(f'=== 已完成 {len(done)}/{len(list(INP.glob("*.cif")))} ===')
for jf in done:
    try:
        d = json.loads(jf.read_text(encoding='utf-8'))[0]
        print(f"  {d['formula']:<16} n={d['n_atoms']:>3} gap={d['pbe_bandgap']:.3f}")
    except Exception as e:
        print(f"  {jf.name}: ERR {e}")

# 运行中
ps = subprocess.run(['ps', '-eo', 'pid,etimes,args'], capture_output=True, text=True).stdout
running = {}
for line in ps.splitlines():
    if 'bandgap_verify' in line and 'grep' not in line:
        parts = line.split()
        pid, et = parts[0], int(parts[1])
        name = None
        for a in parts[3:]:
            if 'gap_all_input/' in a:
                name = a.split('/')[-1].replace('.cif', '')
        if name:
            running[name] = (pid, et)
print(f'\n=== 运行中 {len(running)} 个 ===')
for name, (pid, et) in running.items():
    print(f"  {name:<16} pid={pid} 已跑 {et//60}分{et%60}秒")

"""
全量 bandgap_verify 并行调度 (WSL)
用法: python3 run_bandgap_all.py <并行数>
输入: /home/isaac/p1_dft/gap_all_input/*.cif (CHGNet 弛豫结构)
输出: /home/isaac/p1_dft/gap_all_results/{formula}.json
"""
import subprocess, concurrent.futures, sys, json
from pathlib import Path

WSL_INPUT = Path('/home/isaac/p1_dft/gap_all_input')
OUT = Path('/home/isaac/p1_dft/gap_all_results')
OUT.mkdir(exist_ok=True)
VERIFY = '/home/isaac/p1_dft/bandgap_verify.py'
FAILED_FILE = Path('/home/isaac/p1_dft/gap_all_failed.txt')

# 已知 FAIL 黑名单 (难收敛体系, 跳过不再重试, 附录单独补救)
_failed = set()
if FAILED_FILE.exists():
    _failed = {l.strip() for l in FAILED_FILE.read_text().splitlines() if l.strip()}

cifs = sorted(WSL_INPUT.glob('*.cif'))
print(f'待处理: {len(cifs)} 个候选 (跳过黑名单 {len(_failed)} 个)', flush=True)

def run_one(cif):
    form = cif.stem
    out = OUT / f'{form}.json'
    if form in _failed:
        return form, 0, ['SKIP(黑名单)']
    # 断点续跑: 已有有效结果则跳过
    if out.exists():
        try:
            d = json.loads(out.read_text(encoding='utf-8'))
            if d and d[0].get('pbe_bandgap') is not None:
                return form, 0, ['SKIP(已有结果)']
        except Exception:
            pass
    cmd = ['python3', VERIFY, '--cif', str(cif), '--kpts', '4', '4', '4', '--out', str(out)]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=1500)
        tail = (r.stdout or '').strip().splitlines()
        info = tail[-3:] if tail else []
        return form, r.returncode, info
    except Exception as e:
        return form, -1, [str(e)]

N = int(sys.argv[1]) if len(sys.argv) > 1 else 6
print(f'并行数: {N}', flush=True)

done = ok = 0
with concurrent.futures.ThreadPoolExecutor(max_workers=N) as ex:
    futs = {ex.submit(run_one, c): c for c in cifs}
    for fut in concurrent.futures.as_completed(futs):
        form, rc, info = fut.result()
        done += 1
        if rc == 0:
            ok += 1
        else:
            # 记录 FAIL 到黑名单, 下次续跑不再重试
            with FAILED_FILE.open('a') as f:
                f.write(form + '\n')
        print(f'[{done}/{len(cifs)}] {form}: rc={rc} {"OK" if rc==0 else "FAIL"}', flush=True)
print(f'\n完成: {done}, 成功: {ok}, 失败: {done-ok}', flush=True)

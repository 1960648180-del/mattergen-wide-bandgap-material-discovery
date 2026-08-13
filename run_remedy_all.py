"""
FAIL 补救重跑: 对黑名单候选用长 timeout 重跑 bandgap_verify (4×4×4 同口径)
用法: python3 run_remedy_all.py <并行数>
输入: gap_all_failed.txt (FAIL 列表) + gap_all_input/*.cif
输出: gap_remedy_results/{formula}.json  (独立目录, 放附录, 不混主表)
失败: 记录到 gap_remedy_failed.txt
"""
import subprocess, concurrent.futures, sys, json
from pathlib import Path

INP = Path('/home/isaac/p1_dft/gap_all_input')
OUT = Path('/home/isaac/p1_dft/gap_remedy_results')
OUT.mkdir(exist_ok=True)
VERIFY = '/home/isaac/p1_dft/bandgap_verify.py'
FAILED_FILE = Path('/home/isaac/p1_dft/gap_all_failed.txt')
REMEDY_FAIL = Path('/home/isaac/p1_dft/gap_remedy_failed.txt')
TIMEOUT = None  # 不设超时: 多核并行, 慢样本占一个核无碍, 让 maxiter=200 自然结束(~5-7h/候选), 真不收敛由 SCF 报错兜底

names = [l.strip() for l in FAILED_FILE.read_text().splitlines() if l.strip()]
done = {f.stem for f in OUT.glob('*.json')}
todo = [n for n in names if n not in done]
print(f'黑名单 {len(names)}, 已补救 {len(done)}, 待补救 {len(todo)}', flush=True)

def run_one(name):
    cif = INP / f'{name}.cif'
    out = OUT / f'{name}.json'
    if out.exists():
        try:
            d = json.loads(out.read_text(encoding='utf-8'))
            if d and d[0].get('pbe_bandgap') is not None:
                return name, 0, ['SKIP(已有)']
        except Exception:
            pass
    cmd = ['python3', VERIFY, '--cif', str(cif), '--kpts', '4', '4', '4', '--out', str(out)]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT)
        tail = (r.stdout or '').strip().splitlines()
        return name, r.returncode, (tail[-3:] if tail else [])
    except Exception as e:
        return name, -1, [str(e)]

N = int(sys.argv[1]) if len(sys.argv) > 1 else 6
print(f'并行数: {N}', flush=True)

done_c = ok = 0
with concurrent.futures.ThreadPoolExecutor(max_workers=N) as ex:
    futs = {ex.submit(run_one, n): n for n in todo}
    for fut in concurrent.futures.as_completed(futs):
        name, rc, info = fut.result()
        done_c += 1
        if rc == 0:
            ok += 1
        else:
            with REMEDY_FAIL.open('a') as f:
                f.write(name + '\n')
        print(f'[{done_c}/{len(todo)}] {name}: {"OK" if rc==0 else "FAIL"}', flush=True)
print(f'\n完成: {done_c}, 成功: {ok}, 失败: {done_c-ok}', flush=True)

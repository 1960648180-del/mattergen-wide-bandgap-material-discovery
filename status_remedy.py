"""精确统计补救数目"""
import json, subprocess
from pathlib import Path

RES = Path('/home/isaac/p1_dft/gap_remedy_results')
FAILED = Path('/home/isaac/p1_dft/gap_all_failed.txt')
REMEDY_FAIL = Path('/home/isaac/p1_dft/gap_remedy_failed.txt')

blacklist = [l.strip() for l in FAILED.read_text().splitlines() if l.strip()] if FAILED.exists() else []
print(f'黑名单总数: {len(blacklist)}')

# 补救结果文件
ok_files = []
bad_files = []
for jf in sorted(RES.glob('*.json')):
    try:
        d = json.loads(jf.read_text(encoding='utf-8'))
        if d and d[0].get('pbe_bandgap') is not None:
            ok_files.append(jf.stem)
        else:
            bad_files.append(jf.name)
    except Exception:
        bad_files.append(jf.name)
print(f'补救成功(有效JSON): {len(ok_files)}')
print(f'补救目录无效/空: {len(bad_files)} {bad_files if bad_files else ""}')

# 补救失败记录
remedy_fail = [l.strip() for l in REMEDY_FAIL.read_text().splitlines() if l.strip()] if REMEDY_FAIL.exists() else []
print(f'补救失败(gap_remedy_failed.txt): {len(remedy_fail)}')
for f in remedy_fail:
    print(f'  - {f}')

# 当前运行中的候选
ps = subprocess.run(['ps', '-eo', 'args'], capture_output=True, text=True).stdout
running = set()
for line in ps.splitlines():
    if 'gap_remedy_results/' in line and 'bandgap_verify' in line:
        out = line.split('gap_remedy_results/')[-1].strip()
        running.add(out.replace('.json', ''))
print(f'当前运行中(补救): {len(running)}')
for r in sorted(running):
    print(f'  - {r}')

# 账目: 黑名单 = 成功 + 失败 + 进行中 + 未处理
done_set = set(ok_files)
all_accounted = done_set | set(remedy_fail) | running
unprocessed = [b for b in blacklist if b not in all_accounted]
print(f'\n账目核对:')
print(f'  黑名单 {len(blacklist)} = 成功 {len(done_set)} + 失败 {len(remedy_fail)} + 运行中 {len(running)} + 未处理 {len(unprocessed)}')
if unprocessed:
    print(f'  未处理: {unprocessed}')

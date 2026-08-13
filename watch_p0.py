#!/usr/bin/env python3
"""监控 P0 批次: F6Rb3Y 弛豫 + F9Hf3O3Y/LiO11Re3 带隙计算 (PID 282/288/293)"""
import time, os, glob

out = open('/home/isaac/p1_dft/watch_p0.out', 'a', buffering=1)
PIDS = [282, 288, 293]
for i in range(240):
    time.sleep(300)
    ts = time.strftime('%H:%M')
    line = f'--- check {i} ({ts}) ---'
    # 各进程存活
    alive = [p for p in PIDS if os.path.exists(f'/proc/{p}')]
    line += f' alive={alive}'
    # F6Rb3Y 弛豫步数
    try:
        with open('/home/isaac/p1_dft/f6rb3y_posrelax_new.txt') as f:
            fc = f.read().count('Force computation')
        line += f' F6Rb3Y_steps={fc}'
    except Exception:
        pass
    # 带隙 SCF 迭代数 (gap.txt 中 iter 计数)
    for name in ['f9hf3o3y_posrelaxed', 'li_o11re3_posrelaxed']:
        try:
            with open(f'/home/isaac/p1_dft/{name}.gap.txt') as f:
                niter = sum(1 for l in f if 'iter:' in l and 'SCF' not in l)
            line += f' {name[:6]}_iters={niter}'
        except Exception:
            pass
    # 结果文件
    cifs = glob.glob('/home/isaac/p1_dft/f6rb3y_posrelaxed_new.cif')
    jsons = glob.glob('/home/isaac/p1_dft/gap_*.json')
    line += f' cifs={len(cifs)} jsons={len(jsons)}'
    print(line, flush=True)
    if len(alive) == 0 or (len(cifs) > 0 and len(jsons) >= 2):
        print('DONE', flush=True)
        break
out.close()

#!/usr/bin/env python3
"""Monitor pos-relax for F9Hf3O3Y and LiO11Re3, log to monitor.out"""
import time, os, sys

out = open('/home/isaac/p1_dft/monitor.out', 'a', buffering=1)
for i in range(200):
    time.sleep(300)
    f9 = 0
    li = 0
    try:
        with open('/home/isaac/p1_dft/f9hf3o3y_posrelax.txt') as f:
            f9 = f.read().count('Force computation')
    except Exception:
        pass
    try:
        with open('/home/isaac/p1_dft/li_o11re3_posrelax.txt') as f:
            li = f.read().count('Force computation')
    except Exception:
        pass
    import glob
    cifs = glob.glob('/home/isaac/p1_dft/*posrelaxed.cif')
    print(f'--- check {i} (F9Hf={f9} LiO={li}) {time.strftime("%H:%M")} ---', flush=True)
    if cifs:
        print('DONE', cifs, flush=True)
        break
    # check if processes still alive
    pids = [p for p in (15512, 15650) if os.path.exists(f'/proc/{p}')]
    print(f'   alive pids: {pids}', flush=True)
    if not pids:
        print('ALL EXITED', flush=True)
        break
out.close()

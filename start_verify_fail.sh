#!/bin/bash
# FAIL 时间验证启动脚本
cd /home/isaac/p1_dft
# 清除旧日志/输出
rm -f verify_Al2F12Rb6.json verify_Al3B4DyO12.json
rm -f gap_all_input/Al2F12Rb6.gap.txt gap_all_input/Al3B4DyO12.gap.txt
# 启动 2 个验证 (无 timeout, maxiter=200, 观察是否收敛)
nohup python3 bandgap_verify.py --cif gap_all_input/Al2F12Rb6.cif --kpts 4 4 4 --out verify_Al2F12Rb6.json > verify_Al2F12Rb6.log 2>&1 &
nohup python3 bandgap_verify.py --cif gap_all_input/Al3B4DyO12.cif --kpts 4 4 4 --out verify_Al3B4DyO12.json > verify_Al3B4DyO12.log 2>&1 &
sleep 20
echo "=== 验证进程 ==="
ps -eo pid,etime,args | grep '[b]andgap_verify'
echo "=== 日志 ==="
tail -2 /home/isaac/p1_dft/verify_Al2F12Rb6.log
tail -2 /home/isaac/p1_dft/verify_Al3B4DyO12.log

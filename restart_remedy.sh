#!/bin/bash
# 清理孤儿补救进程 + 改名备份 + 重启补救
echo "=== 清理前进程 ==="
pgrep -af 'python3.*bandgap_verify' | head
pgrep -af 'python3.*run_remedy' | head

# 杀掉补救相关进程 (匹配 python3 开头, 避免误杀自身)
for pid in $(pgrep -f 'python3.*bandgap_verify'); do kill -9 "$pid" 2>/dev/null; done
for pid in $(pgrep -f 'python3.*run_remedy'); do kill -9 "$pid" 2>/dev/null; done
sleep 5

echo "=== 清理后 ==="
pgrep -af 'python3.*bandgap_verify' || echo 'bandgap_verify 已清理'
pgrep -af 'python3.*run_remedy' || echo 'run_remedy 已清理'

# 改名备份
cd /home/isaac/p1_dft/gap_remedy_results
if [ -f verify_Al2F12Rb6.json ]; then mv verify_Al2F12Rb6.json Al2F12Rb6.json; fi
if [ -f verify_Al3B4DyO12.json ]; then mv verify_Al3B4DyO12.json Al3B4DyO12.json; fi
echo "=== 补救目录 ==="
ls

# 重启补救
cd /home/isaac/p1_dft
rm -f run_remedy_all.log
nohup python3 run_remedy_all.py 6 > run_remedy_all.log 2>&1 &
sleep 50
echo "=== 补救日志 ==="
cat /home/isaac/p1_dft/run_remedy_all.log
echo "=== 进程数 ==="
pgrep -fc 'python3.*bandgap_verify'

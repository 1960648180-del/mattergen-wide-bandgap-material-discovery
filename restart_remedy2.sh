#!/bin/bash
# 重启补救(延长timeout后): 杀旧进程 + 断点续跑
cd /home/isaac/p1_dft
echo "=== 重启前已完成 ==="
ls gap_remedy_results/ | wc -l

# 杀掉补救相关进程 (精确匹配 python3 开头, 避免误杀自身)
for pid in $(pgrep -f 'python3.*bandgap_verify'); do kill -9 "$pid" 2>/dev/null; done
for pid in $(pgrep -f 'python3.*run_remedy'); do kill -9 "$pid" 2>/dev/null; done
sleep 5
pgrep -af 'python3.*bandgap_verify' || echo 'bandgap_verify 已清理'
pgrep -af 'python3.*run_remedy' || echo 'run_remedy 已清理'

# 重启 (断点续跑: 已完成的自动跳过)
rm -f run_remedy_all.log
nohup python3 run_remedy_all.py 6 > run_remedy_all.log 2>&1 &
sleep 50
echo "=== 补救日志 ==="
cat /home/isaac/p1_dft/run_remedy_all.log
echo "进程数: $(pgrep -fc 'python3.*bandgap_verify')"

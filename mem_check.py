"""WSL 端: 实测内存占用, 判断能否加并行"""
import subprocess

# 系统内存
mem = subprocess.run(['free', '-g'], capture_output=True, text=True).stdout
print('=== 系统内存 (GB) ===')
print(mem)

# WSL 配置上限
try:
    cfg = subprocess.run(['cat', '/mnt/c/Users/19606/.wslconfig'], capture_output=True, text=True)
    print('=== .wslconfig ===')
    print(cfg.stdout or '(无配置文件, 默认=主机内存的50%)')
except Exception as e:
    print('wslconfig ERR', e)

# 每个 bandgap 进程内存
ps = subprocess.run(['ps', '-eo', 'pid,rss,etimes,args'], capture_output=True, text=True).stdout
print('=== bandgap_verify 进程内存 (RSS MB) ===')
total = 0
n = 0
for line in ps.splitlines():
    if 'bandgap_verify' in line and 'grep' not in line:
        parts = line.split()
        pid, rss_kb = parts[0], int(parts[1])
        rss_mb = rss_kb / 1024
        total += rss_mb
        n += 1
        name = [a for a in parts[3:] if 'gap_all_input/' in a]
        print(f"  pid={pid:<6} RSS={rss_mb:6.0f} MB  已跑{int(parts[2])//60}分 {name}")
print(f'bandgap 进程数: {n}, 总 RSS: {total:.0f} MB')

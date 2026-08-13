#!/bin/bash
# P0 批次总控: 启动 F6Rb3Y 弛豫 + 两个带隙计算
# 全部用 nohup 后台, 写各自日志
cd /home/isaac/p1_dft
export GPAW_SETUP_PATH=/usr/local/lib/python3.12/dist-packages/gpaw_data/setups

# 1. F6Rb3Y 新方案弛豫
if ! pgrep -f relax_pos_F6Rb3Y_new >/dev/null; then
    nohup python3 relax_pos_F6Rb3Y_new.py > f6rb3y_posrelax_new.log 2>&1 &
    echo "启动 F6Rb3Y 弛豫: pid $!"
else
    echo "F6Rb3Y 弛豫已在运行"
fi

# 2. F9Hf3O3Y 带隙
if ! pgrep -f "bandgap_verify.*f9hf3o3y" >/dev/null; then
    nohup python3 bandgap_verify.py --cif f9hf3o3y_posrelaxed.cif --kpts 4 4 4 --out gap_F9Hf3O3Y.json > gap_F9Hf3O3Y.out 2>&1 &
    echo "启动 F9Hf3O3Y 带隙: pid $!"
else
    echo "F9Hf3O3Y 带隙已在运行"
fi

# 3. LiO11Re3 带隙
if ! pgrep -f "bandgap_verify.*li_o11re3" >/dev/null; then
    nohup python3 bandgap_verify.py --cif li_o11re3_posrelaxed.cif --kpts 4 4 4 --out gap_LiO11Re3.json > gap_LiO11Re3.out 2>&1 &
    echo "启动 LiO11Re3 带隙: pid $!"
else
    echo "LiO11Re3 带隙已在运行"
fi

sleep 3
echo "=== 运行中的任务 ==="
pgrep -af "relax_pos_F6Rb3Y|bandgap_verify" || echo "无"

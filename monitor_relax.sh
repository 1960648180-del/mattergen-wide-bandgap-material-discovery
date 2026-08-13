#!/bin/bash
# Monitor pos-relax for F9Hf3O3Y and LiO11Re3
cd /home/isaac/p1_dft
for i in $(seq 1 24); do
  sleep 300
  F9=$(grep -c 'Force computation' f9hf3o3y_posrelax.txt 2>/dev/null)
  Li=$(grep -c 'Force computation' li_o11re3_posrelax.txt 2>/dev/null)
  echo "--- check $i (F9Hf=$F9 LiO=$Li) $(date +%H:%M) ---"
  if ls *posrelaxed.cif >/dev/null 2>&1; then
    echo DONE
    break
  fi
  ps -o pid,etime -p 15512 15650 2>/dev/null | tail -1
done

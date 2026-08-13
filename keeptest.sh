#!/bin/bash
# 心跳测试: 每5秒写时间戳, 用于检测进程是否被杀 / VM是否重启
echo "start $(date +%s)" > /tmp/ping.txt
while true; do
  echo "tick $(date +%s)" >> /tmp/ping.txt
  sleep 5
done

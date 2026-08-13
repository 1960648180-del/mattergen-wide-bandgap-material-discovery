"""
MatterGen 扩展实验 Pipeline
===========================
阶段 1: 生成 100 个候选晶体
阶段 2: CHGNet 批量预测形成能
阶段 3: 统计 (成功率/能量分布/元素分布/重复率)
阶段 4: 筛选 Top 候选
阶段 5: 输出推荐 10 个 DFT 候选

用法: python extended_pipeline.py
"""

import subprocess
import time
import os
import json
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(r"D:\nature reproduction\mattergen")
VENV_PYTHON = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"
MODEL_PATH = PROJECT_ROOT / "checkpoints" / "dft_band_gap"

# 生成配置: 覆盖多个带隙条件以保证多样性
# (输出目录, 目标带隙, 每批数量)
GENERATION_CONFIGS = [
    ("extended_pool/bg_25", 2.5, 20),
    ("extended_pool/bg_30", 3.0, 20),
    ("extended_pool/bg_35", 3.5, 20),
    ("extended_pool/bg_40", 4.0, 20),
    ("extended_pool/bg_45", 4.5, 20),
]


def run_generation(output_dir: Path, band_gap: float, num: int) -> bool:
    """运行一轮 MatterGen 生成"""
    output_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        str(VENV_PYTHON), "-m", "mattergen.scripts.generate",
        str(output_dir),
        f"--model_path={MODEL_PATH}",
        f"--batch_size={num}",
        "--num_batches=1",
        f'--properties_to_condition_on={{"dft_band_gap":{band_gap}}}',
        "--diffusion_guidance_factor=2.0",
        f"--sampling_config_path={PROJECT_ROOT / 'sampling_conf'}",
    ]
    print(f"\n[{datetime.now().strftime('%H:%M')}] 生成: bandgap={band_gap} eV, n={num}")
    print(f"  输出: {output_dir}")
    start = time.time()
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=7200)
        elapsed = (time.time() - start) / 60
        if result.returncode != 0:
            print(f"  [{elapsed:.0f}分] 失败 (returncode={result.returncode})")
            print(result.stderr[-2000:] if result.stderr else "no stderr")
            return False
        print(f"  [{elapsed:.0f}分] 完成")
        return True
    except subprocess.TimeoutExpired:
        print("  超时 (2小时)")
        return False
    except Exception as e:
        print(f"  异常: {e}")
        return False


def main():
    total_start = time.time()
    results = {}
    for output_dir, band_gap, num in GENERATION_CONFIGS:
        od = PROJECT_ROOT / output_dir
        ok = run_generation(od, band_gap, num)
        results[output_dir] = ok
        time.sleep(60)  # 每轮间隔 1 分钟

    hours = (time.time() - total_start) / 3600
    print(f"\n{'='*60}")
    print(f"生成阶段完成! 总耗时 {hours:.1f} 小时")
    print(f"结果: {json.dumps(results, indent=2)}")
    print(f"共计划生成 {sum(c[2] for c in GENERATION_CONFIGS)} 个候选")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()

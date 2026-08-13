"""
MatterGen 扩展生成批处理
生成剩余 4 个带隙条件的候选 (bg_30, bg_35, bg_40, bg_45)
用法: python run_extended_generation.py
"""
import subprocess
import os
import time
from pathlib import Path

PROJECT_ROOT = Path(r"D:\nature reproduction\mattergen")
VENV_PYTHON = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"
MODEL_PATH = PROJECT_ROOT / "checkpoints" / "dft_band_gap"

CONFIGS = [
    ("extended_pool/bg_30", 3.0),
    ("extended_pool/bg_35", 3.5),
    ("extended_pool/bg_40", 4.0),
    ("extended_pool/bg_45", 4.5),
]

def main():
    for output_dir, band_gap in CONFIGS:
        od = PROJECT_ROOT / output_dir
        if od.exists() and (od / "generated_crystals.extxyz").exists():
            print(f"[跳过] {output_dir} 已存在")
            continue
        od.mkdir(parents=True, exist_ok=True)
        cmd = [
            str(VENV_PYTHON), "-m", "mattergen.scripts.generate",
            str(od),
            f"--model_path={MODEL_PATH}",
            "--batch_size=20", "--num_batches=1",
            f'--properties_to_condition_on={{"dft_band_gap":{band_gap}}}',
            "--diffusion_guidance_factor=2.0",
            f"--sampling_config_path={PROJECT_ROOT / 'sampling_conf'}",
        ]
        print(f"\n=== 生成 bg_{band_gap:.1f} ===", flush=True)
        start = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
        elapsed = (time.time() - start) / 60
        # 打印尾部
        lines = (result.stdout or "").splitlines()
        tail = [l for l in lines if "Full Formula" in l or "Reduced" in l]
        print(f"  完成 ({elapsed:.1f} 分), 结构: {len(tail)} 个", flush=True)
        # 保存日志
        log = od / "generation.log"
        log.write_text((result.stdout or "") + "\nSTDERR:\n" + (result.stderr or ""))
        time.sleep(30)

    print("\n全部生成完成!")

if __name__ == "__main__":
    main()

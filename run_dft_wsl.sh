#!/bin/bash
# TbF₃ DFT 验证 - WSL Ubuntu 一键运行脚本
# 用法: bash run_dft_wsl.sh

set -e

echo "=== 步骤1: 安装依赖 ==="
sudo apt-get install -y gpaw gpaw-data python3-ase 2>/dev/null

echo "=== 步骤2: 下载 Tb 赝势 ==="
# GPAW 官方 PAW 数据集
wget -q "https://zenodo.org/records/11236438/files/Tb.PBE.gz" -O /usr/share/gpaw-setups/Tb.PBE.gz || \
wget -q "https://wiki.fysik.dtu.dk/gpaw-files/Tb.PBE.gz" -O /usr/share/gpaw-setups/Tb.PBE.gz || \
echo "需手动下载 Tb.PBE.gz 放到 /usr/share/gpaw-setups/"

export GPAW_SETUP_PATH=/usr/share/gpaw-setups

echo "=== 步骤3: 运行 DFT ==="
python3 << 'PYEOF'
import warnings; warnings.filterwarnings('ignore')
from ase.io import read
from gpaw import GPAW, PW

atoms = read('/home/isaac/tb3_dft.cif')
print(f'原子数: {len(atoms)}')
print(f'化学式: {atoms.get_chemical_formula()}')

# PBE 平面波 DFT
calc = GPAW(mode=PW(400), xc='PBE', kpts=(3,3,3), txt='tb3_dft.txt')
atoms.calc = calc
energy = atoms.get_potential_energy()
n = len(atoms)

# 参考: CHGNet 总能 -27.97 eV
print(f'\n======= DFT 结果 =======')
print(f'DFT 总能:          {energy:.4f} eV')
print(f'DFT 每原子:        {energy/n:.4f} eV/atom')
print(f'CHGNet 总能:       -27.97 eV (参考)')
print(f'CHGNet 每原子:     -6.99 eV/atom (参考)')
print(f'差值 (DFT-CHGNet): {energy + 27.97:.4f} eV')
print(f'=======================')
PYEOF

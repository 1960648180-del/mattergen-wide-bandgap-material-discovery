# 基于扩散模型的宽禁带半导体候选材料发现

> **本项目基于 Microsoft MatterGen 开源模型进行二次应用，以下为独立研究成果。**

## 项目简介

使用 Microsoft MatterGen（Nature 2025）扩散模型，以 **dft_band_gap** 为条件属性，定向生成宽禁带半导体候选晶体结构。共生成 **64 个候选结构**，覆盖 4 个带隙目标。

## 生成结果

| 目标带隙 | 目录 | 结构数 | CIF 文件 |
|---------|------|-------|---------|
| 2.5 eV | `pool_bandgap_25/` | 16 | ✅ |
| 3.0 eV | `results_widegap/` | 16 | ✅ |
| 3.5 eV | `pool_bandgap_35/` | 16 | ✅ |
| 4.0 eV | `pool_bandgap_40/` | 16 | ✅ |

**合计：64 个候选晶体结构**

## 数据说明

每个结果目录包含：
- `cif_files/structure_{1..16}.cif` — 单个晶体结构文件（CIF 格式）
- `generated_crystals.extxyz` — 所有结构的 EXTXYZ 汇总
- `generated_crystals_cif.zip` — CIF 文件打包
- `generated_trajectories.zip` — 生成轨迹

## 实验条件

- **模型**: MatterGen fine-tuned on `dft_band_gap`
- **扩散指导因子**: 2.0
- **每个目标采样**: 16 个结构（batch_size=16, num_batches=1）
- **硬件**: NVIDIA GeForce RTX 4060 Laptop GPU（8GB）
- **环境**: Python 3.10 + PyTorch 2.4.1+cu121

## 后续计划

1. **MatterSim 结构弛豫** — 优化 64 个候选结构
2. **去重筛选** — 去除相似结构，筛选 Top-5
3. **化学合理性检查** — 形成能、键长、对称性
4. **结果整理** — 用于复试展示

---

<details>
<summary><b>📖 模型使用参考（基于 Microsoft MatterGen 官方文档）</b></summary>

> 以下内容为 Microsoft MatterGen 原版文档，供环境搭建和模型使用参考。

### 环境安装

```bash
pip install uv
uv venv .venv --python 3.10
source .venv/bin/activate
uv pip install -e .
```

### 可用预训练模型

| 模型 | 说明 |
|------|------|
| `mattergen_base` | 无条件基模型（Alex-MP-20） |
| `mp_20_base` | 无条件基模型（MP-20） |
| `dft_band_gap` | 条件模型：带隙 |
| `dft_mag_density` | 条件模型：磁矩 |
| `ml_bulk_modulus` | 条件模型：体模量 |
| `chemical_system` | 条件模型：化学体系 |
| `space_group` | 条件模型：空间群 |

### 无条件生成

```bash
mattergen-generate results/ --pretrained-name=mattergen_base --batch_size=16 --num_batches=1
```

### 条件生成（本项目的使用方法）

```bash
mattergen-generate <输出目录> \
  --model_path=checkpoints/dft_band_gap \
  --batch_size=16 --num_batches=1 \
  --properties_to_condition_on="{dft_band_gap:<目标值>}" \
  --diffusion_guidance_factor=2.0
```

### 弛豫评估

```bash
mattergen-evaluate --structures_path=$RESULTS_PATH --relax=True --save_as="metrics.json"
```

> 完整文档请参阅 [Microsoft MatterGen 原版仓库](https://github.com/microsoft/mattergen)。

</details>

---

## 引用

```bibtex
@article{MatterGen2025,
  author  = {Zeni, Claudio and Pinsler, Robert and Z{\"u}gner, Daniel et al.},
  journal = {Nature},
  title   = {A generative model for inorganic materials design},
  year    = {2025},
  doi     = {10.1038/s41586-025-08628-5},
}
```

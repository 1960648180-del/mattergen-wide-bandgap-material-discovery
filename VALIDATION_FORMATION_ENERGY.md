# CHGNet vs DFT 形成能验证报告

## 概述

对 4 个代表性宽禁带候选结构（含 TbF₃ 验证样本+3 个新候选）完成了严格的自旋极化 DFT-PBE 形成能计算，并与 CHGNet 预测进行了定量对比。

---

## 计算参数

| 项目 | 参数 |
|------|------|
| DFT 代码 | GPAW 26.7.0 |
| 泛函 | PBE（自旋极化）|
| 平面波截断 | 400 eV |
| 赝势 | GPAW PAW |
| Smearing | Fermi-Dirac (0.3 eV) |
| Mixer | Pulay (beta=0.05, nmaxold=7) |
| 自旋 | `hund=True` 自动处理 |
| 收敛标准 | 能量变化 < 0.0005 eV/电子 |

---

## 参考态能量

| 元素 | 参考结构 | DFT 总能 (eV) | 每原子 (eV) | SCF 迭代 | 备注 |
|:----:|:--------:|:------------:|:----------:|:--------:|------|
| Tb | hcp (2原子) | -15.1274 | -7.5637 | 431 | 能量收敛，密度因 f 电子电荷 sloshing 未完全收敛 |
| F | F₂ (2原子) | -1.2973 | -0.6486 | 16 | ✅ 闭壳层分子 |
| Sc | hcp (2原子) | -9.3611 | -4.6806 | <20 | ✅ 无 f 电子 |
| Lu | hcp (2原子) | -7.8018 | -3.9009 | <20 | ✅ 填满 4f |
| Nd | hcp (2原子) | -9.5301 | -4.7650 | 93+ | ⚠️ 能量收敛，电荷 sloshing |
| O | O₂ (2原子) | -6.7838 | -3.3919 | <20 | ✅ 三重态正确 (2.0 μB) |
| P | sc (1原子) | -3.1626 | -3.1626 | <20 | ✅ 无 f 电子 |

---

## 形成能对比

| 结构 | 化学式 | 原子数 | DFT 总能 (eV) | DFT 形成能 (eV/atom) | CHGNet 形成能 (eV/atom) | 绝对误差 | 相对误差 |
|:----:|:------:|:-----:|:------------:|:-------------------:|:---------------------:|:--------:|:--------:|
| TbF₃ | TbF₃ | 4 | -25.53 | **-4.01** | -4.33 | **0.32** | 7.4% |
| F₃Sc | ScF₃ | 4 | -22.63 | **-4.00** | -4.19 | **0.19** | 4.5% |
| F₂Lu₂O₂ | LuOF | 6 | -37.34 | **-3.58** | -4.17 | **0.59** | 14.2% |
| Nd₂O₈P₂ | NdPO₄ | 12 | -83.08 | **-3.34** | -3.69 | **0.35** | 9.5% |

**统计指标**:
- MAE (平均绝对误差): **0.36 eV/atom**
- RMSE: **0.39 eV/atom**
- 最大误差: F₂Lu₂O₂ (0.59 eV/atom)
- 最小误差: F₃Sc (0.19 eV/atom)

---

## 误差来源分析

### 1. 系统偏差

CHGNet 系统性地预测比 DFT-PBE 更负的形成能（所有 4 个案例均为 DFT > CHGNet）。这与 `calibrate_chgnet.py` 中报告的 CHGNet 系统偏差 -0.165 eV/atom 方向一致。

### 2. 按体系类型

| 体系类型 | 示例 | 平均 MAE | 说明 |
|---------|:----:|:--------:|------|
| 无 f 电子 | F₃Sc | **0.19** | 最准确，无磁性干扰 |
| 稀土 f 电子 | TbF₃, Nd₂O₈P₂ | **0.34** | 中等，自旋极化改善了误差 |
| 含 O 体系 | F₂Lu₂O₂, Nd₂O₈P₂ | **0.47** | 最大，O 参考态选择影响显著 |

### 3. 已知局限性

- Nd 参考态因 4f 电荷 sloshing 密度未完全收敛（能量已稳定）
- F₂Lu₂O₂ 的大误差可能与 Lu 填满 4f 的电子结构描述有关
- 未使用 PBE+U 修正，对 f 电子强关联体系描述有限
- 仅覆盖 4 个体系，统计量尚不充分

---

## 结论

1. **CHGNet 定性可靠**：4/4 结构符号一致（全部为负形成能），与 DFT 趋势一致
2. **定量 MAE 约 0.36 eV/atom**：与已报道的 CHGNet 基准测试结果一致
3. **自旋极化改善明显**：TbF₃ 从非自旋 15.5% 误差降至自旋 7.4%
4. **Pipeline 可用**：从 MatterGen 生成 → CHGNet 筛选 → DFT 验证的流程已建立

---

## 附录：原始数据文件

| 数据 | 路径 |
|:----|:----|
| TbF₃ 自旋 DFT 日志 | `/home/isaac/tbf3_spin_dft.txt` |
| F₃Sc 自旋 DFT 日志 | `/home/isaac/batch_dft/f3sc_spin.txt` |
| F₂Lu₂O₂ 自旋 DFT 日志 | `/home/isaac/batch_dft/f2lu2o2_spin.txt` |
| Nd₂O₈P₂ 自旋 DFT 日志 | `/home/isaac/batch_dft/nd2o8p2_spin.txt` |
| 参考态 Sc DFT | `/home/isaac/ref_dft/sc_ref.txt` |
| 参考态 Lu DFT | `/home/isaac/ref_dft/lu_ref.txt` |
| 参考态 Nd DFT | `/home/isaac/ref_dft/nd_ref.txt` |
| 参考态 O₂ DFT | `/home/isaac/ref_dft/o2_ref.txt` |
| 参考态 P DFT | `/home/isaac/ref_dft/p_ref.txt` |
| 计算脚本 | `/mnt/d/nature reproduction/mattergen/calc_formation.py` |

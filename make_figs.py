"""生成论文核心图 (v1) — 从 gap_main.json 定稿数据
图:
  Fig2: 目标 vs 实测带隙散点 (对角参考线, 近金属着色, r/斜率标注)
  Fig3: 按目标档位偏差分布 (箱线 + 达成率标注)
  Fig4: 体系 × 目标档位偏差热图 (含 n)
输出到 mattergen/figures/
用法: python3 make_figs.py
"""
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from collections import defaultdict

# ---- 中文字体 ----
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

ROOT = Path(__file__).resolve().parent
FIG = ROOT / 'figures'
FIG.mkdir(exist_ok=True)

d = json.loads((ROOT / 'gap_main.json').read_text(encoding='utf-8'))
print(f'主统计 n = {len(d)}')

CAT_COLOR = {'氟': '#d62728', '非氟': '#1f77b4', '氧氟': '#ff7f0e'}
CAT_MARK = {'氟': 'o', '非氟': 's', '氧氟': '^'}
CAT_LABEL = {'氟': 'Fluoride', '非氟': 'Non-fluoride', '氧氟': 'Oxyfluoride'}

# ---------------- Fig.2 目标 vs 实测散点 (与 fig6 统一风格) ----------------
import matplotlib.lines as mlines
_rng2 = np.random.default_rng(7)
fig, ax = plt.subplots(figsize=(7.2, 5))
fig.subplots_adjust(right=0.82)
targets = np.array([r['target'] for r in d])
gaps = np.array([r['bandgap_eV'] for r in d])
r_val = np.corrcoef(targets, gaps)[0, 1]
slope, intercept = np.polyfit(targets, gaps, 1)

# 近金属阴影带 (0 ~ 0.2 eV): 41% 落在此区
n_nm = int(np.sum(gaps < 0.2))
ax.axhspan(0, 0.2, color='#bbbbbb', alpha=0.25, zorder=0)
ax.text(2.03, 0.10, f'near-metal band ({100*n_nm/len(d):.0f}%)',
        fontsize=8, color='#555', va='center', zorder=4)

# 只画非金属 (清晰展示 r 相关性 + 负偏差); 目标 x 抖动避免 5 档聚成竖线
jx = _rng2.uniform(-0.05, 0.05, len(d))
for cat in ['氟', '非氟', '氧氟']:
    idx = [i for i, r in enumerate(d) if r['category'] == cat and not r['near_metal']]
    ax.scatter(targets[idx] + jx[idx], gaps[idx],
               marker=CAT_MARK[cat], color=CAT_COLOR[cat],
               s=28, alpha=0.8, zorder=3)

xs = np.linspace(0, 9, 100)
ax.plot(xs, xs, 'k--', lw=1.0, zorder=1)
ax.plot(xs, slope * xs + intercept, color='#444', lw=1.3, zorder=1)
ax.fill_between(xs, xs + 0.5, xs - 0.5, color='gray', alpha=0.05, zorder=0)

handles = []
for cat in ['氟', '非氟', '氧氟']:
    handles.append(mlines.Line2D([], [], marker=CAT_MARK[cat], color=CAT_COLOR[cat],
                                 linestyle='None', markersize=5, label=CAT_LABEL[cat]))
handles.append(mlines.Line2D([], [], color='k', ls='--', label='ideal y=x'))
handles.append(mlines.Line2D([], [], color='#444', label='linear fit'))
ax.legend(handles=handles, loc='center left', bbox_to_anchor=(1.02, 0.5),
          fontsize=8, framealpha=0.95, borderaxespad=0.3)

ax.set_xlabel('Target band gap (eV)', fontsize=11)
ax.set_ylabel('DFT-PBE band gap (eV)', fontsize=11)
ax.set_title(f'Target vs DFT-PBE band gap (n={len(d)}, Pearson r = {r_val:.2f})', fontsize=11)
ax.set_xlim(2.0, 5.0)
ax.set_ylim(-0.5, 9.0)
ax.set_xticks([2.5, 3.0, 3.5, 4.0, 4.5])
ax.grid(alpha=0.3, lw=0.6)
fig.tight_layout()
fig.savefig(FIG / 'fig2_target_vs_gap.png', dpi=300)
plt.close(fig)
print('saved', FIG / 'fig2_target_vs_gap.png')

# ---------------- Fig.3 按目标档位偏差分布 ----------------
fig, ax = plt.subplots(figsize=(7, 5))
bins = sorted(set(r['target'] for r in d))
dev_by = defaultdict(list)
ach_by = {}
for t in bins:
    devs = [r['dev'] for r in d if r['target'] == t]
    dev_by[t] = devs
    ach_by[t] = 100 * sum(1 for x in devs if abs(x) <= 0.5) / len(devs)

data = [dev_by[t] for t in bins]
bp = ax.boxplot(data, patch_artist=True, widths=0.55,
                medianprops=dict(color='k', lw=1.8),
                flierprops=dict(markersize=3, alpha=0.5),
                labels=[f'{t:.1f}' for t in bins])
for patch, cat in zip(bp['boxes'], ['#c9e0f5', '#c9e0f5', '#c9e0f5', '#c9e0f5', '#c9e0f5']):
    patch.set_facecolor(cat)
    patch.set_alpha(0.9)

ax.axhline(0, color='k', lw=0.8, ls='--')
# 达成率标注
for i, t in enumerate(bins):
    ax.text(i + 1, min(dev_by[t]) - 1.0, f'Achievement\n{ach_by[t]:.0f}%',
            ha='center', va='top', fontsize=8.5, color='#333')

ax.set_xlabel('Target band gap (eV)', fontsize=11)
ax.set_ylabel('Deviation (measured \u2212 target, eV)', fontsize=11)
ax.set_title('Deviation by target band gap (systematic negative bias, mean \u22121.59 eV)', fontsize=11)
ax.grid(axis='y', alpha=0.3)
fig.tight_layout()
fig.savefig(FIG / 'fig3_dev_by_target.png', dpi=300)
plt.close(fig)
print('saved', FIG / 'fig3_dev_by_target.png')

# ---------------- Fig.4 体系 × 目标档位偏差热图 ----------------
fig, ax = plt.subplots(figsize=(7, 3.2))
cats = ['氟', '非氟', '氧氟']
mat = np.full((len(cats), len(bins)), np.nan)
cnt = np.full((len(cats), len(bins)), 0, dtype=int)
for ci, c in enumerate(cats):
    for bi, t in enumerate(bins):
        devs = [r['dev'] for r in d if r['category'] == c and r['target'] == t]
        if devs:
            mat[ci, bi] = np.mean(devs)
            cnt[ci, bi] = len(devs)

im = ax.imshow(mat, cmap='RdBu_r', vmin=-4, vmax=4, aspect='auto')
ax.set_xticks(range(len(bins)))
ax.set_xticklabels([f'{t:.1f}' for t in bins])
ax.set_yticks(range(len(cats)))
ax.set_yticklabels([CAT_LABEL[c] for c in cats])
# 格内标注 均值 + n
for ci in range(len(cats)):
    for bi in range(len(bins)):
        if np.isnan(mat[ci, bi]):
            ax.text(bi, ci, '\u2014', ha='center', va='center', color='gray', fontsize=10)
        else:
            ax.text(bi, ci, f'{mat[ci, bi]:+.1f}\n(n={cnt[ci, bi]})',
                    ha='center', va='center', fontsize=8.5,
                    color='white' if abs(mat[ci, bi]) > 1.5 else 'black')
ax.set_xlabel('Target band gap (eV)', fontsize=11)
ax.set_title('System \u00d7 target: mean deviation (eV)', fontsize=11)
fig.colorbar(im, ax=ax, shrink=0.85, label='Mean deviation (eV)')
fig.tight_layout()
fig.savefig(FIG / 'fig4_heatmap.png', dpi=300)
plt.close(fig)
print('saved', FIG / 'fig4_heatmap.png')

# ================= Fig.1 流水线示意图 =================
fig, ax = plt.subplots(figsize=(9, 3.4))
ax.axis('off')
steps = [
    ('MatterGen sampling', 'dft_band_gap adapter\nguidance 2.0, N=1000\n148 candidates'),
    ('CHGNet screening', 'relax fmax<0.05\nformation-energy filter\n65-element references'),
    ('DFT-PBE validation', 'GPAW 400eV/4x4x4\nHOMO-LUMO gap\nmain stat. 141/148'),
    ('Attribution checks', 'k-point conv. <2%\nband-gap def. ~0.11 eV\nstruct. approx. <0.1 eV'),
]
n = len(steps)
for i, (title, sub) in enumerate(steps):
    x = i / (n - 1) * 0.85 + 0.08
    ax.add_patch(plt.Rectangle((x - 0.105, 0.18), 0.21, 0.62,
                               facecolor='#eef3fa', edgecolor='#4a6fa5',
                               lw=1.6, zorder=3))
    ax.text(x, 0.66, title, ha='center', va='center', fontsize=11.5, fontweight='bold',
            zorder=4)
    ax.text(x, 0.35, sub, ha='center', va='center', fontsize=8.5, color='#333',
            zorder=4)
    if i < n - 1:
        ax.annotate('', xy=(x + 0.115, 0.49), xytext=(x + 0.105, 0.49),
                    arrowprops=dict(arrowstyle='->', color='#888', lw=1.8))
ax.text(0.5, 0.06, 'Target gaps 2.5-4.5 eV (5 bins) -> 148 conditioned candidates -> 141 valid gaps (95.3%)',
        ha='center', va='center', fontsize=9.5, color='#555')
ax.set_title('Research pipeline', fontsize=13, pad=12)
fig.tight_layout()
fig.savefig(FIG / 'fig1_pipeline.png', dpi=300)
plt.close(fig)
print('saved', FIG / 'fig1_pipeline.png')

# ================= Fig.5 随机抽样负对照 =================
fig, ax = plt.subplots(figsize=(7.2, 5))
fig.subplots_adjust(right=0.82)
names = ['C$_2$N$_2$', 'O$_5$', 'C$_2$Li$_6$N$_4$', 'F$_2$O$_2$', 'Hg$_2$O$_8$S$_2$', 'Cl$_3$LiPb']
chg = [0.189, 0.180, -0.688, -0.378, -1.775, -1.727]
dft = [0.403, 0.173, -0.388, -0.152, -1.270, -1.403]
x = np.arange(len(names))
w = 0.38
ax.bar(x - w/2, chg, w, label='CHGNet', color='#8fbfd9', edgecolor='k', lw=0.6)
ax.bar(x + w/2, dft, w, label='DFT-PBE', color='#d9a08f', edgecolor='k', lw=0.6)
for i in range(len(names)):
    ax.text(x[i], max(chg[i], dft[i]) + 0.05, 'v' if (chg[i] > 0) == (dft[i] > 0) else '?',
            ha='center', fontsize=12, color='#2e7d32')
ax.axhline(0, color='k', lw=0.8)
ax.set_xticks(x)
ax.set_xticklabels(names, fontsize=10)
ax.set_ylabel('Formation energy (eV/atom)', fontsize=11)
ax.set_title('Random sampling: CHGNet vs DFT formation energies (6/6 sign-consistent, MAE 0.26)', fontsize=11)
ax.legend(fontsize=9, loc='center left', bbox_to_anchor=(1.02, 0.5), borderaxespad=0.3)
ax.grid(axis='y', alpha=0.3)
fig.tight_layout()
fig.savefig(FIG / 'fig5_random_validation.png', dpi=300)
plt.close(fig)
print('saved', FIG / 'fig5_random_validation.png')

# ================= Fig.6 形成能 - 带隙关联 =================
fig, ax = plt.subplots(figsize=(7.2, 5))
fig.subplots_adjust(right=0.82)
eff = np.array([r['energy_per_atom'] for r in d])
g6 = np.array([r['bandgap_eV'] for r in d])
for cat in ['氟', '非氟', '氧氟']:
    idx = [i for i, r in enumerate(d) if r['category'] == cat]
    ax.scatter(eff[idx], g6[idx], marker=CAT_MARK[cat], color=CAT_COLOR[cat],
               s=28, alpha=0.8, label=CAT_LABEL[cat], zorder=3)
ax.axhline(0.2, color='gray', ls='--', lw=1, label='near-metal threshold 0.2 eV')
ax.set_xlabel('DFT total energy / atom (eV/atom)', fontsize=11)
ax.set_ylabel('Band gap (eV)', fontsize=11)
ax.set_title(f'Total energy vs measured band gap (n={len(d)})', fontsize=11)
ax.legend(fontsize=8.5, loc='center left', bbox_to_anchor=(1.02, 0.5), borderaxespad=0.3)
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(FIG / 'fig6_energy_vs_gap.png', dpi=300)
plt.close(fig)
print('saved', FIG / 'fig6_energy_vs_gap.png')

print('全部完成')

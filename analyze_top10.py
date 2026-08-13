"""
Top 10 候选 DFT 适用性分析
评分体系:
  - 形成能 (越低越好)
  - 元素复杂度 (越简单越好)
  - f 电子 (无 f 电子越好)
  - DFT 收敛难度 (越易越好)
  - 与已有验证体系的差异性 (越不同越好)
"""
import json

# 读取数据
data = json.load(open("screening_extended_result.json"))

# 有未配对 f 电子的元素 (La 4f⁰ 和 Lu 4f¹⁴ 无未配对 f 电子, 不引起磁性/收敛困难)
F_ELECTRON_ELEMENTS = {
    'Ce','Pr','Nd','Pm','Sm','Eu','Gd','Tb','Dy','Ho','Er','Tm','Yb',
    'Ac','Th','Pa','U','Np','Pu','Am','Cm','Bk','Cf'
}

# 已有 5 个验证体系的元素集合 (用于相似性比较)
VALIDATED_SYSTEMS = [
    {'Tb','F'},          # TbF3
    {'Sc','F'},          # ScF3
    {'Lu','F','O'},      # F2Lu2O2
    {'Nd','O','P'},      # Nd2O8P2
    {'Ho','Rb','F'},     # F6HoRb3
]

def score_candidate(r):
    """返回各项评分和详情"""
    elements = set(r['elements'].keys())
    n_atoms = r['n_atoms']
    ef = r['formation_energy']
    
    # 1. 形成能评分 (0-5): -6.33~-3.86, 越低分越高
    ef_score = min(5, max(0, (ef + 7) / 1.5))
    
    # 2. 元素复杂度 (0-5): 元素种类越少分越高
    n_elements = len(elements)
    complexity_score = max(0, 5 - (n_elements - 1) * 1.5)
    
    # 3. f 电子 (0-5): 无 f 电子 = 5分
    has_f = bool(elements & F_ELECTRON_ELEMENTS)
    f_elements = sorted(elements & F_ELECTRON_ELEMENTS)
    f_score = 0 if has_f else 5
    
    # 4. DFT 收敛难度预测 (0-5): 综合评估
    difficulty = 5  # 默认易
    if has_f:
        difficulty -= 3.5  # f 电子 -3.5
    if n_atoms > 12:
        difficulty -= 1.0  # 大晶胞 -1
    elif n_atoms > 8:
        difficulty -= 0.5
    # 过渡金属 (非 f) 轻微增加难度
    tm = elements & {'Sc','Ti','V','Cr','Mn','Fe','Co','Ni','Cu','Zn',
                     'Y','Zr','Nb','Mo','Tc','Ru','Rh','Pd','Ag','Cd',
                     'Hf','Ta','W','Re','Os','Ir','Pt','Au','Hg'}
    if tm:
        difficulty -= 0.5
    difficulty_score = max(0, difficulty)
    
    # 5. 与已有验证体系差异性 (0-5)
    # 计算元素集合与已有体系的最大相似度
    max_overlap = 0
    for vsys in VALIDATED_SYSTEMS:
        overlap = len(elements & vsys) / len(elements | vsys)
        max_overlap = max(max_overlap, overlap)
    novelty_score = (1 - max_overlap) * 5
    
    # 加权总分 (形成能30%, 收敛30%, 无f电子20%, 新颖性20%, 复杂度扣分)
    total = (ef_score * 0.25 + difficulty_score * 0.30 + f_score * 0.20
             + novelty_score * 0.25)
    
    return {
        'formula': r['formula'],
        'n_atoms': n_atoms,
        'ef': ef,
        'elements': elements,
        'has_f': has_f,
        'f_elements': f_elements,
        'ef_score': ef_score,
        'complexity_score': complexity_score,
        'f_score': f_score,
        'difficulty_score': difficulty_score,
        'novelty_score': novelty_score,
        'total': total,
    }

# 分析 Top 10
print("=" * 80)
print(" Top 10 候选 DFT 适用性分析")
print("=" * 80)

results = [score_candidate(r) for r in data['top_candidates']]
results.sort(key=lambda x: -x['total'])

print(f"\n{'排名':<4} {'化学式':<14} {'原子':>3} {'Ef':>7} {'f电子':>8} {'形成能':>5} {'收敛':>5} {'新颖':>5} {'总分':>6} {'等级':>4}")
print("-" * 80)
for rank, s in enumerate(results, 1):
    # 等级判定
    if s['has_f'] or s['n_atoms'] > 18:
        grade = 'C'
    elif s['total'] >= 3.2:
        grade = 'A'
    else:
        grade = 'B'
    f_el = '+'.join(s['f_elements']) if s['has_f'] else '无'
    print(f"{rank:<4} {s['formula']:<14} {s['n_atoms']:>3} {s['ef']:>7.2f} {f_el:>8} "
          f"{s['ef_score']:>5.1f} {s['difficulty_score']:>5.1f} {s['novelty_score']:>5.1f} "
          f"{s['total']:>6.2f} {grade:>4}")

print()
print("=" * 80)
print(" 详细评估")
print("=" * 80)
for rank, s in enumerate(results, 1):
    print(f"\n[{rank}] {s['formula']} ({s['n_atoms']} 原子, Ef={s['ef']:.2f})")
    print(f"    元素: {', '.join(sorted(s['elements']))}")
    print(f"    f电子: {'有 (' + '+'.join(s['f_elements']) + ')' if s['has_f'] else '无'}  → DFT收敛{'困难' if s['has_f'] else '容易'}")
    print(f"    推荐等级: {('C - 含f电子,DFT难' if s['has_f'] or s['n_atoms']>18 else 'A - 首选' if s['total']>=3.2 else 'B - 次选')}")

print()
print("=" * 80)
print(" 最终推荐 5 个 (A/B 级, 无 f 电子优先)")
print("=" * 80)
count = 0
for s in results:
    if count >= 5:
        break
    if not s['has_f'] and s['n_atoms'] <= 16:
        count += 1
        print(f"  {count}. {s['formula']:<14} {s['n_atoms']:>3}原子 Ef={s['ef']:.3f} 总分={s['total']:.2f}")

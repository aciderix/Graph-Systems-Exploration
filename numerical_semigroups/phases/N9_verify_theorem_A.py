import json
import sys

# Load pre-computed data
with open('/agent/home/Graph-Systems-Exploration/numerical_semigroups/data/n1_results_g20.json') as f:
    data = json.load(f)

print(f"Dataset: {len(data)} semigroupes")
print("="*70)

# Helper: compute Apéry set properties
def analyze_semigroup(sg):
    m = sg['multiplicity']
    e = sg['embedding_dimension']
    d = m - e
    gens = sg['generators']
    
    # Build Apéry set
    # Apéry(S, m) = {w_0=0, w_1, ..., w_{m-1}} where w_i is smallest element ≡ i (mod m) in S
    # Build semigroup up to sufficient bound
    F = sg.get('frobenius', None)
    if F is None:
        return None
    
    c = F + 1
    
    # Build S up to F + m
    limit = F + m + 1
    in_S = [False] * (limit + 1)
    in_S[0] = True
    for x in range(1, limit + 1):
        for g in gens:
            if x >= g and in_S[x - g]:
                in_S[x] = True
                break
    
    # Apéry set
    apery = [0] * m
    for r in range(1, m):
        x = r
        while x <= limit and not in_S[x]:
            x += m
        if x > limit:
            return None  # shouldn't happen
        apery[r] = x
    
    # Kunz levels
    kunz = [apery[r] // m for r in range(m)]  # kunz[0] = 0
    
    k_star = max(kunz[1:])
    r_star = max(r for r in range(1, m) if kunz[r] == k_star)
    
    # L = number of elements in [0, F]
    L = sum(1 for x in range(F + 1) if in_S[x])
    
    # Decomposable residues
    decomposable = set()
    for a in range(1, m):
        for b in range(a, m):
            r = (a + b) % m
            if r == 0:
                continue
            eps = 1 if a + b >= m else 0
            if kunz[a] + kunz[b] + eps == kunz[r]:
                decomposable.add(r)
    
    d_computed = len(decomposable)
    
    W = e * L - c
    
    return {
        'm': m, 'e': e, 'd': d, 'd_computed': d_computed,
        'c': c, 'F': F, 'L': L, 'W': W,
        'k_star': k_star, 'r_star': r_star,
        'kunz': kunz[1:],  # non-zero residues
        'decomposable': decomposable
    }

# Filter d=1 semigroups and analyze
results = []
errors = 0
for sg in data:
    m = sg['multiplicity']
    e = sg['embedding_dimension']
    if m - e != 1:
        continue
    info = analyze_semigroup(sg)
    if info is None:
        errors += 1
        continue
    if info['d_computed'] != 1:
        continue
    results.append(info)

print(f"d=1 semigroupes analysés: {len(results)} (erreurs: {errors})")
print()

# ============================================================
# VERIFICATION 1: W ≥ m-3 for ALL d=1
# ============================================================
print("="*70)
print("VERIFICATION 1: W ≥ m-3 pour TOUT d=1")
print("="*70)
violations_1 = [r for r in results if r['W'] < r['m'] - 3]
print(f"  Violations: {len(violations_1)}")
if violations_1:
    for v in violations_1[:5]:
        print(f"    m={v['m']} W={v['W']} m-3={v['m']-3} L={v['L']} k*={v['k_star']}")
else:
    print("  ✅ CONFIRMÉ: W ≥ m-3 pour tout d=1")
print()

# ============================================================
# VERIFICATION 2: k*=4, L=5 impossible for d=1
# ============================================================
print("="*70)
print("VERIFICATION 2: k*=4, L=5 impossible pour d=1")
print("="*70)
cases_k4_L5 = [r for r in results if r['k_star'] == 4 and r['L'] == 5]
print(f"  Cas k*=4, L=5: {len(cases_k4_L5)}")
if len(cases_k4_L5) == 0:
    print("  ✅ CONFIRMÉ: 0 cas")
print()

# ============================================================
# VERIFICATION 3: Pair Contribution Lemma
# For d=1, decomposable r_d uses pair (a,b).
# Contribution of a and b to L is ≥ k*-2.
# ============================================================
print("="*70)
print("VERIFICATION 3: Lemme de Contribution de Paire (δ_a + δ_b ≥ k*-2)")
print("="*70)

lemma_violations = 0
lemma_checked = 0

for r in results:
    m = r['m']
    k_star = r['k_star']
    r_star = r['r_star']
    kunz = [0] + r['kunz']  # kunz[0]=0, kunz[1..m-1]
    
    if k_star < 5:
        continue
    
    # Find decomposing pair for r_d
    for r_d in r['decomposable']:
        best_contribution = -1
        for a in range(1, m):
            for b in range(a, m):
                rr = (a + b) % m
                if rr != r_d:
                    continue
                eps = 1 if a + b >= m else 0
                if kunz[a] + kunz[b] + eps != kunz[r_d]:
                    continue
                # This is a valid decomposing pair
                # Compute contributions
                if a <= r_star:
                    delta_a = k_star - kunz[a]
                else:
                    delta_a = max(0, k_star - 1 - kunz[a])
                
                if b <= r_star:
                    delta_b = k_star - kunz[b]
                else:
                    delta_b = max(0, k_star - 1 - kunz[b])
                
                contribution = delta_a + delta_b
                best_contribution = max(best_contribution, contribution)
        
        lemma_checked += 1
        if best_contribution < k_star - 2:
            lemma_violations += 1
            if lemma_violations <= 5:
                print(f"  ❌ m={m} k*={k_star} r_d={r_d} best_contrib={best_contribution} need≥{k_star-2}")
                print(f"     kunz={kunz[1:]}")

print(f"  Vérifiés: {lemma_checked}, Violations: {lemma_violations}")
if lemma_violations == 0:
    print("  ✅ CONFIRMÉ: δ_a + δ_b ≥ k*-2 pour tout d=1 avec k*≥5")
print()

# ============================================================
# VERIFICATION 4: L ≥ 2k*-2 for k*≥5, d=1
# ============================================================
print("="*70)
print("VERIFICATION 4: L ≥ 2k*-2 pour k*≥5, d=1")
print("="*70)
cases_k5 = [r for r in results if r['k_star'] >= 5]
violations_4 = [r for r in cases_k5 if r['L'] < 2*r['k_star'] - 2]
print(f"  Cas k*≥5: {len(cases_k5)}")
print(f"  Violations L < 2k*-2: {len(violations_4)}")
if violations_4:
    for v in violations_4[:5]:
        print(f"    m={v['m']} k*={v['k_star']} L={v['L']} 2k*-2={2*v['k_star']-2}")
else:
    print("  ✅ CONFIRMÉ: L ≥ 2k*-2")
print()

# ============================================================
# VERIFICATION 5: r* ≤ m-2 for k*=3, L=4, d=1
# ============================================================
print("="*70)
print("VERIFICATION 5: r* ≤ m-2 pour k*=3, L=4, d=1")
print("="*70)
cases_k3_L4 = [r for r in results if r['k_star'] == 3 and r['L'] == 4]
violations_5 = [r for r in cases_k3_L4 if r['r_star'] >= r['m'] - 1]
print(f"  Cas k*=3, L=4: {len(cases_k3_L4)}")
print(f"  Cas avec r*=m-1: {len(violations_5)}")
if len(violations_5) == 0:
    print("  ✅ CONFIRMÉ: r* ≤ m-2")
print()

# ============================================================
# VERIFICATION 6: W ≥ m-3 by sub-case for L≥5
# ============================================================
print("="*70)
print("VERIFICATION 6: Breakdown par sous-cas pour L≥5, d=1")
print("="*70)
L5 = [r for r in results if r['L'] >= 5]
print(f"  Total d=1, L≥5: {len(L5)}")

for label, subset in [
    ("m=3 (Sylvester)", [r for r in L5 if r['m'] == 3]),
    ("m≥4, k*≤3", [r for r in L5 if r['m'] >= 4 and r['k_star'] <= 3]),
    ("m≥4, k*=4, L≥6", [r for r in L5 if r['m'] >= 4 and r['k_star'] == 4 and r['L'] >= 6]),
    ("m≥4, k*≥5", [r for r in L5 if r['m'] >= 4 and r['k_star'] >= 5]),
]:
    n = len(subset)
    if n == 0:
        print(f"  {label}: 0 cas")
        continue
    viol = [r for r in subset if r['W'] < r['m'] - 3]
    W_min = min(r['W'] for r in subset)
    m_min_bound = min(r['m'] - 3 for r in subset)
    print(f"  {label}: {n} cas, W_min={W_min}, (m-3)_max={max(r['m']-3 for r in subset)}, violations={len(viol)}")
print()

# ============================================================
# SUMMARY
# ============================================================
print("="*70)
print("RÉSUMÉ FINAL")
print("="*70)
all_d1 = results
W_violations = [r for r in all_d1 if r['W'] < r['m'] - 3]
print(f"Total d=1: {len(all_d1)}")
print(f"Violations W < m-3: {len(W_violations)}")
if len(W_violations) == 0:
    print("🏆 THÉORÈME A VÉRIFIÉ: W ≥ m-3 pour tout d=1, sur l'ensemble du dataset.")

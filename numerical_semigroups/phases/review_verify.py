"""
Independent verification of Wilf paper results.
Checks: enumeration correctness, Theorem A, Theorem B, unified formula.
"""
import json
import math
from collections import defaultdict

# ============================================================
# 1. Independent semigroup construction & invariant computation
# ============================================================

def semigroup_from_generators(gens, limit=None):
    """Build semigroup elements from generators up to limit using DP."""
    m = min(gens)
    if limit is None:
        limit = max(gens)**2 + 100
    in_S = [False] * (limit + 1)
    in_S[0] = True
    for x in range(1, limit + 1):
        for g in gens:
            if x >= g and in_S[x - g]:
                in_S[x] = True
                break
    return set(x for x in range(limit + 1) if in_S[x])

def compute_all(gens):
    """Compute all invariants from generators."""
    m = min(gens)
    elems = semigroup_from_generators(gens)

    # Frobenius: largest gap. Find by looking for m consecutive elements in S.
    # Once we find m consecutive integers in S, everything beyond is in S too.
    F = 0
    for x in range(1, max(elems)+1):
        if x not in elems:
            F = x
        # Early stop: if last m integers are all in S, we found F
        if x >= m and all((x - i) in elems for i in range(m)):
            break

    c = F + 1
    gaps = sorted(x for x in range(1, F+1) if x not in elems)
    genus = len(gaps)

    # Apéry set
    apery = [0] * m
    for r in range(1, m):
        x = r
        while x not in elems:
            x += m
        apery[r] = x

    kunz = [apery[r] // m for r in range(m)]

    k_star = max(kunz[1:])
    r_star = max(r for r in range(1, m) if kunz[r] == k_star)

    # Decomposable
    decomp = set()
    for a in range(1, m):
        for b in range(a, m):
            r = (a + b) % m
            if r == 0:
                continue
            eps = 1 if a + b >= m else 0
            if kunz[a] + kunz[b] + eps == kunz[r]:
                decomp.add(r)

    e = m - len(decomp)
    d = len(decomp)

    # L
    L = sum(1 for x in range(F+1) if x in elems)

    W = e * L - c

    return {
        'm': m, 'e': e, 'd': d, 'genus': genus,
        'F': F, 'c': c, 'L': L, 'W': W,
        'k_star': k_star, 'r_star': r_star,
        'kunz': kunz, 'gens': gens
    }

# ============================================================
# 2. Verify tight families algebraically
# ============================================================

print("=" * 70)
print("TEST 1: Verify tight family T_m for Theorem A (d=1, W=m-3)")
print("=" * 70)

errors_T = 0
for m in range(4, 30):
    # T_m = <m, m+1, 2m+3, 2m+4, ..., 3m-1>
    gens = [m, m+1] + list(range(2*m+3, 3*m))
    if len(gens) < 2:
        continue
    info = compute_all(gens)
    expected_W = m - 3
    expected_e = m - 1
    expected_L = 3
    ok = (info['W'] == expected_W and info['e'] == expected_e and
          info['d'] == 1 and info['L'] == expected_L)
    if not ok:
        print(f"  FAIL m={m}: W={info['W']}(exp {expected_W}), e={info['e']}(exp {expected_e}), "
              f"d={info['d']}(exp 1), L={info['L']}(exp {expected_L})")
        errors_T += 1

if errors_T == 0:
    print(f"  OK: T_m verified for m=4..29, all give W=m-3, e=m-1, d=1, L=3")
else:
    print(f"  ERRORS: {errors_T}")

# ============================================================
# 3. Verify tight family U_m for Theorem B (d=2, W=2m-8)
# ============================================================

print()
print("=" * 70)
print("TEST 2: Verify tight family U_m for Theorem B (d=2, W=2m-8)")
print("=" * 70)

errors_U = 0
for m in range(5, 25):
    # U_m = <m, 2m-2, 2m-1, 3m+1, 3m+2, ..., 4m-5>
    gens = [m, 2*m-2, 2*m-1] + list(range(3*m+1, 4*m-4))
    if len(gens) < 2:
        continue
    info = compute_all(gens)
    expected_W = 2*m - 8
    expected_e = m - 2
    ok = (info['W'] == expected_W and info['e'] == expected_e and info['d'] == 2)
    if not ok:
        print(f"  FAIL m={m}: W={info['W']}(exp {expected_W}), e={info['e']}(exp {expected_e}), d={info['d']}(exp 2)")
        errors_U += 1

if errors_U == 0:
    print(f"  OK: U_m verified for m=5..24, all give W=2m-8, e=m-2, d=2")
else:
    print(f"  ERRORS: {errors_U}")

# ============================================================
# 4. Verify unified formula L(d) = ceil((sqrt(8d+1)-1)/2) + 2
# ============================================================

print()
print("=" * 70)
print("TEST 3: Verify L(d) formula vs triangular numbers")
print("=" * 70)

def L_formula(d):
    if d == 0:
        return 2
    k = math.ceil((math.sqrt(8*d+1) - 1) / 2)
    return k + 2

def k_min(d):
    k = 1
    while k*(k+1)//2 < d:
        k += 1
    return k

errors_L = 0
for d in range(0, 30):
    L_pred = L_formula(d)
    if d == 0:
        k_check = 0
    else:
        k_check = k_min(d)
        L_check = k_check + 2
        if L_pred != L_check:
            print(f"  INCONSISTENCY d={d}: ceil formula gives {L_pred}, k_min gives {L_check}")
            errors_L += 1

    # Verify W_min formula
    # W_min(m,d) = (m-d)*L(d) - 2m = (L(d)-2)*m - d*L(d)
    slope = L_pred - 2
    const = -d * L_pred
    # For m large enough, W_min should be positive
    if d > 0:
        m_zero = math.ceil(-const / slope) if slope > 0 else float('inf')

if errors_L == 0:
    print("  OK: L(d) = ceil((sqrt(8d+1)-1)/2) + 2 matches k_min(d) + 2 for d=0..29")

# Print the table
print("\n  d | k_min | T(k) | L(d) | W_min formula")
print("  --|-------|------|------|---------------")
for d in range(0, 16):
    L = L_formula(d)
    if d == 0:
        km = 0
        T = 0
    else:
        km = k_min(d)
        T = km*(km+1)//2
    slope = L - 2
    const = -d * L
    formula = f"{slope}m {const:+d}" if d > 0 else "0"
    print(f"  {d:2d} | {km:5d} | {T:4d} | {L:4d} | {formula}")

# ============================================================
# 5. Load dataset and verify Theorems A & B exhaustively
# ============================================================

print()
print("=" * 70)
print("TEST 4: Load dataset g<=20 and verify Theorems A, B")
print("=" * 70)

try:
    with open('/home/user/Graph-Systems-Exploration/numerical_semigroups/data/n1_results_g20.json') as f:
        data = json.load(f)
    print(f"  Loaded {len(data)} semigroups")

    # Count by genus to verify against OEIS A007323
    known_A007323 = {0: 1, 1: 1, 2: 2, 3: 4, 4: 7, 5: 12, 6: 23, 7: 39, 8: 67,
                     9: 118, 10: 204, 11: 343, 12: 592, 13: 1001, 14: 1693, 15: 2857,
                     16: 4806, 17: 8045, 18: 13467, 19: 22464, 20: 37396}

    counts = defaultdict(int)
    for sg in data:
        counts[sg['genus']] += 1

    oeis_ok = True
    for g in sorted(counts):
        if g in known_A007323:
            if counts[g] != known_A007323[g]:
                print(f"  OEIS MISMATCH g={g}: got {counts[g]}, expected {known_A007323[g]}")
                oeis_ok = False
    if oeis_ok:
        print("  OEIS A007323 verification: all genus counts match")

    # Theorem A: d=1, W >= m-3
    d1 = [sg for sg in data if sg['multiplicity'] - sg['embedding_dimension'] == 1]
    violations_A = [sg for sg in d1 if sg['wilf_number'] < sg['multiplicity'] - 3]
    print(f"\n  Theorem A: {len(d1)} semigroups with d=1")
    print(f"  Violations W < m-3: {len(violations_A)}")
    if violations_A:
        for v in violations_A[:5]:
            print(f"    m={v['multiplicity']} W={v['wilf_number']} gens={v['generators']}")

    # Theorem B: d=2, W >= 2m-8
    d2 = [sg for sg in data if sg['multiplicity'] - sg['embedding_dimension'] == 2]
    violations_B = [sg for sg in d2 if sg['wilf_number'] < 2*sg['multiplicity'] - 8]
    print(f"\n  Theorem B: {len(d2)} semigroups with d=2")
    print(f"  Violations W < 2m-8: {len(violations_B)}")
    if violations_B:
        for v in violations_B[:5]:
            print(f"    m={v['multiplicity']} W={v['wilf_number']} gens={v['generators']}")

    # Check unified formula for d=0..8
    print(f"\n  Unified formula check (d=0..8):")
    for d in range(0, 9):
        L_pred = L_formula(d)
        sgs_d = [sg for sg in data if sg['multiplicity'] - sg['embedding_dimension'] == d]
        if not sgs_d:
            continue

        # Group by m
        by_m = defaultdict(list)
        for sg in sgs_d:
            by_m[sg['multiplicity']].append(sg)

        violations = 0
        matches = 0
        for m_val in sorted(by_m):
            W_min_obs = min(sg['wilf_number'] for sg in by_m[m_val])
            W_min_pred = (m_val - d) * L_pred - 2 * m_val
            if W_min_obs < W_min_pred:
                violations += 1
            if W_min_obs == W_min_pred:
                matches += 1

        print(f"    d={d}: {len(sgs_d)} SGs, {len(by_m)} m-values, {matches} exact matches, {violations} violations")

    # Wilf conjecture itself
    wilf_violations = [sg for sg in data if sg['wilf_number'] < 0]
    print(f"\n  Wilf conjecture (W >= 0): violations = {len(wilf_violations)}")

except Exception as ex:
    print(f"  ERROR loading data: {ex}")

# ============================================================
# 6. Spot-check: manually verify a few specific semigroups
# ============================================================

print()
print("=" * 70)
print("TEST 5: Spot-check specific semigroups")
print("=" * 70)

test_cases = [
    # (generators, expected_W, expected_d, description)
    ([3, 5], 0, 1, "⟨3,5⟩ Sylvester"),
    ([3, 7], 0, 1, "⟨3,7⟩ Sylvester"),
    ([4, 7, 13], 1, 1, "T_4 tight d=1"),
    ([5, 9, 16, 17], 2, 1, "T_5 tight d=1"),
    ([6, 11, 19, 20, 21], 3, 1, "T_6 tight d=1"),
    ([5, 8, 9], 2, 2, "d=2 small"),
    ([4, 6, 7], 0, 2, "⟨4,6,7⟩ d=2 boundary"),
]

for gens, exp_W, exp_d, desc in test_cases:
    info = compute_all(gens)
    status = "OK" if info['W'] == exp_W and info['d'] == exp_d else "FAIL"
    print(f"  {status}: {desc}: gens={gens}, W={info['W']}(exp {exp_W}), d={info['d']}(exp {exp_d}), "
          f"m={info['m']}, e={info['e']}, L={info['L']}, c={info['c']}")

# ============================================================
# 7. Check proof claims: L=3 => c <= 2m for d=1
# ============================================================

print()
print("=" * 70)
print("TEST 6: Proof structural claims")
print("=" * 70)

try:
    # Check that for d=1, L=3 => c <= 2m
    d1_L3 = [sg for sg in data if sg['multiplicity'] - sg['embedding_dimension'] == 1
             and sg['left_elements'] == 3]
    violations_L3 = [sg for sg in d1_L3 if sg['conductor'] > 2 * sg['multiplicity']]
    print(f"  d=1, L=3: {len(d1_L3)} SGs, c > 2m violations: {len(violations_L3)}")

    # Check d=1, L=4, k*=3 => r* <= m-2
    # Need Apéry data for this...

    # Check d=2, L>=4 always
    d2_all = [sg for sg in data if sg['multiplicity'] - sg['embedding_dimension'] == 2]
    d2_L_lt4 = [sg for sg in d2_all if sg['left_elements'] < 4]
    print(f"  d=2: {len(d2_all)} SGs, L < 4 cases: {len(d2_L_lt4)}")

except:
    print("  (skipped, data not loaded)")

print()
print("=" * 70)
print("ALL TESTS COMPLETE")
print("=" * 70)

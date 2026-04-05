"""
N3b: What determines branching factor? Characterize leaves (bf=0).

bf = number of minimal generators x > F(S)
Generators > F live in {F+1, ..., 2F+1} (since x >= 2F+2 always decomposable)
x > F is a generator iff for all a in S, a > 0: x - a is a gap

So bf depends on the "additive structure" of S near F.
"""
import numpy as np
import json
from collections import defaultdict

def enumerate_with_bf(max_genus):
    """Enumerate all semigroups up to max_genus, compute invariants + branching factor."""
    
    results = []  # list of dicts
    
    # BFS: each node = (gap_set as frozenset, F, m)
    current_level = [(frozenset(), -1, 1)]  # genus 0: N
    
    for g in range(max_genus + 1):
        next_level = []
        
        for gap_fs, F, m in current_level:
            gap_set = set(gap_fs)
            
            # Compute Apery set
            if F < 0:
                apery = list(range(m))  # trivial
                gens = [1]
            else:
                apery = [0] * m
                for r in range(1, m):
                    x = r
                    while x in gap_set:
                        x += m
                    apery[r] = x
                
                # Compute generators from Apery set
                gens = [m]
                for r in range(1, m):
                    a = apery[r]
                    is_sum = False
                    for r1 in range(1, m):
                        r2 = (r - r1) % m
                        if r1 == r:
                            continue
                        if r2 == 0:
                            # a = apery[r1] + k*m, check if k >= 1
                            if apery[r1] < a and (a - apery[r1]) % m == 0:
                                is_sum = True
                                break
                        elif apery[r1] + apery[r2] == a:
                            is_sum = True
                            break
                    if not is_sum:
                        gens.append(a)
                gens = sorted(gens)
            
            # Branching factor: generators > F
            gens_above_F = [x for x in gens if x > F]
            bf = len(gens_above_F)
            
            # Compute invariants
            e = len(gens)  # embedding dimension
            conductor = F + 1 if F >= 0 else 0
            t = 0  # type = number of pseudo-Frobenius numbers
            if F >= 0:
                pf_numbers = []
                for gap in sorted(gap_set, reverse=True):
                    # gap is pseudo-Frobenius if gap + s in S for all s in S, s > 0
                    # Equivalent: gap + m in S (since m is the smallest positive element)
                    # AND gap + every generator in S
                    is_pf = True
                    for gen in gens:
                        if (gap + gen) in gap_set:
                            is_pf = False
                            break
                    if is_pf:
                        pf_numbers.append(gap)
                t = len(pf_numbers)
            
            is_symmetric = (t == 1) if F >= 0 else True
            
            # Left elements: elements of S in [0, F]
            L = (F + 1 - g) if F >= 0 else 1
            
            # Wilf number
            W = e * L - conductor if F >= 0 else 0
            
            # Ratio and depth
            ratio = -(-F // m) if F >= 0 and m > 0 else 0  # ceil(F/m)
            
            # Density of gaps in [1, F]
            gap_density = g / F if F > 0 else 0
            
            # Store
            if g > 0:  # skip trivial genus 0
                results.append({
                    'genus': g,
                    'frobenius': F,
                    'multiplicity': m,
                    'embedding_dim': e,
                    'type': t,
                    'conductor': conductor,
                    'left_elements': L,
                    'wilf_number': W,
                    'ratio': ratio,
                    'is_symmetric': is_symmetric,
                    'gap_density': gap_density,
                    'bf': bf,
                    'gens_above_F': len(gens_above_F),
                    'gens_below_F': e - bf,
                    'bf_ratio': bf / e if e > 0 else 0,
                    'max_gen': max(gens) if gens else 0,
                    'gen_span': max(gens) - min(gens) if len(gens) > 1 else 0,
                })
            
            # Generate children
            if g < max_genus:
                for x in gens_above_F:
                    new_gaps = gap_set | {x}
                    new_F = x
                    if x == m:
                        new_m = min(y for y in range(1, new_F + 2) if y not in new_gaps)
                    else:
                        new_m = m
                    next_level.append((frozenset(new_gaps), new_F, new_m))
        
        print(f"g={g}: {len(current_level)} semigroups processed")
        current_level = next_level
    
    return results

# Enumerate up to genus 15
print("=== ENUMERATION WITH BRANCHING FACTOR ===\n")
data = enumerate_with_bf(15)
print(f"\nTotal: {len(data)} semigroups (genus 1-15)\n")

# Convert to numpy for analysis
fields = ['genus', 'frobenius', 'multiplicity', 'embedding_dim', 'type', 
          'conductor', 'left_elements', 'wilf_number', 'ratio', 'gap_density', 
          'bf', 'gens_above_F', 'gens_below_F', 'bf_ratio', 'max_gen', 'gen_span']
bool_fields = ['is_symmetric']

arr = {f: np.array([d[f] for d in data], dtype=float) for f in fields}
arr['is_symmetric'] = np.array([d['is_symmetric'] for d in data], dtype=float)

# 1. CORRELATION: bf vs each invariant
print("=== CORRELATION: bf vs invariants ===")
bf = arr['bf']
for f in fields:
    if f == 'bf':
        continue
    mask = np.isfinite(arr[f]) & np.isfinite(bf)
    if mask.sum() < 10:
        continue
    r = np.corrcoef(bf[mask], arr[f][mask])[0, 1]
    if abs(r) > 0.3:
        print(f"  bf vs {f:20s}: r = {r:+.4f}")

# Also check bf vs is_symmetric
r = np.corrcoef(bf, arr['is_symmetric'])[0, 1]
print(f"  bf vs {'is_symmetric':20s}: r = {r:+.4f}")

# 2. CHARACTERIZE LEAVES (bf=0)
print("\n=== LEAVES (bf=0) ===")
leaves = [d for d in data if d['bf'] == 0]
non_leaves = [d for d in data if d['bf'] > 0]
print(f"Leaves: {len(leaves)} ({100*len(leaves)/len(data):.1f}%)")
print(f"Non-leaves: {len(non_leaves)} ({100*len(non_leaves)/len(data):.1f}%)")

# Compare distributions
for f in ['multiplicity', 'embedding_dim', 'type', 'gap_density', 'ratio', 'wilf_number']:
    lv = np.array([d[f] for d in leaves])
    nlv = np.array([d[f] for d in non_leaves])
    print(f"\n  {f}:")
    print(f"    Leaves:     mean={np.mean(lv):.3f}, median={np.median(lv):.1f}, std={np.std(lv):.3f}")
    print(f"    Non-leaves: mean={np.mean(nlv):.3f}, median={np.median(nlv):.1f}, std={np.std(nlv):.3f}")

# 3. KEY QUESTION: bf = f(e, m, genus)?
# bf = number of generators above F. 
# All generators are in Apery set (except m). Apery elements in [1, F] are generators below F.
# Generators above F are Apery elements > F (if they're generators) plus possibly others... no.
# Actually: generators = m + {Apery elements that are irreducible in the Apery set}
# Generators above F are those among these with value > F.
# 
# Simple model: bf ≈ e - (generators below F)
# generators below F = generators in Apery set that are <= F
#
# Can we predict bf from e alone?
print("\n=== bf vs embedding_dim (e) ===")
for e_val in range(2, 12):
    mask = arr['embedding_dim'] == e_val
    if mask.sum() < 5:
        continue
    bf_e = bf[mask]
    print(f"  e={e_val:2d}: n={mask.sum():5d}  bf_mean={np.mean(bf_e):.3f}  bf_std={np.std(bf_e):.3f}  bf_range=[{int(np.min(bf_e))},{int(np.max(bf_e))}]")

# 4. CONDITIONAL: bf given (m, e)
print("\n=== bf given (m, e) — selected ===")
for m_val in [2, 3, 4, 5, 6]:
    for e_val in range(2, m_val + 1):
        mask = (arr['multiplicity'] == m_val) & (arr['embedding_dim'] == e_val)
        if mask.sum() < 3:
            continue
        bf_me = bf[mask]
        g_me = arr['genus'][mask]
        print(f"  m={m_val}, e={e_val}: n={mask.sum():4d}  bf_mean={np.mean(bf_me):.3f}  bf_range=[{int(np.min(bf_me))},{int(np.max(bf_me))}]  genus_range=[{int(np.min(g_me))},{int(np.max(g_me))}]")

# 5. IS THERE AN EXACT FORMULA?
# Hypothesis: bf = max(0, e - genus + F) ? No, doesn't type-check.
# Hypothesis: bf = number of Apery elements > F
# Since F is the largest gap, Apery(r) can be > F.
# The number of Apery elements > F is m - L (where L = left elements = F+1-g = elements of S in [0,F])
# Wait: elements of S in [0,F] = {0} + {Apery elements in [1,F]} ... no.
# Apery set has m elements (including 0). Elements > F: m - |{apery elements <= F}|
# Elements of S in [0,F] = L = F+1-g. These include 0 and all Apery elements <= F (each residue class has exactly one Apery element, which is the smallest in its class)
# Number of Apery elements <= F: this is L - (number of non-Apery elements of S in [0,F])
# Hmm, this is getting complicated. Let me just check empirically.

# Actually: bf = e - gens_below_F = e - (e - bf) = bf. Tautological.
# Better: bf vs (e - something simple)

# Let me check: does bf = e - (number of generators <= F)?
# And does the number of generators <= F have a formula?

# Check: for m=2, all semigroups are <2, 2k+1>. F = 2k-1. 
# Generators: 2 and 2k+1. 2 <= F (for k >= 2). 2k+1 > F = 2k-1. So bf = 1 always.
# Confirmed by data above.

# For m=3, e=3: <3, 3k+1, 3k+2>. F = 3k-1. All generators: 3, 3k+1, 3k+2.
# 3 <= F for k >= 2. 3k+1 > F = 3k-1 iff k >= 1. 3k+2 > F always.
# So bf = 2 for k >= 2 (gens above F: 3k+1, 3k+2), bf = 3 for k=1 (F=2, gens 3,4,5 all > 2)

# 6. THE REAL QUESTION: Is there structure in the bf=0 semigroups beyond "small multiplicity / high genus"?
print("\n=== LEAVES: multiplicity distribution ===")
leaf_m = np.array([d['multiplicity'] for d in leaves])
for m_val in range(2, 16):
    ct = (leaf_m == m_val).sum()
    if ct > 0:
        total_m = (arr['multiplicity'] == m_val).sum()
        print(f"  m={m_val:2d}: {ct:4d} leaves / {int(total_m):4d} total ({100*ct/total_m:.1f}% are leaves)")

print("\n=== LEAF FRACTION BY GENUS ===")
for g_val in range(1, 16):
    mask = arr['genus'] == g_val
    if mask.sum() == 0:
        continue
    leaf_frac = (bf[mask] == 0).sum() / mask.sum()
    print(f"  g={g_val:2d}: {100*leaf_frac:.1f}% leaves ({int((bf[mask]==0).sum())}/{int(mask.sum())})")

# 7. SURPRISING FINDING CHECK: Does bf=0 always imply something about the relationship between gens and F?
# bf=0 means ALL generators <= F. Since m <= F always (m is the smallest positive element, if m > F then all of 1..F are gaps which means m >= F+1 but then genus >= F >= m-1, and m > F means F < m so genus >= F... actually for m = F+1, gap set = {1,...,F} and genus = F = m-1. The semigroup is <m, m+1, ..., 2m-1>. Its generators are m, m+1,..., 2m-1, all > F = m-1. So bf = m. So MED semigroups are NOT leaves.)
# 
# For bf=0: even the LARGEST generator <= F. 
# Largest generator is max(Apery elements that are generators) or m.
# If max_gen <= F, then all generators are "small" compared to F.

print("\n=== LEAVES: max_gen vs F ===")
for d in leaves[:20]:
    print(f"  g={d['genus']:2d} m={d['multiplicity']:2d} e={d['embedding_dim']:2d} F={d['frobenius']:3d} max_gen={d['max_gen']:3d} gap={d['frobenius']-d['max_gen']:3d}")


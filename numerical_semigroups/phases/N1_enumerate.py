
"""
Phase N1 — Enumeration and invariant computation for numerical semigroups.

Enumerates all numerical semigroups up to a given genus and computes ~20 invariants.

Algorithm: tree of numerical semigroups (Bras-Amorós 2008).
Each semigroup of genus g has children of genus g+1 obtained by removing
one of its "left elements" (smallest elements that can be removed while keeping
the semigroup property).

Output: data/n1_results.json
"""

import json
import sys
from collections import defaultdict
from math import gcd, log2
from functools import reduce

# ============================================================
# CORE: Numerical semigroup representation
# ============================================================

def make_semigroup(generators, check_limit=200):
    """Create a numerical semigroup from generators.
    Returns the set of elements up to check_limit and the gap set."""
    g = reduce(gcd, generators)
    if g != 1:
        raise ValueError(f"Generators {generators} have gcd {g} != 1, not a numerical semigroup")
    
    elements = set()
    elements.add(0)
    for gen in generators:
        new_elements = set()
        for e in range(0, check_limit + 1):
            if e in elements:
                for k in range(1, (check_limit - e) // gen + 1):
                    new_elements.add(e + k * gen)
        elements.update(new_elements)
    
    # Iterative closure
    changed = True
    while changed:
        changed = False
        new = set()
        for a in elements:
            for b in elements:
                s = a + b
                if s <= check_limit and s not in elements:
                    new.add(s)
                    changed = True
        elements.update(new)
    
    return frozenset(e for e in elements if e <= check_limit)


def enumerate_by_genus(max_genus):
    """
    Enumerate all numerical semigroups by genus using the tree method.
    
    The tree root is N = {0,1,2,...} (genus 0).
    Children of S with genus g are obtained by removing "leaves" of S:
    a leaf x of S is an element x > 0 such that S \ {x} is still a numerical semigroup.
    
    x is removable from S if:
    - x is in S, x > 0
    - x is not the multiplicity (smallest nonzero element) unless x = F(S)+1
    - For all a,b in S\{x} with a+b=x, we need a or b = 0 (i.e., x is not a sum of two nonzero elements of S)
    
    Actually, the standard approach: S has genus g. The children of S at genus g+1
    are S' = S \ {x} where x is a "generator" of S that is > F(S).
    
    More precisely: enumerate by removing generators > Frobenius number.
    
    Reference: Fromentin & Hivert (2016), Bras-Amorós (2008).
    """
    # Represent a semigroup by its gap set (finite)
    # For efficiency, represent as a sorted tuple of gaps
    
    # Root: S = N (no gaps), genus 0
    results_by_genus = defaultdict(list)
    
    # We'll use a different representation: 
    # A numerical semigroup with Frobenius number F can be represented
    # by its Apery set or by its gap set.
    # For the tree enumeration, we track the gap set.
    
    # Start: gap_set = empty (S = N)
    initial_gaps = frozenset()
    
    # BFS/DFS through the tree
    stack = [(initial_gaps, 0)]  # (gap_set, genus)
    count_by_genus = defaultdict(int)
    
    all_semigroups = []
    
    while stack:
        gaps, g = stack.pop()
        
        if g > max_genus:
            continue
        
        count_by_genus[g] += 1
        
        # Store this semigroup
        if g > 0:  # Skip trivial N
            all_semigroups.append(gaps)
        
        if g == max_genus:
            continue
        
        # Find the Frobenius number (largest gap), or -1 if no gaps
        F = max(gaps) if gaps else 0
        
        # The multiplicity is the smallest positive integer NOT in gaps
        m = 1
        while m in gaps:
            m += 1
        
        # Children: remove element x from S where x > F and x is a generator
        # An element x > F is in S (since F is the largest gap).
        # x is a generator if x cannot be written as a + b with a, b in S, a,b > 0
        # i.e., for all ways to write x = a + b with 0 < a <= b, at least one of a,b is a gap
        
        # Elements of S that are > F and <= 2F+1 (beyond that they can't be generators in practice)
        # Actually, generators are bounded by F + m
        
        upper = F + m if F > 0 else m  # For genus 0, F=0, generators up to m
        
        for x in range(F + 1, upper + 1):
            if x in gaps:
                continue
            
            # Check if x is a generator (not expressible as sum of two positive elements of S)
            is_generator = True
            for a in range(1, x // 2 + 1):
                b = x - a
                if a not in gaps and b not in gaps:
                    is_generator = False
                    break
            
            if is_generator:
                # New semigroup: add x to gaps
                new_gaps = frozenset(gaps | {x})
                stack.append((new_gaps, g + 1))
    
    return count_by_genus, all_semigroups


# ============================================================
# INVARIANTS
# ============================================================

def compute_invariants(gap_set, limit=300):
    """Compute all invariants of a numerical semigroup given its gap set."""
    gaps = sorted(gap_set)
    genus = len(gaps)
    
    if genus == 0:
        return None  # Trivial semigroup N
    
    F = max(gaps)  # Frobenius number
    conductor = F + 1
    
    # Elements of S up to some limit
    S_elements = sorted(x for x in range(0, limit + 1) if x not in gap_set)
    
    # Multiplicity
    m = S_elements[1] if len(S_elements) > 1 else 1
    
    # Minimal generators
    generators = []
    for x in S_elements[1:]:
        if x > F + m:
            break
        is_gen = True
        for a in range(1, x // 2 + 1):
            b = x - a
            if a not in gap_set and b not in gap_set and a > 0:
                is_gen = False
                break
        if is_gen:
            generators.append(x)
    
    embedding_dim = len(generators)
    
    # Apéry set
    apery = [0] * m
    for i in range(m):
        for s in S_elements:
            if s % m == i and s > 0:
                apery[i] = s
                break
        if i == 0:
            apery[0] = 0  # Convention: w_0 = 0 or m*something? Usually w_0 = 0
    # Actually w_0 should be 0 by convention, and w_i = min{s in S : s ≡ i mod m}
    apery[0] = 0
    for i in range(1, m):
        for s in S_elements:
            if s > 0 and s % m == i:
                apery[i] = s
                break
    
    # Type: number of pseudo-Frobenius numbers
    # x is pseudo-Frobenius if x not in S but x + s in S for all s in S, s > 0
    pseudo_frobenius = []
    for x in gaps:
        is_pf = True
        for s in S_elements[1:]:
            if s > 0 and (x + s) in gap_set:
                is_pf = False
                break
            if s > F:  # x + s > F + F, certainly in S
                break
        if is_pf:
            pseudo_frobenius.append(x)
    
    sg_type = len(pseudo_frobenius)
    
    # Ratio
    ratio = (F + m - 1) // m  # ceil(F/m)
    
    # Left elements: l(S) = |S ∩ [0, conductor)|
    left_elements = len([x for x in S_elements if x < conductor])
    
    # Wilf number
    wilf_number = embedding_dim * left_elements - conductor
    
    # Depth
    depth = max(apery) // m if m > 0 else 0
    
    # Symmetry: S is symmetric if for all x not in S, F-x is in S
    is_symmetric = all((F - x) not in gap_set for x in gaps)
    
    # Almost symmetric: S is almost symmetric if PF(S) = {F} or {F, F/2}
    # Simpler: type = 1 iff symmetric (for irreducible)
    
    # Density of gaps in [0, F]
    gap_density = genus / (F + 1) if F > 0 else 0
    
    # Kunz coordinates: k_i = (w_i - i) / m for i = 1..m-1
    kunz = []
    if m > 1:
        kunz = [(apery[i] - i) // m for i in range(1, m)]
    
    # Delta set (factorization lengths)
    # For simplicity, compute for small elements
    # The elasticity is max L / min L for elements with multiple factorizations
    # This requires factorization computation — skip for Phase N1, add in N2
    
    # Gap distribution statistics
    gap_gaps = [gaps[i+1] - gaps[i] for i in range(len(gaps)-1)] if len(gaps) > 1 else []
    
    result = {
        'genus': genus,
        'frobenius': F,
        'conductor': conductor,
        'multiplicity': m,
        'embedding_dimension': embedding_dim,
        'generators': generators,
        'type': sg_type,
        'pseudo_frobenius': pseudo_frobenius,
        'ratio': ratio,
        'left_elements': left_elements,
        'wilf_number': wilf_number,
        'depth': depth,
        'is_symmetric': is_symmetric,
        'gap_density': gap_density,
        'kunz_coordinates': kunz,
        'apery_set': apery,
        'apery_max': max(apery) if apery else 0,
        'apery_sum': sum(apery),
        'gap_max_consecutive': max(gap_gaps) if gap_gaps else 0,
        'gap_mean_spacing': sum(gap_gaps) / len(gap_gaps) if gap_gaps else 0,
        'num_even_gaps': len([g for g in gaps if g % 2 == 0]),
        'num_odd_gaps': len([g for g in gaps if g % 2 == 1]),
    }
    
    return result


# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    MAX_GENUS = int(sys.argv[1]) if len(sys.argv) > 1 else 15
    
    print(f"Enumerating numerical semigroups up to genus {MAX_GENUS}...")
    counts, all_sg = enumerate_by_genus(MAX_GENUS)
    
    print(f"\nCounts by genus:")
    total = 0
    for g in sorted(counts.keys()):
        print(f"  g={g}: {counts[g]}")
        total += counts[g]
    print(f"  TOTAL: {total}")
    
    # Known sequence (OEIS A007323): 1, 1, 2, 4, 7, 12, 23, 39, 67, 118, 204, 343, 592, 1001, 1693, 2857, ...
    known = [1, 1, 2, 4, 7, 12, 23, 39, 67, 118, 204, 343, 592, 1001, 1693, 2857]
    print(f"\nVerification against OEIS A007323:")
    for g in range(min(MAX_GENUS + 1, len(known))):
        match = "✅" if counts[g] == known[g] else "❌"
        print(f"  g={g}: got {counts[g]}, expected {known[g]} {match}")
    
    print(f"\nComputing invariants for {len(all_sg)} semigroups...")
    results = []
    for i, gaps in enumerate(all_sg):
        inv = compute_invariants(gaps)
        if inv is not None:
            results.append(inv)
        if (i + 1) % 1000 == 0:
            print(f"  {i+1}/{len(all_sg)} done...")
    
    output_path = '../data/n1_results.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=1)
    
    print(f"\n✅ Saved {len(results)} semigroups to {output_path}")
    print(f"Invariants per semigroup: {len(results[0]) if results else 0}")
    
    # Quick Wilf check
    wilf_violations = [r for r in results if r['wilf_number'] < 0]
    print(f"\nWilf conjecture violations: {len(wilf_violations)}")
    if wilf_violations:
        print("🚨 WILF CONJECTURE COUNTER-EXAMPLE FOUND!")
        for v in wilf_violations:
            print(f"  generators={v['generators']}, genus={v['genus']}, W={v['wilf_number']}")
    else:
        print("✅ Wilf conjecture holds for all computed semigroups")

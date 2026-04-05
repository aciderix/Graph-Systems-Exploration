"""
N3c: Exact relationship between bf (branching factor) and type.

Hypothesis: bf = type when m <= F (non-MED), bf = type + 1 for MED (e=m).
Check and find the EXACT correction term.
"""
import numpy as np
import json
from collections import defaultdict, Counter

def enumerate_with_details(max_genus):
    """Full enumeration with bf, type, and PF details."""
    results = []
    current_level = [(frozenset(), -1, 1)]
    
    for g in range(max_genus + 1):
        next_level = []
        for gap_fs, F, m in current_level:
            gap_set = set(gap_fs)
            
            if F < 0:
                gens = [1]
                pf_numbers = []
                t = 0
            else:
                # Apery set
                apery = [0] * m
                for r in range(1, m):
                    x = r
                    while x in gap_set:
                        x += m
                    apery[r] = x
                
                # Generators from Apery
                gens = [m]
                for r in range(1, m):
                    a = apery[r]
                    is_sum = False
                    for r1 in range(1, m):
                        r2 = (r - r1) % m
                        if r1 == r:
                            continue
                        if r2 == 0:
                            if apery[r1] < a and (a - apery[r1]) % m == 0:
                                is_sum = True; break
                        elif apery[r1] + apery[r2] == a:
                            is_sum = True; break
                    if not is_sum:
                        gens.append(a)
                gens = sorted(gens)
                
                # Pseudo-Frobenius numbers
                pf_numbers = []
                for gap in sorted(gap_set, reverse=True):
                    is_pf = True
                    for gen in gens:
                        if (gap + gen) in gap_set:
                            is_pf = False; break
                    if is_pf:
                        pf_numbers.append(gap)
                pf_numbers = sorted(pf_numbers)
                t = len(pf_numbers)
            
            gens_above_F = [x for x in gens if x > F]
            bf = len(gens_above_F)
            e = len(gens)
            is_MED = (e == m)
            
            if g > 0:
                # Key: what's the relationship between bf and type?
                # For each PF number pf, is pf + m a generator above F?
                pf_plus_m = sorted([pf + m for pf in pf_numbers])
                pf_plus_m_above_F = [x for x in pf_plus_m if x > F]
                pf_plus_m_are_gens = [x for x in pf_plus_m_above_F if x in gens_above_F]
                
                # Is m itself above F?
                m_above_F = m > F
                
                results.append({
                    'genus': g, 'F': F, 'm': m, 'e': e, 't': t,
                    'bf': bf,
                    'is_MED': is_MED,
                    'm_above_F': m_above_F,
                    'bf_minus_t': bf - t,
                    'pf_plus_m_count': len(pf_plus_m_above_F),
                    'pf_plus_m_are_gens_count': len(pf_plus_m_are_gens),
                    'gens_above_F': sorted(gens_above_F),
                    'pf_numbers': pf_numbers,
                    'pf_plus_m': pf_plus_m,
                })
            
            if g < max_genus:
                for x in gens_above_F:
                    new_gaps = gap_set | {x}
                    new_F = x
                    new_m = min(y for y in range(1, new_F + 2) if y not in new_gaps) if x == m else m
                    next_level.append((frozenset(new_gaps), new_F, new_m))
        
        current_level = next_level
    
    return results

data = enumerate_with_details(15)
print(f"Total: {len(data)} semigroups\n")

# 1. Distribution of bf - type
diff = Counter(d['bf_minus_t'] for d in data)
print("=== bf - type distribution ===")
for k in sorted(diff.keys()):
    print(f"  bf - type = {k:+d}: {diff[k]:5d} ({100*diff[k]/len(data):.1f}%)")

# 2. When is bf = type exactly?
bf_eq_t = [d for d in data if d['bf'] == d['t']]
bf_gt_t = [d for d in data if d['bf'] > d['t']]
bf_lt_t = [d for d in data if d['bf'] < d['t']]
print(f"\nbf = type: {len(bf_eq_t)} ({100*len(bf_eq_t)/len(data):.1f}%)")
print(f"bf > type: {len(bf_gt_t)} ({100*len(bf_gt_t)/len(data):.1f}%)")
print(f"bf < type: {len(bf_lt_t)} ({100*len(bf_lt_t)/len(data):.1f}%)")

# 3. Is bf > type iff MED?
print("\n=== bf > type vs MED ===")
med = [d for d in data if d['is_MED']]
non_med = [d for d in data if not d['is_MED']]
print(f"MED: {len(med)}, of which bf > t: {sum(1 for d in med if d['bf'] > d['t'])}")
print(f"non-MED: {len(non_med)}, of which bf > t: {sum(1 for d in non_med if d['bf'] > d['t'])}")
print(f"MED with bf = t+1: {sum(1 for d in med if d['bf'] == d['t'] + 1)}")
print(f"MED with bf != t+1: {sum(1 for d in med if d['bf'] != d['t'] + 1)}")

# 4. Among bf > type non-MED: what's happening?
if any(d['bf'] > d['t'] and not d['is_MED'] for d in data):
    print("\n=== non-MED with bf > type ===")
    for d in data:
        if d['bf'] > d['t'] and not d['is_MED']:
            print(f"  g={d['genus']} m={d['m']} e={d['e']} t={d['t']} bf={d['bf']} F={d['F']}")
            print(f"    PF: {d['pf_numbers']}")
            print(f"    gens>F: {d['gens_above_F']}")
            print(f"    PF+m: {d['pf_plus_m']}")
            if len([x for x in data if x['bf'] > x['t'] and not x['is_MED']]) > 10:
                break

# 5. Among bf < type: what's happening?
print("\n=== bf < type: examples ===")
count = 0
for d in data:
    if d['bf'] < d['t'] and count < 15:
        print(f"  g={d['genus']} m={d['m']} e={d['e']} t={d['t']} bf={d['bf']} F={d['F']} diff={d['bf']-d['t']:+d}")
        print(f"    PF: {d['pf_numbers']}")
        print(f"    gens>F: {d['gens_above_F']}")
        print(f"    PF+m: {d['pf_plus_m']}")
        count += 1

# 6. THE KEY: is bf = |{pf : pf + m > F and pf + m is a generator}| + (1 if m > F else 0)?
print("\n=== TEST: bf = pf_gens_above_F + (m > F) ===")
match = 0
for d in data:
    predicted = d['pf_plus_m_are_gens_count'] + (1 if d['m_above_F'] else 0)
    if predicted == d['bf']:
        match += 1
print(f"Match: {match}/{len(data)} ({100*match/len(data):.1f}%)")

# 7. Better: the generators above F are EXACTLY the pf+m that are generators, plus m if m > F
# Check if gens_above_F = {pf+m that are gens} ∪ {m if m > F}
match2 = 0
for d in data:
    predicted_set = set(d['pf_plus_m']) & set(d['gens_above_F'])
    if d['m_above_F']:
        predicted_set.add(d['m'])
    if predicted_set == set(d['gens_above_F']):
        match2 += 1
    elif len(data) - match2 < 20:  # show mismatches
        print(f"  MISMATCH g={d['genus']} m={d['m']} e={d['e']}: predicted={sorted(predicted_set)} actual={d['gens_above_F']}")
print(f"Set match: {match2}/{len(data)} ({100*match2/len(data):.1f}%)")

# 8. Alternative: generators above F are exactly {pf + m : pf in PF(S)} (when m <= F)
# i.e., is the map pf -> pf + m a bijection to generators above F?
print("\n=== TEST: gens_above_F = {pf + m : pf in PF} when m <= F ===")
match3 = 0
mismatch_examples = []
for d in data:
    if d['m_above_F']:
        continue  # skip MED
    predicted = set(pf + d['m'] for pf in d['pf_numbers'])
    actual = set(d['gens_above_F'])
    if predicted == actual:
        match3 += 1
    else:
        mismatch_examples.append(d)

non_med_count = sum(1 for d in data if not d['m_above_F'])
print(f"Match: {match3}/{non_med_count} ({100*match3/non_med_count:.1f}%) among non-MED")

if mismatch_examples:
    print(f"\nMismatches: {len(mismatch_examples)}")
    for d in mismatch_examples[:10]:
        predicted = sorted(pf + d['m'] for pf in d['pf_numbers'])
        print(f"  g={d['genus']} m={d['m']} e={d['e']} t={d['t']} bf={d['bf']} F={d['F']}")
        print(f"    PF+m = {predicted}")
        print(f"    gens>F = {d['gens_above_F']}")
        diff_extra = set(d['gens_above_F']) - set(predicted)
        diff_miss = set(predicted) - set(d['gens_above_F'])
        if diff_extra: print(f"    EXTRA gens: {sorted(diff_extra)}")
        if diff_miss: print(f"    MISSING (PF+m not gen): {sorted(diff_miss)}")


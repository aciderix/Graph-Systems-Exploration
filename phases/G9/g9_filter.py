#!/usr/bin/env python3
"""
G9 FILTER — Separate trivial laws from potentially novel ones.
Then stress-test the non-trivial survivors on larger/weirder graphs.
"""

import json
import numpy as np

with open('/tmp/g9_laws.json') as f:
    laws = json.load(f)

print(f"Total raw laws: {len(laws)}")
print("=" * 70)

# =====================================================================
# STEP 1: Identify tautological metric groups
# =====================================================================
# These metrics are algebraically identical or directly derivable:
#   deg_sum = lap_trace = adj_trace_sq = 2m  (always)
#   adj_trace_cube = 6 * triangles  (always)
#   avg_deg = 2m/n = 2 * m_over_n  (always)
#   density = 2m / (n*(n-1))  (always)
#   energy_over_n = energy/n, energy_over_m = energy/m  (by definition)
#   lap_max_over_max_deg = lap_max / max_deg  (by definition)
#   sr_over_avg_deg = spectral_radius / avg_deg  (by definition)
#   tri_over_m = triangles / m  (by definition)

# Group 1: All proportional to m (or each other) for fixed n
EDGE_GROUP = {'m', 'deg_sum', 'lap_trace', 'adj_trace_sq', 'avg_deg', 'm_over_n', 'density'}
# Group 2: All proportional to triangle count
TRI_GROUP = {'triangles', 'adj_trace_cube'}
# Group 3: Defined as ratio of other metrics
RATIO_DEFS = {
    'energy_over_n': ('energy', 'n'),
    'energy_over_m': ('energy', 'm'),
    'lap_max_over_max_deg': ('lap_max', 'max_deg'),
    'sr_over_avg_deg': ('spectral_radius', 'avg_deg'),
    'tri_over_m': ('triangles', 'm'),
}
# Trivially preserved
TRIVIAL_PRESERVED = {
    ('complement', 'n'), ('square', 'n'), ('square', 'components'),
    ('subdivision', 'components'), ('corona', 'components'),
    ('mycielskian', 'components'), ('cart_K2', 'components'),
    ('double', 'components'), ('line', 'components'),
}
# Known from operation definition
KNOWN_FROM_DEFINITION = {
    ('subdivision', 'm'),  # subdivision doubles edges
    ('subdivision', 'max_deg'),  # subdivision preserves max degree
    ('corona', 'n'),  # corona adds n nodes
    ('cart_K2', 'n'),  # doubles nodes
    ('double', 'n'),  # doubles nodes
    ('corona', 'triangles'),  # pendants don't create triangles
    ('mycielskian', 'min_deg'),  # mycielskian adds 1 to min degree
}
# Known from spectral theory of products
KNOWN_SPECTRAL_PRODUCTS = {
    ('cart_K2', 'spectral_radius'),  # λ₁(G□K₂) = λ₁(G) + λ₁(K₂) = λ₁(G) + 1
    ('double', 'spectral_radius'),   # same mechanism
    ('cart_K2', 'lap_max'),  # μ_max(G□K₂) = μ_max(G) + 2
    ('double', 'lap_max'),
    ('cart_K2', 'avg_deg'),  # avg_deg increases by 1
    ('double', 'avg_deg'),
    ('cart_K2', 'max_deg'),
    ('double', 'max_deg'),
    ('cart_K2', 'min_deg'),
    ('double', 'min_deg'),
    ('cart_K2', 'deg_std'),
    ('double', 'deg_std'),
}

def is_trivial_s1(law):
    """Check if a Strategy 1 law is trivially derivable."""
    op = law['op']
    metric = law['metric']
    
    # Preserved by definition
    if (op, metric) in TRIVIAL_PRESERVED:
        return True, "preserved by definition"
    
    # Known from operation definition
    if (op, metric) in KNOWN_FROM_DEFINITION:
        return True, "follows from operation definition"
    
    # Known spectral product formula
    if (op, metric) in KNOWN_SPECTRAL_PRODUCTS:
        return True, "known spectral product formula"
    
    # Edge-group metrics under any operation
    if metric in EDGE_GROUP:
        return True, f"{metric} is in edge-group (∝ 2m)"
    
    # Triangle-group
    if metric in TRI_GROUP:
        return True, f"{metric} is in triangle-group (∝ triangles)"
    
    # Ratio definitions where both parts have known behavior
    if metric in RATIO_DEFS:
        num, den = RATIO_DEFS[metric]
        return True, f"{metric} = {num}/{den} (ratio of tracked metrics)"
    
    return False, ""

def is_trivial_s2(law):
    """Check if a Strategy 2 co-invariance is trivially derivable."""
    op = law['op']
    m1, m2 = law['metrics']
    
    # Both in edge group → trivially co-invariant
    if m1 in EDGE_GROUP and m2 in EDGE_GROUP:
        return True, "both in edge-group"
    
    # Both in triangle group
    if m1 in TRI_GROUP and m2 in TRI_GROUP:
        return True, "both in triangle-group"
    
    # One is ratio of the other with n or m
    if m1 in RATIO_DEFS or m2 in RATIO_DEFS:
        return True, "one is ratio-defined from the other"
    
    # If both metrics have known simple behavior under this op
    both_simple = EDGE_GROUP | TRI_GROUP | {'n', 'components'}
    if m1 in both_simple and m2 in both_simple:
        return True, "both have trivially known behavior"
    
    # deg_std preserved under complement (degree sequence is reflected)
    if 'deg_std' in {m1, m2} and op == 'complement':
        return True, "complement preserves degree variance"
    
    return False, ""

# =====================================================================
# STEP 2: Filter
# =====================================================================

trivial_count = 0
nontrivial = []

print("\n--- STRATEGY 1 FILTER ---")
s1 = [l for l in laws if l['strat'] == 1]
for law in s1:
    triv, reason = is_trivial_s1(law)
    if triv:
        trivial_count += 1
    else:
        nontrivial.append(law)
        print(f"  ✅ NON-TRIVIAL: {law['formula']}")

print(f"\n  S1: {len(s1)} total, {len(s1) - len([l for l in nontrivial if l['strat']==1])} trivial, {len([l for l in nontrivial if l['strat']==1])} non-trivial")

print("\n--- STRATEGY 2 FILTER ---")
s2 = [l for l in laws if l['strat'] == 2]
s2_nt = []
for law in s2:
    triv, reason = is_trivial_s2(law)
    if triv:
        trivial_count += 1
    else:
        s2_nt.append(law)
        nontrivial.append(law)
        print(f"  ✅ NON-TRIVIAL: {law['formula']}")

print(f"\n  S2: {len(s2)} total, {len(s2) - len(s2_nt)} trivial, {len(s2_nt)} non-trivial")

print("\n--- STRATEGY 3 ANALYSIS ---")
s3 = [l for l in laws if l['strat'] == 3]
for law in s3:
    coeffs = law.get('coefficients', {})
    # Check if it's purely edge-group
    involved = set(coeffs.keys())
    if involved.issubset(EDGE_GROUP | TRI_GROUP | {'n'}):
        trivial_count += 1
        continue
    
    sigma = law.get('sigma', 999)
    
    # Laws with very small sigma involving spectral quantities are interesting
    spectral_involved = involved & {'spectral_radius', 'spectral_gap', 'lap_energy', 'lap_max', 
                                      'energy', 'sr_over_avg_deg', 'lap_max_over_max_deg',
                                      'transitivity', 'clustering', 'spanning_trees_log', 'adj_rank'}
    
    if spectral_involved and sigma < 0.15:
        nontrivial.append(law)
        print(f"  ✅ σ={sigma:.6f} | {law['formula']}")
    else:
        trivial_count += 1

print(f"\n  S3: {len(s3)} total, {len(s3) - len([l for l in nontrivial if l['strat']==3])} filtered, {len([l for l in nontrivial if l['strat']==3])} kept")

print("\n--- STRATEGY 4 ANALYSIS ---")
s4 = [l for l in laws if l['strat'] == 4]
for law in s4:
    metric = law.get('metric', '')
    op = law.get('op', '')
    
    # square^k → complete graph is trivial
    if op == 'square' and metric in {'density', 'clustering', 'transitivity', 'components', 'deg_std', 'sr_over_avg_deg'}:
        trivial_count += 1
        continue
    
    # line^k → components=1 is trivial for connected graphs
    if op == 'line' and metric == 'components':
        trivial_count += 1
        continue
    
    nontrivial.append(law)
    print(f"  ✅ {law['formula']}")

print(f"\n  S4: {len(s4)} total, {len(s4) - len([l for l in nontrivial if l['strat']==4])} trivial, {len([l for l in nontrivial if l['strat']==4])} non-trivial")

# =====================================================================
# SUMMARY
# =====================================================================
print("\n" + "=" * 70)
print(f"FILTER RESULTS: {len(laws)} total → {len(nontrivial)} non-trivial")
print("=" * 70)

print("\n🏆 ALL NON-TRIVIAL CANDIDATE LAWS:")
for i, law in enumerate(nontrivial):
    print(f"\n  [{i+1}] Strategy {law['strat']} | {law.get('op', 'N/A')}")
    print(f"      {law['formula']}")
    if 'cv' in law:
        print(f"      CV={law['cv']}, n={law['n']}")
    elif 'sigma' in law:
        print(f"      σ={law['sigma']}, n={law['n']}")

# Save filtered results
with open('/tmp/g9_nontrivial.json', 'w') as f:
    json.dump(nontrivial, f, indent=2)

print(f"\n{len(nontrivial)} non-trivial laws saved to /tmp/g9_nontrivial.json")

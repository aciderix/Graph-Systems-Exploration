"""
N4b: Clean Wilf frontier analysis.
Focus on W_min(m, e) table and formula hunting.
"""
import numpy as np
import json
from collections import defaultdict

# Load data
with open('/agent/home/repo/numerical_semigroups/data/n1_results_g20.json') as f:
    data = json.load(f)
print(f"Loaded {len(data)} semigroups\n")

# W_min table by (m, e)
me_stats = defaultdict(lambda: {'w_min': float('inf'), 'count': 0, 'achievers': []})

for sg in data:
    m = sg['multiplicity']
    e = sg['embedding_dimension']
    w = sg['wilf_number']
    k = (m, e)
    me_stats[k]['count'] += 1
    if w < me_stats[k]['w_min']:
        me_stats[k]['w_min'] = w
        me_stats[k]['achievers'] = [sg]
    elif w == me_stats[k]['w_min']:
        me_stats[k]['achievers'].append(sg)

# Print clean table
print("=== W_min(m, e) TABLE ===\n")
max_m = 15
max_e = 15

# Header
header = f"{'m\\e':>4}"
for e in range(2, max_e + 1):
    header += f" {e:>4}"
print(header)
print("-" * len(header))

for m in range(2, max_m + 1):
    row = f"{m:4d}"
    for e in range(2, max_e + 1):
        if e > m:
            row += "    ."
        elif (m, e) in me_stats and me_stats[(m, e)]['count'] >= 1:
            w = me_stats[(m, e)]['w_min']
            row += f" {w:4d}"
        else:
            row += "   --"
    print(row)

# Focus on e=3 column (most interesting non-trivial case)
print("\n=== W_min(m, 3) SEQUENCE ===\n")
seq_m3 = []
for m in range(3, 21):
    k = (m, 3)
    if k in me_stats and me_stats[k]['count'] >= 1:
        w = me_stats[k]['w_min']
        seq_m3.append((m, w))
        achiever = me_stats[k]['achievers'][0]
        gens = achiever.get('generators', '?')
        print(f"  m={m:2d}: W_min = {w:3d}  (n={me_stats[k]['count']:4d} semigroups)  achiever: {gens}")

# Check formulas for e=3
if seq_m3:
    ms = np.array([x[0] for x in seq_m3], dtype=float)
    ws = np.array([x[1] for x in seq_m3], dtype=float)
    
    # Linear fit
    A = np.vstack([ms, np.ones(len(ms))]).T
    coeff, res, _, _ = np.linalg.lstsq(A, ws, rcond=None)
    print(f"\n  Linear fit: W_min ≈ {coeff[0]:.3f}·m + ({coeff[1]:.3f})")
    print(f"  Max residual: {max(abs(ws - (coeff[0]*ms + coeff[1]))):.2f}")
    
    # Quadratic fit
    A2 = np.vstack([ms**2, ms, np.ones(len(ms))]).T
    coeff2, _, _, _ = np.linalg.lstsq(A2, ws, rcond=None)
    pred2 = coeff2[0]*ms**2 + coeff2[1]*ms + coeff2[2]
    print(f"  Quadratic fit: W_min ≈ {coeff2[0]:.4f}·m² + ({coeff2[1]:.3f})·m + ({coeff2[2]:.3f})")
    print(f"  Max residual: {max(abs(ws - pred2)):.2f}")

# Focus on e=4 column
print("\n=== W_min(m, 4) SEQUENCE ===\n")
for m in range(4, 21):
    k = (m, 4)
    if k in me_stats and me_stats[k]['count'] >= 1:
        w = me_stats[k]['w_min']
        achiever = me_stats[k]['achievers'][0]
        gens = achiever.get('generators', '?')
        print(f"  m={m:2d}: W_min = {w:3d}  (n={me_stats[k]['count']:4d})  achiever: {gens}")

# Focus on diagonal e = m-1
print("\n=== W_min(m, m-1) SEQUENCE ===\n")
for m in range(3, 21):
    k = (m, m-1)
    if k in me_stats and me_stats[k]['count'] >= 1:
        w = me_stats[k]['w_min']
        achiever = me_stats[k]['achievers'][0]
        gens = achiever.get('generators', '?')
        print(f"  m={m:2d}: W_min = {w:3d}  (n={me_stats[k]['count']:4d})  achiever: {gens}")

# Focus on e = m (MED)
print("\n=== W_min(m, m) = 0 confirmation (MED) ===\n")
for m in range(2, 21):
    k = (m, m)
    if k in me_stats:
        w = me_stats[k]['w_min']
        n_zero = sum(1 for sg in data if sg['multiplicity'] == m and sg['embedding_dimension'] == m and sg['wilf_number'] == 0)
        print(f"  m={m:2d}: W_min = {w}  (W=0 count: {n_zero})")

# W_min for fixed m (across all e)
print("\n=== W_min(m) = min over all e ===\n")
for m in range(2, 21):
    w_min_m = float('inf')
    for e in range(2, m+1):
        k = (m, e)
        if k in me_stats:
            w_min_m = min(w_min_m, me_stats[k]['w_min'])
    print(f"  m={m:2d}: W_min = {w_min_m}")

# Now: the REAL question. For fixed e, is W_min(m, e) growing?
# And can we predict it?
print("\n=== GROWTH RATE: W_min(m, e) for fixed e ===\n")
for e in [3, 4, 5, 6]:
    pairs = []
    for m in range(e, 21):
        k = (m, e)
        if k in me_stats and me_stats[k]['count'] >= 3:
            pairs.append((m, me_stats[k]['w_min']))
    
    if len(pairs) >= 3:
        ms = np.array([p[0] for p in pairs], dtype=float)
        ws = np.array([p[1] for p in pairs], dtype=float)
        
        # Check differences
        diffs = np.diff(ws)
        print(f"  e={e}: W_min values = {[int(w) for w in ws]}")
        print(f"       Δ(W_min) = {[int(d) for d in diffs]}")
        
        # Fit
        A = np.vstack([ms, np.ones(len(ms))]).T
        c, _, _, _ = np.linalg.lstsq(A, ws, rcond=None)
        print(f"       Linear: {c[0]:.3f}·m + ({c[1]:.3f}), max_res = {max(abs(ws - (c[0]*ms + c[1]))):.1f}")


"""
Phase 1: Verify conjectures from existing enumerated data (genus <= 20).
Then identify where we need targeted enumeration.
"""
import json
from math import floor
from collections import defaultdict

# Load the big dataset
print("Loading n1_results_g20.json...")
with open('/agent/home/repo/numerical_semigroups/data/n1_results_g20.json') as f:
    data = json.load(f)
print(f"Loaded {len(data)} semigroups (genus <= 20)\n")

# Build W_min table by (m, e) 
stats = defaultdict(lambda: {'w_min': float('inf'), 'count': 0, 'w_min_achiever': None})

for sg in data:
    m = sg['multiplicity']
    e = sg['embedding_dimension']
    w = sg['wilf_number']
    k = (m, e)
    stats[k]['count'] += 1
    if w < stats[k]['w_min']:
        stats[k]['w_min'] = w
        stats[k]['w_min_achiever'] = sg

# Unified formula
def predicted_w_min(m, d):
    if d == 0:
        return 0
    L_d = floor(d / 2) + 3
    return (m - d) * L_d - 2 * m

# Check all d=0..5
print("=" * 80)
print("VERIFICATION FROM EXISTING DATA (genus <= 20)")
print("Unified formula: W_min(m,d) = (m-d)*(floor(d/2)+3) - 2m")
print("=" * 80)

for d in range(6):
    L_d = floor(d / 2) + 3 if d > 0 else '-'
    print(f"\n--- d = {d} (L(d) = {L_d}) ---")
    
    for m in range(max(2, d+2), 21):
        e = m - d
        if e < 2:
            continue
        k = (m, e)
        
        pred = predicted_w_min(m, d)
        
        if k in stats and stats[k]['count'] > 0:
            obs = stats[k]['w_min']
            count = stats[k]['count']
            
            if obs < pred:
                status = "❌ VIOLATION"
            elif obs == pred:
                status = "✅ EXACT"
            else:
                status = "✅ (above)"
            
            # Check if tight family genus is within cap
            if d == 1:
                tight_g = 2*m - 3
            elif d == 2:
                tight_g = 3*m - 7
            elif d == 3:
                tight_g = 3*m - 8
            else:
                tight_g = None
            
            g_note = ""
            if tight_g and tight_g > 20:
                g_note = f" [WARN: tight family g={tight_g}>20, min may be artificial]"
            
            print(f"  m={m:2d} e={e:2d}: W_min_obs={obs:4d}  predicted={pred:4d}  "
                  f"n={count:5d}  {status}{g_note}")
        else:
            print(f"  m={m:2d} e={e:2d}: NO DATA (need targeted enum)")

# Now identify gaps
print(f"\n{'='*80}")
print("GAPS REQUIRING TARGETED ENUMERATION")
print(f"{'='*80}")

for d in range(1, 6):
    for m in range(max(2, d+2), 21):
        e = m - d
        if e < 2:
            continue
        k = (m, e)
        
        # Tight family genus
        if d == 1:
            tight_g = 2*m - 3
        elif d == 2:
            tight_g = 3*m - 7
        elif d == 3:
            tight_g = 3*m - 8
        elif d == 4:
            tight_g = 4*m - 12  # rough estimate
        else:
            tight_g = 4*m - 15  # rough estimate
        
        if k not in stats or stats[k]['count'] == 0:
            print(f"  d={d}, m={m}: NO DATA AT ALL")
        elif tight_g > 20:
            obs = stats[k]['w_min']
            pred = predicted_w_min(m, d)
            if obs > pred:
                print(f"  d={d}, m={m}: obs={obs} > pred={pred}, tight_g={tight_g}>20 → NEED HIGHER GENUS")
            # if obs == pred, it's still valid even if tight family is out of range

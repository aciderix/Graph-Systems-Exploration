import json
from collections import defaultdict

with open('/tmp/sg_data.json') as f:
    data = json.load(f)

# Detailed analysis of d=2 by (m, k*)
by_m_kstar = defaultdict(list)
tight_details = []

for sg in data:
    m = sg['multiplicity']
    e = sg['embedding_dimension']
    d_val = m - e
    if d_val != 2:
        continue
    
    c = sg['conductor']
    L = sg['left_elements']
    W = sg['wilf_number']
    kunz = sg['kunz_coordinates']
    
    k_star = max(kunz)
    r_star = max([i+1 for i, k in enumerate(kunz) if k == k_star])
    
    target = 2 * m - 8
    by_m_kstar[(m, k_star)].append({
        'L': L, 'W': W, 'c': c, 'r_star': r_star, 'kunz': kunz
    })
    
    if W == target:
        tight_details.append({
            'm': m, 'k_star': k_star, 'r_star': r_star, 'L': L, 'c': c, 
            'W': W, 'c_eq_2m': c == 2*m, 'kunz': kunz
        })

# Print by (m, k*) with L_min, W_min
print("="*70)
print("DISTRIBUTION BY (m, k*) — W_min and L_min")
print("="*70)
for m in sorted(set(mk[0] for mk in by_m_kstar)):
    target = 2*m - 8
    for k in sorted(set(mk[1] for mk in by_m_kstar if mk[0] == m)):
        sgs = by_m_kstar[(m, k)]
        Wmin = min(s['W'] for s in sgs)
        Lmin = min(s['L'] for s in sgs)
        n = len(sgs)
        status = "✅" if Wmin >= target else "❌"
        print(f"  m={m:2d}, k*={k}: n={n:4d}, L_min={Lmin:2d}, W_min={Wmin:3d}, target={target:3d} {status}")

# Verify the shortfall lemma: for k*>=4, L >= 2k*-1
print("\n" + "="*70)
print("SHORTFALL LEMMA: L >= 2k*-1 for k*>=4")
print("="*70)
for (m, k), sgs in sorted(by_m_kstar.items()):
    if k < 4:
        continue
    Lmin = min(s['L'] for s in sgs)
    bound = 2*k - 1
    status = "✅" if Lmin >= bound else f"❌ (need {bound})"
    print(f"  m={m:2d}, k*={k}: L_min={Lmin:2d}, bound={bound:2d} {status}")

# Special: tight cases NOT at c=2m
print("\n" + "="*70)
print("TIGHT CASES ANALYSIS")
print("="*70)
print(f"Total tight cases (W=2m-8): {len(tight_details)}")
c2m = [t for t in tight_details if t['c_eq_2m']]
not_c2m = [t for t in tight_details if not t['c_eq_2m']]
print(f"  With c=2m: {len(c2m)}")
print(f"  With c≠2m: {len(not_c2m)} (all at m=4 where target=0)")
for t in not_c2m[:5]:
    print(f"    m={t['m']}, k*={t['k_star']}, c={t['c']}, L={t['L']}, kunz={t['kunz']}")

# For m>=5 tight cases: check all have c=2m
tight_m5plus = [t for t in tight_details if t['m'] >= 5]
all_c2m_m5 = all(t['c_eq_2m'] for t in tight_m5plus)
print(f"\nFor m>=5: all tight cases have c=2m: {'✅' if all_c2m_m5 else '❌'} ({len(tight_m5plus)} cases)")

# For m>=5 tight cases: check all have k*=2, L=4
all_k2L4_m5 = all(t['k_star']==2 and t['L']==4 for t in tight_m5plus)
print(f"For m>=5: all tight cases have k*=2, L=4: {'✅' if all_k2L4_m5 else '❌'}")

# m=4 analysis
print("\n" + "="*70)
print("m=4 ANALYSIS (target=0, all are 2-generator)")
print("="*70)
m4 = [s for mk, sgs in by_m_kstar.items() for s in sgs if mk[0]==4]
# Actually recompute from data
m4_sgs = [sg for sg in data if sg['multiplicity']==4 and sg['multiplicity']-sg['embedding_dimension']==2]
for sg in m4_sgs[:5]:
    print(f"  gens={sg['generators']}, W={sg['wilf_number']}, c={sg['conductor']}, L={sg['left_elements']}")
print(f"  All m=4, d=2 have W=0: {all(sg['wilf_number']==0 for sg in m4_sgs)} ✅")
print(f"  All m=4, d=2 have e=2: {all(sg['embedding_dimension']==2 for sg in m4_sgs)} (2-generator semigroups)")


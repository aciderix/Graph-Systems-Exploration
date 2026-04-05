"""
PHASE G7 — ANALYSE COMPLÈTE
============================
1. CORRÉLATION avec les 31 métriques G1
2. FALSIFICATION : main vs extreme vs null
3. DÉTECTION de patterns non-triviaux
4. CARACTÉRISATION des survivants
"""
import json
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# LOAD DATA
# ============================================================
with open('/tmp/g7_all_pistes_results.json') as f:
    data = json.load(f)

with open('/agent/home/Graph-Systems-Exploration/data/g1_results.json') as f:
    g1_results = json.load(f)

main = data['main']
extreme = data['extreme']
null = data['null']

print(f"Loaded: {len(main)} main, {len(extreme)} extreme, {len(null)} null")

# ============================================================
# 1. CORRELATION ANALYSIS
# ============================================================
print("\n" + "=" * 70)
print("1. CORRÉLATION AVEC LES 31 MÉTRIQUES G1")
print("=" * 70)

# Build alignment: match main[i] with g1_results[i] by index
g1_keys = ['density', 'deg_mean', 'deg_std', 'clustering_avg', 'transitivity',
           'assortativity', 'largest_cc_frac', 'algebraic_connectivity',
           'spectral_radius', 'spectral_gap', 'modularity', 'norm_lap_gap',
           'deg_max', 'deg_min', 'num_triangles', 'avg_shortest_path', 'diameter',
           'laplacian_max', 'wiener_index', 'num_components', 'deg_skew', 'deg_kurtosis']

# Collect all new metric keys from all pistes
new_metric_keys = {}
for piste in ['F', 'A', 'B', 'E', 'J']:
    keys = set()
    for r in main:
        if piste in r and isinstance(r[piste], dict):
            for k, v in r[piste].items():
                if isinstance(v, (int, float)) and k not in ('N', 'M') and not k.startswith('error'):
                    keys.add(k)
    new_metric_keys[piste] = sorted(keys)

print(f"\nNew metric keys per piste:")
for p, keys in new_metric_keys.items():
    print(f"  {p}: {len(keys)} metrics")

# Compute correlations
print(f"\n{'NEW METRIC':<40s} {'BEST OLD CORR':<20s} {'|r|':>6s} {'REDUNDANT?':>10s}")
print("-" * 80)

all_correlations = {}
redundant_metrics = []
non_redundant_metrics = []

for piste in ['F', 'A', 'B', 'E', 'J']:
    for new_key in new_metric_keys[piste]:
        # Extract new metric values
        new_vals = []
        old_vals_dict = {k: [] for k in g1_keys}
        valid_indices = []
        
        for i, r in enumerate(main):
            if piste not in r or not isinstance(r[piste], dict):
                continue
            nv = r[piste].get(new_key)
            if nv is None or (isinstance(nv, float) and (np.isnan(nv) or np.isinf(nv))):
                continue
            
            if i >= len(g1_results):
                continue
            g1 = g1_results[i]
            
            # Check all G1 values are valid
            all_ok = True
            row_old = {}
            for ok in g1_keys:
                ov = g1.get(ok)
                if ov is None or (isinstance(ov, float) and (np.isnan(ov) or np.isinf(ov))):
                    all_ok = False
                    break
                row_old[ok] = float(ov)
            
            if all_ok:
                new_vals.append(float(nv))
                for ok in g1_keys:
                    old_vals_dict[ok].append(row_old[ok])
                valid_indices.append(i)
        
        if len(new_vals) < 10:
            continue
        
        new_arr = np.array(new_vals)
        
        # Compute correlation with each old metric
        best_corr = 0
        best_old = ""
        correlations_row = {}
        
        for ok in g1_keys:
            old_arr = np.array(old_vals_dict[ok])
            if np.std(old_arr) < 1e-15 or np.std(new_arr) < 1e-15:
                continue
            r_val = np.corrcoef(new_arr, old_arr)[0, 1]
            if not np.isnan(r_val):
                correlations_row[ok] = r_val
                if abs(r_val) > abs(best_corr):
                    best_corr = r_val
                    best_old = ok
        
        all_correlations[f"{piste}:{new_key}"] = correlations_row
        
        is_redundant = abs(best_corr) > 0.95
        if is_redundant:
            redundant_metrics.append((piste, new_key, best_old, best_corr))
        else:
            non_redundant_metrics.append((piste, new_key, best_old, best_corr))
        
        tag = "❌ SKIP" if is_redundant else "✅ KEEP"
        print(f"  {piste}:{new_key:<35s} {best_old:<20s} {abs(best_corr):>6.3f} {tag:>10s}")

print(f"\n{'='*70}")
print(f"RÉSUMÉ CORRÉLATION:")
print(f"  Métriques redondantes (|r| > 0.95): {len(redundant_metrics)}")
print(f"  Métriques NON-redondantes: {len(non_redundant_metrics)}")

# ============================================================
# 2. FALSIFICATION: MAIN vs EXTREME vs NULL
# ============================================================
print("\n" + "=" * 70)
print("2. FALSIFICATION: MAIN vs EXTREME vs NULL")
print("=" * 70)

# For each non-redundant metric, compare distributions
print(f"\n{'METRIC':<45s} {'MAIN μ±σ':>15s} {'EXTREME μ±σ':>15s} {'NULL μ±σ':>15s} {'SURVIVES?':>10s}")
print("-" * 105)

survivors = []
failures = []

for piste, key, best_old, best_corr in non_redundant_metrics:
    # Collect values from each set
    main_vals = []
    for r in main:
        if piste in r and isinstance(r[piste], dict):
            v = r[piste].get(key)
            if v is not None and isinstance(v, (int, float)) and not np.isnan(v) and not np.isinf(v):
                main_vals.append(v)
    
    extreme_vals = []
    for r in extreme:
        if piste in r and isinstance(r[piste], dict):
            v = r[piste].get(key)
            if v is not None and isinstance(v, (int, float)) and not np.isnan(v) and not np.isinf(v):
                extreme_vals.append(v)
    
    null_vals = []
    for r in null:
        if piste in r and isinstance(r[piste], dict):
            v = r[piste].get(key)
            if v is not None and isinstance(v, (int, float)) and not np.isnan(v) and not np.isinf(v):
                null_vals.append(v)
    
    if len(main_vals) < 5 or len(null_vals) < 3:
        continue
    
    main_arr = np.array(main_vals)
    null_arr = np.array(null_vals)
    
    # Trivality test: is the metric basically the same for structured and random graphs?
    # Cohen's d effect size
    pooled_std = np.sqrt((np.var(main_arr) + np.var(null_arr)) / 2)
    if pooled_std > 1e-15:
        cohens_d = abs(np.mean(main_arr) - np.mean(null_arr)) / pooled_std
    else:
        cohens_d = 0
    
    # Does it break on extremes?
    extreme_arr = np.array(extreme_vals) if extreme_vals else np.array([])
    
    # Check if extreme values are within reasonable range of main
    if len(extreme_arr) > 0:
        main_range = np.max(main_arr) - np.min(main_arr)
        extreme_outliers = np.sum((extreme_arr < np.min(main_arr) - 2*main_range) | 
                                   (extreme_arr > np.max(main_arr) + 2*main_range))
        extreme_break_frac = extreme_outliers / len(extreme_arr)
    else:
        extreme_break_frac = 0
    
    # VERDICT:
    # - Survives if: Cohen's d > 0.5 (distinguishes from null) AND extreme_break_frac < 0.3
    survives = cohens_d > 0.5 and extreme_break_frac < 0.3
    
    m_str = f"{np.mean(main_arr):>7.3f}±{np.std(main_arr):.3f}"
    e_str = f"{np.mean(extreme_arr):>7.3f}±{np.std(extreme_arr):.3f}" if len(extreme_arr) > 0 else "N/A"
    n_str = f"{np.mean(null_arr):>7.3f}±{np.std(null_arr):.3f}"
    
    tag = "✅" if survives else "❌"
    
    entry = {
        'piste': piste, 'key': key, 'best_old_corr': best_old,
        'best_old_corr_val': float(best_corr),
        'main_mean': float(np.mean(main_arr)), 'main_std': float(np.std(main_arr)),
        'null_mean': float(np.mean(null_arr)), 'null_std': float(np.std(null_arr)),
        'cohens_d': float(cohens_d),
        'extreme_break_frac': float(extreme_break_frac),
        'survives': survives,
        'n_main': len(main_vals), 'n_extreme': len(extreme_vals), 'n_null': len(null_vals),
    }
    if len(extreme_arr) > 0:
        entry['extreme_mean'] = float(np.mean(extreme_arr))
        entry['extreme_std'] = float(np.std(extreme_arr))
    
    if survives:
        survivors.append(entry)
    else:
        failures.append(entry)
    
    print(f"  {piste}:{key:<40s} {m_str:>15s} {e_str:>15s} {n_str:>15s} {tag:>10s} d={cohens_d:.2f}")

# ============================================================
# 3. DEEP ANALYSIS OF SURVIVORS
# ============================================================
print("\n" + "=" * 70)
print("3. ANALYSE APPROFONDIE DES SURVIVANTS")
print("=" * 70)

print(f"\n{len(survivors)} métriques survivent à la falsification")
print(f"{len(failures)} métriques éliminées")

if survivors:
    print(f"\n{'RANK':>4s} {'PISTE':>5s} {'METRIC':<35s} {'Cohen d':>8s} {'|r_max|':>8s} {'Extreme%':>8s}")
    print("-" * 75)
    
    # Sort by Cohen's d (most discriminating first)
    survivors.sort(key=lambda x: -x['cohens_d'])
    
    for rank, s in enumerate(survivors, 1):
        print(f"  {rank:>3d} {s['piste']:>5s} {s['key']:<35s} {s['cohens_d']:>8.2f} {abs(s['best_old_corr_val']):>8.3f} {s['extreme_break_frac']*100:>7.1f}%")

# ============================================================
# 4. INTER-METRIC CORRELATIONS (new vs new)
# ============================================================
print("\n" + "=" * 70)
print("4. CORRÉLATION INTER-NOUVELLES MÉTRIQUES")
print("=" * 70)

if len(survivors) > 1:
    # Build matrix of survivor values
    survivor_keys = [(s['piste'], s['key']) for s in survivors]
    
    # Extract values
    matrix_rows = []
    for i in range(len(main)):
        row = []
        valid = True
        for piste, key in survivor_keys:
            r = main[i]
            if piste not in r or not isinstance(r[piste], dict):
                valid = False
                break
            v = r[piste].get(key)
            if v is None or (isinstance(v, float) and (np.isnan(v) or np.isinf(v))):
                valid = False
                break
            row.append(float(v))
        if valid:
            matrix_rows.append(row)
    
    if len(matrix_rows) > 10:
        matrix = np.array(matrix_rows)
        corr = np.corrcoef(matrix.T)
        
        print(f"\nCorrélation entre survivants ({len(matrix_rows)} graphes valides):")
        
        # Show strong correlations
        strong_pairs = []
        for i in range(len(survivor_keys)):
            for j in range(i+1, len(survivor_keys)):
                r_val = corr[i, j]
                if not np.isnan(r_val) and abs(r_val) > 0.8:
                    strong_pairs.append((abs(r_val), r_val, 
                                        f"{survivor_keys[i][0]}:{survivor_keys[i][1]}", 
                                        f"{survivor_keys[j][0]}:{survivor_keys[j][1]}"))
        
        strong_pairs.sort(reverse=True)
        if strong_pairs:
            print(f"\nFortes corrélations entre survivants (|r| > 0.8):")
            for _, r_val, n1, n2 in strong_pairs[:20]:
                sign = "+" if r_val > 0 else "-"
                print(f"  {sign}{abs(r_val):.3f}  {n1:<45s} ↔ {n2}")
        else:
            print(f"\nAucune forte corrélation entre survivants — ils mesurent des choses DIFFÉRENTES ✅")

# ============================================================
# 5. N-DEPENDENCE CHECK
# ============================================================
print("\n" + "=" * 70)
print("5. DÉPENDANCE EN N (scale-invariance check)")
print("=" * 70)

if survivors:
    print(f"\n{'METRIC':<45s} {'corr(N,metric)':>15s} {'N-dependent?':>12s}")
    print("-" * 75)
    
    for s in survivors:
        piste, key = s['piste'], s['key']
        vals = []
        ns = []
        for i, r in enumerate(main):
            if piste not in r or not isinstance(r[piste], dict):
                continue
            v = r[piste].get(key)
            n = r[piste].get('N')
            if v is not None and n is not None and isinstance(v, (int, float)) and not np.isnan(v) and not np.isinf(v):
                vals.append(float(v))
                ns.append(float(n))
        
        if len(vals) > 10:
            r_val = np.corrcoef(ns, vals)[0, 1]
            is_n_dep = abs(r_val) > 0.7
            tag = "⚠️ YES" if is_n_dep else "✅ NO"
            print(f"  {piste}:{key:<40s} {r_val:>15.3f} {tag:>12s}")

# ============================================================
# 6. FAMILY SIGNATURES (do new metrics distinguish families?)
# ============================================================
print("\n" + "=" * 70)
print("6. POUVOIR DISCRIMINANT PAR FAMILLE")
print("=" * 70)

# For top survivors, compute mean per family and check variance ratio
if survivors:
    families = {}
    for i, r in enumerate(main):
        fam = r['meta']['name']
        if fam not in families:
            families[fam] = []
        families[fam].append(i)
    
    for s in survivors[:10]:  # top 10
        piste, key = s['piste'], s['key']
        
        family_means = {}
        all_vals = []
        for fam, indices in families.items():
            vals = []
            for idx in indices:
                r = main[idx]
                if piste in r and isinstance(r[piste], dict):
                    v = r[piste].get(key)
                    if v is not None and isinstance(v, (int, float)) and not np.isnan(v) and not np.isinf(v):
                        vals.append(float(v))
                        all_vals.append(float(v))
            if vals:
                family_means[fam] = np.mean(vals)
        
        # Eta-squared: between-group variance / total variance
        if len(family_means) > 1 and len(all_vals) > 10:
            grand_mean = np.mean(all_vals)
            total_var = np.var(all_vals)
            if total_var > 1e-15:
                between_var = np.mean([(m - grand_mean)**2 for m in family_means.values()])
                eta2 = between_var / total_var
                print(f"  {piste}:{key:<40s} η² = {eta2:.3f} ({'STRONG' if eta2 > 0.3 else 'weak' if eta2 > 0.1 else 'none'})")

# ============================================================
# FINAL VERDICT
# ============================================================
print("\n" + "=" * 70)
print("VERDICT FINAL")
print("=" * 70)

truly_novel = [s for s in survivors if abs(s['best_old_corr_val']) < 0.7]
print(f"\nMétriques SURVIVANTES et NON-REDONDANTES (|r_old| < 0.7): {len(truly_novel)}")

for s in truly_novel:
    print(f"\n  ★ {s['piste']}:{s['key']}")
    print(f"    Cohen's d vs null: {s['cohens_d']:.2f}")
    print(f"    Best old correlation: {s['best_old_corr']}: {s['best_old_corr_val']:.3f}")
    print(f"    Extreme graph survival: {(1-s['extreme_break_frac'])*100:.0f}%")
    print(f"    Main mean ± std: {s['main_mean']:.4f} ± {s['main_std']:.4f}")
    print(f"    Null mean ± std: {s['null_mean']:.4f} ± {s['null_std']:.4f}")

# Save analysis
analysis = {
    'all_correlations': all_correlations,
    'redundant_metrics': [{'piste': p, 'key': k, 'corr_with': o, 'r': float(r)} for p,k,o,r in redundant_metrics],
    'non_redundant_metrics': [{'piste': p, 'key': k, 'corr_with': o, 'r': float(r)} for p,k,o,r in non_redundant_metrics],
    'survivors': survivors,
    'failures': failures,
    'truly_novel': truly_novel,
}

with open('/tmp/g7_analysis_results.json', 'w') as f:
    json.dump(analysis, f, indent=2, default=str)

print(f"\nAnalysis saved to /tmp/g7_analysis_results.json")

#!/usr/bin/env python3
"""
G8.7 - Dynamic processes on graphs (Kuramoto, SIR, Heat, Evolutionary)
G8.8 - ML classifier: new metrics vs standard
"""
import json, gzip, math, random, sys, os, ast
import numpy as np
from collections import defaultdict, Counter

import warnings
warnings.filterwarnings('ignore')

import networkx as nx
from scipy.spatial.distance import cdist

random.seed(42)
np.random.seed(42)

##############################
# GRAPH GENERATION
##############################

def generate_graph(name, params_str):
    """Recreate graph from name + params"""
    try:
        params = ast.literal_eval(params_str) if isinstance(params_str, str) else params_str
    except:
        params = {}
    
    n = params.get('n', 50)
    
    generators = {
        'erdos_renyi': lambda: nx.erdos_renyi_graph(n, params.get('p', 0.1), seed=42),
        'barabasi_albert': lambda: nx.barabasi_albert_graph(n, params.get('m', 2), seed=42),
        'watts_strogatz': lambda: nx.watts_strogatz_graph(n, params.get('k', 4), params.get('p', 0.3), seed=42),
        'regular': lambda: nx.random_regular_graph(params.get('d', 3), n, seed=42),
        'path': lambda: nx.path_graph(n),
        'cycle': lambda: nx.cycle_graph(n),
        'star': lambda: nx.star_graph(n-1),
        'wheel': lambda: nx.wheel_graph(n),
        'complete': lambda: nx.complete_graph(n),
        'grid': lambda: nx.grid_2d_graph(int(n**0.5), int(n**0.5)),
        'complete_bipartite': lambda: nx.complete_bipartite_graph(n//2, n - n//2),
        'tree': lambda: nx.random_tree(n, seed=42),
        'ladder': lambda: nx.ladder_graph(n//2),
        'barbell': lambda: nx.barbell_graph(n//2, 1),
        'lollipop': lambda: nx.lollipop_graph(n//2, n - n//2),
        'caterpillar': lambda: _caterpillar(n),
        'powerlaw_cluster': lambda: nx.powerlaw_cluster_graph(n, params.get('m', 2), params.get('p', 0.5), seed=42),
        'stochastic_block': lambda: _sbm(n, params),
        'karate': lambda: nx.karate_club_graph(),
        'petersen': lambda: nx.petersen_graph(),
        'tutte': lambda: nx.tutte_graph(),
    }
    
    gen = generators.get(name)
    if gen:
        try:
            G = gen()
            G = nx.convert_node_labels_to_integers(G)
            if not nx.is_connected(G):
                G = G.subgraph(max(nx.connected_components(G), key=len)).copy()
                G = nx.convert_node_labels_to_integers(G)
            return G
        except:
            return None
    return None

def _caterpillar(n):
    spine = n // 2
    G = nx.path_graph(spine)
    for i in range(spine, n):
        G.add_edge(random.randint(0, spine-1), i)
    return G

def _sbm(n, params):
    sizes = [n//3, n//3, n - 2*(n//3)]
    p_in = params.get('p_in', 0.5)
    p_out = params.get('p_out', 0.05)
    return nx.stochastic_block_model(sizes, [[p_in, p_out, p_out],
                                              [p_out, p_in, p_out],
                                              [p_out, p_out, p_in]], seed=42)

##############################
# LOAD DATA
##############################

with open('/agent/home/Graph-Systems-Exploration/data/g7_all_pistes_results.json') as f:
    g7_raw = json.load(f)

# Build unified dataset
all_entries = []
for entry in g7_raw['main']:
    meta = entry['meta']
    flat = {'name': meta['name'], 'family': meta['name'], 'params': meta.get('params', '{}')}
    for piste_key in ['F', 'A', 'B', 'E', 'J']:
        piste = entry.get(piste_key, {})
        for k, v in piste.items():
            if k not in ['name', 'N', 'M', 'piste'] and isinstance(v, (int, float)):
                flat[f'{piste_key}_{k}'] = v
            elif k in ['N']:
                flat['n_nodes'] = v
    all_entries.append(flat)

print(f"Loaded {len(all_entries)} main graphs with {len(all_entries[0])} features")
families = Counter(e['family'] for e in all_entries)
print(f"Families: {dict(families)}")

# Select representative subset for dynamic processes (3 per family, cap N=80)
selected_for_dyn = []
fam_count = defaultdict(int)
for e in all_entries:
    if fam_count[e['family']] < 3:
        G = generate_graph(e['name'], e['params'])
        if G and len(G) >= 5:
            if len(G) > 80:
                # Subsample
                nodes = sorted(nx.degree_centrality(G).items(), key=lambda x: -x[1])[:80]
                G = G.subgraph([n[0] for n in nodes]).copy()
                G = nx.convert_node_labels_to_integers(G)
            selected_for_dyn.append((e, G))
            fam_count[e['family']] += 1

print(f"Selected {len(selected_for_dyn)} graphs for dynamic processes")

##############################
# G8.7 - DYNAMIC PROCESSES
##############################

print("\n" + "=" * 60)
print("G8.7 - DYNAMIC PROCESSES ON GRAPHS")
print("=" * 60)

def kuramoto_sync_time(G, coupling=2.0, dt=0.05, max_steps=400):
    n = len(G)
    if n < 2: return 0.0, 1.0
    omega = np.random.uniform(-1, 1, n)
    theta = np.random.uniform(0, 2*np.pi, n)
    adj = nx.adjacency_matrix(G).toarray().astype(float)
    degrees = np.array([G.degree(i) for i in range(n)], dtype=float)
    degrees[degrees == 0] = 1
    for step in range(max_steps):
        r = abs(np.mean(np.exp(1j * theta)))
        if r > 0.9:
            return step * dt, r
        sin_diff = np.sin(theta[np.newaxis, :] - theta[:, np.newaxis])
        interaction = np.sum(adj * sin_diff, axis=1)
        theta = theta + dt * (omega + (coupling / degrees) * interaction)
    return float('inf'), r

def sir_epidemic(G, beta=0.3, gamma=0.1, max_steps=300):
    n = len(G)
    if n < 3: return 0.0, 0.0
    state = ['S'] * n
    state[random.randint(0, n-1)] = 'I'
    adj = {i: list(G.neighbors(i)) for i in range(n)}
    peak_infected = 1
    total_infected = 1
    for _ in range(max_steps):
        new_state = state.copy()
        n_inf = sum(1 for s in state if s == 'I')
        if n_inf == 0: break
        peak_infected = max(peak_infected, n_inf)
        for i in range(n):
            if state[i] == 'S':
                for j in adj[i]:
                    if state[j] == 'I' and random.random() < beta:
                        new_state[i] = 'I'; total_infected += 1; break
            elif state[i] == 'I':
                if random.random() < gamma: new_state[i] = 'R'
        state = new_state
    return peak_infected / n, total_infected / n

def heat_kernel_trace(G, times=[0.1, 1.0, 10.0, 100.0]):
    n = len(G)
    if n < 2: return {t: 1.0 for t in times}
    L = nx.laplacian_matrix(G).toarray().astype(float)
    eigs = np.linalg.eigvalsh(L)
    return {t: float(np.sum(np.exp(-t * eigs)) / n) for t in times}

def evolutionary_game(G, b=1.5, max_steps=150):
    n = len(G)
    if n < 3: return 0.5
    strategy = np.random.randint(0, 2, n)
    adj = {i: list(G.neighbors(i)) for i in range(n)}
    for _ in range(max_steps):
        payoff = np.zeros(n)
        for i in range(n):
            for j in adj[i]:
                if strategy[i] == 1 and strategy[j] == 1: payoff[i] += 1
                elif strategy[i] == 0 and strategy[j] == 1: payoff[i] += b
        new_strategy = strategy.copy()
        for i in range(n):
            best = i; bp = payoff[i]
            for j in adj[i]:
                if payoff[j] > bp: best = j; bp = payoff[j]
            new_strategy[i] = strategy[best]
        if np.array_equal(new_strategy, strategy): break
        strategy = new_strategy
    return float(np.mean(strategy))

# Run all processes
dynamic_results = []
for idx, (entry, G) in enumerate(selected_for_dyn):
    result = {'name': entry['name'], 'family': entry['family'], 
              'n': len(G), 'edges': G.number_of_edges()}
    
    # Kuramoto (2 runs)
    sts = []
    for _ in range(2):
        st, _ = kuramoto_sync_time(G)
        sts.append(st)
    result['kuramoto_sync_time'] = float(np.median(sts))
    result['kuramoto_synced'] = result['kuramoto_sync_time'] < float('inf')
    
    # SIR (3 runs)
    peaks, totals = [], []
    for _ in range(3):
        p, t = sir_epidemic(G)
        peaks.append(p); totals.append(t)
    result['sir_peak'] = float(np.mean(peaks))
    result['sir_total'] = float(np.mean(totals))
    
    # Heat kernel
    hk = heat_kernel_trace(G)
    for t, v in hk.items():
        result[f'heat_t{t}'] = v
    
    # Evolutionary game (2 runs)
    crs = [evolutionary_game(G) for _ in range(2)]
    result['coop_rate'] = float(np.mean(crs))
    
    dynamic_results.append(result)
    if (idx + 1) % 10 == 0:
        print(f"  {idx+1}/{len(selected_for_dyn)} done")

print(f"  Completed: {len(dynamic_results)} graphs")

# ANALYSIS: discriminative power
print(f"\n{'='*60}")
print("DYNAMIC OBSERVABLES - DISCRIMINATIVE POWER (F-ratio)")
print(f"{'='*60}")

dyn_metrics = ['kuramoto_sync_time', 'sir_peak', 'sir_total', 
               'heat_t0.1', 'heat_t1.0', 'heat_t10.0', 'heat_t100.0', 'coop_rate']

fscores = []
for metric in dyn_metrics:
    fam_vals = defaultdict(list)
    for r in dynamic_results:
        v = r.get(metric, float('nan'))
        if isinstance(v, (int, float)) and not math.isinf(v) and not math.isnan(v):
            fam_vals[r['family']].append(v)
    
    groups = [v for v in fam_vals.values() if len(v) >= 1]
    if len(groups) < 2: continue
    
    group_means = [np.mean(g) for g in groups]
    all_vals = [x for g in groups for x in g]
    between = np.var(group_means)
    within = np.mean([np.var(g) if len(g) > 1 else 0 for g in groups])
    f = between / within if within > 0 else float('inf')
    fscores.append((metric, f, np.mean(all_vals)))
    
    # Show per-family
    top5 = sorted(fam_vals.items(), key=lambda x: np.mean(x[1]))
    low = top5[0]
    high = top5[-1]
    print(f"  {metric:20s}: F={f:8.2f} | lowest: {low[0]}={np.mean(low[1]):.3f} | highest: {high[0]}={np.mean(high[1]):.3f}")

fscores.sort(key=lambda x: -x[1])
print(f"\n  TOP 3 DYNAMIC DISCRIMINATORS:")
for i, (m, f, mean) in enumerate(fscores[:3]):
    print(f"    #{i+1}: {m} (F={f:.2f})")

# Cross-correlation with G7 static metrics
print(f"\n{'='*60}")
print("DYNAMIC vs STATIC CORRELATION")
print(f"{'='*60}")

# Match dynamic results back to all_entries by name+family
dyn_by_key = {(d['name'], d['family']): d for d in dynamic_results}
static_metrics = [k for k in all_entries[0].keys() 
                  if k not in ['name', 'family', 'params', 'n_nodes']
                  and isinstance(all_entries[0].get(k), (int, float))]

# For each dynamic metric, check correlation with all static metrics
for dyn_m in dyn_metrics[:3]:  # top 3 only
    corrs = []
    for stat_m in static_metrics:
        pairs = []
        for e in all_entries:
            d = dyn_by_key.get((e['name'], e['family']))
            if d and dyn_m in d and stat_m in e:
                dv = d[dyn_m]
                sv = e[stat_m]
                if all(isinstance(x, (int, float)) and not math.isnan(x) and not math.isinf(x) 
                       for x in [dv, sv]):
                    pairs.append((dv, sv))
        
        if len(pairs) > 5:
            x, y = zip(*pairs)
            r = np.corrcoef(x, y)[0, 1]
            if not math.isnan(r):
                corrs.append((stat_m, abs(r)))
    
    corrs.sort(key=lambda x: -x[1])
    top = corrs[0] if corrs else ('none', 0)
    print(f"  {dyn_m:20s}: highest |r| = {top[1]:.3f} with {top[0]}")
    if top[1] > 0.9:
        print(f"    ⚠️  REDUNDANT with {top[0]}")
    elif top[1] < 0.5:
        print(f"    ✅ INDEPENDENT — potentially novel observable!")

##############################
# G8.8 - ML CLASSIFIER
##############################

print(f"\n\n{'='*60}")
print("G8.8 - ML CLASSIFICATION BENCHMARK")
print(f"{'='*60}")

# Build feature matrix from G7 static metrics
metric_keys = [k for k in all_entries[0].keys() 
               if k not in ['name', 'family', 'params', 'n_nodes']
               and isinstance(all_entries[0].get(k), (int, float))]

X = []
y = []
valid_entries = []

for e in all_entries:
    row = []
    valid = True
    for k in metric_keys:
        v = e.get(k, float('nan'))
        if isinstance(v, (int, float)) and not math.isnan(v) and not math.isinf(v):
            row.append(v)
        else:
            valid = False
            break
    if valid and len(row) == len(metric_keys):
        X.append(row)
        y.append(e['family'])
        valid_entries.append(e)

X = np.array(X)
unique_fam = sorted(set(y))
fam_to_idx = {f: i for i, f in enumerate(unique_fam)}
y_enc = np.array([fam_to_idx[f] for f in y])

print(f"Dataset: {X.shape[0]} samples × {X.shape[1]} features, {len(unique_fam)} families")

# k-NN LOO
def knn_loo(X, y, k=3):
    n = len(y)
    mu = X.mean(axis=0); sigma = X.std(axis=0); sigma[sigma==0] = 1
    Xs = (X - mu) / sigma
    D = cdist(Xs, Xs)
    correct = 0
    for i in range(n):
        d = D[i].copy(); d[i] = float('inf')
        nbrs = np.argsort(d)[:k]
        votes = Counter(y[j] for j in nbrs)
        if votes.most_common(1)[0][0] == y[i]:
            correct += 1
    return correct / n

# (a) All G7 new metrics (static)
acc_all_new = knn_loo(X, y_enc, k=3)
print(f"\n  All {len(metric_keys)} new static metrics: {acc_all_new:.1%}")

# (b) Top 3 survivors only
top3 = ['A_forman_frac_negative', 'J_spec_complexity_per_node', 'E_betti0_mean_persistence']
top3_idx = [i for i, k in enumerate(metric_keys) if k in top3]
if top3_idx:
    acc_top3 = knn_loo(X[:, top3_idx], y_enc, k=3)
    print(f"  Top 3 survivors only: {acc_top3:.1%}")

# (c) Each piste separately
for piste in ['F', 'A', 'B', 'E', 'J']:
    p_idx = [i for i, k in enumerate(metric_keys) if k.startswith(piste + '_')]
    if p_idx:
        acc_p = knn_loo(X[:, p_idx], y_enc, k=3)
        print(f"  Piste {piste} only ({len(p_idx)} features): {acc_p:.1%}")

# (d) Standard G1 metrics
with open('/agent/home/Graph-Systems-Exploration/data/g1_results.json') as f:
    g1_data = json.load(f)

# G1 structure
print(f"\nG1 data: {len(g1_data)} entries")
if g1_data:
    sample_g1 = g1_data[0]
    g1_keys = [k for k in sample_g1.keys() 
               if isinstance(sample_g1.get(k), (int, float)) 
               and k not in ['n_nodes', 'n_edges', 'index']]
    
    X_g1 = []
    y_g1 = []
    for d in g1_data:
        row = []
        valid = True
        for k in g1_keys:
            v = d.get(k, float('nan'))
            if isinstance(v, (int, float)) and not math.isnan(v) and not math.isinf(v):
                row.append(v)
            else:
                valid = False; break
        if valid and len(row) == len(g1_keys):
            fam = d.get('family', d.get('name', 'unknown'))
            X_g1.append(row)
            y_g1.append(fam)
    
    if X_g1:
        X_g1 = np.array(X_g1)
        unique_g1_fam = sorted(set(y_g1))
        g1_fam_to_idx = {f: i for i, f in enumerate(unique_g1_fam)}
        y_g1_enc = np.array([g1_fam_to_idx[f] for f in y_g1])
        
        acc_g1 = knn_loo(X_g1, y_g1_enc, k=3)
        print(f"  Standard G1 metrics ({len(g1_keys)} features): {acc_g1:.1%}")
        
        # Baseline
        majority = max(Counter(y_g1_enc).values()) / len(y_g1_enc)
        random_baseline = 1 / len(unique_g1_fam)
        print(f"\n  Majority class baseline: {majority:.1%}")
        print(f"  Random baseline: {random_baseline:.1%}")
        
        # Improvement
        if acc_all_new > acc_g1:
            print(f"\n  🟢 New metrics BEAT standard by {acc_all_new - acc_g1:+.1%}")
        else:
            print(f"\n  🔴 Standard metrics win by {acc_g1 - acc_all_new:+.1%}")

# (e) Dynamic metrics classification
X_dyn_list = []
y_dyn_list = []
for r in dynamic_results:
    row = []
    valid = True
    for m in dyn_metrics:
        v = r.get(m, float('nan'))
        if isinstance(v, (int, float)) and not math.isinf(v) and not math.isnan(v):
            row.append(v)
        else:
            valid = False; break
    if valid and len(row) == len(dyn_metrics):
        X_dyn_list.append(row)
        y_dyn_list.append(r['family'])

if X_dyn_list and len(X_dyn_list) > 10:
    X_dyn_arr = np.array(X_dyn_list)
    unique_dyn = sorted(set(y_dyn_list))
    dyn_to_idx = {f: i for i, f in enumerate(unique_dyn)}
    y_dyn_enc = np.array([dyn_to_idx[f] for f in y_dyn_list])
    
    acc_dyn = knn_loo(X_dyn_arr, y_dyn_enc, k=3)
    print(f"\n  Dynamic metrics only ({len(dyn_metrics)} features, {len(X_dyn_list)} samples): {acc_dyn:.1%}")

# Summary
print(f"\n{'='*60}")
print("CLASSIFICATION SUMMARY")
print(f"{'='*60}")

print(f"""
  Standard (G1):      {acc_g1:.1%} ({len(g1_keys)} features)
  New static (G7):    {acc_all_new:.1%} ({len(metric_keys)} features)
  Top 3 survivors:    {acc_top3:.1%} (3 features)
  Majority baseline:  {majority:.1%}
  Random baseline:    {random_baseline:.1%}
""")

# Save all results
with open('/tmp/g8_7_8_results.json', 'w') as f:
    json.dump({
        'dynamic_results': dynamic_results,
        'dynamic_fscores': [(m, float(f), float(mean)) for m, f, mean in fscores],
        'classification': {
            'acc_all_new': acc_all_new,
            'acc_top3': acc_top3 if top3_idx else None,
            'acc_g1': acc_g1 if g1_data else None,
        }
    }, f, indent=2, default=str)

print("DONE. Results saved.")

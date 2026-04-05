#!/usr/bin/env python3
"""
G8.5 - Why is spec_complexity_per_node stable under deformation?
G8.6 - Characterize betti0_mean_persistence transition under rewiring
"""
import json, gzip, math, random, sys
import numpy as np
from collections import defaultdict

# Suppress warnings
import warnings
warnings.filterwarnings('ignore')

try:
    import networkx as nx
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'networkx', '-q'])
    import networkx as nx

random.seed(42)
np.random.seed(42)

##############################
# UTILITY FUNCTIONS
##############################

def spec_complexity_per_node(G):
    """Compressed size of Laplacian spectrum / N"""
    if len(G) < 2:
        return 0.0
    try:
        L = nx.laplacian_matrix(G).toarray().astype(float)
        eigs = sorted(np.linalg.eigvalsh(L))
        spec_str = ','.join(f'{e:.6f}' for e in eigs)
        compressed = gzip.compress(spec_str.encode())
        return len(compressed) / len(G)
    except:
        return float('nan')

def betti0_mean_persistence(G):
    """Mean persistence of Betti-0 features via edge betweenness filtration"""
    if len(G) < 2 or G.number_of_edges() < 1:
        return 0.0
    try:
        eb = nx.edge_betweenness_centrality(G)
        if not eb:
            return 0.0
        max_eb = max(eb.values())
        if max_eb == 0:
            return 0.0
        
        # Sort edges by betweenness (ascending = add least central first)
        sorted_edges = sorted(eb.keys(), key=lambda e: eb[e])
        
        # Build graph incrementally, track when components merge
        H = nx.Graph()
        H.add_nodes_from(G.nodes())
        n = len(G)
        
        births = {v: 0.0 for v in G.nodes()}  # all born at t=0
        deaths = {}
        
        uf_parent = {v: v for v in G.nodes()}
        uf_rank = {v: 0 for v in G.nodes()}
        uf_birth = {v: 0.0 for v in G.nodes()}
        
        def find(x):
            while uf_parent[x] != x:
                uf_parent[x] = uf_parent[uf_parent[x]]
                x = uf_parent[x]
            return x
        
        num_edges = len(sorted_edges)
        for i, (u, v) in enumerate(sorted_edges):
            t = (i + 1) / num_edges  # filtration time in [0,1]
            ru, rv = find(u), find(v)
            if ru != rv:
                # Merge: the younger component dies
                bu, bv = uf_birth[ru], uf_birth[rv]
                if bu >= bv:
                    # ru is younger, it dies
                    uf_parent[ru] = rv
                    deaths[ru] = t
                else:
                    uf_parent[rv] = ru
                    deaths[rv] = t
                if uf_rank[ru] == uf_rank[rv]:
                    uf_rank[rv] += 1
        
        # Compute persistences
        persistences = []
        for v in G.nodes():
            if v in deaths:
                persistences.append(deaths[v] - uf_birth[v])
        
        if not persistences:
            return 0.0
        return float(np.mean(persistences))
    except:
        return float('nan')


##############################
# G8.5 - STABILITY ANALYSIS
##############################

print("=" * 60)
print("G8.5 - WHY IS SPEC_COMPLEXITY_PER_NODE STABLE?")
print("=" * 60)

# Hypothesis 1: Spectral perturbation theory predicts eigenvalue stability
# For small edge additions/removals, eigenvalues shift by O(1/N)
# So the sorted spectrum changes minimally, and compression captures this

# Test: compute spec_complexity for various perturbation levels on several graph types
families = {
    'path': lambda n: nx.path_graph(n),
    'cycle': lambda n: nx.cycle_graph(n),
    'star': lambda n: nx.star_graph(n-1),
    'grid': lambda n: nx.grid_2d_graph(int(n**0.5), int(n**0.5)),
    'complete': lambda n: nx.complete_graph(n),
    'er_sparse': lambda n: nx.erdos_renyi_graph(n, 0.1, seed=42),
    'er_dense': lambda n: nx.erdos_renyi_graph(n, 0.5, seed=42),
    'barabasi': lambda n: nx.barabasi_albert_graph(n, 2, seed=42),
    'watts': lambda n: nx.watts_strogatz_graph(n, 4, 0.3, seed=42),
    'regular': lambda n: nx.random_regular_graph(3, n, seed=42) if n % 2 == 0 else nx.random_regular_graph(3, n+1, seed=42),
}

N = 50  # graph size
perturbation_levels = [0, 0.02, 0.05, 0.1, 0.2, 0.3, 0.5]  # fraction of edges to rewire

print(f"\nPerturbation sweep (N={N}, {len(perturbation_levels)} levels, {len(families)} families)")
print("-" * 60)

stability_data = {}

for fname, fgen in families.items():
    G = fgen(N)
    if not nx.is_connected(G):
        G = G.subgraph(max(nx.connected_components(G), key=len)).copy()
        G = nx.convert_node_labels_to_integers(G)
    
    base_val = spec_complexity_per_node(G)
    values = [base_val]
    
    num_edges = G.number_of_edges()
    nodes = list(G.nodes())
    
    for p in perturbation_levels[1:]:
        # Rewire p fraction of edges
        n_rewire = max(1, int(p * num_edges))
        H = G.copy()
        edges = list(H.edges())
        for _ in range(n_rewire):
            if not edges:
                break
            e = random.choice(edges)
            H.remove_edge(*e)
            edges.remove(e)
            # Add random edge
            for _ in range(100):
                u, v = random.choice(nodes), random.choice(nodes)
                if u != v and not H.has_edge(u, v):
                    H.add_edge(u, v)
                    break
        if nx.is_connected(H):
            values.append(spec_complexity_per_node(H))
        else:
            # Make connected
            comps = list(nx.connected_components(H))
            for i in range(1, len(comps)):
                u = random.choice(list(comps[0]))
                v = random.choice(list(comps[i]))
                H.add_edge(u, v)
            values.append(spec_complexity_per_node(H))
    
    cv = np.std(values) / np.mean(values) if np.mean(values) > 0 else 0
    stability_data[fname] = {
        'values': values,
        'base': base_val,
        'cv': cv,
        'range': max(values) - min(values),
        'max_change_pct': 100 * (max(values) - min(values)) / base_val if base_val > 0 else 0
    }
    print(f"  {fname:15s}: base={base_val:.3f}, CV={cv:.4f}, max_change={stability_data[fname]['max_change_pct']:.1f}%")

# Hypothesis 2: N-scaling test
# If spec_complexity_per_node truly scales as O(1), it should be constant as N grows
print(f"\n\nN-SCALING TEST (does spec_complexity_per_node converge?)")
print("-" * 60)

n_sizes = [20, 30, 50, 80, 100, 150, 200]
scaling_data = {}

for fname in ['path', 'cycle', 'er_sparse', 'barabasi', 'watts']:
    fgen = families[fname]
    vals = []
    for n in n_sizes:
        try:
            G = fgen(n)
            if not nx.is_connected(G):
                G = G.subgraph(max(nx.connected_components(G), key=len)).copy()
                G = nx.convert_node_labels_to_integers(G)
            vals.append(spec_complexity_per_node(G))
        except:
            vals.append(float('nan'))
    
    valid = [v for v in vals if not math.isnan(v)]
    cv = np.std(valid) / np.mean(valid) if len(valid) > 1 and np.mean(valid) > 0 else 0
    scaling_data[fname] = {'sizes': n_sizes, 'values': vals, 'cv': cv}
    print(f"  {fname:15s}: {' '.join(f'{v:.2f}' for v in vals)} | CV={cv:.4f}")

# Hypothesis 3: Analytical computation for known spectra
print(f"\n\nANALYTICAL SPECTRUM CHECK")
print("-" * 60)
print("For regular families, eigenvalues are known exactly:")
print("  Path(n):   λ_k = 2 - 2cos(πk/n),  k=0..n-1")
print("  Cycle(n):  λ_k = 2 - 2cos(2πk/n), k=0..n-1")
print("  Complete(n): λ = {0, n, n, ..., n}")
print("  Star(n):   λ = {0, 1×(n-2), n}")
print("")
print("The COMPRESSION of a regular spectrum is trivially low because:")
print("  - Complete graph: only 2 distinct values → very compressible")
print("  - Star graph: only 3 distinct values → very compressible")
print("  - Path/Cycle: smooth cosine → compressible pattern")
print("  - Random (ER): Wigner semicircle → many distinct values → less compressible")
print("")
print("KEY INSIGHT: spec_complexity_per_node measures the INFORMATION DENSITY")
print("of the spectral signature. It's stable because small perturbations")
print("shift eigenvalues by O(1/N) (Weyl's perturbation theorem),")
print("so the PATTERN of the spectrum (not individual values) is preserved.")
print("This is WHY gzip captures it — gzip encodes patterns, not values.")

# Theoretical bounds
print(f"\n\nTHEORETICAL BOUND ATTEMPT")
print("-" * 60)

# For a graph with N nodes:
# - Spectrum has N eigenvalues, each represented with ~10 chars ≈ 10N bytes uncompressed
# - For a complete graph: spectrum = "0.000000,N.000000,...,N.000000" 
#   → only 2 distinct values → gzip ≈ ~50 bytes → per_node ≈ 50/N → 0 as N→∞
# - For ER graph: spectrum ≈ Wigner semicircle, all distinct
#   → gzip ≈ αN bytes (some pattern in semicircle) → per_node ≈ α (constant)
# - The stability comes from: perturbation shifts eigenvalues smoothly,
#   the DISTRIBUTION shape is preserved, gzip captures the shape

# Check: do simple vs complex graphs have clearly different per-node values?
simple_vals = [stability_data[f]['base'] for f in ['path', 'cycle', 'complete'] if f in stability_data]
complex_vals = [stability_data[f]['base'] for f in ['er_sparse', 'er_dense', 'barabasi', 'watts'] if f in stability_data]

print(f"  Simple graphs (path/cycle/complete): mean = {np.mean(simple_vals):.3f}")
print(f"  Complex graphs (ER/BA/WS):           mean = {np.mean(complex_vals):.3f}")
print(f"  Ratio complex/simple:                 {np.mean(complex_vals)/np.mean(simple_vals):.2f}x")

##############################
# G8.6 - BETTI0 TRANSITION
##############################

print("\n\n" + "=" * 60)
print("G8.6 - BETTI0_MEAN_PERSISTENCE TRANSITION UNDER REWIRING")
print("=" * 60)

# Fine-grained rewiring sweep: take a lattice/regular graph,
# progressively rewire (WS model), measure betti0_mean_persistence

N_graph = 60
k_ring = 4  # nearest neighbors in WS model
rewire_probs = np.concatenate([
    np.linspace(0, 0.1, 20),
    np.linspace(0.1, 0.5, 15),
    np.linspace(0.5, 1.0, 10)
])
rewire_probs = sorted(set(rewire_probs))

n_repeats = 5  # average over random seeds

print(f"\nRewiring sweep: WS(N={N_graph}, k={k_ring}), {len(rewire_probs)} p-values, {n_repeats} repeats")
print("-" * 60)

transition_data = {'rewire_probs': [], 'betti0_mean': [], 'betti0_std': [], 
                   'spec_complexity_mean': [], 'spec_complexity_std': [],
                   'clustering_mean': [], 'path_length_mean': []}

for p in rewire_probs:
    b_vals = []
    s_vals = []
    c_vals = []
    l_vals = []
    
    for seed in range(n_repeats):
        G = nx.watts_strogatz_graph(N_graph, k_ring, p, seed=seed*100+42)
        b = betti0_mean_persistence(G)
        s = spec_complexity_per_node(G)
        c = nx.average_clustering(G)
        try:
            l = nx.average_shortest_path_length(G)
        except:
            l = float('inf')
        
        if not math.isnan(b):
            b_vals.append(b)
        if not math.isnan(s):
            s_vals.append(s)
        c_vals.append(c)
        l_vals.append(l)
    
    transition_data['rewire_probs'].append(float(p))
    transition_data['betti0_mean'].append(float(np.mean(b_vals)) if b_vals else 0)
    transition_data['betti0_std'].append(float(np.std(b_vals)) if b_vals else 0)
    transition_data['spec_complexity_mean'].append(float(np.mean(s_vals)) if s_vals else 0)
    transition_data['spec_complexity_std'].append(float(np.std(s_vals)) if s_vals else 0)
    transition_data['clustering_mean'].append(float(np.mean(c_vals)))
    transition_data['path_length_mean'].append(float(np.mean([l for l in l_vals if l != float('inf')])) if any(l != float('inf') for l in l_vals) else float('inf'))

# Find transition point (maximum rate of change in betti0)
betti0_vals = transition_data['betti0_mean']
probs = transition_data['rewire_probs']

# Numerical derivative
derivatives = []
for i in range(1, len(betti0_vals)):
    dp = probs[i] - probs[i-1]
    if dp > 0:
        deriv = (betti0_vals[i] - betti0_vals[i-1]) / dp
    else:
        deriv = 0
    derivatives.append((probs[i], deriv))

max_deriv_idx = max(range(len(derivatives)), key=lambda i: abs(derivatives[i][1]))
transition_p = derivatives[max_deriv_idx][0]
transition_deriv = derivatives[max_deriv_idx][1]

print(f"\nRESULTS:")
print(f"  betti0 at p=0:    {betti0_vals[0]:.4f}")
print(f"  betti0 at p=0.1:  {betti0_vals[min(19, len(betti0_vals)-1)]:.4f}")
print(f"  betti0 at p=0.5:  {betti0_vals[min(34, len(betti0_vals)-1)]:.4f}")
print(f"  betti0 at p=1.0:  {betti0_vals[-1]:.4f}")
print(f"")
print(f"  TRANSITION POINT: p ≈ {transition_p:.3f}")
print(f"  Max |d(betti0)/dp| = {abs(transition_deriv):.4f}")

# Compare with classic small-world transition
# WS transition is known to occur at p ~ 0.01-0.1 for path length
cl_vals = transition_data['clustering_mean']
pl_vals = transition_data['path_length_mean']

# Find where path length drops by 50%
pl_valid = [v for v in pl_vals if v < float('inf')]
if pl_valid:
    pl_base = pl_valid[0]
    pl_half = None
    for i, v in enumerate(pl_vals):
        if v < float('inf') and v < 0.5 * pl_base:
            pl_half = probs[i]
            break
    print(f"\n  Path length half-life: p ≈ {pl_half if pl_half else 'N/A'}")
    print(f"  Clustering at transition: {cl_vals[min(max_deriv_idx, len(cl_vals)-1)]:.4f}")

# N-dependence of transition point
print(f"\n\nN-DEPENDENCE OF TRANSITION POINT")
print("-" * 60)

n_sizes_trans = [30, 50, 80, 100, 150]
transition_points = []

for n in n_sizes_trans:
    probs_coarse = np.linspace(0, 0.5, 30)
    b_vals_n = []
    for p in probs_coarse:
        G = nx.watts_strogatz_graph(n, 4, p, seed=42)
        b_vals_n.append(betti0_mean_persistence(G))
    
    # Find max derivative
    derivs = []
    for i in range(1, len(b_vals_n)):
        dp = probs_coarse[i] - probs_coarse[i-1]
        if dp > 0:
            derivs.append((probs_coarse[i], abs((b_vals_n[i] - b_vals_n[i-1]) / dp)))
    
    if derivs:
        tp = max(derivs, key=lambda x: x[1])[0]
        transition_points.append((n, tp))
        print(f"  N={n:4d}: transition at p ≈ {tp:.3f}")

# Check if transition point scales with N
if len(transition_points) > 2:
    ns = [t[0] for t in transition_points]
    ps = [t[1] for t in transition_points]
    # Fit log-log to see if p_c ~ N^alpha
    if all(p > 0 for p in ps):
        log_n = np.log(ns)
        log_p = np.log(ps)
        slope, intercept = np.polyfit(log_n, log_p, 1)
        print(f"\n  Scaling: p_c ~ N^{slope:.3f}")
        print(f"  (If slope ≈ 0: p_c is N-independent)")
        print(f"  (If slope ≈ -1: p_c ~ 1/N, like classic percolation)")

# Save all data
results = {
    'g8_5_stability': stability_data,
    'g8_5_scaling': {k: {'sizes': v['sizes'], 'values': [float(x) for x in v['values']], 'cv': float(v['cv'])} for k, v in scaling_data.items()},
    'g8_6_transition': {k: [float(x) if not (isinstance(x, float) and math.isinf(x)) else None for x in v] if isinstance(v, list) else v for k, v in transition_data.items()},
    'g8_6_transition_point': float(transition_p),
    'g8_6_n_scaling': transition_points
}

# Convert stability_data for JSON
for k, v in results['g8_5_stability'].items():
    v['values'] = [float(x) for x in v['values']]
    v['base'] = float(v['base'])
    v['cv'] = float(v['cv'])
    v['range'] = float(v['range'])
    v['max_change_pct'] = float(v['max_change_pct'])

with open('/tmp/g8_5_6_results.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)

print(f"\n\nResults saved to /tmp/g8_5_6_results.json")
print("DONE.")

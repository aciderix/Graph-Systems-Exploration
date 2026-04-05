#!/usr/bin/env python3
"""
G9 FALSIFICATION — Test nonlinear conservation laws on FRESH graphs.
If residual stays small → real law. If it blows up → overfitting.
"""

import networkx as nx
import numpy as np
import json
import warnings
warnings.filterwarnings('ignore')

# Load the laws
with open('/tmp/g9_nontrivial.json') as f:
    all_laws = json.load(f)

# Only Strategy 3 (nonlinear)
s3_laws = [l for l in all_laws if l.get('strat') == 3]
print(f"Testing {len(s3_laws)} nonlinear laws on fresh graphs")

# ===================== OPERATIONS (same as before) =====================
def op_line(G):
    L = nx.line_graph(G)
    return L if len(L) >= 3 else None
def op_complement(G):
    C = nx.complement(G)
    return C if C.number_of_edges() > 0 else None
def op_square(G): return nx.power(G, 2)
def op_subdivision(G):
    S = nx.Graph()
    nid = max(G.nodes()) + 1
    S.add_nodes_from(G.nodes())
    for u, v in G.edges():
        S.add_node(nid); S.add_edge(u, nid); S.add_edge(nid, v); nid += 1
    return S
def op_corona(G):
    C = G.copy(); nid = max(G.nodes()) + 1
    for v in list(G.nodes()): C.add_node(nid); C.add_edge(v, nid); nid += 1
    return C
def op_mycielskian(G): return nx.mycielskian(G)
def op_cartesian_K2(G): return nx.cartesian_product(G, nx.path_graph(2))
def op_double(G):
    n = max(G.nodes()) + 1; D = G.copy()
    for v in list(G.nodes()): D.add_node(v + n)
    for u, v in G.edges(): D.add_edge(u + n, v + n)
    for v in list(G.nodes()): D.add_edge(v, v + n)
    return D

OPS = {'line': op_line, 'complement': op_complement, 'square': op_square,
       'subdivision': op_subdivision, 'corona': op_corona, 'mycielskian': op_mycielskian,
       'cart_K2': op_cartesian_K2, 'double': op_double}

# ===================== METRICS (same as before) =====================
def eigenvalues_adj(G):
    return np.linalg.eigvalsh(nx.adjacency_matrix(G).todense())
def eigenvalues_lap(G):
    return np.linalg.eigvalsh(nx.laplacian_matrix(G).todense().astype(float))

def safe(f, G):
    try:
        v = f(G)
        if v is None or (isinstance(v, float) and (np.isnan(v) or np.isinf(v))): return None
        return float(v)
    except: return None

def spanning_trees(G):
    if not nx.is_connected(G): return 0.0
    eigs = sorted(eigenvalues_lap(G))
    nz = [e for e in eigs if e > 1e-10]
    if not nz: return 0.0
    return float(np.exp(sum(np.log(e) for e in nz) - np.log(G.number_of_nodes())))

METRICS = {
    'n': lambda G: G.number_of_nodes(),
    'm': lambda G: G.number_of_edges(),
    'density': lambda G: nx.density(G),
    'avg_deg': lambda G: 2*G.number_of_edges()/G.number_of_nodes(),
    'max_deg': lambda G: max(d for _,d in G.degree()),
    'min_deg': lambda G: min(d for _,d in G.degree()),
    'deg_std': lambda G: np.std([d for _,d in G.degree()]),
    'clustering': lambda G: nx.average_clustering(G),
    'transitivity': lambda G: nx.transitivity(G),
    'triangles': lambda G: sum(nx.triangles(G).values())//3,
    'components': lambda G: nx.number_connected_components(G),
    'spectral_radius': lambda G: float(max(abs(eigenvalues_adj(G)))),
    'energy': lambda G: float(np.sum(np.abs(eigenvalues_adj(G)))),
    'lap_energy': lambda G: float(np.sum(np.abs(eigenvalues_lap(G) - np.mean(eigenvalues_lap(G))))),
    'spectral_gap': lambda G: float(sorted(eigenvalues_lap(G))[1]) if nx.is_connected(G) else 0.0,
    'lap_max': lambda G: float(max(eigenvalues_lap(G))),
    'adj_rank': lambda G: float(np.linalg.matrix_rank(nx.adjacency_matrix(G).todense())),
    'adj_trace_cube': lambda G: float(np.sum(eigenvalues_adj(G)**3)),
    'spanning_trees_log': lambda G: np.log1p(spanning_trees(G)),
    'edges_per_node': lambda G: G.number_of_edges() / G.number_of_nodes(),
    'm_over_n': lambda G: G.number_of_edges() / G.number_of_nodes(),
    'energy_over_n': lambda G: float(np.sum(np.abs(eigenvalues_adj(G)))) / G.number_of_nodes(),
    'energy_over_m': lambda G: float(np.sum(np.abs(eigenvalues_adj(G)))) / G.number_of_edges() if G.number_of_edges() > 0 else None,
    'sr_over_avg_deg': lambda G: float(max(abs(eigenvalues_adj(G)))) / (2*G.number_of_edges()/G.number_of_nodes()),
    'lap_max_over_max_deg': lambda G: float(max(eigenvalues_lap(G))) / max(d for _,d in G.degree()),
    'tri_over_m': lambda G: (sum(nx.triangles(G).values())//3) / G.number_of_edges() if G.number_of_edges() > 0 else 0,
}

# ===================== FRESH GRAPHS =====================
def gen_fresh():
    """100 completely new graphs with different seeds and sizes."""
    gs = []
    rng = np.random.RandomState(12345)  # Different seed from training
    
    for n in [7, 9, 11, 13, 17, 19, 22, 27, 33, 40]:
        # ER with random p
        for _ in range(3):
            p = rng.uniform(0.1, 0.6)
            G = nx.erdos_renyi_graph(n, p, seed=int(rng.randint(10000)))
            if nx.is_connected(G) and G.number_of_edges() > 0:
                gs.append((f'ER_{n}_{p:.2f}', G))
        
        # BA
        m = rng.randint(1, min(4, n))
        gs.append((f'BA_{n}_{m}', nx.barabasi_albert_graph(n, m, seed=int(rng.randint(10000)))))
        
        # WS
        k = 4 if n > 5 else 2
        p = rng.uniform(0.05, 0.5)
        gs.append((f'WS_{n}_{p:.2f}', nx.watts_strogatz_graph(n, k, p, seed=int(rng.randint(10000)))))
        
        # Random regular
        d = 3 if (n*3)%2==0 else 4
        if d < n:
            try:
                gs.append((f'REG_{n}_{d}', nx.random_regular_graph(d, n, seed=int(rng.randint(10000)))))
            except: pass
        
        # Special structures
        gs.append((f'CYCLE_{n}', nx.cycle_graph(n)))
        if n <= 15:
            gs.append((f'COMPLETE_{n}', nx.complete_graph(n)))
        gs.append((f'TREE_{n}', nx.random_labeled_tree(n, seed=int(rng.randint(10000)))))
    
    # Exotic graphs
    gs.append(('MOEBIUS_KANTOR', nx.moebius_kantor_graph()))
    gs.append(('PAPPUS', nx.pappus_graph()))
    gs.append(('HEAWOOD', nx.heawood_graph()))
    
    # Random bipartite
    for n in [10, 20, 30]:
        G = nx.complete_bipartite_graph(n//3, n - n//3)
        gs.append((f'BIPARTITE_{n}', G))
    
    # Barbell
    for n in [5, 8, 10]:
        gs.append((f'BARBELL_{n}', nx.barbell_graph(n, 1)))
    
    print(f"Generated {len(gs)} fresh test graphs")
    return gs

# ===================== TEST LAWS =====================
def main():
    print("="*70)
    print("G9 FALSIFICATION — Testing nonlinear laws on fresh data")
    print("="*70)
    
    graphs = gen_fresh()
    
    # Compute metrics
    print("\nComputing metrics on fresh graphs...")
    orig = {}
    for key, G in graphs:
        orig[key] = {m: safe(f, G) for m, f in METRICS.items()}
    
    # Apply transformations
    print("Applying transformations...")
    trans = {}
    for opname, opfunc in OPS.items():
        trans[opname] = {}
        for key, G in graphs:
            try:
                T = opfunc(G)
                if T and len(T) >= 3 and T.number_of_edges() > 0 and len(T) <= 500:
                    trans[opname][key] = {m: safe(f, T) for m, f in METRICS.items()}
            except: pass
    
    # Test each law
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    
    surviving = []
    killed = []
    
    for i, law in enumerate(s3_laws):
        op = law['op']
        coeffs = law.get('coefficients', {})
        orig_sigma = law.get('sigma', 999)
        
        if op not in trans:
            continue
        
        # Compute the combination for each fresh graph
        residuals = []
        for key in trans[op]:
            combo_val = 0.0
            valid = True
            for metric_name, coeff in coeffs.items():
                o = orig.get(key, {}).get(metric_name)
                t = trans[op].get(key, {}).get(metric_name)
                if o is None or t is None or o <= 1e-10 or t <= 1e-10:
                    valid = False
                    break
                combo_val += coeff * np.log(t / o)
            
            if valid:
                residuals.append(combo_val)
        
        if len(residuals) < 5:
            continue
        
        new_std = np.std(residuals)
        new_mean = np.mean(residuals)
        
        # A law should have: residuals close to 0 (mean ≈ 0, std small)
        # Compare to original sigma
        status = ""
        if new_std < 0.3 and abs(new_mean) < 0.3:
            status = "✅ SURVIVES"
            surviving.append({
                'law': law,
                'new_std': float(new_std),
                'new_mean': float(new_mean),
                'orig_sigma': orig_sigma,
                'n_test': len(residuals)
            })
        else:
            status = "❌ KILLED"
            killed.append({
                'law': law,
                'new_std': float(new_std),
                'new_mean': float(new_mean),
                'orig_sigma': orig_sigma,
                'n_test': len(residuals)
            })
        
        formula = law['formula'][:80]
        print(f"\n  [{i+1}] {status} | orig_σ={orig_sigma:.4f} | new_std={new_std:.4f} | new_mean={new_mean:.4f} | n={len(residuals)}")
        print(f"      {formula}")
    
    print("\n" + "="*70)
    print(f"VERDICT: {len(surviving)} SURVIVE / {len(killed)} KILLED")
    print("="*70)
    
    if surviving:
        print("\n🏆 SURVIVING LAWS:")
        for s in surviving:
            print(f"\n  σ_orig={s['orig_sigma']:.6f} → σ_new={s['new_std']:.6f}")
            print(f"  Op: {s['law']['op']}")
            print(f"  {s['law']['formula']}")
    
    # Extra: check if any law holds across MULTIPLE operations
    print("\n\n--- CROSS-OPERATION CHECK ---")
    print("Do any coefficient patterns repeat across operations?")
    
    # Group by the dominant metrics involved
    from collections import defaultdict
    pattern_groups = defaultdict(list)
    for s in surviving:
        key_metrics = frozenset(s['law'].get('coefficients', {}).keys())
        pattern_groups[key_metrics].append(s)
    
    for metrics_set, laws_group in pattern_groups.items():
        if len(laws_group) > 1:
            ops_involved = [l['law']['op'] for l in laws_group]
            print(f"\n  Metrics: {sorted(metrics_set)}")
            print(f"  Appears in: {ops_involved}")
            for l in laws_group:
                print(f"    {l['law']['op']}: σ_new={l['new_std']:.4f}, coeffs={l['law'].get('coefficients',{})}")
    
    # Save
    results = {
        'surviving': surviving,
        'killed': killed,
        'total_tested': len(s3_laws),
        'fresh_graphs': len(graphs)
    }
    with open('/tmp/g9_falsification.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nResults saved to /tmp/g9_falsification.json")

if __name__ == '__main__':
    main()

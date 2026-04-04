"""
PHASE G1 — Génération systématique de graphes + mesures baseline exhaustives
=============================================================================
15+ familles × paramètres variés → ~500 graphes
20+ métriques par graphe
Zéro biais, zéro approximation.
"""
import networkx as nx
import numpy as np
import json
import time
import warnings
from collections import Counter
warnings.filterwarnings('ignore')

# ============================================================
# METRICS ENGINE
# ============================================================
def compute_metrics(G, name, params):
    """Compute ALL metrics for a graph. Returns dict."""
    n = G.number_of_nodes()
    m = G.number_of_edges()
    if n == 0:
        return None
    
    metrics = {
        'name': name,
        'params': params,
        'n': n,
        'm': m,
        'density': nx.density(G),
    }
    
    # Degree distribution
    degrees = [d for _, d in G.degree()]
    if degrees:
        metrics['deg_mean'] = float(np.mean(degrees))
        metrics['deg_std'] = float(np.std(degrees))
        metrics['deg_min'] = int(np.min(degrees))
        metrics['deg_max'] = int(np.max(degrees))
        metrics['deg_median'] = float(np.median(degrees))
        if np.std(degrees) > 0:
            metrics['deg_skew'] = float(((np.array(degrees) - np.mean(degrees))**3).mean() / np.std(degrees)**3)
            metrics['deg_kurtosis'] = float(((np.array(degrees) - np.mean(degrees))**4).mean() / np.std(degrees)**4 - 3)
        else:
            metrics['deg_skew'] = 0.0
            metrics['deg_kurtosis'] = 0.0
    
    # Connected components
    if G.is_directed():
        ccs = list(nx.weakly_connected_components(G))
    else:
        ccs = list(nx.connected_components(G))
    metrics['num_components'] = len(ccs)
    metrics['largest_cc_frac'] = len(max(ccs, key=len)) / n
    
    # Work on largest CC for path-based metrics
    lcc_nodes = max(ccs, key=len)
    H = G.subgraph(lcc_nodes).copy()
    n_lcc = H.number_of_nodes()
    
    # Clustering
    metrics['clustering_avg'] = nx.average_clustering(G)
    metrics['transitivity'] = nx.transitivity(G)
    
    # Triangles
    if not G.is_directed():
        tri = sum(nx.triangles(G).values()) // 3
        metrics['num_triangles'] = tri
    
    # Path metrics (on LCC only, skip if too large)
    if n_lcc > 1 and n_lcc <= 2000:
        try:
            metrics['avg_shortest_path'] = nx.average_shortest_path_length(H)
            metrics['diameter'] = nx.diameter(H)
        except:
            metrics['avg_shortest_path'] = None
            metrics['diameter'] = None
    else:
        # Sample-based estimation for large graphs
        if n_lcc > 1:
            nodes_sample = list(H.nodes())[:min(200, n_lcc)]
            dists = []
            for src in nodes_sample[:50]:
                sp = nx.single_source_shortest_path_length(H, src)
                dists.extend(sp.values())
            metrics['avg_shortest_path_est'] = float(np.mean(dists)) if dists else None
        metrics['avg_shortest_path'] = None
        metrics['diameter'] = None
    
    # Assortativity
    try:
        metrics['assortativity'] = nx.degree_assortativity_coefficient(G)
    except:
        metrics['assortativity'] = None
    
    # Spectral properties (adjacency matrix)
    if n <= 1000:
        try:
            A = nx.adjacency_matrix(G).toarray().astype(float)
            eigs_A = np.sort(np.linalg.eigvalsh(A))[::-1]
            metrics['spectral_radius'] = float(eigs_A[0])
            metrics['spectral_gap'] = float(eigs_A[0] - eigs_A[1]) if len(eigs_A) > 1 else 0
            metrics['eig_A_min'] = float(eigs_A[-1])
            
            # Laplacian
            L = nx.laplacian_matrix(G).toarray().astype(float)
            eigs_L = np.sort(np.linalg.eigvalsh(L))
            metrics['algebraic_connectivity'] = float(eigs_L[1]) if len(eigs_L) > 1 else 0  # Fiedler
            metrics['laplacian_max'] = float(eigs_L[-1])
            metrics['spectral_ratio'] = float(eigs_L[-1] / eigs_L[1]) if eigs_L[1] > 1e-10 else None
            
            # Normalized Laplacian spectrum
            nL = nx.normalized_laplacian_matrix(G).toarray().astype(float)
            eigs_nL = np.sort(np.linalg.eigvalsh(nL))
            metrics['norm_lap_gap'] = float(eigs_nL[1]) if len(eigs_nL) > 1 else 0
        except:
            pass
    
    # Girth (shortest cycle) — expensive, only for small graphs
    if n <= 500 and m > 0:
        try:
            girth = nx.girth(G)
            metrics['girth'] = girth if girth != float('inf') else None
        except:
            metrics['girth'] = None
    
    # Modularity (greedy)
    if n > 2 and m > 0:
        try:
            communities = nx.community.greedy_modularity_communities(G)
            metrics['modularity'] = nx.community.modularity(G, communities)
            metrics['num_communities'] = len(communities)
        except:
            pass
    
    # Wiener index (sum of all shortest paths)
    if n_lcc <= 500 and n_lcc > 1:
        try:
            metrics['wiener_index'] = nx.wiener_index(H)
        except:
            pass
    
    return metrics

# ============================================================
# GRAPH GENERATORS
# ============================================================
def generate_all_graphs():
    """Generate 15+ families of graphs with systematic parameter variation."""
    graphs = []
    
    # ------- 1. ERDŐS-RÉNYI G(n, p) -------
    for n in [50, 100, 200, 500]:
        for p in [0.01, 0.02, 0.05, 0.1, 0.2, 0.5]:
            G = nx.erdos_renyi_graph(n, p, seed=42)
            graphs.append((G, 'erdos_renyi', {'n': n, 'p': p}))
    
    # ------- 2. BARABÁSI-ALBERT (preferential attachment) -------
    for n in [50, 100, 200, 500]:
        for m_ba in [1, 2, 3, 5, 10]:
            G = nx.barabasi_albert_graph(n, m_ba, seed=42)
            graphs.append((G, 'barabasi_albert', {'n': n, 'm': m_ba}))
    
    # ------- 3. WATTS-STROGATZ (small world) -------
    for n in [50, 100, 200, 500]:
        for k in [4, 6, 10]:
            for p in [0.0, 0.01, 0.05, 0.1, 0.3, 1.0]:
                G = nx.watts_strogatz_graph(n, k, p, seed=42)
                graphs.append((G, 'watts_strogatz', {'n': n, 'k': k, 'p': p}))
    
    # ------- 4. REGULAR LATTICES -------
    # Ring
    for n in [50, 100, 200]:
        G = nx.cycle_graph(n)
        graphs.append((G, 'cycle', {'n': n}))
    
    # 2D Grid
    for side in [7, 10, 15, 20]:
        G = nx.grid_2d_graph(side, side)
        G = nx.convert_node_labels_to_integers(G)
        graphs.append((G, 'grid_2d', {'side': side, 'n': side*side}))
    
    # Triangular lattice
    for side in [5, 8, 12]:
        G = nx.triangular_lattice_graph(side, side)
        G = nx.convert_node_labels_to_integers(G)
        graphs.append((G, 'triangular_lattice', {'side': side}))
    
    # ------- 5. TREES -------
    # Random tree
    for n in [50, 100, 200, 500]:
        G = nx.random_labeled_tree(n, seed=42)
        graphs.append((G, 'random_tree', {'n': n}))
    
    # Balanced tree
    for r in [2, 3, 4]:
        for h in [3, 4, 5]:
            n_tree = sum(r**i for i in range(h+1))
            if n_tree <= 1500:
                G = nx.balanced_tree(r, h)
                graphs.append((G, 'balanced_tree', {'r': r, 'h': h, 'n': n_tree}))
    
    # Star
    for n in [20, 50, 100, 200]:
        G = nx.star_graph(n-1)
        graphs.append((G, 'star', {'n': n}))
    
    # Path
    for n in [20, 50, 100, 200]:
        G = nx.path_graph(n)
        graphs.append((G, 'path', {'n': n}))
    
    # ------- 6. COMPLETE GRAPHS -------
    for n in [10, 20, 50, 100]:
        G = nx.complete_graph(n)
        graphs.append((G, 'complete', {'n': n}))
    
    # ------- 7. COMPLETE BIPARTITE -------
    for n1 in [10, 25, 50]:
        for n2 in [10, 25, 50]:
            G = nx.complete_bipartite_graph(n1, n2)
            graphs.append((G, 'complete_bipartite', {'n1': n1, 'n2': n2}))
    
    # ------- 8. RANDOM REGULAR -------
    for n in [50, 100, 200]:
        for d in [3, 4, 6, 10]:
            if d < n:
                try:
                    G = nx.random_regular_graph(d, n, seed=42)
                    graphs.append((G, 'random_regular', {'n': n, 'd': d}))
                except:
                    pass
    
    # ------- 9. RANDOM GEOMETRIC -------
    for n in [50, 100, 200, 500]:
        for radius in [0.1, 0.15, 0.2, 0.3]:
            G = nx.random_geometric_graph(n, radius, seed=42)
            graphs.append((G, 'random_geometric', {'n': n, 'radius': radius}))
    
    # ------- 10. STOCHASTIC BLOCK MODEL -------
    for n_per_block in [25, 50]:
        for k_blocks in [2, 4]:
            for p_in in [0.3, 0.5]:
                for p_out in [0.01, 0.05, 0.1]:
                    sizes = [n_per_block] * k_blocks
                    probs = [[p_in if i==j else p_out for j in range(k_blocks)] for i in range(k_blocks)]
                    G = nx.stochastic_block_model(sizes, probs, seed=42)
                    graphs.append((G, 'stochastic_block', {'n_per_block': n_per_block, 'k': k_blocks, 'p_in': p_in, 'p_out': p_out}))
    
    # ------- 11. POWERLAW CLUSTER -------
    for n in [50, 100, 200, 500]:
        for m_plc in [2, 3, 5]:
            for p in [0.1, 0.5, 0.9]:
                try:
                    G = nx.powerlaw_cluster_graph(n, m_plc, p, seed=42)
                    graphs.append((G, 'powerlaw_cluster', {'n': n, 'm': m_plc, 'p': p}))
                except:
                    pass
    
    # ------- 12. CIRCULANT GRAPHS -------
    for n in [50, 100, 200]:
        for offsets in [[1,2], [1,3], [1,5], [1,2,5], [1,n//4]]:
            G = nx.circulant_graph(n, offsets)
            graphs.append((G, 'circulant', {'n': n, 'offsets': offsets}))
    
    # ------- 13. NEWMAN-WATTS-STROGATZ (shortcuts, no rewiring) -------
    for n in [50, 100, 200]:
        for k in [4, 6]:
            for p in [0.01, 0.05, 0.1, 0.3]:
                G = nx.newman_watts_strogatz_graph(n, k, p, seed=42)
                graphs.append((G, 'newman_watts_strogatz', {'n': n, 'k': k, 'p': p}))
    
    # ------- 14. CAVEMAN / CONNECTED CAVEMAN -------
    for l in [5, 10, 20]:
        for k in [5, 10]:
            if l * k <= 500:
                G = nx.connected_caveman_graph(l, k)
                graphs.append((G, 'connected_caveman', {'l': l, 'k': k, 'n': l*k}))
    
    # ------- 15. DUAL BARABÁSI-ALBERT -------
    for n in [100, 200, 500]:
        for m1 in [1, 2]:
            for m2 in [1, 2]:
                for p_dba in [0.3, 0.5, 0.7]:
                    try:
                        G = nx.dual_barabasi_albert_graph(n, m1, m2, p_dba, seed=42)
                        graphs.append((G, 'dual_barabasi_albert', {'n': n, 'm1': m1, 'm2': m2, 'p': p_dba}))
                    except:
                        pass
    
    # ------- 16. RANDOM LOBSTER -------
    for n in [50, 100, 200]:
        for p1 in [0.3, 0.5, 0.8]:
            for p2 in [0.1, 0.3, 0.5]:
                G = nx.random_lobster(n, p1, p2, seed=42)
                graphs.append((G, 'random_lobster', {'n_backbone': n, 'p1': p1, 'p2': p2}))
    
    return graphs

# ============================================================
# MAIN EXECUTION
# ============================================================
print("="*70)
print("PHASE G1 — GÉNÉRATION MASSIVE + MESURES BASELINE")
print("="*70)

t0 = time.time()
all_graphs = generate_all_graphs()
print(f"\n{len(all_graphs)} graphes générés en {time.time()-t0:.1f}s")

# Count by family
families = Counter(g[1] for g in all_graphs)
print(f"\n{len(families)} familles:")
for fam, cnt in sorted(families.items(), key=lambda x: -x[1]):
    print(f"  {fam:30s} {cnt:>4d} graphes")

# Compute metrics
t1 = time.time()
results = []
errors = 0
for i, (G, name, params) in enumerate(all_graphs):
    if i % 50 == 0:
        print(f"  Computing metrics... {i}/{len(all_graphs)}")
    try:
        m = compute_metrics(G, name, params)
        if m is not None:
            results.append(m)
    except Exception as e:
        errors += 1

print(f"\n{len(results)} graphes mesurés en {time.time()-t1:.1f}s ({errors} erreurs)")

# Save raw results
with open('/tmp/g1_results.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)

# ============================================================
# STATISTICAL OVERVIEW
# ============================================================
print("\n" + "="*70)
print("APERÇU STATISTIQUE DES MÉTRIQUES")
print("="*70)

# Collect all metric keys
all_keys = set()
for r in results:
    all_keys.update(k for k, v in r.items() if isinstance(v, (int, float)) and v is not None)

numeric_keys = sorted(all_keys - {'n', 'm'})

print(f"\n{'Métrique':>30s} {'min':>10s} {'median':>10s} {'max':>10s} {'non-null':>8s}")
print("-"*75)
for key in numeric_keys:
    vals = [r[key] for r in results if key in r and r[key] is not None and not np.isnan(r[key]) and not np.isinf(r[key])]
    if vals:
        arr = np.array(vals, dtype=float)
        print(f"{key:>30s} {np.min(arr):>10.4f} {np.median(arr):>10.4f} {np.max(arr):>10.4f} {len(vals):>8d}")

# ============================================================
# EXTREME DETECTION
# ============================================================
print("\n" + "="*70)
print("DÉTECTION DES EXTRÊMES (top/bottom par métrique)")
print("="*70)

for key in ['clustering_avg', 'algebraic_connectivity', 'spectral_gap', 
            'assortativity', 'modularity', 'transitivity']:
    vals = [(r[key], r['name'], r['params']) for r in results if key in r and r[key] is not None]
    if len(vals) > 2:
        vals.sort()
        print(f"\n{key}:")
        print(f"  MIN = {vals[0][0]:.4f} → {vals[0][1]} {vals[0][2]}")
        print(f"  MAX = {vals[-1][0]:.4f} → {vals[-1][1]} {vals[-1][2]}")

# ============================================================
# CORRELATION MATRIX (between metrics)
# ============================================================
print("\n" + "="*70)
print("CORRÉLATIONS FORTES ENTRE MÉTRIQUES (|r| > 0.8)")
print("="*70)

# Build matrix
metric_names = ['density', 'deg_mean', 'deg_std', 'clustering_avg', 'transitivity',
                'assortativity', 'largest_cc_frac', 'num_triangles',
                'algebraic_connectivity', 'spectral_radius', 'spectral_gap',
                'modularity', 'norm_lap_gap']

data_matrix = []
valid_names = []
for r in results:
    row = []
    ok = True
    for k in metric_names:
        v = r.get(k)
        if v is None or (isinstance(v, float) and (np.isnan(v) or np.isinf(v))):
            ok = False
            break
        row.append(float(v))
    if ok:
        data_matrix.append(row)

data_matrix = np.array(data_matrix)
print(f"\n{len(data_matrix)} graphes avec toutes les métriques disponibles")

if len(data_matrix) > 10:
    corr = np.corrcoef(data_matrix.T)
    strong = []
    for i in range(len(metric_names)):
        for j in range(i+1, len(metric_names)):
            r_val = corr[i, j]
            if abs(r_val) > 0.8 and not np.isnan(r_val):
                strong.append((abs(r_val), r_val, metric_names[i], metric_names[j]))
    
    strong.sort(reverse=True)
    for _, r_val, n1, n2 in strong[:20]:
        sign = "+" if r_val > 0 else "-"
        print(f"  {sign}{abs(r_val):.3f}  {n1:>25s}  ↔  {n2}")

# ============================================================
# PER-FAMILY SIGNATURES
# ============================================================
print("\n" + "="*70)
print("SIGNATURES PAR FAMILLE")
print("="*70)

family_data = {}
for r in results:
    fam = r['name']
    if fam not in family_data:
        family_data[fam] = []
    family_data[fam].append(r)

print(f"\n{'Famille':>25s} {'n':>5s} {'clust':>7s} {'trans':>7s} {'assort':>7s} {'spec_gap':>9s} {'modul':>7s}")
print("-"*80)
for fam in sorted(family_data.keys()):
    rs = family_data[fam]
    def med(key):
        vals = [r[key] for r in rs if key in r and r[key] is not None]
        return float(np.median(vals)) if vals else float('nan')
    
    print(f"{fam:>25s} {len(rs):>5d} {med('clustering_avg'):>7.3f} {med('transitivity'):>7.3f} "
          f"{med('assortativity'):>7.3f} {med('spectral_gap'):>9.3f} {med('modularity'):>7.3f}")

print(f"\nTotal: {len(results)} graphes, {len(families)} familles")
print(f"Temps total: {time.time()-t0:.1f}s")
print("\nResultats sauvés dans /tmp/g1_results.json")

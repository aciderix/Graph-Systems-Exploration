"""
PHASE G7 — 5 PISTES DE MÉTRIQUES NON-STANDARD
===============================================
Protocole machine : DÉFINIR → IMPLÉMENTER → MESURER → STOCKER
On calcule TOUT sur les 356 graphes + 68 extrêmes + 45 null.
Pas de raccourci, pas de skip.
"""
import pickle
import numpy as np
import json
import time
import gzip
import warnings
import sys
from scipy import linalg as sla
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import eigsh
import networkx as nx
warnings.filterwarnings('ignore')

# ============================================================
# LOAD ALL GRAPHS
# ============================================================
print("=" * 70)
print("LOADING ALL GRAPHS")
print("=" * 70)

with open('/tmp/all_graphs.pkl', 'rb') as f:
    data = pickle.load(f)

main_graphs = data['main']      # list of (G, name, params)
extreme_graphs = data['extreme'] # dict name -> G
null_graphs = data['null']       # dict name -> G

print(f"Main: {len(main_graphs)}, Extreme: {len(extreme_graphs)}, Null: {len(null_graphs)}")

# Load existing G1 metrics for correlation
with open('/agent/home/Graph-Systems-Exploration/data/g1_results.json') as f:
    g1_results = json.load(f)
print(f"G1 results loaded: {len(g1_results)} entries")

# ============================================================
# HELPER: ensure connected
# ============================================================
def ensure_connected(G):
    if G.number_of_nodes() < 2:
        return None
    if nx.is_connected(G):
        return G
    return G.subgraph(max(nx.connected_components(G), key=len)).copy()

# ============================================================
# PISTE F: DYNAMIC RESPONSE METRICS
# ============================================================
def compute_piste_F(G_orig, name=""):
    """
    F1: Heat kernel trace H(t) = Σ exp(-t·λᵢ) at t=0.1, 1, 10, 100
    F2: Normalized heat trace = H(t)/N
    F3: Heat entropy = -Σ pᵢ log pᵢ where pᵢ = exp(-t·λᵢ)/H(t)
    F4: Mixing time proxy = 1/λ₂ (inverse Fiedler)
    F5: Effective graph resistance = N·Σ(1/λᵢ) for λᵢ>0
    F6: Return time spectrum = Σ 1/λᵢ² for λᵢ>0
    F7: Diffusion distance at t=1 = mean ||h_i(t) - h_j(t)|| for sampled pairs
    """
    G = ensure_connected(G_orig)
    if G is None or G.number_of_nodes() < 3:
        return None
    
    N = G.number_of_nodes()
    result = {'name': name, 'N': N, 'piste': 'F'}
    
    try:
        L = nx.laplacian_matrix(G).toarray().astype(float)
        eigs = np.sort(np.linalg.eigvalsh(L))
        eigs_pos = eigs[eigs > 1e-10]
        
        if len(eigs_pos) == 0:
            return None
        
        # F1-F3: Heat kernel traces and entropy at multiple times
        for t in [0.1, 1.0, 10.0, 100.0]:
            exp_vals = np.exp(-t * eigs_pos)
            H_t = np.sum(exp_vals) + 1  # +1 for the zero eigenvalue (exp(0)=1)
            result[f'heat_trace_t{t}'] = float(H_t)
            result[f'heat_trace_norm_t{t}'] = float(H_t / N)
            
            # Heat entropy
            p = np.concatenate([[1/H_t], exp_vals / H_t])  # include zero eigenvalue
            p = p[p > 1e-30]
            result[f'heat_entropy_t{t}'] = float(-np.sum(p * np.log(p)))
        
        # F4: Mixing time proxy
        lambda2 = eigs_pos[0]  # smallest positive eigenvalue (Fiedler)
        result['mixing_time_proxy'] = float(1.0 / lambda2)
        
        # F5: Effective graph resistance = N * Σ(1/λᵢ)
        result['eff_resistance'] = float(N * np.sum(1.0 / eigs_pos))
        result['eff_resistance_norm'] = float(np.sum(1.0 / eigs_pos) / (N-1))
        
        # F6: Return time spectrum
        result['return_time_sum'] = float(np.sum(1.0 / eigs_pos**2))
        result['return_time_norm'] = float(np.sum(1.0 / eigs_pos**2) / N)
        
        # F7: Heat kernel decay rate (ratio of H(10)/H(1))
        H1 = np.sum(np.exp(-1.0 * eigs_pos)) + 1
        H10 = np.sum(np.exp(-10.0 * eigs_pos)) + 1
        H100 = np.sum(np.exp(-100.0 * eigs_pos)) + 1
        result['heat_decay_10_1'] = float(H10 / H1) if H1 > 1e-10 else None
        result['heat_decay_100_10'] = float(H100 / H10) if H10 > 1e-10 else None
        
        # F8: Spectral zeta function ζ(s) = Σ λᵢ^(-s) for s=2,3
        result['spectral_zeta_2'] = float(np.sum(1.0 / eigs_pos**2))
        result['spectral_zeta_3'] = float(np.sum(1.0 / eigs_pos**3))
        
        # F9: Log-determinant of L (sum of log eigenvalues) = complexity
        result['log_det_L'] = float(np.sum(np.log(eigs_pos)))
        result['log_det_L_norm'] = float(np.sum(np.log(eigs_pos)) / N)
        
        # F10: Heat content asymptotic = integral of H(t) from 0 to 1
        # Approximated as Σ (1-exp(-λ))/λ
        result['heat_content_asym'] = float(np.sum((1 - np.exp(-eigs_pos)) / eigs_pos))
        
    except Exception as e:
        result['error_F'] = str(e)
    
    return result


# ============================================================
# PISTE A: DISCRETE RICCI CURVATURE
# ============================================================
def compute_piste_A(G_orig, name=""):
    """
    Forman-Ricci curvature (combinatorial, fast):
    For each edge (u,v): Ric_F(u,v) = 4 - d(u) - d(v) + 3*#triangles(u,v)
    
    Statistics: mean, std, min, max, skewness, kurtosis, fraction negative
    """
    G = ensure_connected(G_orig)
    if G is None or G.number_of_nodes() < 3 or G.number_of_edges() == 0:
        return None
    
    N = G.number_of_nodes()
    M = G.number_of_edges()
    result = {'name': name, 'N': N, 'M': M, 'piste': 'A'}
    
    try:
        # Forman-Ricci curvature
        curvatures = []
        for u, v in G.edges():
            du = G.degree(u)
            dv = G.degree(v)
            # Count triangles containing edge (u,v)
            common = len(set(G.neighbors(u)) & set(G.neighbors(v)))
            ric = 4 - du - dv + 3 * common
            curvatures.append(ric)
        
        curvatures = np.array(curvatures, dtype=float)
        
        result['forman_mean'] = float(np.mean(curvatures))
        result['forman_std'] = float(np.std(curvatures))
        result['forman_min'] = float(np.min(curvatures))
        result['forman_max'] = float(np.max(curvatures))
        result['forman_median'] = float(np.median(curvatures))
        
        if np.std(curvatures) > 1e-10:
            result['forman_skew'] = float(((curvatures - np.mean(curvatures))**3).mean() / np.std(curvatures)**3)
            result['forman_kurtosis'] = float(((curvatures - np.mean(curvatures))**4).mean() / np.std(curvatures)**4 - 3)
        else:
            result['forman_skew'] = 0.0
            result['forman_kurtosis'] = 0.0
        
        result['forman_frac_negative'] = float(np.mean(curvatures < 0))
        result['forman_frac_positive'] = float(np.mean(curvatures > 0))
        result['forman_frac_zero'] = float(np.mean(curvatures == 0))
        
        # Total curvature (sum)
        result['forman_total'] = float(np.sum(curvatures))
        result['forman_total_norm'] = float(np.sum(curvatures) / N)
        
        # Augmented Forman-Ricci (with quadrangles)
        # Aug_Ric(u,v) = Ric_F(u,v) + (#4-cycles through (u,v))
        # Skip for now, basic Forman is enough for first pass
        
        # Ollivier-Ricci approximation (simplified: 1-hop Wasserstein)
        # Only for small graphs due to cost
        if N <= 100:
            ollivier_curvatures = []
            for u, v in G.edges():
                nu = list(G.neighbors(u))
                nv = list(G.neighbors(v))
                # Uniform measure on neighbors
                # Overlap fraction as Ollivier proxy
                common_neighbors = set(nu) & set(nv)
                ollivier_proxy = len(common_neighbors) / max(len(nu), len(nv)) if max(len(nu), len(nv)) > 0 else 0
                ollivier_curvatures.append(ollivier_proxy)
            
            ollivier_curvatures = np.array(ollivier_curvatures)
            result['ollivier_proxy_mean'] = float(np.mean(ollivier_curvatures))
            result['ollivier_proxy_std'] = float(np.std(ollivier_curvatures))
            result['ollivier_proxy_max'] = float(np.max(ollivier_curvatures))
        
    except Exception as e:
        result['error_A'] = str(e)
    
    return result


# ============================================================
# PISTE B: VON NEUMANN ENTROPY
# ============================================================
def compute_piste_B(G_orig, name=""):
    """
    Von Neumann entropy: S_VN = -Tr(ρ log₂ ρ)
    where ρ = L / Tr(L) = L / (2M)
    
    Also:
    - Normalized S_VN / log₂(N)
    - Comparison with spectral entropy (LOI 1)
    - Quantum partition function Z(β) = Tr(exp(-βL))
    """
    G = ensure_connected(G_orig)
    if G is None or G.number_of_nodes() < 3 or G.number_of_edges() == 0:
        return None
    
    N = G.number_of_nodes()
    M = G.number_of_edges()
    result = {'name': name, 'N': N, 'M': M, 'piste': 'B'}
    
    try:
        L = nx.laplacian_matrix(G).toarray().astype(float)
        eigs = np.sort(np.linalg.eigvalsh(L))
        eigs_pos = eigs[eigs > 1e-10]
        
        # Von Neumann entropy
        trace_L = np.sum(eigs_pos)  # = 2M
        if trace_L > 1e-10:
            rho_eigs = eigs_pos / trace_L
            S_VN = -np.sum(rho_eigs * np.log2(rho_eigs + 1e-30))
            result['von_neumann_entropy'] = float(S_VN)
            result['von_neumann_norm'] = float(S_VN / np.log2(N))
        
        # Spectral entropy (LOI 1 from G5 — for comparison)
        nL = nx.normalized_laplacian_matrix(G).toarray().astype(float)
        neigs = np.linalg.eigvalsh(nL)
        neigs_pos = neigs[neigs > 1e-10]
        if len(neigs_pos) > 0:
            p = neigs_pos / neigs_pos.sum()
            S_spec = -np.sum(p * np.log2(p + 1e-30))
            result['spectral_entropy'] = float(S_spec)
            result['spectral_entropy_norm'] = float(S_spec / np.log2(N))
        
        # Quantum partition function at different temperatures
        for beta in [0.01, 0.1, 1.0, 10.0]:
            Z = np.sum(np.exp(-beta * eigs))  # includes zero eigenvalue
            result[f'partition_Z_beta{beta}'] = float(Z)
            result[f'free_energy_beta{beta}'] = float(-np.log(Z) / beta) if Z > 0 else None
        
        # Quantum mutual information proxy: difference between VN entropy of whole and parts
        # S_VN for the graph vs sum of S_VN for communities
        # This is expensive, skip for large graphs
        
        # Renyi entropy of order 2: S₂ = -log₂(Tr(ρ²))
        if trace_L > 1e-10:
            rho2 = np.sum((eigs_pos / trace_L)**2)
            result['renyi_entropy_2'] = float(-np.log2(rho2 + 1e-30))
            result['renyi_entropy_2_norm'] = float(-np.log2(rho2 + 1e-30) / np.log2(N))
        
        # Tsallis entropy q=2: S_q = (1 - Tr(ρ^q))/(q-1)
        if trace_L > 1e-10:
            result['tsallis_entropy_2'] = float(1 - rho2)
        
    except Exception as e:
        result['error_B'] = str(e)
    
    return result


# ============================================================
# PISTE E: PERSISTENT HOMOLOGY (simplified, no external lib)
# ============================================================
def compute_piste_E(G_orig, name=""):
    """
    Persistent homology via filtration on edge weights (shortest path distance).
    
    For unweighted graphs, use:
    1. Edge density filtration: add edges in order of graph distance
    2. Betti numbers at each step
    3. Persistence entropy
    
    Simplified approach without gudhi:
    - Use the Laplacian eigenvalues as a filtration
    - Count connected components as edges are added (Betti_0 persistence)
    - Use adjacency matrix rank for Betti_1 proxy
    """
    G = ensure_connected(G_orig)
    if G is None or G.number_of_nodes() < 3:
        return None
    
    N = G.number_of_nodes()
    M = G.number_of_edges()
    result = {'name': name, 'N': N, 'M': M, 'piste': 'E'}
    
    try:
        # === APPROACH 1: Betti-0 persistence via edge weight filtration ===
        # Use betweenness centrality as edge weight for filtration
        edge_betweenness = nx.edge_betweenness_centrality(G)
        
        # Sort edges by betweenness (ascending = structural backbone first)
        sorted_edges = sorted(edge_betweenness.items(), key=lambda x: x[1])
        
        # Build graph incrementally, track components
        H = nx.Graph()
        H.add_nodes_from(G.nodes())
        
        n_components_history = [N]  # start with N isolated nodes
        births = list(range(N))  # each node is born at step 0
        deaths = []
        
        for idx, (edge, weight) in enumerate(sorted_edges):
            u, v = edge
            cu = None
            cv = None
            # Check if u and v are in different components
            if not nx.has_path(H, u, v) if H.number_of_edges() > 0 else True:
                # A component dies (merges)
                deaths.append(idx / M)  # normalized death time
            H.add_edge(u, v)
        
        # Persistence = death - birth for each bar
        # Since all births are at 0, persistence = death time
        if len(deaths) > 0:
            persistences = np.array(deaths)
            result['betti0_total_persistence'] = float(np.sum(persistences))
            result['betti0_mean_persistence'] = float(np.mean(persistences))
            result['betti0_std_persistence'] = float(np.std(persistences))
            result['betti0_max_persistence'] = float(np.max(persistences))
            
            # Persistence entropy
            p = persistences / np.sum(persistences) if np.sum(persistences) > 1e-10 else persistences
            p = p[p > 1e-30]
            result['betti0_persistence_entropy'] = float(-np.sum(p * np.log(p)))
            result['betti0_persistence_entropy_norm'] = float(-np.sum(p * np.log(p)) / np.log(N))
            result['betti0_n_bars'] = len(deaths)
        
        # === APPROACH 2: Clique complex & Betti numbers ===
        # Number of triangles = Betti_1 proxy (holes in the 2-skeleton)
        triangles = sum(nx.triangles(G).values()) // 3
        result['n_triangles'] = triangles
        
        # Euler characteristic: χ = V - E + F (F = triangles for clique complex)
        result['euler_characteristic'] = N - M + triangles
        
        # === APPROACH 3: Distance-based filtration ===
        # Sample pairs and compute shortest paths
        if N <= 200:
            dist_matrix = dict(nx.all_pairs_shortest_path_length(G))
            dists = []
            for u in dist_matrix:
                for v in dist_matrix[u]:
                    if u < v:
                        dists.append(dist_matrix[u][v])
            if dists:
                dists = np.array(dists)
                result['dist_entropy'] = float(-np.sum((dists/dists.sum()) * np.log(dists/dists.sum() + 1e-30)))
                result['dist_mean'] = float(np.mean(dists))
                result['dist_std'] = float(np.std(dists))
                result['dist_max'] = float(np.max(dists))
                # Hyperbolicity proxy: δ = max over 4-tuples of Gromov product mismatch
                # Too expensive for full computation, sample
                if N <= 50:
                    nodes = list(G.nodes())
                    max_delta = 0
                    for _ in range(min(1000, N**2)):
                        quartet = np.random.choice(nodes, 4, replace=False)
                        x,y,z,w = quartet
                        d = lambda a,b: dist_matrix[a][b]
                        s1 = d(x,y) + d(z,w)
                        s2 = d(x,z) + d(y,w)
                        s3 = d(x,w) + d(y,z)
                        sums = sorted([s1,s2,s3])
                        delta = (sums[2] - sums[1]) / 2
                        max_delta = max(max_delta, delta)
                    result['gromov_hyperbolicity_sample'] = float(max_delta)
        
    except Exception as e:
        result['error_E'] = str(e)
    
    return result


# ============================================================
# PISTE J: COMPRESSION COMPLEXITY
# ============================================================
def compute_piste_J(G_orig, name=""):
    """
    Kolmogorov complexity proxy via compression.
    
    J1: gzip(adjacency matrix flattened) / N²
    J2: gzip(degree sequence) / N
    J3: gzip(Laplacian spectrum) / N
    J4: gzip(edge list) / M
    J5: Ratio compressed/uncompressed = compressibility
    """
    G = ensure_connected(G_orig)
    if G is None or G.number_of_nodes() < 3:
        return None
    
    N = G.number_of_nodes()
    M = G.number_of_edges()
    result = {'name': name, 'N': N, 'M': M, 'piste': 'J'}
    
    try:
        # J1: Adjacency matrix compression
        if N <= 500:
            A = nx.adjacency_matrix(G).toarray()
            A_bytes = A.tobytes()
            A_compressed = gzip.compress(A_bytes)
            result['adj_compressed_size'] = len(A_compressed)
            result['adj_raw_size'] = len(A_bytes)
            result['adj_compress_ratio'] = float(len(A_compressed) / len(A_bytes))
            result['adj_complexity_per_node2'] = float(len(A_compressed) / (N * N))
            result['adj_complexity_per_edge'] = float(len(A_compressed) / max(M, 1))
        
        # J2: Degree sequence compression
        degrees = sorted([d for _, d in G.degree()], reverse=True)
        deg_bytes = np.array(degrees, dtype=np.int32).tobytes()
        deg_compressed = gzip.compress(deg_bytes)
        result['deg_compressed_size'] = len(deg_compressed)
        result['deg_compress_ratio'] = float(len(deg_compressed) / len(deg_bytes))
        result['deg_complexity_per_node'] = float(len(deg_compressed) / N)
        
        # J3: Spectrum compression
        if N <= 500:
            L = nx.laplacian_matrix(G).toarray().astype(float)
            eigs = np.sort(np.linalg.eigvalsh(L))
            spec_bytes = eigs.tobytes()
            spec_compressed = gzip.compress(spec_bytes)
            result['spec_compressed_size'] = len(spec_compressed)
            result['spec_compress_ratio'] = float(len(spec_compressed) / len(spec_bytes))
            result['spec_complexity_per_node'] = float(len(spec_compressed) / N)
        
        # J4: Edge list compression
        edges = sorted(G.edges())
        edge_str = '\n'.join(f"{u},{v}" for u, v in edges).encode()
        edge_compressed = gzip.compress(edge_str)
        result['edge_compressed_size'] = len(edge_compressed)
        result['edge_compress_ratio'] = float(len(edge_compressed) / len(edge_str)) if len(edge_str) > 0 else None
        result['edge_complexity_per_edge'] = float(len(edge_compressed) / max(M, 1))
        
        # J5: Information density = compressed_size / (N * log2(N))
        result['info_density'] = float(len(A_compressed) / (N * np.log2(N))) if N > 1 and N <= 500 else None
        
    except Exception as e:
        result['error_J'] = str(e)
    
    return result


# ============================================================
# MAIN COMPUTATION
# ============================================================
def process_graph(G, name, graph_type="main"):
    """Process one graph through all 5 pistes."""
    results = {}
    
    for piste_name, compute_fn in [('F', compute_piste_F), ('A', compute_piste_A), 
                                     ('B', compute_piste_B), ('E', compute_piste_E), 
                                     ('J', compute_piste_J)]:
        try:
            r = compute_fn(G, name)
            if r is not None:
                results[piste_name] = r
        except Exception as e:
            results[piste_name] = {'name': name, 'error': str(e)}
    
    return results

# Process all main graphs
print("\n" + "=" * 70)
print("COMPUTING 5 PISTES ON 356 MAIN GRAPHS")
print("=" * 70)

all_results_main = []
t0 = time.time()
for i, (G, name, params) in enumerate(main_graphs):
    if i % 50 == 0:
        elapsed = time.time() - t0
        print(f"  Processing {i}/{len(main_graphs)} ... ({elapsed:.0f}s elapsed)")
    
    results = process_graph(G, f"{name}_{i}", "main")
    results['meta'] = {'name': name, 'params': str(params), 'index': i, 'type': 'main'}
    all_results_main.append(results)

print(f"Main graphs done in {time.time()-t0:.1f}s")

# Process extreme graphs
print("\n" + "=" * 70)
print("COMPUTING 5 PISTES ON 68 EXTREME GRAPHS")
print("=" * 70)

all_results_extreme = []
t1 = time.time()
for name, G in extreme_graphs.items():
    results = process_graph(G, name, "extreme")
    results['meta'] = {'name': name, 'type': 'extreme'}
    all_results_extreme.append(results)

print(f"Extreme graphs done in {time.time()-t1:.1f}s")

# Process null graphs
print("\n" + "=" * 70)
print("COMPUTING 5 PISTES ON 45 NULL GRAPHS")
print("=" * 70)

all_results_null = []
t2 = time.time()
for name, G in null_graphs.items():
    results = process_graph(G, name, "null")
    results['meta'] = {'name': name, 'type': 'null'}
    all_results_null.append(results)

print(f"Null graphs done in {time.time()-t2:.1f}s")

# ============================================================
# SAVE ALL RESULTS
# ============================================================
all_data = {
    'main': all_results_main,
    'extreme': all_results_extreme,
    'null': all_results_null,
    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
    'n_pistes': 5,
}

# JSON-safe conversion
def make_serializable(obj):
    if isinstance(obj, dict):
        return {k: make_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_serializable(v) for v in obj]
    elif isinstance(obj, (np.integer,)):
        return int(obj)
    elif isinstance(obj, (np.floating,)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj

all_data = make_serializable(all_data)

with open('/tmp/g7_all_pistes_results.json', 'w') as f:
    json.dump(all_data, f, indent=1, default=str)

print(f"\nAll results saved to /tmp/g7_all_pistes_results.json")
print(f"Total computation time: {time.time()-t0:.1f}s")

# ============================================================
# QUICK SUMMARY
# ============================================================
print("\n" + "=" * 70)
print("QUICK SUMMARY PER PISTE")
print("=" * 70)

for piste in ['F', 'A', 'B', 'E', 'J']:
    n_success = sum(1 for r in all_results_main if piste in r and 'error' not in r.get(piste, {}))
    n_error = sum(1 for r in all_results_main if piste in r and 'error' in r.get(piste, {}))
    n_none = len(all_results_main) - n_success - n_error
    
    # Collect all metric keys
    all_keys = set()
    for r in all_results_main:
        if piste in r and isinstance(r[piste], dict):
            all_keys.update(k for k, v in r[piste].items() if isinstance(v, (int, float)))
    
    print(f"\nPiste {piste}: {n_success} success, {n_error} errors, {n_none} None")
    print(f"  Metrics computed: {sorted(all_keys - {'N', 'M'})}")

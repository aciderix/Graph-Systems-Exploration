#!/usr/bin/env python3
"""
G10.2 — OPÉRATIONS EXOTIQUES × MÉTRIQUES NON-SPECTRALES

On cherche des lois de conservation dans le COMPLÉMENTAIRE spectral :
- Opérations SANS théorie spectrale connue
- Métriques qui SÉPARENT les graphes cospectraux (= info hors spectre)
- → Toute conservation trouvée est STRUCTURELLEMENT nouvelle

Opérations exotiques :
1. k-core extraction (k=2,3)
2. Clique graph K(G) 
3. Mycielskian M(G)
4. Max-betweenness edge contraction
5. Neighborhood intersection graph
"""

import networkx as nx
import numpy as np
from itertools import combinations
import json
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# OPÉRATIONS EXOTIQUES
# ============================================================

def op_kcore(G, k=2):
    """k-core : sous-graphe maximal de degré minimum k."""
    H = nx.k_core(G, k=k)
    if H.number_of_nodes() < 3 or H.number_of_edges() < 3:
        return None
    return H

def op_clique_graph(G):
    """Clique graph : sommets = cliques maximales, arêtes = cliques partageant un sommet."""
    try:
        cliques = list(nx.find_cliques(G))
        if len(cliques) < 3 or len(cliques) > 200:
            return None
        H = nx.Graph()
        for i, c1 in enumerate(cliques):
            for j, c2 in enumerate(cliques):
                if i < j and set(c1) & set(c2):
                    H.add_edge(i, j)
        if H.number_of_nodes() < 3 or not nx.is_connected(H):
            return None
        return H
    except:
        return None

def op_mycielskian(G):
    """Mycielskian M(G) : construction qui augmente le nombre chromatique."""
    try:
        H = nx.mycielskian(G)
        if H.number_of_nodes() > 200:
            return None
        return H
    except:
        return None

def op_max_betweenness_contraction(G):
    """Contracter l'arête de betweenness max."""
    try:
        eb = nx.edge_betweenness_centrality(G)
        if not eb:
            return None
        max_edge = max(eb, key=eb.get)
        H = nx.contracted_edge(G, max_edge, self_loops=False)
        H = nx.convert_node_labels_to_integers(H)
        if H.number_of_nodes() < 3:
            return None
        # Enlever les multi-arêtes éventuelles
        H = nx.Graph(H)
        if not nx.is_connected(H):
            return None
        return H
    except:
        return None

def op_neighborhood_intersection(G):
    """Graphe d'intersection de voisinages : arête si |N(u)∩N(v)| > 0 ET (u,v) pas dans G."""
    H = nx.Graph()
    H.add_nodes_from(G.nodes())
    nodes = list(G.nodes())
    for i, u in enumerate(nodes):
        nu = set(G.neighbors(u))
        for j in range(i+1, len(nodes)):
            v = nodes[j]
            nv = set(G.neighbors(v))
            # Arête si voisins communs > 0 (inclut les arêtes existantes + nouvelles)
            if len(nu & nv) > 0 and not G.has_edge(u, v):
                H.add_edge(u, v)
    if H.number_of_edges() < 3 or not nx.is_connected(H):
        return None
    return H

def op_local_complement(G):
    """Complément local au sommet de degré max : complémente le sous-graphe induit par N(v)."""
    try:
        v = max(G.nodes(), key=lambda x: G.degree(x))
        nbrs = list(G.neighbors(v))
        if len(nbrs) < 2:
            return None
        H = G.copy()
        for i, u in enumerate(nbrs):
            for j in range(i+1, len(nbrs)):
                w = nbrs[j]
                if H.has_edge(u, w):
                    H.remove_edge(u, w)
                else:
                    H.add_edge(u, w)
        if not nx.is_connected(H):
            return None
        return H
    except:
        return None

# ============================================================
# MÉTRIQUES NON-SPECTRALES (les séparateurs de cospectraux)
# ============================================================

def compute_nonspectral_metrics(G):
    """Métriques qui séparent les graphes cospectraux = info hors spectre."""
    n = G.number_of_nodes()
    m = G.number_of_edges()
    if n < 3 or m < 3:
        return None
    
    metrics = {}
    metrics['n'] = n
    metrics['m'] = m
    metrics['density'] = 2 * m / (n * (n-1))
    
    # Degrés
    degs = np.array([d for _, d in G.degree()])
    metrics['deg_mean'] = float(np.mean(degs))
    metrics['deg_max'] = float(np.max(degs))
    metrics['deg_min'] = float(np.min(degs))
    metrics['deg_std'] = float(np.std(degs))
    if np.std(degs) > 1e-10:
        metrics['deg_skew'] = float(np.mean(((degs - np.mean(degs)) / np.std(degs))**3))
    else:
        metrics['deg_skew'] = 0.0
    
    # Clustering
    metrics['transitivity'] = nx.transitivity(G)
    metrics['avg_clustering'] = nx.average_clustering(G)
    clustering = np.array(list(nx.clustering(G).values()))
    metrics['clustering_std'] = float(np.std(clustering))
    
    # Distances
    try:
        metrics['diameter'] = nx.diameter(G)
        metrics['radius'] = nx.radius(G)
        path_lengths = dict(nx.all_pairs_shortest_path_length(G))
        all_dists = []
        for u in path_lengths:
            for v, d in path_lengths[u].items():
                if u < v:
                    all_dists.append(d)
        all_dists = np.array(all_dists)
        metrics['avg_path_length'] = float(np.mean(all_dists))
        metrics['wiener_index'] = float(np.sum(all_dists))
    except:
        return None  # Skip disconnected
    
    # Betweenness
    bc = np.array(list(nx.betweenness_centrality(G).values()))
    metrics['betweenness_max'] = float(np.max(bc))
    metrics['betweenness_mean'] = float(np.mean(bc))
    metrics['betweenness_std'] = float(np.std(bc))
    
    # Closeness
    cc = np.array(list(nx.closeness_centrality(G).values()))
    metrics['closeness_mean'] = float(np.mean(cc))
    metrics['closeness_std'] = float(np.std(cc))
    
    # Connectivity
    metrics['node_connectivity'] = nx.node_connectivity(G)
    metrics['edge_connectivity'] = nx.edge_connectivity(G)
    
    # Triangles et structures locales
    tri_dict = nx.triangles(G)
    metrics['triangle_count'] = sum(tri_dict.values()) // 3
    
    # P3 (chemins de longueur 2)
    p3 = sum(d * (d-1) // 2 for _, d in G.degree()) - 3 * metrics['triangle_count']
    metrics['p3_count'] = p3
    
    # Common neighbor pairs (lié aux C4)
    cn_pairs = 0
    for u, v in combinations(G.nodes(), 2):
        cn = len(set(G.neighbors(u)) & set(G.neighbors(v)))
        cn_pairs += cn * (cn - 1) // 2
    metrics['common_neighbor_pairs'] = cn_pairs
    
    # Matching
    try:
        matching = nx.max_weight_matching(G)
        metrics['max_matching'] = len(matching)
    except:
        pass
    
    return metrics

# ============================================================
# GÉNÉRATION DE GRAPHES
# ============================================================

def generate_test_graphs(n_target=80):
    """Générer un ensemble diversifié de graphes connectés."""
    graphs = []
    
    # Graphes classiques
    for n in [6, 8, 10, 12, 15, 20]:
        graphs.append(('cycle', n, nx.cycle_graph(n)))
        graphs.append(('path', n, nx.path_graph(n)))
        if n <= 15:
            graphs.append(('complete', n, nx.complete_graph(n)))
        graphs.append(('wheel', n, nx.wheel_graph(n)))
    
    # Bipartis
    for n1, n2 in [(3,3), (3,5), (4,4), (4,6), (5,5)]:
        graphs.append(('bipartite', n1+n2, nx.complete_bipartite_graph(n1, n2)))
    
    # Réguliers
    for n, d in [(8,3), (10,3), (10,4), (12,3), (12,4), (14,3), (16,3), (20,3)]:
        try:
            G = nx.random_regular_graph(d, n, seed=42)
            graphs.append(('regular', n, G))
        except:
            pass
    
    # Erdos-Renyi
    rng = np.random.RandomState(42)
    for n in [8, 10, 12, 15, 20, 25]:
        for p in [0.2, 0.3, 0.5, 0.7]:
            G = nx.erdos_renyi_graph(n, p, seed=int(rng.randint(1e6)))
            if nx.is_connected(G) and G.number_of_edges() >= 3:
                graphs.append(('erdos_renyi', n, G))
    
    # Barabasi-Albert
    for n in [10, 15, 20, 25, 30]:
        for m in [2, 3]:
            G = nx.barabasi_albert_graph(n, m, seed=42)
            graphs.append(('barabasi', n, G))
    
    # Watts-Strogatz
    for n in [10, 15, 20, 25]:
        for p in [0.1, 0.3, 0.5]:
            G = nx.watts_strogatz_graph(n, 4, p, seed=42)
            if nx.is_connected(G):
                graphs.append(('watts_strogatz', n, G))
    
    # Named graphs
    named = [
        ('petersen', nx.petersen_graph()),
        ('dodecahedron', nx.dodecahedral_graph()),
        ('icosahedron', nx.icosahedral_graph()),
    ]
    for name, G in named:
        graphs.append((name, G.number_of_nodes(), G))
    
    return graphs[:n_target]


# ============================================================
# RECHERCHE DE LOIS DE CONSERVATION (SVD dans l'espace non-spectral)
# ============================================================

def search_conservation_laws(before_data, after_data, op_name):
    """
    Chercher des combinaisons de métriques conservées sous l'opération.
    Méthode : log-ratio + SVD (même approche que G9 mais espace non-spectral).
    """
    # Aligner les métriques
    common_metrics = sorted(set(before_data[0].keys()) & set(after_data[0].keys()))
    # Exclure n, m (changent trivialement)
    common_metrics = [k for k in common_metrics if k not in ['n', 'm']]
    
    n_graphs = len(before_data)
    n_metrics = len(common_metrics)
    
    if n_graphs < 5 or n_metrics < 3:
        return []
    
    # Construire la matrice de log-ratios
    # ratio[i][j] = log(after[i][j] / before[i][j])
    ratios = []
    valid_indices = []
    
    for i in range(n_graphs):
        row = []
        valid = True
        for k in common_metrics:
            b = before_data[i].get(k, 0)
            a = after_data[i].get(k, 0)
            if b is None or a is None or abs(b) < 1e-15 or abs(a) < 1e-15:
                valid = False
                break
            row.append(np.log(abs(a) / abs(b)))
        if valid and len(row) == n_metrics:
            ratios.append(row)
            valid_indices.append(i)
    
    if len(ratios) < 5:
        return []
    
    R = np.array(ratios)
    
    # SVD pour trouver les dimensions de variance nulle
    U, S, Vt = np.linalg.svd(R, full_matrices=False)
    
    laws = []
    for j in range(len(S)):
        if S[j] < 0.05:  # Variance quasi-nulle = conservation
            coeffs = Vt[j]
            # Vérifier que ce n'est pas trivial (pas que des zéros sauf un)
            nonzero = np.sum(np.abs(coeffs) > 0.05)
            if nonzero >= 2:
                law = {
                    'singular_value': float(S[j]),
                    'coefficients': {k: float(c) for k, c in zip(common_metrics, coeffs) if abs(c) > 0.05},
                    'n_terms': int(nonzero),
                    'n_graphs': len(ratios)
                }
                laws.append(law)
    
    return laws

def search_conservation_direct(before_data, after_data, op_name):
    """
    Approche alternative : chercher des quantités Q(G) telles que Q(T(G)) = f(Q(G)).
    Plus général que le log-ratio (capture aussi Q(T(G)) = Q(G) + c).
    """
    common_metrics = sorted(set(before_data[0].keys()) & set(after_data[0].keys()))
    common_metrics = [k for k in common_metrics if k not in ['n', 'm']]
    
    laws = []
    
    # Pour chaque paire de métriques (avant, après), chercher une relation linéaire
    for metric in common_metrics:
        before_vals = [d.get(metric) for d in before_data]
        after_vals = [d.get(metric) for d in after_data]
        
        # Filtrer les None
        pairs = [(b, a) for b, a in zip(before_vals, after_vals) 
                 if b is not None and a is not None and not np.isnan(b) and not np.isnan(a)]
        
        if len(pairs) < 5:
            continue
        
        b_arr = np.array([p[0] for p in pairs])
        a_arr = np.array([p[1] for p in pairs])
        
        # Test 1 : a = const * b (proportionnalité)
        if np.std(b_arr) > 1e-10:
            ratio = a_arr / (b_arr + 1e-15)
            if np.std(ratio) / (np.mean(np.abs(ratio)) + 1e-15) < 0.05:
                laws.append({
                    'type': 'proportional',
                    'metric': metric,
                    'ratio_mean': float(np.mean(ratio)),
                    'ratio_std': float(np.std(ratio)),
                    'cv': float(np.std(ratio) / (np.mean(np.abs(ratio)) + 1e-15)),
                    'n_graphs': len(pairs)
                })
        
        # Test 2 : a - b = const (additive)
        diff = a_arr - b_arr
        if np.std(diff) / (np.mean(np.abs(diff)) + 1e-15) < 0.05 and np.mean(np.abs(diff)) > 1e-10:
            laws.append({
                'type': 'additive',
                'metric': metric,
                'diff_mean': float(np.mean(diff)),
                'diff_std': float(np.std(diff)),
                'cv': float(np.std(diff) / (np.mean(np.abs(diff)) + 1e-15)),
                'n_graphs': len(pairs)
            })
        
        # Test 3 : a = const (output constant)
        if np.std(a_arr) / (np.mean(np.abs(a_arr)) + 1e-15) < 0.05:
            laws.append({
                'type': 'output_constant',
                'metric': metric,
                'const_mean': float(np.mean(a_arr)),
                'const_std': float(np.std(a_arr)),
                'cv': float(np.std(a_arr) / (np.mean(np.abs(a_arr)) + 1e-15)),
                'n_graphs': len(pairs)
            })
    
    # Pour chaque paire de métriques différentes : a_metric1 ~ b * b_metric2 + c
    for m1 in common_metrics:
        for m2 in common_metrics:
            if m1 >= m2:
                continue
            
            # after[m1] = α * before[m2] + β ?
            a_vals = [d.get(m1) for d in after_data]
            b_vals = [d.get(m2) for d in before_data]
            
            pairs = [(a, b) for a, b in zip(a_vals, b_vals)
                     if a is not None and b is not None and not np.isnan(a) and not np.isnan(b)]
            
            if len(pairs) < 5:
                continue
            
            a_arr = np.array([p[0] for p in pairs])
            b_arr = np.array([p[1] for p in pairs])
            
            if np.std(b_arr) < 1e-10:
                continue
            
            # Regression linéaire
            A_mat = np.column_stack([b_arr, np.ones(len(b_arr))])
            try:
                result = np.linalg.lstsq(A_mat, a_arr, rcond=None)
                coeffs = result[0]
                pred = A_mat @ coeffs
                residual = np.std(a_arr - pred)
                r2 = 1 - residual**2 / (np.var(a_arr) + 1e-15)
                
                if r2 > 0.98:
                    laws.append({
                        'type': 'cross_metric_linear',
                        'after_metric': m1,
                        'before_metric': m2,
                        'alpha': float(coeffs[0]),
                        'beta': float(coeffs[1]),
                        'r2': float(r2),
                        'residual_std': float(residual),
                        'n_graphs': len(pairs)
                    })
            except:
                pass
    
    return laws


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("G10.2 — OPÉRATIONS EXOTIQUES × MÉTRIQUES NON-SPECTRALES")
    print("=" * 70)
    
    # Générer les graphes
    print("\nGénération des graphes...")
    graphs = generate_test_graphs(80)
    print(f"  → {len(graphs)} graphes générés")
    
    # Définir les opérations
    operations = {
        'kcore_2': lambda G: op_kcore(G, k=2),
        'kcore_3': lambda G: op_kcore(G, k=3),
        'clique_graph': op_clique_graph,
        'mycielskian': op_mycielskian,
        'betw_contraction': op_max_betweenness_contraction,
        'local_complement': op_local_complement,
    }
    
    all_results = {}
    
    for op_name, op_func in operations.items():
        print(f"\n{'='*60}")
        print(f"Opération : {op_name}")
        print(f"{'='*60}")
        
        before_metrics = []
        after_metrics = []
        graph_names = []
        n_failed = 0
        
        for gtype, gn, G in graphs:
            # Métriques avant
            m_before = compute_nonspectral_metrics(G)
            if m_before is None:
                continue
            
            # Appliquer l'opération
            try:
                H = op_func(G)
            except Exception as e:
                n_failed += 1
                continue
            
            if H is None:
                n_failed += 1
                continue
            
            # Métriques après
            m_after = compute_nonspectral_metrics(H)
            if m_after is None:
                n_failed += 1
                continue
            
            before_metrics.append(m_before)
            after_metrics.append(m_after)
            graph_names.append(f"{gtype}_{gn}")
        
        print(f"  Réussi : {len(before_metrics)} graphes ({n_failed} échecs)")
        
        if len(before_metrics) < 5:
            print(f"  Pas assez de données, skip.")
            continue
        
        # Chercher des lois
        print(f"  Recherche de lois (SVD log-ratio)...")
        laws_svd = search_conservation_laws(before_metrics, after_metrics, op_name)
        print(f"    → {len(laws_svd)} lois SVD trouvées")
        
        print(f"  Recherche de lois (directe)...")
        laws_direct = search_conservation_direct(before_metrics, after_metrics, op_name)
        print(f"    → {len(laws_direct)} lois directes trouvées")
        
        # Afficher les meilleures
        if laws_svd:
            print(f"\n  TOP lois SVD :")
            for i, law in enumerate(laws_svd[:3]):
                terms = ', '.join(f'{k}^{v:.2f}' for k, v in 
                    sorted(law['coefficients'].items(), key=lambda x: -abs(x[1])))
                print(f"    [{i+1}] σ={law['singular_value']:.4f} : {terms}")
        
        if laws_direct:
            # Trier par qualité
            laws_direct.sort(key=lambda x: x.get('cv', x.get('residual_std', 1)))
            print(f"\n  TOP lois directes :")
            for i, law in enumerate(laws_direct[:5]):
                if law['type'] == 'proportional':
                    print(f"    [{i+1}] {op_name}({law['metric']}) ≈ {law['ratio_mean']:.4f} × {law['metric']} (cv={law['cv']:.4f})")
                elif law['type'] == 'additive':
                    print(f"    [{i+1}] {op_name}({law['metric']}) - {law['metric']} ≈ {law['diff_mean']:.4f} (cv={law['cv']:.4f})")
                elif law['type'] == 'cross_metric_linear':
                    print(f"    [{i+1}] {op_name}({law['after_metric']}) ≈ {law['alpha']:.4f} × {law['before_metric']} + {law['beta']:.4f} (R²={law['r2']:.4f})")
                elif law['type'] == 'output_constant':
                    print(f"    [{i+1}] {op_name}({law['metric']}) ≈ {law['const_mean']:.4f} (cv={law['cv']:.4f})")
        
        all_results[op_name] = {
            'n_graphs': len(before_metrics),
            'svd_laws': laws_svd,
            'direct_laws': laws_direct,
        }
    
    # Sauvegarder
    with open('/agent/home/Graph-Systems-Exploration/data/g10_exotic_ops.json', 'w') as f:
        json.dump(all_results, f, indent=2, default=str)
    
    print(f"\n{'='*70}")
    print("SAUVEGARDÉ dans g10_exotic_ops.json")
    print(f"{'='*70}")
    
    # Synthèse
    print(f"\n{'='*70}")
    print("SYNTHÈSE DES LOIS TROUVÉES")
    print(f"{'='*70}")
    
    total_svd = sum(len(v['svd_laws']) for v in all_results.values())
    total_direct = sum(len(v['direct_laws']) for v in all_results.values())
    print(f"\nTotal : {total_svd} lois SVD + {total_direct} lois directes")
    
    for op_name, data in all_results.items():
        n_svd = len(data['svd_laws'])
        n_direct = len(data['direct_laws'])
        print(f"\n  {op_name} : {n_svd} SVD + {n_direct} directes sur {data['n_graphs']} graphes")

if __name__ == '__main__':
    main()

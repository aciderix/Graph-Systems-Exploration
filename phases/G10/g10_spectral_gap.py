#!/usr/bin/env python3
"""
G10.1 — LA FAILLE SPECTRALE
Objectif : Trouver ce que le spectre RATE.

Stratégie :
1. Générer des paires de graphes cospectraux (même spectre, structure différente)
2. Calculer un maximum de métriques sur chaque paire
3. Identifier les métriques qui SÉPARENT les paires cospectrales
   → Ces métriques capturent de l'information HORS spectre

Si une métrique sépare des graphes cospectraux, elle encode quelque chose
que les eigenvalues ne voient pas. C'est la seule zone où une loi nouvelle
peut exister.
"""

import networkx as nx
import numpy as np
from itertools import combinations
import json
import sys
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# PARTIE 1 : Générer des paires cospectrales
# ============================================================

def adj_spectrum(G):
    """Spectre de la matrice d'adjacence, trié et arrondi."""
    A = nx.adjacency_matrix(G).toarray().astype(float)
    eigs = np.sort(np.linalg.eigvalsh(A))
    return np.round(eigs, 8)

def lap_spectrum(G):
    """Spectre du Laplacien, trié et arrondi."""
    L = nx.laplacian_matrix(G).toarray().astype(float)
    eigs = np.sort(np.linalg.eigvalsh(L))
    return np.round(eigs, 8)

def are_cospectral(G1, G2, matrix='adj'):
    """Vérifie si deux graphes sont cospectraux."""
    if G1.number_of_nodes() != G2.number_of_nodes():
        return False
    if G1.number_of_edges() != G2.number_of_edges():
        return False
    if matrix == 'adj':
        s1, s2 = adj_spectrum(G1), adj_spectrum(G2)
    else:
        s1, s2 = lap_spectrum(G1), lap_spectrum(G2)
    return np.allclose(s1, s2, atol=1e-6)

def are_isomorphic(G1, G2):
    """Vérifie si deux graphes sont isomorphes."""
    return nx.is_isomorphic(G1, G2)

# --- Méthode 1 : Paires cospectrales connues ---

def known_cospectral_pairs():
    """Paires cospectrales classiques de la littérature."""
    pairs = []
    
    # Paire 1 : Les plus petites cospectrales (n=6)
    # C6 vs K3,3-minus-matching
    G1 = nx.cycle_graph(6)
    # Union of two triangles
    G2 = nx.Graph()
    G2.add_edges_from([(0,1),(1,2),(2,0),(3,4),(4,5),(5,3)])
    if are_cospectral(G1, G2, 'adj') and not are_isomorphic(G1, G2):
        pairs.append(('C6', 'K3+K3', G1, G2))
    
    # Paire 2 : Graphes de Schwenk (arbres cospectraux n=11)
    # Deux arbres non-isomorphes avec même spectre d'adjacence
    T1 = nx.Graph()
    T1.add_edges_from([(0,1),(1,2),(2,3),(3,4),(4,5),(2,6),(6,7),(7,8),(6,9),(9,10)])
    T2 = nx.Graph()
    T2.add_edges_from([(0,1),(1,2),(2,3),(3,4),(2,5),(5,6),(6,7),(5,8),(8,9),(9,10)])
    if are_cospectral(T1, T2, 'adj') and not are_isomorphic(T1, T2):
        pairs.append(('tree_11a', 'tree_11b', T1, T2))
    
    # Paire 3 : Graphes réguliers cospectraux classiques
    # Shrikhande graph vs L(K4,4) — 16 nœuds, 6-regular
    # Construisons le Shrikhande
    shrikhande = nx.Graph()
    for i in range(4):
        for j in range(4):
            v = i * 4 + j
            # voisins : (i, j±1), (i±1, j), (i+1, j+1), (i-1, j-1) mod 4
            neighbors = [
                ((i) % 4) * 4 + ((j+1) % 4),
                ((i) % 4) * 4 + ((j-1) % 4),
                ((i+1) % 4) * 4 + ((j) % 4),
                ((i-1) % 4) * 4 + ((j) % 4),
                ((i+1) % 4) * 4 + ((j+1) % 4),
                ((i-1) % 4) * 4 + ((j-1) % 4),
            ]
            for n in neighbors:
                if n != v:
                    shrikhande.add_edge(v, n)
    
    # L(K4,4) = line graph of complete bipartite K4,4
    K44 = nx.complete_bipartite_graph(4, 4)
    LK44 = nx.line_graph(K44)
    LK44 = nx.convert_node_labels_to_integers(LK44)
    
    if shrikhande.number_of_nodes() == LK44.number_of_nodes():
        if are_cospectral(shrikhande, LK44, 'adj') and not are_isomorphic(shrikhande, LK44):
            pairs.append(('shrikhande', 'L(K44)', shrikhande, LK44))
    
    # Paire 4 : Petersen vs K_{1,4,4} complement-like
    # Utilisons des graphes strongly regular connus
    petersen = nx.petersen_graph()
    # Kneser(5,2) = Petersen, cherchons un graphe (10,3,0,1) SRG s'il en existe un autre
    # En fait Petersen est l'unique SRG(10,3,0,1), essayons autre chose
    
    # Paire 4 : deux graphes de 7 nœuds cospectraux
    G4a = nx.Graph()
    G4a.add_edges_from([(0,1),(0,2),(0,3),(1,2),(3,4),(4,5),(5,6)])
    G4b = nx.Graph()
    G4b.add_edges_from([(0,1),(0,2),(1,2),(1,3),(3,4),(4,5),(4,6)])
    if are_cospectral(G4a, G4b, 'adj') and not are_isomorphic(G4a, G4b):
        pairs.append(('G7a', 'G7b', G4a, G4b))
    
    return pairs

# --- Méthode 2 : Godsil-McKay switching ---

def godsil_mckay_switch(G, partition_seed=42):
    """
    Godsil-McKay switching : produit un graphe cospectral.
    
    Idée : trouver un sous-ensemble C de sommets tel que chaque sommet hors C
    a 0, |C|/2, ou |C| voisins dans C. Puis switcher les arêtes.
    """
    rng = np.random.RandomState(partition_seed)
    nodes = list(G.nodes())
    n = len(nodes)
    
    # Essayer des sous-ensembles aléatoires de taille paire
    for attempt in range(200):
        size = rng.choice([2, 4, 6])
        if size >= n:
            continue
        C = set(rng.choice(nodes, size=size, replace=False))
        rest = [v for v in nodes if v not in C]
        
        # Vérifier la condition GM : chaque v hors C a 0, |C|/2, ou |C| voisins dans C
        valid = True
        half = len(C) / 2
        for v in rest:
            nbrs_in_C = len(set(G.neighbors(v)) & C)
            if nbrs_in_C not in [0, half, len(C)]:
                valid = False
                break
        
        if not valid:
            continue
        
        # Switcher : pour chaque v avec |C|/2 voisins dans C, inverser les arêtes
        H = G.copy()
        for v in rest:
            nbrs_in_C = set(G.neighbors(v)) & C
            if len(nbrs_in_C) == half:
                # Inverser : supprimer les arêtes existantes, ajouter les manquantes
                non_nbrs_in_C = C - nbrs_in_C
                for u in nbrs_in_C:
                    H.remove_edge(v, u)
                for u in non_nbrs_in_C:
                    H.add_edge(v, u)
        
        if not are_isomorphic(G, H) and nx.is_connected(H):
            return H
    
    return None

# --- Méthode 3 : Recherche brute dans les graphes de petite taille ---

def find_cospectral_bruteforce(n_range=(6, 9), max_per_n=500):
    """Chercher des paires cospectrales parmi des graphes aléatoires."""
    pairs = []
    rng = np.random.RandomState(42)
    
    for n in range(n_range[0], n_range[1] + 1):
        graphs = []
        spectra = []
        
        # Générer des graphes aléatoires
        for i in range(max_per_n):
            p = rng.uniform(0.2, 0.8)
            G = nx.erdos_renyi_graph(n, p, seed=int(rng.randint(1e6)))
            if not nx.is_connected(G):
                continue
            spec = tuple(adj_spectrum(G))
            
            # Chercher un match
            for j, prev_spec in enumerate(spectra):
                if len(spec) == len(prev_spec) and np.allclose(spec, prev_spec, atol=1e-6):
                    if not are_isomorphic(G, graphs[j]):
                        pairs.append((f'rand_{n}_{j}', f'rand_{n}_{i}', graphs[j], G))
                        if len(pairs) >= 5:
                            return pairs
            
            graphs.append(G)
            spectra.append(spec)
    
    return pairs

# --- Méthode 4 : Graphes cospectraux par construction algébrique ---

def algebraic_cospectral():
    """Constructions algébriques connues de paires cospectrales."""
    pairs = []
    
    # Construction par produit : G×K2 et H×K2 peuvent être cospectraux
    # même si G et H ne le sont pas
    
    # Seidel switching sur graphes réguliers
    for n in [8, 10, 12]:
        G = nx.random_regular_graph(3, n, seed=42)
        H = godsil_mckay_switch(G, partition_seed=42)
        if H is not None:
            pairs.append((f'regular_{n}', f'GM_switch_{n}', G, H))
        
        # Essayer plusieurs seeds
        for seed in range(10):
            G = nx.random_regular_graph(3, n, seed=seed)
            H = godsil_mckay_switch(G, partition_seed=seed*7+1)
            if H is not None:
                pairs.append((f'reg3_{n}_s{seed}', f'GM_{n}_s{seed}', G, H))
                break
    
    # Paires de graphes bipartis
    for n1, n2 in [(3,4), (4,4), (3,5)]:
        G = nx.complete_bipartite_graph(n1, n2)
        H = godsil_mckay_switch(G)
        if H is not None:
            pairs.append((f'K_{n1}_{n2}', f'GM_K_{n1}_{n2}', G, H))
    
    return pairs

# ============================================================
# PARTIE 2 : Métriques exhaustives (spectrales ET non-spectrales)
# ============================================================

def compute_all_metrics(G):
    """Calcule un large ensemble de métriques, classées par type."""
    n = G.number_of_nodes()
    m = G.number_of_edges()
    
    if n == 0 or m == 0:
        return {}
    
    metrics = {}
    
    # --- SPECTRALEMENT DÉTERMINÉES (contrôle) ---
    A = nx.adjacency_matrix(G).toarray().astype(float)
    L = nx.laplacian_matrix(G).toarray().astype(float)
    adj_eigs = np.sort(np.linalg.eigvalsh(A))
    lap_eigs = np.sort(np.linalg.eigvalsh(L))
    
    metrics['adj_spectral_radius'] = float(adj_eigs[-1])
    metrics['adj_energy'] = float(np.sum(np.abs(adj_eigs)))
    metrics['lap_spectral_gap'] = float(lap_eigs[1]) if n > 1 else 0
    metrics['lap_largest'] = float(lap_eigs[-1])
    metrics['adj_trace_sq'] = float(np.sum(adj_eigs**2))  # = 2m
    metrics['adj_trace_cube'] = float(np.sum(adj_eigs**3))  # = 6*triangles
    metrics['adj_trace_4'] = float(np.sum(adj_eigs**4))
    metrics['n_nodes'] = n
    metrics['n_edges'] = m
    
    # --- POTENTIELLEMENT NON-SPECTRALES ---
    
    # Degrés
    degs = [d for _, d in G.degree()]
    metrics['deg_max'] = max(degs)
    metrics['deg_min'] = min(degs)
    metrics['deg_std'] = float(np.std(degs))
    metrics['deg_skew'] = float(np.mean(((np.array(degs) - np.mean(degs)) / (np.std(degs) + 1e-10))**3))
    metrics['deg_kurtosis'] = float(np.mean(((np.array(degs) - np.mean(degs)) / (np.std(degs) + 1e-10))**4))
    bc_degs = np.bincount(degs)[1:]
    p_degs = bc_degs / n
    p_degs = p_degs[p_degs > 0]
    metrics['deg_entropy'] = float(-np.sum(p_degs * np.log(p_degs + 1e-15)))
    
    # Clustering / transitivity
    metrics['transitivity'] = nx.transitivity(G)
    metrics['avg_clustering'] = nx.average_clustering(G)
    clustering = list(nx.clustering(G).values())
    metrics['clustering_std'] = float(np.std(clustering))
    metrics['clustering_max'] = float(max(clustering))
    metrics['clustering_min'] = float(min(clustering))
    hist_cl = np.histogram(clustering, bins=10, density=True)[0] * 0.1
    hist_cl = hist_cl[hist_cl > 0]
    metrics['clustering_entropy'] = float(-np.sum(hist_cl * np.log(hist_cl + 1e-15)))
    
    # Distances
    try:
        diam = nx.diameter(G)
        metrics['diameter'] = diam
        metrics['radius'] = nx.radius(G)
        
        # Distribution des distances
        path_lengths = dict(nx.all_pairs_shortest_path_length(G))
        all_dists = []
        for u in path_lengths:
            for v, d in path_lengths[u].items():
                if u < v:
                    all_dists.append(d)
        all_dists = np.array(all_dists)
        metrics['avg_path_length'] = float(np.mean(all_dists))
        metrics['path_length_std'] = float(np.std(all_dists))
        metrics['path_length_max'] = float(np.max(all_dists))
        
        # Wiener index
        metrics['wiener_index'] = float(np.sum(all_dists))
    except:
        metrics['diameter'] = -1
    
    # Centralités
    try:
        bc = list(nx.betweenness_centrality(G).values())
        metrics['betweenness_max'] = float(max(bc))
        metrics['betweenness_mean'] = float(np.mean(bc))
        metrics['betweenness_std'] = float(np.std(bc))
        hist_bc = np.histogram(bc, bins=10, density=True)[0] * 0.1
        hist_bc = hist_bc[hist_bc > 0]
        metrics['betweenness_entropy'] = float(-np.sum(hist_bc * np.log(hist_bc + 1e-15)))
    except:
        pass
    
    try:
        cc = list(nx.closeness_centrality(G).values())
        metrics['closeness_max'] = float(max(cc))
        metrics['closeness_mean'] = float(np.mean(cc))
        metrics['closeness_std'] = float(np.std(cc))
    except:
        pass
    
    # Automorphismes (approximation via orbites)
    # Le groupe d'automorphismes n'est PAS spectralement déterminé
    try:
        # Nombre d'orbites via les orbites de couleur (hash des voisinages)
        color = {}
        for v in G.nodes():
            nbr_degs = tuple(sorted([G.degree(u) for u in G.neighbors(v)]))
            color[v] = (G.degree(v), nbr_degs)
        n_orbits = len(set(color.values()))
        metrics['n_color_orbits'] = n_orbits
        metrics['orbit_ratio'] = n_orbits / n
    except:
        pass
    
    # Indépendance et matching
    try:
        # Approximation greedy de l'independent set
        indep = nx.maximal_independent_set(G, seed=42)
        metrics['max_indep_approx'] = len(indep)
    except:
        pass
    
    try:
        matching = nx.max_weight_matching(G)
        metrics['max_matching'] = len(matching)
    except:
        pass
    
    # Connectivité
    metrics['node_connectivity'] = nx.node_connectivity(G)
    metrics['edge_connectivity'] = nx.edge_connectivity(G)
    
    # Nombre chromatique (approximation greedy)
    try:
        coloring = nx.greedy_color(G, strategy='largest_first')
        metrics['chromatic_greedy'] = max(coloring.values()) + 1
    except:
        pass
    
    # Clique
    try:
        metrics['clique_number'] = nx.graph_clique_number(G)
    except:
        try:
            cliques = list(nx.find_cliques(G))
            metrics['clique_number'] = max(len(c) for c in cliques)
        except:
            pass
    
    # Girth (plus petit cycle)
    try:
        girth = float('inf')
        for v in G.nodes():
            for u in G.neighbors(v):
                # BFS sans l'arête (v,u)
                H = G.copy()
                H.remove_edge(v, u)
                try:
                    path = nx.shortest_path_length(H, v, u)
                    girth = min(girth, path + 1)
                except nx.NetworkXNoPath:
                    pass
            if girth <= 3:
                break
        metrics['girth'] = int(girth) if girth < float('inf') else -1
    except:
        pass
    
    # Structure locale : nombre de sous-graphes induits spécifiques
    # P3 count (chemins de longueur 2)
    p3_count = 0
    for v in G.nodes():
        d = G.degree(v)
        p3_count += d * (d - 1) // 2
    # Soustraire les triangles (chaque triangle contribue 3 P3)
    triangles = sum(nx.triangles(G).values()) // 3
    p3_count -= 3 * triangles
    metrics['p3_count'] = p3_count
    metrics['triangle_count'] = triangles
    
    # C4 count approximé (4-cycles)
    # trace(A^4) = 2m + 4*triangles_adj + 8*C4 + ...
    # Difficile à isoler, utilisons les paires de voisins communs
    c4_count = 0
    for u, v in combinations(G.nodes(), 2):
        cn = len(set(G.neighbors(u)) & set(G.neighbors(v)))
        c4_count += cn * (cn - 1) // 2
    # Correction : chaque C4 est compté 3 fois, et les triangles contribuent aussi
    metrics['common_neighbor_pairs'] = c4_count
    
    # Résistance effective (Kirchhoff index)
    try:
        if lap_eigs[1] > 1e-10:
            kirchhoff = n * np.sum(1.0 / lap_eigs[1:])
            metrics['kirchhoff_index'] = float(kirchhoff)
    except:
        pass
    
    # Normalized Laplacian spectrum
    try:
        NL = nx.normalized_laplacian_matrix(G).toarray().astype(float)
        nl_eigs = np.sort(np.linalg.eigvalsh(NL))
        metrics['norm_lap_spectral_gap'] = float(nl_eigs[1]) if n > 1 else 0
        metrics['norm_lap_largest'] = float(nl_eigs[-1])
        metrics['norm_lap_energy'] = float(np.sum(np.abs(nl_eigs - 1)))
    except:
        pass
    
    # Signless Laplacian
    try:
        D = np.diag(degs)
        Q = D + A
        q_eigs = np.sort(np.linalg.eigvalsh(Q))
        metrics['signless_lap_largest'] = float(q_eigs[-1])
        metrics['signless_lap_smallest'] = float(q_eigs[0])
        metrics['signless_lap_gap'] = float(q_eigs[-1] - q_eigs[-2]) if n > 1 else 0
    except:
        pass
    
    # Estrada index
    try:
        metrics['estrada_index'] = float(np.sum(np.exp(adj_eigs)))
    except:
        pass
    
    # Distance matrix spectrum
    try:
        dist_matrix = np.zeros((n, n))
        for i, u in enumerate(G.nodes()):
            for j, v in enumerate(G.nodes()):
                if i != j:
                    dist_matrix[i][j] = nx.shortest_path_length(G, u, v)
        dist_eigs = np.sort(np.linalg.eigvalsh(dist_matrix))
        metrics['dist_spectral_radius'] = float(np.abs(dist_eigs).max())
        metrics['dist_energy'] = float(np.sum(np.abs(dist_eigs)))
    except:
        pass
    
    return metrics


# ============================================================
# PARTIE 3 : MAIN — Trouver la faille
# ============================================================

def main():
    print("=" * 70)
    print("G10.1 — LA FAILLE SPECTRALE")
    print("Objectif : trouver ce que le spectre ne voit pas")
    print("=" * 70)
    
    # --- Collecter toutes les paires cospectrales ---
    all_pairs = []
    
    print("\n[1/4] Paires cospectrales connues...")
    known = known_cospectral_pairs()
    all_pairs.extend(known)
    print(f"  → {len(known)} paires trouvées")
    for name1, name2, _, _ in known:
        print(f"    {name1} ↔ {name2}")
    
    print("\n[2/4] Godsil-McKay switching sur graphes réguliers...")
    gm_pairs = algebraic_cospectral()
    all_pairs.extend(gm_pairs)
    print(f"  → {len(gm_pairs)} paires trouvées")
    for name1, name2, _, _ in gm_pairs:
        print(f"    {name1} ↔ {name2}")
    
    print("\n[3/4] Recherche brute force (n=6..9)...")
    brute = find_cospectral_bruteforce(n_range=(6, 9), max_per_n=300)
    all_pairs.extend(brute)
    print(f"  → {len(brute)} paires trouvées")
    
    # --- Méthode 4 : GM switching sur plus de graphes ---
    print("\n[4/4] GM switching systématique...")
    extra_pairs = []
    for n in [8, 10, 12, 14, 16]:
        for d in [3, 4]:
            if d >= n:
                continue
            for seed in range(20):
                try:
                    G = nx.random_regular_graph(d, n, seed=seed)
                    H = godsil_mckay_switch(G, partition_seed=seed*13+7)
                    if H is not None:
                        extra_pairs.append((f'rr_{d}_{n}_s{seed}', f'GM_{d}_{n}_s{seed}', G, H))
                except:
                    pass
    all_pairs.extend(extra_pairs)
    print(f"  → {len(extra_pairs)} paires supplémentaires")
    
    total = len(all_pairs)
    print(f"\n{'='*70}")
    print(f"TOTAL : {total} paires cospectrales non-isomorphes")
    print(f"{'='*70}")
    
    if total == 0:
        print("ERREUR : aucune paire trouvée. Ajuster les méthodes.")
        return
    
    # --- Vérification : confirmer cospectrialité ---
    print("\nVérification de cospectrialité...")
    verified_pairs = []
    for name1, name2, G1, G2 in all_pairs:
        if are_cospectral(G1, G2, 'adj'):
            verified_pairs.append((name1, name2, G1, G2))
        else:
            print(f"  ⚠ {name1} ↔ {name2} : PAS cospectraux ! Rejeté.")
    
    print(f"  → {len(verified_pairs)} paires VÉRIFIÉES")
    
    # --- Calculer les métriques ---
    print(f"\nCalcul des métriques sur {len(verified_pairs)} paires...")
    results = []
    
    for idx, (name1, name2, G1, G2) in enumerate(verified_pairs):
        print(f"  [{idx+1}/{len(verified_pairs)}] {name1} ↔ {name2} (n={G1.number_of_nodes()})...")
        
        m1 = compute_all_metrics(G1)
        m2 = compute_all_metrics(G2)
        
        # Trouver les métriques qui diffèrent
        all_keys = sorted(set(m1.keys()) & set(m2.keys()))
        
        separating = {}
        identical = {}
        
        for k in all_keys:
            v1, v2 = m1[k], m2[k]
            if isinstance(v1, (int, float)) and isinstance(v2, (int, float)):
                if abs(v1 - v2) > 1e-8:
                    separating[k] = {'G1': v1, 'G2': v2, 'diff': abs(v1 - v2), 
                                     'rel_diff': abs(v1 - v2) / (abs(v1) + abs(v2) + 1e-15)}
                else:
                    identical[k] = v1
        
        results.append({
            'pair': f'{name1} ↔ {name2}',
            'n': G1.number_of_nodes(),
            'm': G1.number_of_edges(),
            'n_separating': len(separating),
            'n_identical': len(identical),
            'separating': separating,
            'identical': list(identical.keys()),
            'G1_edges': list(G1.edges()),
            'G2_edges': list(G2.edges())
        })
        
        if separating:
            print(f"    → {len(separating)} métriques SÉPARENT, {len(identical)} identiques")
            for k, v in sorted(separating.items(), key=lambda x: -x[1]['rel_diff'])[:5]:
                print(f"      {k}: {v['G1']:.4f} vs {v['G2']:.4f} (Δ={v['rel_diff']:.3f})")
        else:
            print(f"    → AUCUNE métrique ne sépare ! (toutes identiques)")
    
    # --- Synthèse : quelles métriques séparent le plus souvent ? ---
    print(f"\n{'='*70}")
    print("SYNTHÈSE : Métriques qui séparent les paires cospectrales")
    print(f"{'='*70}")
    
    metric_separation_count = {}
    metric_avg_diff = {}
    
    for r in results:
        for k, v in r['separating'].items():
            if k not in metric_separation_count:
                metric_separation_count[k] = 0
                metric_avg_diff[k] = []
            metric_separation_count[k] += 1
            metric_avg_diff[k].append(v['rel_diff'])
    
    n_pairs = len(verified_pairs)
    print(f"\nSur {n_pairs} paires cospectrales :")
    print(f"\n{'Métrique':<35} {'Sépare':<12} {'%':<8} {'Diff_moy':<10}")
    print("-" * 65)
    
    for k, count in sorted(metric_separation_count.items(), key=lambda x: -x[1]):
        pct = 100 * count / n_pairs
        avg_diff = np.mean(metric_avg_diff[k])
        print(f"{k:<35} {count:<12} {pct:<8.1f} {avg_diff:<10.4f}")
    
    # --- Identifier les métriques PUREMENT non-spectrales ---
    # (celles qui séparent mais ne sont pas des dérivées spectrales)
    spectral_metrics = {
        'adj_spectral_radius', 'adj_energy', 'lap_spectral_gap', 'lap_largest',
        'adj_trace_sq', 'adj_trace_cube', 'adj_trace_4', 'n_nodes', 'n_edges',
        'estrada_index', 'kirchhoff_index', 'norm_lap_spectral_gap', 
        'norm_lap_largest', 'norm_lap_energy', 'signless_lap_largest',
        'signless_lap_smallest', 'signless_lap_gap', 'dist_spectral_radius',
        'dist_energy'
    }
    
    print(f"\n{'='*70}")
    print("MÉTRIQUES NON-SPECTRALES QUI SÉPARENT")
    print(f"{'='*70}")
    
    non_spectral_separators = {}
    for k, count in metric_separation_count.items():
        if k not in spectral_metrics:
            non_spectral_separators[k] = {
                'count': count,
                'pct': 100 * count / n_pairs,
                'avg_diff': float(np.mean(metric_avg_diff[k]))
            }
    
    for k, v in sorted(non_spectral_separators.items(), key=lambda x: -x[1]['count']):
        print(f"  {k:<35} sépare {v['count']}/{n_pairs} ({v['pct']:.0f}%)  avg_diff={v['avg_diff']:.4f}")
    
    # --- Sauvegarder ---
    output = {
        'n_pairs': n_pairs,
        'pairs': [{
            'pair': r['pair'],
            'n': r['n'],
            'm': r['m'],
            'n_separating': r['n_separating'],
            'separating_metrics': list(r['separating'].keys()),
            'separating_details': r['separating'],
            'G1_edges': r['G1_edges'],
            'G2_edges': r['G2_edges']
        } for r in results],
        'metric_separation_frequency': {
            k: {'count': v['count'], 'pct': v['pct'], 'avg_diff': v['avg_diff']}
            for k, v in non_spectral_separators.items()
        },
        'spectral_controls_never_separate': [
            k for k in spectral_metrics 
            if k not in metric_separation_count
        ]
    }
    
    with open('/agent/home/Graph-Systems-Exploration/data/g10_spectral_gap.json', 'w') as f:
        json.dump(output, f, indent=2, default=str)
    
    print(f"\n→ Résultats sauvegardés dans g10_spectral_gap.json")
    
    # --- Contrôle de sanité : les métriques spectrales ne doivent JAMAIS séparer ---
    print(f"\n{'='*70}")
    print("CONTRÔLE DE SANITÉ")
    print(f"{'='*70}")
    
    spectral_that_separate = [k for k in spectral_metrics if k in metric_separation_count]
    if spectral_that_separate:
        print(f"  ⚠ ALERTE : métriques spectrales qui séparent (bug possible) :")
        for k in spectral_that_separate:
            print(f"    {k} : sépare {metric_separation_count[k]} paires")
    else:
        print(f"  ✅ Aucune métrique spectrale ne sépare — cohérent.")

if __name__ == '__main__':
    main()

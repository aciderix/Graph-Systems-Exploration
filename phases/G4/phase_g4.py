"""
PHASE G4 — CHASSE AUX INVARIANTS
=================================
Approche MACHINE: tester TOUTES les combinaisons algébriques de métriques
pour trouver des quantités invariantes sous déformation.

1. Combinaisons linéaires, produits, ratios de métriques
2. PCA sur l'espace des métriques → axes naturels
3. Fonctions non-triviales (entropie, log-ratios)
4. Test de stabilité sous 5 types de déformations
"""
import json
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Load G2 trajectories
with open('/tmp/g2_trajectories.json') as f:
    trajectories = json.load(f)

# Core metrics to combine
METRICS = ['density', 'deg_mean', 'deg_std', 'clustering', 'transitivity',
           'lcc_frac', 'fiedler', 'spectral_radius', 'assortativity',
           'deg_max', 'lap_max']

def extract_vector(point, keys=METRICS):
    """Extract metric vector from a trajectory point."""
    vec = []
    for k in keys:
        v = point.get(k)
        if v is None or (isinstance(v, float) and (np.isnan(v) or np.isinf(v))):
            return None
        vec.append(float(v))
    return np.array(vec)

# ============================================================
# 1. BRUTE-FORCE ALGEBRAIC INVARIANT SEARCH
# ============================================================
print("="*70)
print("PHASE G4.1 — RECHERCHE EXHAUSTIVE DE COMBINAISONS INVARIANTES")
print("="*70)

# For each (graph, deformation), extract all metric vectors
# Then for all pairs (a, b) of metrics, test:
#   a/b, a*b, a+b, a-b, a/√b, log(a)/log(b), a²/b, a/b²
# Find which have the lowest CV across deformation steps

def generate_combinations(vecs, metric_names):
    """Generate all algebraic combinations and compute their CV."""
    n_metrics = len(metric_names)
    combos = []
    
    for i in range(n_metrics):
        for j in range(n_metrics):
            if i == j:
                continue
            ai = vecs[:, i]
            aj = vecs[:, j]
            
            # Skip if any zeros where we divide
            safe_j = np.all(np.abs(aj) > 1e-10)
            safe_i = np.all(np.abs(ai) > 1e-10)
            
            # Ratio a/b
            if safe_j:
                vals = ai / aj
                mu = np.mean(vals)
                if abs(mu) > 1e-10:
                    cv = np.std(vals) / abs(mu)
                    combos.append((cv, f"{metric_names[i]}/{metric_names[j]}", mu, np.std(vals)))
            
            # Product a*b
            vals = ai * aj
            mu = np.mean(vals)
            if abs(mu) > 1e-10:
                cv = np.std(vals) / abs(mu)
                combos.append((cv, f"{metric_names[i]}*{metric_names[j]}", mu, np.std(vals)))
            
            # Sum a+b (only i < j to avoid duplicates)
            if i < j:
                vals = ai + aj
                mu = np.mean(vals)
                if abs(mu) > 1e-10:
                    cv = np.std(vals) / abs(mu)
                    combos.append((cv, f"{metric_names[i]}+{metric_names[j]}", mu, np.std(vals)))
            
            # a/sqrt(b)
            if safe_j and np.all(aj > 0):
                vals = ai / np.sqrt(aj)
                mu = np.mean(vals)
                if abs(mu) > 1e-10:
                    cv = np.std(vals) / abs(mu)
                    combos.append((cv, f"{metric_names[i]}/√{metric_names[j]}", mu, np.std(vals)))
            
            # a²/b
            if safe_j:
                vals = ai**2 / aj
                mu = np.mean(vals)
                if abs(mu) > 1e-10:
                    cv = np.std(vals) / abs(mu)
                    combos.append((cv, f"{metric_names[i]}²/{metric_names[j]}", mu, np.std(vals)))
    
    # Triple combinations: a*b/c
    for i in range(n_metrics):
        for j in range(i+1, n_metrics):
            for k in range(n_metrics):
                if k == i or k == j:
                    continue
                ak = vecs[:, k]
                if np.all(np.abs(ak) > 1e-10):
                    vals = vecs[:, i] * vecs[:, j] / ak
                    mu = np.mean(vals)
                    if abs(mu) > 1e-10:
                        cv = np.std(vals) / abs(mu)
                        if cv < 0.02:  # Only keep very stable ones
                            combos.append((cv, f"{metric_names[i]}*{metric_names[j]}/{metric_names[k]}", mu, np.std(vals)))
    
    combos.sort()
    return combos

# Run on all (graph, deformation) pairs
all_invariants = {}
for gname in trajectories:
    for dname in trajectories[gname]:
        traj = trajectories[gname][dname]
        if len(traj) < 5:
            continue
        
        vecs = []
        for pt in traj:
            v = extract_vector(pt)
            if v is not None:
                vecs.append(v)
        
        if len(vecs) < 5:
            continue
        
        vecs = np.array(vecs)
        combos = generate_combinations(vecs, METRICS)
        
        key = f"{gname}__{dname}"
        if combos:
            all_invariants[key] = combos[:10]  # Top 10 most stable

# Find invariants that appear across MULTIPLE (graph, deformation) pairs
print(f"\nAnalysé {len(all_invariants)} paires (graphe, déformation)")

# Count how often each formula appears in top-10 with CV < 0.05
formula_counts = {}
formula_cvs = {}
for key, combos in all_invariants.items():
    for cv, formula, mu, std in combos:
        if cv < 0.05:
            if formula not in formula_counts:
                formula_counts[formula] = 0
                formula_cvs[formula] = []
            formula_counts[formula] += 1
            formula_cvs[formula].append((cv, key, mu))

# Sort by frequency
sorted_formulas = sorted(formula_counts.items(), key=lambda x: -x[1])

print(f"\n{len(sorted_formulas)} formules avec CV < 5%")
print(f"\nTOP 30 INVARIANTS LES PLUS UNIVERSELS:")
print(f"{'count':>5s} {'avg_CV':>8s} {'formula':>45s} {'example_values'}")
print("-"*100)

for formula, count in sorted_formulas[:30]:
    cvs = [x[0] for x in formula_cvs[formula]]
    vals = [x[2] for x in formula_cvs[formula]]
    avg_cv = np.mean(cvs)
    # Show which graph/deformation pairs
    examples = [x[1].split('__') for x in formula_cvs[formula][:3]]
    print(f"{count:>5d} {avg_cv:>8.4f} {formula:>45s}  vals=[{min(vals):.3f}, {max(vals):.3f}]")

# ============================================================
# 2. PCA — NATURAL AXES OF GRAPH SPACE
# ============================================================
print("\n" + "="*70)
print("PHASE G4.2 — PCA SUR L'ESPACE DES MÉTRIQUES")
print("="*70)

# Load G1 results
with open('/tmp/g1_results.json') as f:
    g1_results = json.load(f)

# Build matrix
pca_keys = ['density', 'deg_mean', 'deg_std', 'clustering_avg', 'transitivity',
            'assortativity', 'algebraic_connectivity', 'spectral_radius', 
            'spectral_gap', 'modularity']

data = []
labels = []
for r in g1_results:
    row = []
    ok = True
    for k in pca_keys:
        v = r.get(k)
        if v is None or (isinstance(v, float) and (np.isnan(v) or np.isinf(v))):
            ok = False
            break
        row.append(float(v))
    if ok:
        data.append(row)
        labels.append(r['name'])

X = np.array(data)
print(f"\n{X.shape[0]} graphes × {X.shape[1]} métriques")

# Standardize
mu = X.mean(axis=0)
sigma = X.std(axis=0)
sigma[sigma < 1e-10] = 1
X_std = (X - mu) / sigma

# PCA
cov = np.cov(X_std.T)
eigenvalues, eigenvectors = np.linalg.eigh(cov)
idx = np.argsort(eigenvalues)[::-1]
eigenvalues = eigenvalues[idx]
eigenvectors = eigenvectors[:, idx]

total_var = np.sum(eigenvalues)
cumvar = np.cumsum(eigenvalues) / total_var

print(f"\nVariance expliquée par composante:")
for i in range(min(8, len(eigenvalues))):
    bar = "█" * int(eigenvalues[i] / total_var * 50)
    print(f"  PC{i+1}: {eigenvalues[i]/total_var*100:>5.1f}% (cum: {cumvar[i]*100:>5.1f}%) {bar}")

print(f"\nLoadings PC1 (axe principal de l'espace des graphes):")
for i, name in enumerate(pca_keys):
    v = eigenvectors[i, 0]
    bar = "█" * int(abs(v) * 20)
    sign = "+" if v > 0 else "-"
    print(f"  {sign}{abs(v):.3f} {bar:>10s} {name}")

print(f"\nLoadings PC2:")
for i, name in enumerate(pca_keys):
    v = eigenvectors[i, 1]
    bar = "█" * int(abs(v) * 20)
    sign = "+" if v > 0 else "-"
    print(f"  {sign}{abs(v):.3f} {bar:>10s} {name}")

# Project and find clusters
proj = X_std @ eigenvectors[:, :2]

# Group by family
family_positions = {}
for i, label in enumerate(labels):
    if label not in family_positions:
        family_positions[label] = []
    family_positions[label].append(proj[i])

print(f"\nPosition des familles dans l'espace PC1-PC2 (centroïdes):")
print(f"{'Famille':>25s} {'PC1':>8s} {'PC2':>8s}")
print("-"*45)
for fam in sorted(family_positions.keys()):
    pts = np.array(family_positions[fam])
    c = pts.mean(axis=0)
    print(f"{fam:>25s} {c[0]:>8.2f} {c[1]:>8.2f}")

# ============================================================
# 3. ENTROPY-BASED INVARIANTS
# ============================================================
print("\n" + "="*70)
print("PHASE G4.3 — INVARIANTS ENTROPIQUES")
print("="*70)

import networkx as nx

def degree_entropy(G):
    """Shannon entropy of degree distribution."""
    degrees = [d for _, d in G.degree()]
    if not degrees:
        return 0
    counts = np.bincount(degrees)
    probs = counts[counts > 0] / len(degrees)
    return -np.sum(probs * np.log2(probs))

def normalized_degree_entropy(G):
    """H(degree) / log2(n)"""
    H = degree_entropy(G)
    n = G.number_of_nodes()
    return H / np.log2(n) if n > 1 else 0

N = 100
test_graphs = {
    'ER_005': nx.erdos_renyi_graph(N, 0.05, seed=42),
    'ER_010': nx.erdos_renyi_graph(N, 0.10, seed=42),
    'ER_030': nx.erdos_renyi_graph(N, 0.30, seed=42),
    'BA_m1':  nx.barabasi_albert_graph(N, 1, seed=42),
    'BA_m3':  nx.barabasi_albert_graph(N, 3, seed=42),
    'BA_m5':  nx.barabasi_albert_graph(N, 5, seed=42),
    'WS_p01': nx.watts_strogatz_graph(N, 6, 0.01, seed=42),
    'WS_p10': nx.watts_strogatz_graph(N, 6, 0.10, seed=42),
    'WS_p50': nx.watts_strogatz_graph(N, 6, 0.50, seed=42),
    'grid':   nx.convert_node_labels_to_integers(nx.grid_2d_graph(10, 10)),
    'reg_4':  nx.random_regular_graph(4, N, seed=42),
    'geo_02': nx.random_geometric_graph(N, 0.2, seed=42),
}

print(f"\n{'Graph':>10s} {'H_deg':>6s} {'H_norm':>6s} {'clust':>6s} {'H*C':>6s} {'H/log(m)':>8s}")
print("-"*50)
for gname, G in test_graphs.items():
    H = degree_entropy(G)
    Hn = normalized_degree_entropy(G)
    C = nx.average_clustering(G)
    m = G.number_of_edges()
    HlogM = H / np.log2(m) if m > 1 else 0
    print(f"{gname:>10s} {H:>6.3f} {Hn:>6.3f} {C:>6.3f} {H*C:>6.3f} {HlogM:>8.3f}")

# Test entropy stability under rewiring
print(f"\nStabilité de H_deg sous rewiring progressif:")
G0 = nx.watts_strogatz_graph(N, 6, 0.1, seed=42)
nodes = list(G0.nodes())
for frac in [0.0, 0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 0.9]:
    G = G0.copy()
    edges = list(G.edges())
    to_rewire = int(frac * len(edges))
    for _ in range(to_rewire):
        if len(list(G.edges())) == 0:
            break
        elist = list(G.edges())
        u, v = elist[np.random.randint(len(elist))]
        G.remove_edge(u, v)
        w = np.random.choice(nodes)
        while w == u or G.has_edge(u, w):
            w = np.random.choice(nodes)
        G.add_edge(u, w)
    
    H = degree_entropy(G)
    C = nx.average_clustering(G)
    n_comp = nx.number_connected_components(G)
    print(f"  frac={frac:.2f}: H={H:.3f}, C={C:.3f}, H*C={H*C:.3f}, comp={n_comp}")

# ============================================================
# 4. SPECTRAL ENTROPY
# ============================================================
print("\n" + "="*70)
print("PHASE G4.4 — ENTROPIE SPECTRALE")
print("="*70)

def spectral_entropy(G):
    """Von Neumann entropy of the graph: S = -Σ λ_i log(λ_i) where λ_i are normalized Laplacian eigenvalues."""
    if G.number_of_nodes() < 2 or G.number_of_edges() == 0:
        return 0
    L = nx.normalized_laplacian_matrix(G).toarray().astype(float)
    eigs = np.linalg.eigvalsh(L)
    eigs = eigs[eigs > 1e-10]  # remove zeros
    eigs_norm = eigs / eigs.sum()
    return -np.sum(eigs_norm * np.log2(eigs_norm))

print(f"\n{'Graph':>10s} {'S_spec':>7s} {'H_deg':>6s} {'S/logN':>7s} {'H/logN':>7s} {'S-H':>6s}")
print("-"*55)
for gname, G in test_graphs.items():
    S = spectral_entropy(G)
    H = degree_entropy(G)
    n = G.number_of_nodes()
    logN = np.log2(n)
    print(f"{gname:>10s} {S:>7.3f} {H:>6.3f} {S/logN:>7.3f} {H/logN:>7.3f} {S-H:>6.3f}")

# Test spectral entropy stability
print(f"\nStabilité de S_spectral sous déformations (WS_p10):")
G0 = nx.watts_strogatz_graph(N, 6, 0.1, seed=42)
S0 = spectral_entropy(G0)

for deform_name, deform_fracs in [('add_edge', [0.05, 0.1, 0.2, 0.3, 0.5]),
                                    ('remove_edge', [0.05, 0.1, 0.2, 0.3, 0.5]),
                                    ('rewire', [0.05, 0.1, 0.2, 0.3, 0.5])]:
    print(f"  {deform_name}:")
    for frac in deform_fracs:
        G = G0.copy()
        edges = list(G.edges())
        if deform_name == 'add_edge':
            n_add = int(frac * len(edges))
            nodes = list(G.nodes())
            for _ in range(n_add):
                u, v = np.random.choice(nodes, 2, replace=False)
                G.add_edge(u, v)
        elif deform_name == 'remove_edge':
            n_rem = int(frac * len(edges))
            idx = np.random.choice(len(edges), min(n_rem, len(edges)-1), replace=False)
            for i in idx:
                G.remove_edge(*edges[i])
        elif deform_name == 'rewire':
            n_rew = int(frac * len(edges))
            nodes = list(G.nodes())
            for _ in range(n_rew):
                elist = list(G.edges())
                if not elist: break
                u, v = elist[np.random.randint(len(elist))]
                G.remove_edge(u, v)
                w = np.random.choice(nodes)
                while w == u or G.has_edge(u, w):
                    w = np.random.choice(nodes)
                G.add_edge(u, w)
        
        S = spectral_entropy(G)
        delta = (S - S0) / S0 * 100
        print(f"    frac={frac:.2f}: S={S:.4f} (Δ={delta:+.1f}%)")

print("\nDone.")

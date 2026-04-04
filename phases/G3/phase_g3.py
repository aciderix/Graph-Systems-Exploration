"""
PHASE G3 — Détection fine des transitions de phase
===================================================
1. Percolation par suppression d'arêtes (100 points de résolution)
2. Percolation par suppression de nœuds (random vs targeted)
3. Formation du giant component (ajout progressif d'arêtes)
4. Recherche de lois d'échelle universelles
"""
import networkx as nx
import numpy as np
import json
import time
import warnings; warnings.filterwarnings("ignore")

np.random.seed(42)

def lcc_fraction(G):
    if G.number_of_nodes() == 0:
        return 0.0
    ccs = list(nx.connected_components(G))
    return len(max(ccs, key=len)) / G.number_of_nodes()

def num_components(G):
    if G.number_of_nodes() == 0:
        return 0
    return nx.number_connected_components(G)

# ============================================================
# 1. EDGE PERCOLATION (fine-grained)
# ============================================================
def edge_percolation(G0, n_steps=100):
    """Remove edges one by one, track LCC."""
    G = G0.copy()
    edges = list(G.edges())
    np.random.shuffle(edges)
    
    n = G.number_of_nodes()
    m_total = len(edges)
    
    trajectory = []
    trajectory.append({
        'frac_removed': 0.0,
        'frac_remaining': 1.0,
        'lcc_frac': lcc_fraction(G),
        'n_components': num_components(G),
    })
    
    step_size = max(1, m_total // n_steps)
    
    for i in range(0, m_total, step_size):
        batch = edges[i:i+step_size]
        G.remove_edges_from(batch)
        frac = (i + len(batch)) / m_total
        trajectory.append({
            'frac_removed': frac,
            'frac_remaining': 1 - frac,
            'lcc_frac': lcc_fraction(G),
            'n_components': num_components(G),
        })
    
    return trajectory

# ============================================================
# 2. NODE PERCOLATION (random vs targeted)
# ============================================================
def node_percolation_random(G0, n_steps=50):
    G = G0.copy()
    n_total = G.number_of_nodes()
    nodes = list(G.nodes())
    np.random.shuffle(nodes)
    
    trajectory = [{'frac_removed': 0.0, 'lcc_frac': lcc_fraction(G), 'n_components': num_components(G)}]
    step_size = max(1, n_total // n_steps)
    
    for i in range(0, n_total - 2, step_size):
        batch = nodes[i:i+step_size]
        G.remove_nodes_from(batch)
        if G.number_of_nodes() < 2:
            break
        trajectory.append({
            'frac_removed': (i + len(batch)) / n_total,
            'lcc_frac': lcc_fraction(G),
            'n_components': num_components(G),
        })
    return trajectory

def node_percolation_targeted(G0, n_steps=50):
    G = G0.copy()
    n_total = G.number_of_nodes()
    step_size = max(1, n_total // n_steps)
    
    trajectory = [{'frac_removed': 0.0, 'lcc_frac': lcc_fraction(G), 'n_components': num_components(G)}]
    removed = 0
    
    while G.number_of_nodes() > 2 and removed < n_total - 2:
        # Remove highest degree nodes
        degrees = dict(G.degree())
        sorted_nodes = sorted(degrees, key=degrees.get, reverse=True)
        batch = sorted_nodes[:step_size]
        G.remove_nodes_from(batch)
        removed += len(batch)
        if G.number_of_nodes() < 2:
            break
        trajectory.append({
            'frac_removed': removed / n_total,
            'lcc_frac': lcc_fraction(G),
            'n_components': num_components(G),
        })
    return trajectory

# ============================================================
# REFERENCE GRAPHS (n=200 for better resolution)
# ============================================================
N = 200
graphs = {
    'ER_subcrit':     nx.erdos_renyi_graph(N, 0.003, seed=42),   # p < 1/N
    'ER_crit':        nx.erdos_renyi_graph(N, 0.005, seed=42),   # p ≈ 1/N
    'ER_supercrit':   nx.erdos_renyi_graph(N, 0.02, seed=42),    # p > 1/N
    'ER_connected':   nx.erdos_renyi_graph(N, 0.05, seed=42),
    'BA_m1':          nx.barabasi_albert_graph(N, 1, seed=42),
    'BA_m3':          nx.barabasi_albert_graph(N, 3, seed=42),
    'WS_k6_p01':      nx.watts_strogatz_graph(N, 6, 0.01, seed=42),
    'WS_k6_p30':      nx.watts_strogatz_graph(N, 6, 0.30, seed=42),
    'grid_14x14':     nx.convert_node_labels_to_integers(nx.grid_2d_graph(14, 14)),
    'random_geo_02':  nx.random_geometric_graph(N, 0.2, seed=42),
    'caveman_10x20':  nx.connected_caveman_graph(10, 20),
    'regular_4':      nx.random_regular_graph(4, N, seed=42),
    'regular_8':      nx.random_regular_graph(8, N, seed=42),

}

# Fix SBM prob matrix
SBM_p = [[0.3 if i==j else 0.01 for j in range(4)] for i in range(4)]
graphs['SBM_4x50'] = nx.stochastic_block_model([50]*4, SBM_p, seed=42)

print("="*70)
print("PHASE G3 — PERCOLATION ET TRANSITIONS DE PHASE")
print("="*70)

# ============================================================
# RUN PERCOLATION
# ============================================================
t0 = time.time()
results = {}

for gname, G0 in graphs.items():
    print(f"\n--- {gname} (n={G0.number_of_nodes()}, m={G0.number_of_edges()}) ---")
    results[gname] = {}
    
    # Edge percolation
    results[gname]['edge_perc'] = edge_percolation(G0, n_steps=100)
    
    # Node percolation (random)
    results[gname]['node_random'] = node_percolation_random(G0, n_steps=50)
    
    # Node percolation (targeted)
    results[gname]['node_targeted'] = node_percolation_targeted(G0, n_steps=50)
    
    # Find critical threshold (where LCC drops below 0.5)
    for perc_type in ['edge_perc', 'node_random', 'node_targeted']:
        traj = results[gname][perc_type]
        fc = None
        for i in range(1, len(traj)):
            if traj[i]['lcc_frac'] < 0.5 and traj[i-1]['lcc_frac'] >= 0.5:
                fc = (traj[i-1]['frac_removed'] + traj[i]['frac_removed']) / 2
                break
        results[gname][f'{perc_type}_fc'] = fc
        if fc is not None:
            print(f"  {perc_type}: f_c = {fc:.3f}")
        else:
            print(f"  {perc_type}: no transition (LCC never < 0.5 or always < 0.5)")

print(f"\nPercolation done in {time.time()-t0:.1f}s")

# ============================================================
# CRITICAL THRESHOLDS COMPARISON
# ============================================================
print("\n" + "="*70)
print("SEUILS CRITIQUES f_c (fraction supprimée pour briser le giant component)")
print("="*70)

print(f"\n{'Graphe':>18s} {'edge_fc':>8s} {'node_rand_fc':>12s} {'node_targ_fc':>12s} {'ratio_t/r':>10s}")
print("-"*65)
for gname in graphs:
    e_fc = results[gname].get('edge_perc_fc')
    nr_fc = results[gname].get('node_random_fc')
    nt_fc = results[gname].get('node_targeted_fc')
    
    e_s = f"{e_fc:.3f}" if e_fc else "---"
    nr_s = f"{nr_fc:.3f}" if nr_fc else "---"
    nt_s = f"{nt_fc:.3f}" if nt_fc else "---"
    
    ratio = ""
    if nr_fc and nt_fc and nr_fc > 0:
        ratio = f"{nt_fc/nr_fc:.3f}"
    
    print(f"{gname:>18s} {e_s:>8s} {nr_s:>12s} {nt_s:>12s} {ratio:>10s}")

# ============================================================
# ROBUSTNESS RATIO: targeted/random
# ============================================================
print("\n" + "="*70)
print("RATIO DE VULNÉRABILITÉ (f_c_targeted / f_c_random)")
print("="*70)
print("Plus le ratio est petit, plus le graphe est vulnérable aux attaques ciblées")

vuln = []
for gname in graphs:
    nr_fc = results[gname].get('node_random_fc')
    nt_fc = results[gname].get('node_targeted_fc')
    if nr_fc and nt_fc and nr_fc > 0.01:
        ratio = nt_fc / nr_fc
        vuln.append((ratio, gname))
        
vuln.sort()
for ratio, gname in vuln:
    bar = "█" * int(ratio * 30)
    label = "VULNÉRABLE" if ratio < 0.3 else ("MODÉRÉ" if ratio < 0.7 else "ROBUSTE")
    print(f"  {gname:>18s}: {ratio:.3f} {bar} [{label}]")

# ============================================================
# UNIVERSALITY: does LCC(f) follow a universal curve?
# ============================================================
print("\n" + "="*70)
print("UNIVERSALITÉ — LCC(f/f_c) collapse sur une courbe unique ?")
print("="*70)

# Rescale by f_c and check if curves collapse
rescaled_curves = {}
for gname in graphs:
    fc = results[gname].get('edge_perc_fc')
    if fc and fc > 0.05:
        traj = results[gname]['edge_perc']
        xs = np.array([t['frac_removed'] / fc for t in traj])
        ys = np.array([t['lcc_frac'] for t in traj])
        rescaled_curves[gname] = (xs, ys)

# Sample at x/fc = 0.5, 0.8, 1.0, 1.2, 1.5
sample_points = [0.5, 0.8, 1.0, 1.2, 1.5]
print(f"\n{'Graphe':>18s}", end="")
for sp in sample_points:
    print(f" {'f/fc='+str(sp):>8s}", end="")
print()
print("-"*65)

collected = {sp: [] for sp in sample_points}
for gname, (xs, ys) in rescaled_curves.items():
    print(f"{gname:>18s}", end="")
    for sp in sample_points:
        # Interpolate
        idx = np.argmin(np.abs(xs - sp))
        val = ys[idx]
        collected[sp].append(val)
        print(f" {val:>8.3f}", end="")
    print()

print(f"\n{'MEAN':>18s}", end="")
for sp in sample_points:
    vals = collected[sp]
    print(f" {np.mean(vals):>8.3f}", end="")
print()
print(f"{'STD':>18s}", end="")
for sp in sample_points:
    vals = collected[sp]
    print(f" {np.std(vals):>8.3f}", end="")
print()
print(f"{'CV':>18s}", end="")
for sp in sample_points:
    vals = collected[sp]
    mu = np.mean(vals)
    cv = np.std(vals) / mu if mu > 0.01 else float('inf')
    print(f" {cv:>8.3f}", end="")
print()

# ============================================================
# SCALING LAW: f_c vs graph properties
# ============================================================
print("\n\n" + "="*70)
print("LOI D'ÉCHELLE: f_c corrélé à quelles propriétés ?")
print("="*70)

# Load G1 data for correlations
properties = {}
for gname, G0 in graphs.items():
    d = dict(G0.degree())
    degrees = list(d.values())
    properties[gname] = {
        'density': nx.density(G0),
        'deg_mean': np.mean(degrees),
        'deg_std': np.std(degrees),
        'clustering': nx.average_clustering(G0),
        'deg_max': max(degrees),
        'heterogeneity': np.std(degrees)**2 / np.mean(degrees)**2 if np.mean(degrees) > 0 else 0,
    }

fc_edge = []
prop_vals = {k: [] for k in ['density', 'deg_mean', 'deg_std', 'clustering', 'deg_max', 'heterogeneity']}
gnames_fc = []

for gname in graphs:
    fc = results[gname].get('edge_perc_fc')
    if fc and fc > 0.01:
        fc_edge.append(fc)
        gnames_fc.append(gname)
        for k in prop_vals:
            prop_vals[k].append(properties[gname][k])

fc_arr = np.array(fc_edge)
print(f"\n{len(fc_arr)} graphes avec f_c > 0.01")

for k in prop_vals:
    vals = np.array(prop_vals[k])
    if len(vals) > 3 and np.std(vals) > 1e-10:
        corr = np.corrcoef(vals, fc_arr)[0, 1]
        print(f"  corr(f_c, {k:>15s}) = {corr:>+.3f}")

# Cohen et al. formula: f_c = 1 - 1/(κ-1) where κ = <k²>/<k>
print(f"\n--- Test formule de Cohen: f_c = 1 - 1/(κ-1), κ = <k²>/<k> ---")
for gname in gnames_fc:
    d = dict(graphs[gname].degree())
    degrees = np.array(list(d.values()), dtype=float)
    kappa = np.mean(degrees**2) / np.mean(degrees)
    fc_pred = 1 - 1/(kappa - 1) if kappa > 1 else 0
    fc_obs = results[gname].get('edge_perc_fc', 0)
    err = abs(fc_pred - fc_obs)
    print(f"  {gname:>18s}: κ={kappa:.2f}, fc_pred={fc_pred:.3f}, fc_obs={fc_obs:.3f}, err={err:.3f}")

with open('/tmp/g3_results.json', 'w') as f:
    json.dump(results, f, default=str)

print("\nDone.")

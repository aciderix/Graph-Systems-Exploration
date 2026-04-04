"""
PHASE G2 — Déformations contrôlées + tracking métriques
========================================================
Pour chaque graphe de référence:
1. Ajout progressif d'arêtes (random, preferential, bridging)
2. Suppression progressive d'arêtes (random, targeted betweenness)
3. Rewiring (Watts-Strogatz style)
4. Suppression progressive de nœuds (random, hub-targeted)

Objectif: détecter transitions de phase, invariants, hystérésis.
"""
import networkx as nx
import numpy as np
import json
import time
import warnings
warnings.filterwarnings('ignore')

def quick_metrics(G):
    """Fast metrics for tracking during deformation."""
    n = G.number_of_nodes()
    m = G.number_of_edges()
    if n < 2:
        return None
    
    degrees = [d for _, d in G.degree()]
    ccs = list(nx.connected_components(G))
    lcc = max(ccs, key=len)
    n_lcc = len(lcc)
    
    metrics = {
        'n': n, 'm': m,
        'density': nx.density(G),
        'deg_mean': float(np.mean(degrees)),
        'deg_std': float(np.std(degrees)),
        'deg_max': int(np.max(degrees)),
        'clustering': nx.average_clustering(G),
        'transitivity': nx.transitivity(G),
        'num_components': len(ccs),
        'lcc_frac': n_lcc / n,
    }
    
    # Path metrics only on small LCC
    if n_lcc <= 500 and n_lcc > 1:
        H = G.subgraph(lcc).copy()
        try:
            metrics['avg_path'] = nx.average_shortest_path_length(H)
            metrics['diameter'] = nx.diameter(H)
        except:
            pass
    
    # Spectral (small graphs only)
    if n <= 300:
        try:
            L = nx.laplacian_matrix(G).toarray().astype(float)
            eigs = np.sort(np.linalg.eigvalsh(L))
            metrics['fiedler'] = float(eigs[1]) if len(eigs) > 1 else 0
            metrics['lap_max'] = float(eigs[-1])
            
            A = nx.adjacency_matrix(G).toarray().astype(float)
            eigs_A = np.sort(np.linalg.eigvalsh(A))[::-1]
            metrics['spectral_radius'] = float(eigs_A[0])
        except:
            pass
    
    try:
        metrics['assortativity'] = nx.degree_assortativity_coefficient(G)
    except:
        pass
    
    return metrics

# ============================================================
# DEFORMATION OPERATIONS
# ============================================================
def add_random_edges(G, frac):
    """Add frac * m random edges."""
    G = G.copy()
    n = G.number_of_nodes()
    nodes = list(G.nodes())
    m_orig = G.number_of_edges()
    to_add = max(1, int(frac * m_orig))
    added = 0
    attempts = 0
    while added < to_add and attempts < to_add * 10:
        u, v = np.random.choice(nodes, 2, replace=False)
        if not G.has_edge(u, v):
            G.add_edge(u, v)
            added += 1
        attempts += 1
    return G

def remove_random_edges(G, frac):
    """Remove frac * m random edges."""
    G = G.copy()
    edges = list(G.edges())
    to_remove = max(1, int(frac * len(edges)))
    to_remove = min(to_remove, len(edges) - 1)
    if to_remove <= 0:
        return G
    indices = np.random.choice(len(edges), to_remove, replace=False)
    for i in indices:
        G.remove_edge(*edges[i])
    return G

def remove_hub_targeted(G, frac):
    """Remove nodes with highest degree first."""
    G = G.copy()
    n_orig = G.number_of_nodes()
    to_remove = max(1, int(frac * n_orig))
    for _ in range(to_remove):
        if G.number_of_nodes() < 3:
            break
        hub = max(G.nodes(), key=lambda x: G.degree(x))
        G.remove_node(hub)
    return G

def remove_random_nodes(G, frac):
    """Remove random nodes."""
    G = G.copy()
    n = G.number_of_nodes()
    to_remove = max(1, int(frac * n))
    to_remove = min(to_remove, n - 2)
    nodes = list(G.nodes())
    victims = np.random.choice(nodes, to_remove, replace=False)
    G.remove_nodes_from(victims)
    return G

def rewire_edges(G, frac):
    """Rewire frac of edges randomly (keep degree sequence approx)."""
    G = G.copy()
    edges = list(G.edges())
    to_rewire = max(1, int(frac * len(edges)))
    nodes = list(G.nodes())
    for _ in range(to_rewire):
        if len(edges) == 0:
            break
        idx = np.random.randint(len(edges))
        u, v = edges[idx]
        G.remove_edge(u, v)
        new_v = np.random.choice(nodes)
        while new_v == u or G.has_edge(u, new_v):
            new_v = np.random.choice(nodes)
        G.add_edge(u, new_v)
        edges = list(G.edges())
    return G

# ============================================================
# REFERENCE GRAPHS
# ============================================================
np.random.seed(42)
N = 100  # standard size

ref_graphs = {
    'ER_sparse':      nx.erdos_renyi_graph(N, 0.03, seed=42),
    'ER_medium':      nx.erdos_renyi_graph(N, 0.1, seed=42),
    'ER_dense':       nx.erdos_renyi_graph(N, 0.3, seed=42),
    'BA_m1':          nx.barabasi_albert_graph(N, 1, seed=42),
    'BA_m3':          nx.barabasi_albert_graph(N, 3, seed=42),
    'WS_low':         nx.watts_strogatz_graph(N, 6, 0.05, seed=42),
    'WS_high':        nx.watts_strogatz_graph(N, 6, 0.5, seed=42),
    'grid':           nx.convert_node_labels_to_integers(nx.grid_2d_graph(10, 10)),
    'random_geo':     nx.random_geometric_graph(N, 0.2, seed=42),
    'caveman':        nx.connected_caveman_graph(10, 10),
    'regular_4':      nx.random_regular_graph(4, N, seed=42),
    'SBM':            nx.stochastic_block_model([25,25,25,25], [[0.4,0.02,0.02,0.02],[0.02,0.4,0.02,0.02],[0.02,0.02,0.4,0.02],[0.02,0.02,0.02,0.4]], seed=42),
}

# Deformation steps
fracs = [0.0, 0.02, 0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

deformations = {
    'add_random': add_random_edges,
    'remove_random': remove_random_edges,
    'remove_hubs': remove_hub_targeted,
    'remove_nodes': remove_random_nodes,
    'rewire': rewire_edges,
}

# ============================================================
# MAIN LOOP
# ============================================================
print("="*70)
print("PHASE G2 — DÉFORMATIONS CONTRÔLÉES")
print("="*70)
print(f"\n{len(ref_graphs)} graphes de référence × {len(deformations)} déformations × {len(fracs)} niveaux")

t0 = time.time()
all_trajectories = {}

for gname, G0 in ref_graphs.items():
    print(f"\n--- {gname} (n={G0.number_of_nodes()}, m={G0.number_of_edges()}) ---")
    all_trajectories[gname] = {}
    
    for dname, dfunc in deformations.items():
        trajectory = []
        for frac in fracs:
            try:
                if frac == 0:
                    Gd = G0.copy()
                else:
                    Gd = dfunc(G0, frac)
                m = quick_metrics(Gd)
                if m:
                    m['frac'] = frac
                    trajectory.append(m)
            except Exception as e:
                pass
        all_trajectories[gname][dname] = trajectory
        print(f"  {dname}: {len(trajectory)} points")

print(f"\nTotal time: {time.time()-t0:.1f}s")

# Save
with open('/tmp/g2_trajectories.json', 'w') as f:
    json.dump(all_trajectories, f, default=str)

# ============================================================
# PHASE TRANSITION DETECTION
# ============================================================
print("\n" + "="*70)
print("DÉTECTION DE TRANSITIONS DE PHASE")
print("="*70)
print("Critère: dérivée normalisée |Δmetric/Δfrac| / range > seuil")

transitions = []

for gname, deforms in all_trajectories.items():
    for dname, traj in deforms.items():
        if len(traj) < 4:
            continue
        for key in ['lcc_frac', 'clustering', 'transitivity', 'num_components', 
                     'fiedler', 'diameter', 'assortativity', 'avg_path']:
            vals = [(t['frac'], t.get(key)) for t in traj if key in t and t[key] is not None]
            if len(vals) < 4:
                continue
            xs = np.array([v[0] for v in vals])
            ys = np.array([v[1] for v in vals], dtype=float)
            
            # Range
            y_range = np.max(ys) - np.min(ys)
            if y_range < 1e-10:
                continue
            
            # Normalized derivative
            for i in range(1, len(xs)):
                dx = xs[i] - xs[i-1]
                if dx < 1e-10:
                    continue
                dy = abs(ys[i] - ys[i-1])
                deriv_norm = (dy / y_range) / dx  # normalized rate of change
                
                if deriv_norm > 5:  # sharp transition
                    transitions.append({
                        'graph': gname,
                        'deform': dname,
                        'metric': key,
                        'frac_before': float(xs[i-1]),
                        'frac_after': float(xs[i]),
                        'val_before': float(ys[i-1]),
                        'val_after': float(ys[i]),
                        'deriv_norm': float(deriv_norm),
                    })

transitions.sort(key=lambda x: -x['deriv_norm'])
print(f"\n{len(transitions)} transitions détectées")
print(f"\nTOP 20 transitions les plus brutales:")
print(f"{'deriv':>7s} {'graph':>14s} {'deform':>14s} {'metric':>15s} {'frac':>10s} {'before':>8s} {'after':>8s}")
print("-"*80)
for t in transitions[:20]:
    print(f"{t['deriv_norm']:>7.1f} {t['graph']:>14s} {t['deform']:>14s} {t['metric']:>15s} "
          f"{t['frac_before']:.2f}→{t['frac_after']:.2f} {t['val_before']:>8.3f} {t['val_after']:>8.3f}")

# ============================================================
# INVARIANT DETECTION
# ============================================================
print("\n" + "="*70)
print("CHASSE AUX INVARIANTS — métriques stables sous déformation")
print("="*70)
print("Critère: CV < 0.05 à travers les niveaux de déformation")

invariants = []
for gname, deforms in all_trajectories.items():
    for dname, traj in deforms.items():
        if len(traj) < 5:
            continue
        for key in ['clustering', 'transitivity', 'lcc_frac', 'fiedler', 
                     'assortativity', 'spectral_radius', 'deg_mean', 'deg_std']:
            vals = [t[key] for t in traj if key in t and t[key] is not None]
            vals = [v for v in vals if not np.isnan(float(v)) and not np.isinf(float(v))]
            if len(vals) < 5:
                continue
            arr = np.array(vals, dtype=float)
            mu = np.mean(arr)
            if abs(mu) < 1e-10:
                continue
            cv = np.std(arr) / abs(mu)
            if cv < 0.05:
                invariants.append({
                    'graph': gname,
                    'deform': dname,
                    'metric': key,
                    'cv': float(cv),
                    'mean': float(mu),
                    'range': f"[{np.min(arr):.4f}, {np.max(arr):.4f}]",
                })

invariants.sort(key=lambda x: x['cv'])
print(f"\n{len(invariants)} invariants trouvés (CV < 5%)")
print(f"\nTOP 20 plus stables:")
print(f"{'CV':>6s} {'graph':>14s} {'deform':>14s} {'metric':>16s} {'mean':>8s} {'range':>20s}")
print("-"*85)
for inv in invariants[:20]:
    print(f"{inv['cv']:>6.4f} {inv['graph']:>14s} {inv['deform']:>14s} {inv['metric']:>16s} "
          f"{inv['mean']:>8.4f} {inv['range']:>20s}")

# ============================================================
# HYSTÉRÉSIS CHECK — add then remove, same metrics?
# ============================================================
print("\n" + "="*70)
print("HYSTÉRÉSIS — add_random vs remove_random (réversibilité)")
print("="*70)

for gname in ref_graphs:
    add_traj = all_trajectories[gname].get('add_random', [])
    rem_traj = all_trajectories[gname].get('remove_random', [])
    if len(add_traj) < 3 or len(rem_traj) < 3:
        continue
    
    # Compare metric at frac=0 (baseline) vs at frac=0.3
    m_base = add_traj[0] if add_traj[0]['frac'] == 0 else None
    m_add30 = next((t for t in add_traj if abs(t['frac'] - 0.3) < 0.01), None)
    m_rem30 = next((t for t in rem_traj if abs(t['frac'] - 0.3) < 0.01), None)
    
    if m_base and m_add30 and m_rem30:
        for key in ['clustering', 'lcc_frac', 'transitivity']:
            v0 = m_base.get(key)
            va = m_add30.get(key)
            vr = m_rem30.get(key)
            if v0 is not None and va is not None and vr is not None:
                asym = abs(va - v0) - abs(vr - v0)
                if abs(asym) > 0.01:
                    direction = "add > remove" if asym > 0 else "remove > add"
                    print(f"  {gname:>14s} {key:>14s}: add→{va:.3f}, base={v0:.3f}, rem→{vr:.3f} [{direction}]")

print(f"\nDone. Trajectories saved to /tmp/g2_trajectories.json")

"""
PHASE G7 — DÉFORMATION OPTIMISÉE + SYNTHÈSE
=============================================
Focus sur TOP 10 finalistes × 6 graphes × 5 déformations × 5 niveaux
"""
import pickle
import numpy as np
import json
import time
import gzip
import warnings
import networkx as nx
warnings.filterwarnings('ignore')
np.random.seed(42)

with open('/tmp/all_graphs.pkl', 'rb') as f:
    graph_data = pickle.load(f)
with open('/tmp/g7_analysis_results.json') as f:
    analysis = json.load(f)

main_graphs = graph_data['main']
survivors = analysis['survivors']

# ============================================================
# DEDUPLICATE
# ============================================================
n_dependent = {'partition_Z_beta0.1', 'heat_trace_t0.1', 'adj_raw_size',
    'heat_content_asym', 'betti0_total_persistence', 'partition_Z_beta0.01',
    'betti0_n_bars', 'heat_trace_t1.0', 'partition_Z_beta1.0',
    'heat_trace_t10.0', 'partition_Z_beta10.0'}

filtered = [s for s in survivors if s['key'] not in n_dependent]

# Remove redundant within-group
to_remove = {'spec_compress_ratio', 'adj_compress_ratio', 'von_neumann_norm'}
filtered = [s for s in filtered if s['key'] not in to_remove]
filtered.sort(key=lambda x: -x['cohens_d'])

# TOP 10 only for deformation
top10 = filtered[:10]
print("TOP 10 FINALISTES:")
for i, s in enumerate(top10, 1):
    print(f"  {i}. {s['piste']}:{s['key']:<35s} d={s['cohens_d']:.2f}, |r|={abs(s['best_old_corr_val']):.3f}")

# ============================================================
# METRIC COMPUTATION (streamlined)
# ============================================================
def ensure_connected(G):
    if G.number_of_nodes() < 3: return None
    if nx.is_connected(G): return G
    return G.subgraph(max(nx.connected_components(G), key=len)).copy()

def get_laplacian_eigs(G):
    L = nx.laplacian_matrix(G).toarray().astype(float)
    eigs = np.sort(np.linalg.eigvalsh(L))
    return eigs, eigs[eigs > 1e-10]

def compute_metric(G_orig, piste, key):
    G = ensure_connected(G_orig)
    if G is None: return None
    N = G.number_of_nodes()
    M = G.number_of_edges()
    if M == 0: return None
    
    try:
        if piste == 'F':
            eigs, eigs_pos = get_laplacian_eigs(G)
            if len(eigs_pos) == 0: return None
            
            if 'heat_entropy' in key:
                t = float(key.split('_t')[1])
                exp_v = np.exp(-t * eigs_pos)
                H = np.sum(exp_v) + 1
                p = np.concatenate([[1/H], exp_v/H])
                p = p[p > 1e-30]
                return float(-np.sum(p * np.log(p)))
            elif key == 'heat_decay_100_10':
                return float((np.sum(np.exp(-100*eigs_pos))+1) / (np.sum(np.exp(-10*eigs_pos))+1))
            elif key == 'heat_decay_10_1':
                return float((np.sum(np.exp(-10*eigs_pos))+1) / (np.sum(np.exp(-1*eigs_pos))+1))
            elif 'heat_trace_norm' in key:
                t = float(key.split('_t')[1])
                return float((np.sum(np.exp(-t*eigs_pos))+1) / N)
            elif key == 'log_det_L_norm':
                return float(np.sum(np.log(eigs_pos)) / N)

        elif piste == 'A':
            curvatures = []
            for u, v in G.edges():
                common = len(set(G.neighbors(u)) & set(G.neighbors(v)))
                curvatures.append(4 - G.degree(u) - G.degree(v) + 3*common)
            c = np.array(curvatures, dtype=float)
            if key == 'forman_frac_negative': return float(np.mean(c < 0))
            elif key == 'forman_frac_positive': return float(np.mean(c > 0))
            elif key == 'forman_frac_zero': return float(np.mean(c == 0))
            elif key == 'forman_median': return float(np.median(c))

        elif piste == 'B':
            eigs, eigs_pos = get_laplacian_eigs(G)
            if len(eigs_pos) == 0: return None
            if 'free_energy' in key:
                beta = float(key.split('beta')[1])
                Z = np.sum(np.exp(-beta * eigs))
                return float(-np.log(Z)/beta) if Z > 0 else None
            elif key == 'renyi_entropy_2_norm':
                tr = np.sum(eigs_pos)
                rho2 = np.sum((eigs_pos/tr)**2)
                return float(-np.log2(rho2+1e-30) / np.log2(N))

        elif piste == 'E':
            if key in ('betti0_mean_persistence', 'betti0_std_persistence', 'betti0_persistence_entropy_norm'):
                eb = nx.edge_betweenness_centrality(G)
                se = sorted(eb.items(), key=lambda x: x[1])
                H = nx.Graph(); H.add_nodes_from(G.nodes())
                deaths = []
                for idx, (edge, w) in enumerate(se):
                    u, v = edge
                    if H.number_of_edges() == 0 or not nx.has_path(H, u, v):
                        deaths.append(idx / M)
                    H.add_edge(u, v)
                if not deaths: return None
                d = np.array(deaths)
                if key == 'betti0_mean_persistence': return float(np.mean(d))
                elif key == 'betti0_std_persistence': return float(np.std(d))
                else:
                    p = d / np.sum(d) if np.sum(d) > 1e-10 else d
                    p = p[p > 1e-30]
                    return float(-np.sum(p*np.log(p)) / np.log(N))

        elif piste == 'J':
            if key == 'spec_complexity_per_node':
                eigs = np.sort(np.linalg.eigvalsh(nx.laplacian_matrix(G).toarray().astype(float)))
                return float(len(gzip.compress(eigs.tobytes())) / N)
            elif key == 'adj_complexity_per_node2':
                A = nx.adjacency_matrix(G).toarray()
                return float(len(gzip.compress(A.tobytes())) / (N*N))
            elif key == 'info_density':
                A = nx.adjacency_matrix(G).toarray()
                return float(len(gzip.compress(A.tobytes())) / (N*np.log2(N))) if N > 1 else None
    except:
        return None
    return None

# ============================================================
# DEFORMATION
# ============================================================
def deform(G, dtype, frac):
    G2 = G.copy()
    nodes = list(G2.nodes())
    edges = list(G2.edges())
    
    if dtype == 'edge_removal':
        np.random.shuffle(edges)
        G2.remove_edges_from(edges[:int(frac*len(edges))])
    elif dtype == 'edge_addition':
        n_add = int(frac * len(edges))
        added = 0
        for _ in range(n_add * 10):
            u, v = np.random.choice(nodes, 2, replace=False)
            if not G2.has_edge(u, v):
                G2.add_edge(u, v)
                added += 1
                if added >= n_add: break
    elif dtype == 'rewiring':
        np.random.shuffle(edges)
        for e in edges[:int(frac*len(edges))]:
            G2.remove_edge(*e)
            for _ in range(50):
                u, v = np.random.choice(nodes, 2, replace=False)
                if not G2.has_edge(u, v):
                    G2.add_edge(u, v); break
    elif dtype == 'node_removal':
        np.random.shuffle(nodes)
        G2.remove_nodes_from(nodes[:int(frac*len(nodes))])
    elif dtype == 'degree_attack':
        for _ in range(int(frac*len(nodes))):
            if G2.number_of_nodes() < 4: break
            G2.remove_node(max(G2.nodes(), key=lambda x: G2.degree(x)))
    return G2

# Pick 6 representative graphs (N~100)
test_graphs = []
for fam in ['erdos_renyi', 'barabasi_albert', 'watts_strogatz', 'random_regular', 'random_geometric', 'connected_caveman']:
    for i, (G, name, params) in enumerate(main_graphs):
        if name == fam and 80 <= G.number_of_nodes() <= 120:
            test_graphs.append((G, f"{name}_{i}"))
            break

print(f"\nTesting {len(test_graphs)} graphs × 5 deformations × 5 levels × {len(top10)} metrics")

dtypes = ['edge_removal', 'edge_addition', 'rewiring', 'node_removal', 'degree_attack']
levels = [0.02, 0.05, 0.1, 0.2, 0.4]

t0 = time.time()
results = {}

for s in top10:
    pid = f"{s['piste']}:{s['key']}"
    cvs = {}
    transitions = []
    
    for dt in dtypes:
        all_trajs = []
        for G_base, gname in test_graphs:
            G_c = ensure_connected(G_base)
            if G_c is None: continue
            base = compute_metric(G_c, s['piste'], s['key'])
            if base is None: continue
            
            traj = [base]
            for frac in levels:
                try:
                    G_d = deform(G_c, dt, frac)
                    v = compute_metric(G_d, s['piste'], s['key'])
                    traj.append(v if v is not None else np.nan)
                except:
                    traj.append(np.nan)
            all_trajs.append(traj)
        
        if all_trajs:
            arr = np.array(all_trajs)
            graph_cvs = []
            for row in arr:
                valid = row[~np.isnan(row)]
                if len(valid) > 2 and np.abs(np.mean(valid)) > 1e-10:
                    graph_cvs.append(np.std(valid) / np.abs(np.mean(valid)))
            if graph_cvs:
                cvs[dt] = float(np.mean(graph_cvs))
            
            # Transition: look for sudden jumps
            for row in arr:
                valid = row[~np.isnan(row)]
                if len(valid) > 3:
                    d = np.diff(valid)
                    if np.std(d) > 0 and np.max(np.abs(d)) > 4*np.std(d):
                        if dt not in transitions:
                            transitions.append(dt)
    
    mean_cv = float(np.mean(list(cvs.values()))) if cvs else None
    results[pid] = {
        'cvs': cvs, 'mean_cv': mean_cv, 'transitions': transitions,
        'cohens_d': s['cohens_d'], 'best_old_r': abs(s['best_old_corr_val']),
        'piste': s['piste'], 'key': s['key']
    }

print(f"Done in {time.time()-t0:.1f}s")

# ============================================================
# RESULTS
# ============================================================
print("\n" + "=" * 70)
print("STABILITÉ SOUS DÉFORMATION")
print("=" * 70)

print(f"\n{'METRIC':<40s} {'CV':>6s} {'edge-':>6s} {'edge+':>6s} {'rewire':>6s} {'node-':>6s} {'deg_atk':>7s} {'TRANS':>10s} {'STATUS':>15s}")
print("-" * 115)

for pid, r in sorted(results.items(), key=lambda x: x[1].get('mean_cv', 999)):
    mcv = r.get('mean_cv')
    if mcv is None: continue
    c = r['cvs']
    trans = ','.join(r['transitions']) if r['transitions'] else '-'
    
    if mcv < 0.1: status = "🔒 INVARIANT"
    elif mcv < 0.25: status = "📉 STABLE"
    elif mcv < 0.5: status = "〰️ MODERATE"
    else: status = "❌ UNSTABLE"
    
    print(f"  {pid:<38s} {mcv:>6.3f} {c.get('edge_removal',0):>6.3f} {c.get('edge_addition',0):>6.3f} {c.get('rewiring',0):>6.3f} {c.get('node_removal',0):>6.3f} {c.get('degree_attack',0):>6.3f} {trans:>10s} {status:>15s}")

# ============================================================
# UNIVERSALITY CHECK (quick)
# ============================================================
print("\n" + "=" * 70)
print("UNIVERSALITÉ (même valeur pour toutes les familles?)")
print("=" * 70)

for pid, r in sorted(results.items(), key=lambda x: x[1].get('mean_cv', 999)):
    mcv = r.get('mean_cv')
    if mcv is None or mcv > 0.5: continue
    
    fam_vals = {}
    for i, (G, name, params) in enumerate(main_graphs):
        if G.number_of_nodes() < 50: continue
        G_c = ensure_connected(G)
        if G_c is None: continue
        v = compute_metric(G_c, r['piste'], r['key'])
        if v is not None:
            fam_vals.setdefault(name, []).append(v)
    
    fam_means = {f: np.mean(v) for f, v in fam_vals.items() if len(v) >= 2}
    means = list(fam_means.values())
    if means:
        gcv = np.std(means) / np.abs(np.mean(means)) if np.abs(np.mean(means)) > 1e-10 else 999
        tag = "🌍 UNIVERSAL" if gcv < 0.15 else ("~semi" if gcv < 0.3 else "varied")
        print(f"\n  {pid}: mean={np.mean(means):.4f}, CV_families={gcv:.3f} → {tag}")
        for f, m in sorted(fam_means.items(), key=lambda x: x[1]):
            print(f"    {f:<30s} {m:.4f}")

# ============================================================
# FINAL VERDICT
# ============================================================
print("\n" + "=" * 70)
print("=" * 70)
print("VERDICT FINAL")
print("=" * 70)

final = []
for pid, r in results.items():
    mcv = r.get('mean_cv')
    if mcv is None: continue
    
    passes = (
        r['cohens_d'] > 0.5 and          # non-trivial
        r['best_old_r'] < 0.7 and         # non-redundant
        (mcv < 0.5 or r['transitions'])   # stable or transition
    )
    
    if passes:
        final.append({**r, 'id': pid})

final.sort(key=lambda x: -x['cohens_d'])

print(f"\n🏆 {len(final)} MÉTRIQUES PASSENT TOUS LES CRITÈRES:\n")
for i, c in enumerate(final, 1):
    stab = "🔒 INVARIANT" if c['mean_cv'] < 0.1 else ("📉 STABLE" if c['mean_cv'] < 0.25 else "〰️ MODERATE")
    print(f"  {i}. {c['id']}")
    print(f"     Cohen's d = {c['cohens_d']:.2f} | |r_old| = {c['best_old_r']:.3f} | Deform CV = {c['mean_cv']:.3f} {stab}")
    if c['transitions']:
        print(f"     ★ Transitions détectées sous: {', '.join(c['transitions'])}")
    print()

with open('/tmp/g7_final.json', 'w') as f:
    json.dump({'final': final, 'all_results': results}, f, indent=2, default=str)
print("Saved to /tmp/g7_final.json")

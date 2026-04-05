#!/usr/bin/env python3
"""
G9 FAST — Conservation laws search. Optimized for speed.
"""

import networkx as nx
import numpy as np
import json
import warnings
warnings.filterwarnings('ignore')

np.random.seed(42)

# ===================== OPERATIONS =====================
def op_line(G):
    L = nx.line_graph(G)
    return L if len(L) >= 3 else None

def op_complement(G):
    C = nx.complement(G)
    return C if C.number_of_edges() > 0 else None

def op_square(G):
    return nx.power(G, 2)

def op_subdivision(G):
    S = nx.Graph()
    nid = max(G.nodes()) + 1
    S.add_nodes_from(G.nodes())
    for u, v in G.edges():
        S.add_node(nid)
        S.add_edge(u, nid)
        S.add_edge(nid, v)
        nid += 1
    return S

def op_corona(G):
    C = G.copy()
    nid = max(G.nodes()) + 1
    for v in list(G.nodes()):
        C.add_node(nid)
        C.add_edge(v, nid)
        nid += 1
    return C

def op_mycielskian(G):
    return nx.mycielskian(G)

def op_cartesian_K2(G):
    return nx.cartesian_product(G, nx.path_graph(2))

def op_double(G):
    n = max(G.nodes()) + 1
    D = G.copy()
    for v in list(G.nodes()):
        D.add_node(v + n)
    for u, v in G.edges():
        D.add_edge(u + n, v + n)
    for v in list(G.nodes()):
        D.add_edge(v, v + n)
    return D

OPS = {
    'line': op_line,
    'complement': op_complement,
    'square': op_square,
    'subdivision': op_subdivision,
    'corona': op_corona,
    'mycielskian': op_mycielskian,
    'cart_K2': op_cartesian_K2,
    'double': op_double,
}

# ===================== METRICS (fast only) =====================
def safe(f, G):
    try:
        v = f(G)
        if v is None or (isinstance(v, float) and (np.isnan(v) or np.isinf(v))):
            return None
        return float(v)
    except:
        return None

def eigenvalues_adj(G):
    A = nx.adjacency_matrix(G).todense()
    return np.linalg.eigvalsh(A)

def eigenvalues_lap(G):
    L = nx.laplacian_matrix(G).todense().astype(float)
    return np.linalg.eigvalsh(L)

METRICS = {}

# Basic
METRICS['n'] = lambda G: G.number_of_nodes()
METRICS['m'] = lambda G: G.number_of_edges()
METRICS['density'] = lambda G: nx.density(G)
METRICS['avg_deg'] = lambda G: 2*G.number_of_edges()/G.number_of_nodes()

# Degree stats
METRICS['max_deg'] = lambda G: max(d for _,d in G.degree())
METRICS['min_deg'] = lambda G: min(d for _,d in G.degree())
METRICS['deg_std'] = lambda G: np.std([d for _,d in G.degree()])
METRICS['deg_sum'] = lambda G: sum(d for _,d in G.degree())  # = 2m

# Triangles & clustering
METRICS['triangles'] = lambda G: sum(nx.triangles(G).values())//3
METRICS['clustering'] = lambda G: nx.average_clustering(G)
METRICS['transitivity'] = lambda G: nx.transitivity(G)

# Components
METRICS['components'] = lambda G: nx.number_connected_components(G)

# Spectral
METRICS['spectral_radius'] = lambda G: float(max(abs(eigenvalues_adj(G))))
METRICS['energy'] = lambda G: float(np.sum(np.abs(eigenvalues_adj(G))))
METRICS['lap_energy'] = lambda G: float(np.sum(np.abs(eigenvalues_lap(G) - np.mean(eigenvalues_lap(G)))))
METRICS['spectral_gap'] = lambda G: float(sorted(eigenvalues_lap(G))[1]) if nx.is_connected(G) else 0.0
METRICS['lap_trace'] = lambda G: float(np.sum(eigenvalues_lap(G)))  # = 2m
METRICS['adj_trace_sq'] = lambda G: float(np.sum(eigenvalues_adj(G)**2))  # = 2m
METRICS['adj_trace_cube'] = lambda G: float(np.sum(eigenvalues_adj(G)**3))  # = 6*triangles
METRICS['lap_max'] = lambda G: float(max(eigenvalues_lap(G)))
METRICS['adj_rank'] = lambda G: float(np.linalg.matrix_rank(nx.adjacency_matrix(G).todense()))

# Spanning trees (Kirchhoff)
def spanning_trees(G):
    if not nx.is_connected(G):
        return 0.0
    eigs = sorted(eigenvalues_lap(G))
    nz = [e for e in eigs if e > 1e-10]
    if not nz:
        return 0.0
    return float(np.exp(sum(np.log(e) for e in nz) - np.log(G.number_of_nodes())))
METRICS['spanning_trees_log'] = lambda G: np.log1p(spanning_trees(G))

# Ratios (the interesting ones for conservation)
METRICS['m_over_n'] = lambda G: G.number_of_edges() / G.number_of_nodes()
METRICS['energy_over_n'] = lambda G: float(np.sum(np.abs(eigenvalues_adj(G)))) / G.number_of_nodes()
METRICS['energy_over_m'] = lambda G: float(np.sum(np.abs(eigenvalues_adj(G)))) / G.number_of_edges() if G.number_of_edges() > 0 else None
METRICS['sr_over_avg_deg'] = lambda G: float(max(abs(eigenvalues_adj(G)))) / (2*G.number_of_edges()/G.number_of_nodes())
METRICS['lap_max_over_max_deg'] = lambda G: float(max(eigenvalues_lap(G))) / max(d for _,d in G.degree())
METRICS['tri_over_m'] = lambda G: (sum(nx.triangles(G).values())//3) / G.number_of_edges() if G.number_of_edges() > 0 else 0

# Algebraic/combinatorial
METRICS['chromatic_ub'] = lambda G: max(nx.coloring.greedy_color(G, strategy='largest_first').values()) + 1

# ===================== GRAPH GENERATION =====================
def gen_graphs():
    gs = []
    for n in [8, 12, 16, 20, 25, 30]:
        # ER
        for p in [0.15, 0.3, 0.5]:
            G = nx.erdos_renyi_graph(n, p, seed=42+n)
            if nx.is_connected(G) and G.number_of_edges() > 0:
                gs.append((f'ER_{n}_{p}', G))
        # BA
        for mm in [1, 2, 3]:
            if mm < n:
                gs.append((f'BA_{n}_{mm}', nx.barabasi_albert_graph(n, mm, seed=42)))
        # WS
        for k in [4]:
            if k < n:
                gs.append((f'WS_{n}_{k}', nx.watts_strogatz_graph(n, k, 0.3, seed=42)))
        # Regular
        for d in [3, 4]:
            if d < n and (n*d)%2==0:
                gs.append((f'REG_{n}_{d}', nx.random_regular_graph(d, n, seed=42)))
        # Cycle, Path, Star, Complete(small)
        gs.append((f'CYCLE_{n}', nx.cycle_graph(n)))
        gs.append((f'PATH_{n}', nx.path_graph(n)))
        gs.append((f'STAR_{n}', nx.star_graph(n-1)))
        if n <= 15:
            gs.append((f'COMPLETE_{n}', nx.complete_graph(n)))
        # Tree
        gs.append((f'TREE_{n}', nx.random_labeled_tree(n, seed=42)))
        # Wheel
        gs.append((f'WHEEL_{n}', nx.wheel_graph(n)))
        # Grid
        s = int(np.sqrt(n))
        if s >= 2:
            G = nx.convert_node_labels_to_integers(nx.grid_2d_graph(s, s))
            gs.append((f'GRID_{s}x{s}', G))
    
    # Special
    gs.append(('PETERSEN', nx.petersen_graph()))
    gs.append(('DODECA', nx.dodecahedral_graph()))
    gs.append(('ICOSA', nx.icosahedral_graph()))
    gs.append(('CUBICAL', nx.cubical_graph()))
    gs.append(('TUTTE', nx.tutte_graph()))
    gs.append(('DESARGUES', nx.desargues_graph()))
    
    print(f"Generated {len(gs)} graphs")
    return gs

# ===================== MAIN =====================
def main():
    print("="*70)
    print("G9 — CONSERVATION LAWS SEARCH")
    print("="*70)
    
    graphs = gen_graphs()
    
    # Compute original metrics
    print("\nComputing original metrics...")
    orig = {}
    for key, G in graphs:
        orig[key] = {}
        for mname, mfunc in METRICS.items():
            orig[key][mname] = safe(mfunc, G)
    print(f"  Done: {len(orig)} graphs × {len(METRICS)} metrics")
    
    # Apply transformations
    print("\nApplying transformations + computing metrics...")
    trans = {}
    for opname, opfunc in OPS.items():
        trans[opname] = {}
        ok, fail = 0, 0
        for key, G in graphs:
            try:
                T = opfunc(G)
                if T and len(T) >= 3 and T.number_of_edges() > 0 and len(T) <= 500:
                    mvals = {}
                    for mname, mfunc in METRICS.items():
                        mvals[mname] = safe(mfunc, T)
                    trans[opname][key] = mvals
                    ok += 1
                else:
                    fail += 1
            except:
                fail += 1
        print(f"  {opname}: {ok} ok, {fail} fail")
    
    # ===================== SEARCH =====================
    mnames = list(METRICS.keys())
    laws = []
    
    # STRATEGY 1: Exact ratios M(T(G))/M(G) = const
    print("\n" + "="*70)
    print("STRATEGY 1: Single metric ratio/diff invariance")
    print("="*70)
    
    for opname in OPS:
        for mname in mnames:
            ratios, diffs = [], []
            for key in trans[opname]:
                o = orig.get(key, {}).get(mname)
                t = trans[opname][key].get(mname)
                if o is not None and t is not None:
                    if abs(o) > 1e-10:
                        ratios.append(t/o)
                    diffs.append(t - o)
            
            # Ratio check
            if len(ratios) >= 15:
                mu = np.mean(ratios)
                cv = np.std(ratios)/abs(mu) if abs(mu) > 1e-10 else 999
                if cv < 0.005:
                    law = {
                        'strat': 1, 'type': 'ratio', 'op': opname, 'metric': mname,
                        'value': round(mu, 8), 'cv': round(cv, 8), 'n': len(ratios),
                        'formula': f"{mname}(T)//{mname}(G) = {mu:.6f}  [T={opname}]"
                    }
                    laws.append(law)
                    print(f"  🔥 {law['formula']}  CV={cv:.8f}  n={len(ratios)}")
            
            # Diff check (only if not size-dependent trivially)
            if len(diffs) >= 15 and mname not in ('n', 'm', 'deg_sum', 'lap_trace'):
                mu = np.mean(diffs)
                cv = np.std(diffs)/abs(mu) if abs(mu) > 1e-10 else (0 if np.std(diffs) < 1e-10 else 999)
                if cv < 0.005 and abs(mu) > 1e-8:
                    law = {
                        'strat': 1, 'type': 'diff', 'op': opname, 'metric': mname,
                        'value': round(mu, 8), 'cv': round(cv, 8), 'n': len(diffs),
                        'formula': f"{mname}(T) - {mname}(G) = {mu:.6f}  [T={opname}]"
                    }
                    laws.append(law)
                    print(f"  🔥 {law['formula']}  CV={cv:.8f}  n={len(diffs)}")
    
    # STRATEGY 2: Pairwise co-invariance
    print("\n" + "="*70)
    print("STRATEGY 2: Pairwise co-invariance (ratio of ratios)")
    print("="*70)
    
    for opname in OPS:
        # Collect ratios per metric
        ratio_data = {}
        for mname in mnames:
            rd = {}
            for key in trans[opname]:
                o = orig.get(key, {}).get(mname)
                t = trans[opname][key].get(mname)
                if o is not None and t is not None and abs(o) > 1e-10:
                    rd[key] = t/o
            if len(rd) >= 15:
                ratio_data[mname] = rd
        
        rm = list(ratio_data.keys())
        for i in range(len(rm)):
            for j in range(i+1, len(rm)):
                m1, m2 = rm[i], rm[j]
                common = set(ratio_data[m1]) & set(ratio_data[m2])
                if len(common) < 15:
                    continue
                rr = [ratio_data[m1][k]/ratio_data[m2][k] for k in common if abs(ratio_data[m2][k]) > 1e-10]
                if len(rr) < 15:
                    continue
                mu = np.mean(rr)
                cv = np.std(rr)/abs(mu) if abs(mu) > 1e-10 else 999
                if cv < 0.005:
                    # Skip trivially related metrics
                    if {m1, m2} in [{'m', 'deg_sum'}, {'m', 'lap_trace'}, {'adj_trace_sq', 'deg_sum'}, {'n', 'deg_sum'}]:
                        continue
                    law = {
                        'strat': 2, 'type': 'co_inv', 'op': opname, 
                        'metrics': [m1, m2], 'value': round(mu, 8),
                        'cv': round(cv, 8), 'n': len(rr),
                        'formula': f"Δ{m1}/Δ{m2} = {mu:.6f}  [T={opname}]"
                    }
                    laws.append(law)
                    print(f"  🔥 {law['formula']}  CV={cv:.8f}  n={len(rr)}")
    
    # STRATEGY 3: SVD null-space (nonlinear conservation)
    print("\n" + "="*70)
    print("STRATEGY 3: Nonlinear conservation (SVD null-space in log-ratio space)")
    print("="*70)
    
    for opname in OPS:
        # Build log-ratio matrix
        lr = {}
        for mname in mnames:
            vals = {}
            for key in trans[opname]:
                o = orig.get(key, {}).get(mname)
                t = trans[opname][key].get(mname)
                if o is not None and t is not None and o > 1e-10 and t > 1e-10:
                    vals[key] = np.log(t/o)
            if len(vals) >= 10:
                lr[mname] = vals
        
        if len(lr) < 3:
            continue
        
        common = set.intersection(*[set(v.keys()) for v in lr.values()])
        if len(common) < 10:
            continue
        common = sorted(common)
        
        mlist = list(lr.keys())
        M = np.array([[lr[m][k] for m in mlist] for k in common])
        
        U, S, Vt = np.linalg.svd(M, full_matrices=False)
        
        # Null space = singular values close to 0
        thresh = 0.005 * S[0] if S[0] > 0 else 0.005
        null_idx = np.where(S < thresh)[0]
        
        if len(null_idx) > 0:
            print(f"\n  {opname}: σ = {S[:min(8,len(S))]}")
            for idx in null_idx[:3]:
                c = Vt[idx]
                order = np.argsort(np.abs(c))[::-1]
                dom = [(mlist[k], round(c[k], 4)) for k in order[:6] if abs(c[k]) > 0.03]
                
                combo = M @ c
                resid = np.std(combo)
                
                formula = " + ".join(f"{coeff}*log(Δ{m})" for m, coeff in dom)
                
                law = {
                    'strat': 3, 'type': 'nonlinear', 'op': opname,
                    'coefficients': dict(dom), 'sigma': round(float(S[idx]), 8),
                    'residual_std': round(float(resid), 8), 'n': len(common),
                    'formula': f"{formula} ≈ 0  [T={opname}]"
                }
                laws.append(law)
                print(f"  🔥 σ={S[idx]:.6f}: {formula}")
    
    # STRATEGY 4: Fixed points under iteration
    print("\n" + "="*70)
    print("STRATEGY 4: Fixed-point convergence under iteration")
    print("="*70)
    
    for opname in ['line', 'square']:
        print(f"\n  Iterating: {opname}")
        opfunc = OPS[opname]
        
        final_metrics = {m: [] for m in mnames}
        
        for key, G in graphs[:20]:
            cur = G.copy()
            for step in range(5):
                try:
                    nxt = opfunc(cur)
                    if nxt is None or len(nxt) < 3 or len(nxt) > 300:
                        break
                    cur = nxt
                except:
                    break
            
            # Record final metrics
            for mname, mfunc in METRICS.items():
                v = safe(mfunc, cur)
                if v is not None:
                    final_metrics[mname].append(v)
        
        for mname in mnames:
            vals = final_metrics[mname]
            if len(vals) < 8:
                continue
            mu = np.mean(vals)
            cv = np.std(vals)/abs(mu) if abs(mu) > 1e-10 else (0 if np.std(vals) < 1e-10 else 999)
            if cv < 0.05:
                law = {
                    'strat': 4, 'type': 'fixed_point', 'op': opname,
                    'metric': mname, 'value': round(mu, 6), 'cv': round(cv, 6),
                    'n': len(vals),
                    'formula': f"lim {opname}^k(G) → {mname} ≈ {mu:.4f}  (CV={cv:.4f})"
                }
                laws.append(law)
                print(f"  🔥 {law['formula']}  n={len(vals)}")
    
    # ===================== SUMMARY =====================
    print("\n" + "="*70)
    print(f"TOTAL CANDIDATE LAWS: {len(laws)}")
    print("="*70)
    
    # Group by strategy
    for s in [1,2,3,4]:
        subset = [l for l in laws if l['strat'] == s]
        print(f"\n  Strategy {s}: {len(subset)} laws")
        for l in subset:
            print(f"    {l['formula']}")
    
    # Save
    with open('/tmp/g9_laws.json', 'w') as f:
        json.dump(laws, f, indent=2)
    
    print(f"\nSaved to /tmp/g9_laws.json")

if __name__ == '__main__':
    main()

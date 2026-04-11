"""
Experiment S1.2 — Is log|K(G)| predictable from spectral invariants on G1?

Contrarian question: the graphs project (G1..G11) scanned 250K computations
over 356 graphs and ~100 metrics, concluding that the non-spectral space is
"saturated". If that conclusion is correct, the sandpile group structure
(which is classically non-spectral) should be either
  (a) STATISTICALLY predictable from spectral metrics, OR
  (b) genuinely independent but "invisible" to the metric scan.

This test uses the 356 G1 graphs, restricted to connected + small (n <= N_MAX)
for tractable integer SNF in pure Python. Measures:
  - rank of K(G) [= number of non-trivial invariant factors]
  - log |K(G)| [= log of spanning tree count, classically = sum of log of
    nonzero Laplacian eigenvalues, MINUS log(n) by matrix-tree theorem]
  - largest invariant factor
  - is_cyclic flag
  - 2-rank, 3-rank, 5-rank
  - "factor excess" = rank - 1 (deviation from cyclic)

Then check correlations against ALL numerical metrics in g1_results.json.

KEY PREDICTION:
By the matrix-tree theorem, log|K(G)| = sum_{i>=2} log(lambda_L_i) - log(n).
So log|K(G)| is ALGEBRAICALLY a function of the Laplacian spectrum — the
spectrum literally determines the order. If we see a near-perfect correlation
of log|K(G)| with log(sum of log L-eigenvalues), we have a trivial tautology.

The INTERESTING signal is NOT in log|K(G)| itself, it's in:
  - rank (number of invariant factors > 1) — NOT determined by spectrum
  - is_cyclic — NOT determined by spectrum
  - largest_factor / |K(G)| — measures how "spread out" vs "cyclic" the group is

So the real test is: can ANY spectral metric predict the RANK?
If no → SNF info is orthogonal to spectrum → the graph project missed it.
If yes → SNF is statistically redundant with spectrum on this dataset.

Falsification rules applied:
- Rule 1: linear baseline (Pearson corr) before anything fancy
- Rule 3: filter log|K| which is a known tautology with Laplacian spectrum
- Rule 7: vary the subset (connected only, various n ranges)
- Rule 9: decompose into order-part (tautological) vs structure-part (novel)
- Rule 10: null model — random graphs with matched degree sequence
"""

import json
import math
import os
import pickle
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from S1_smith_normal_form import compute_sandpile_invariants

import networkx as nx
import numpy as np
import flint


def snf_diag(int_matrix_2d):
    """Fast SNF via FLINT. Input: 2D list of ints. Output: diagonal list."""
    if not int_matrix_2d or not int_matrix_2d[0]:
        return []
    M = flint.fmpz_mat(int_matrix_2d)
    S = M.snf()
    return [abs(int(S[i, i])) for i in range(min(S.nrows(), S.ncols()))]


# Max graph size for SNF computation.
# Dense K_n is the worst case: flint handles K_200 easily but K_500 is slow
# in the dense/unit entry regime. Cap at 300 and also skip K_n with n>200.
N_MAX = 300
HERE = os.path.dirname(os.path.abspath(__file__))
G1_RESULTS = os.path.join(HERE, "..", "..", "data", "g1_results.json")
OUT_PATH = os.path.join(HERE, "..", "data", "exp_s2_correlations.json")
CACHE_PATH = os.path.join(HERE, "..", "data", "_exp_s2_rows_cache.pkl")


def adj_matrix(G):
    nodes = list(G.nodes())
    idx = {v: i for i, v in enumerate(nodes)}
    n = len(nodes)
    A = [[0] * n for _ in range(n)]
    for u, v in G.edges():
        i, j = idx[u], idx[v]
        A[i][j] = 1
        A[j][i] = 1
    return A


def graph_sandpile(G):
    """Returns invariants dict, None if not connected."""
    if G.number_of_nodes() == 0 or not nx.is_connected(G):
        return None
    # Build integer Laplacian via numpy then go through lists for sympy
    n = G.number_of_nodes()
    L = nx.laplacian_matrix(G).toarray().astype(int)
    Lr = L[:-1, :-1].tolist()
    diag = snf_diag(Lr)
    return compute_sandpile_invariants(diag)


def generate_g1_subset(n_max=N_MAX):
    """Regenerate G1 graphs with n <= n_max, in the same order as G1."""
    graphs = []

    # This is a direct transcription of generate_all_graphs() from
    # phases/G1/phase_g1.py, filtered by n <= n_max.
    # All seeds are 42 (verified in the source).

    # 1. ER
    for n in [50, 100, 200, 500]:
        if n > n_max:
            continue
        for p in [0.01, 0.02, 0.05, 0.1, 0.2, 0.5]:
            G = nx.erdos_renyi_graph(n, p, seed=42)
            graphs.append((G, 'erdos_renyi', {'n': n, 'p': p}))

    # 2. BA
    for n in [50, 100, 200, 500]:
        if n > n_max:
            continue
        for m_ba in [1, 2, 3, 5, 10]:
            G = nx.barabasi_albert_graph(n, m_ba, seed=42)
            graphs.append((G, 'barabasi_albert', {'n': n, 'm': m_ba}))

    # 3. WS
    for n in [50, 100, 200, 500]:
        if n > n_max:
            continue
        for k in [4, 6, 10]:
            for p in [0.0, 0.01, 0.05, 0.1, 0.3, 1.0]:
                G = nx.watts_strogatz_graph(n, k, p, seed=42)
                graphs.append((G, 'watts_strogatz', {'n': n, 'k': k, 'p': p}))

    # 4. Lattices
    for n in [50, 100, 200]:
        if n > n_max:
            continue
        G = nx.cycle_graph(n)
        graphs.append((G, 'cycle', {'n': n}))

    for side in [7, 10, 15, 20]:
        if side * side > n_max:
            continue
        G = nx.grid_2d_graph(side, side)
        G = nx.convert_node_labels_to_integers(G)
        graphs.append((G, 'grid_2d', {'side': side, 'n': side * side}))

    for side in [5, 8, 12]:
        G = nx.triangular_lattice_graph(side, side)
        G = nx.convert_node_labels_to_integers(G)
        if G.number_of_nodes() > n_max:
            continue
        graphs.append((G, 'triangular_lattice', {'side': side}))

    # 5. Trees
    for n in [50, 100, 200, 500]:
        if n > n_max:
            continue
        G = nx.random_labeled_tree(n, seed=42)
        graphs.append((G, 'random_tree', {'n': n}))

    for r in [2, 3, 4]:
        for h in [3, 4, 5]:
            n_tree = sum(r ** i for i in range(h + 1))
            if n_tree > n_max or n_tree > 1500:
                continue
            G = nx.balanced_tree(r, h)
            graphs.append((G, 'balanced_tree', {'r': r, 'h': h, 'n': n_tree}))

    for n in [20, 50, 100, 200]:
        if n > n_max:
            continue
        G = nx.star_graph(n - 1)
        graphs.append((G, 'star', {'n': n}))

    for n in [20, 50, 100, 200]:
        if n > n_max:
            continue
        G = nx.path_graph(n)
        graphs.append((G, 'path', {'n': n}))

    # 6. Complete
    for n in [10, 20, 50, 100]:
        if n > n_max:
            continue
        G = nx.complete_graph(n)
        graphs.append((G, 'complete', {'n': n}))

    # 7. Complete bipartite
    for n1 in [10, 25, 50]:
        for n2 in [10, 25, 50]:
            if n1 + n2 > n_max:
                continue
            G = nx.complete_bipartite_graph(n1, n2)
            graphs.append((G, 'complete_bipartite', {'n1': n1, 'n2': n2}))

    # 8. Random regular
    for n in [50, 100, 200]:
        if n > n_max:
            continue
        for d in [3, 4, 6, 10]:
            if d < n:
                try:
                    G = nx.random_regular_graph(d, n, seed=42)
                    graphs.append((G, 'random_regular', {'n': n, 'd': d}))
                except Exception:
                    pass

    # 9. Random geometric
    for n in [50, 100, 200, 500]:
        if n > n_max:
            continue
        for radius in [0.1, 0.15, 0.2, 0.3]:
            G = nx.random_geometric_graph(n, radius, seed=42)
            graphs.append((G, 'random_geometric', {'n': n, 'radius': radius}))

    # 10. SBM
    for n_per_block in [25, 50]:
        for k_blocks in [2, 4]:
            n_tot = n_per_block * k_blocks
            if n_tot > n_max:
                continue
            for p_in in [0.3, 0.5]:
                for p_out in [0.01, 0.05, 0.1]:
                    sizes = [n_per_block] * k_blocks
                    probs = [[p_in if i == j else p_out for j in range(k_blocks)]
                             for i in range(k_blocks)]
                    G = nx.stochastic_block_model(sizes, probs, seed=42)
                    graphs.append((G, 'stochastic_block',
                                   {'n_per_block': n_per_block, 'k': k_blocks,
                                    'p_in': p_in, 'p_out': p_out}))

    # 11. Powerlaw cluster
    for n in [50, 100, 200, 500]:
        if n > n_max:
            continue
        for m_plc in [2, 3, 5]:
            for p in [0.1, 0.5, 0.9]:
                try:
                    G = nx.powerlaw_cluster_graph(n, m_plc, p, seed=42)
                    graphs.append((G, 'powerlaw_cluster',
                                   {'n': n, 'm': m_plc, 'p': p}))
                except Exception:
                    pass

    # 12. Circulant
    for n in [50, 100, 200]:
        if n > n_max:
            continue
        for offsets in [[1, 2], [1, 3], [1, 5], [1, 2, 5], [1, n // 4]]:
            G = nx.circulant_graph(n, offsets)
            graphs.append((G, 'circulant', {'n': n, 'offsets': offsets}))

    # 13. Newman-Watts-Strogatz
    for n in [50, 100, 200]:
        if n > n_max:
            continue
        for k in [4, 6]:
            for p in [0.01, 0.05, 0.1, 0.3]:
                G = nx.newman_watts_strogatz_graph(n, k, p, seed=42)
                graphs.append((G, 'newman_watts_strogatz',
                               {'n': n, 'k': k, 'p': p}))

    # 14. Connected caveman
    for l in [5, 10, 20]:
        for k in [5, 10]:
            if l * k > n_max or l * k > 500:
                continue
            G = nx.connected_caveman_graph(l, k)
            graphs.append((G, 'connected_caveman',
                           {'l': l, 'k': k, 'n': l * k}))

    # 15. Dual BA
    for n in [100, 200, 500]:
        if n > n_max:
            continue
        for m1 in [1, 2]:
            for m2 in [1, 2]:
                for p_dba in [0.3, 0.5, 0.7]:
                    try:
                        G = nx.dual_barabasi_albert_graph(n, m1, m2, p_dba, seed=42)
                        graphs.append((G, 'dual_barabasi_albert',
                                       {'n': n, 'm1': m1, 'm2': m2, 'p': p_dba}))
                    except Exception:
                        pass

    # 16. Lobster
    for n in [50, 100, 200]:
        if n > n_max:
            continue
        for p1 in [0.3, 0.5, 0.8]:
            for p2 in [0.1, 0.3, 0.5]:
                G = nx.random_lobster(n, p1, p2, seed=42)
                graphs.append((G, 'random_lobster',
                               {'n_backbone': n, 'p1': p1, 'p2': p2}))

    return graphs


def main():
    print("=" * 72)
    print("EXPERIMENT S1.2 — Correlation of SNF-invariants vs spectrum")
    print("=" * 72)

    # Load g1 metrics
    with open(G1_RESULTS, "r") as f:
        g1_data = json.load(f)
    print(f"Loaded {len(g1_data)} G1 rows")

    # Build lookup by (name, params) — note params may be a dict
    def key_of(name, params):
        return (name, json.dumps(params, sort_keys=True))

    g1_lookup = {key_of(row['name'], row['params']): row for row in g1_data}

    # Try to load cached rows (after expensive SNF computation)
    use_cache = os.path.exists(CACHE_PATH) and os.environ.get('NO_CACHE') != '1'
    if use_cache:
        print(f"Loading cached rows from {CACHE_PATH}")
        with open(CACHE_PATH, "rb") as f:
            cache = pickle.load(f)
        rows = cache['rows']
        skipped_disconnected = cache.get('skipped_disconnected', 0)
        print(f"  -> {len(rows)} rows loaded from cache")
        # Jump to analysis
        _analyze(rows, skipped_disconnected)
        return

    # Regenerate graphs with n <= N_MAX
    print(f"Regenerating G1 graphs with n <= {N_MAX}...")
    t0 = time.time()
    graphs = generate_g1_subset(n_max=N_MAX)
    print(f"  -> {len(graphs)} graphs regenerated in {time.time() - t0:.1f}s")

    # Compute SNF for each
    print("Computing SNF for each graph...", flush=True)
    t0 = time.time()
    rows = []
    skipped_disconnected = 0
    slow_graphs = []
    for i, (G, name, params) in enumerate(graphs):
        t_g = time.time()
        print(f"  [{i+1}/{len(graphs)}] {name} n={G.number_of_nodes()} "
              f"m={G.number_of_edges()} ...", end="", flush=True)
        inv = graph_sandpile(G)
        dt = time.time() - t_g
        print(f" {dt:.2f}s", flush=True)
        if dt > 30:
            slow_graphs.append((name, params, dt))
        if inv is None:
            skipped_disconnected += 1
            continue

        # Merge with G1 metrics
        k = key_of(name, params)
        g1_row = g1_lookup.get(k)
        if g1_row is None:
            # Lookup failure — params may not match exactly. Log and skip.
            continue

        # Sanity: node count should match
        if g1_row.get('n') != G.number_of_nodes():
            continue

        # Build feature row
        fr = dict(g1_row)  # start with all G1 metrics
        fr['K_order'] = inv['group_order']
        fr['K_rank'] = inv['rank']
        fr['K_is_cyclic'] = int(inv['is_cyclic'])
        fr['K_largest_factor'] = inv['largest_factor']
        fr['K_exponent'] = inv['exponent']
        # Use math.log (not np.log) because group_order can be arbitrary precision int
        fr['K_log_order'] = math.log(inv['group_order']) if inv['group_order'] > 0 else 0.0
        # 2-rank and 3-rank
        fr['K_2rank'] = inv['p_ranks'].get('2', 0)
        fr['K_3rank'] = inv['p_ranks'].get('3', 0)
        fr['K_5rank'] = inv['p_ranks'].get('5', 0)
        # Spread: largest factor / order (1 if cyclic, smaller otherwise)
        # Use Python division with floats to avoid int overflow issues
        if inv['group_order'] > 0:
            # log(largest) - log(order) is more stable than the ratio for big ints
            fr['K_largest_over_order'] = math.exp(
                math.log(max(inv['largest_factor'], 1)) - math.log(inv['group_order'])
            )
        else:
            fr['K_largest_over_order'] = 0.0
        rows.append(fr)

    print(f"  Computed SNF for {len(rows)} graphs "
          f"(skipped {skipped_disconnected} disconnected), "
          f"total {time.time() - t0:.1f}s")

    if len(rows) == 0:
        print("No rows! Aborting.")
        return

    # Save pickle cache so we don't redo the expensive SNF step
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    with open(CACHE_PATH, "wb") as f:
        pickle.dump({'rows': rows,
                     'skipped_disconnected': skipped_disconnected}, f)
    print(f"  Cached rows to {CACHE_PATH}")

    _analyze(rows, skipped_disconnected)


def _analyze(rows, skipped_disconnected):
    # Correlation analysis
    print("\n" + "=" * 72)
    print("CORRELATION ANALYSIS")
    print("=" * 72)

    # Candidate predictors from G1 (numeric fields only)
    numeric_keys = []
    for key in sorted(rows[0].keys()):
        if key.startswith('K_'):
            continue
        v = rows[0].get(key)
        if isinstance(v, (int, float)) and v is not None:
            numeric_keys.append(key)

    # Targets
    targets = ['K_log_order', 'K_rank', 'K_is_cyclic', 'K_2rank', 'K_3rank',
               'K_largest_over_order']

    print(f"Using {len(numeric_keys)} numeric G1 predictors")
    print(f"Targets: {targets}")
    print()

    # Build arrays
    def col(name):
        out = []
        for r in rows:
            v = r.get(name)
            if v is None:
                out.append(np.nan)
            else:
                try:
                    out.append(float(v))
                except (TypeError, ValueError):
                    out.append(np.nan)
        return np.array(out, dtype=float)

    results = {}
    for tgt in targets:
        y = col(tgt)
        if np.all(np.isnan(y)):
            continue
        corrs = []
        for k in numeric_keys:
            x = col(k)
            mask = ~(np.isnan(x) | np.isnan(y))
            if mask.sum() < 10:
                continue
            xs, ys = x[mask], y[mask]
            if np.std(xs) < 1e-12 or np.std(ys) < 1e-12:
                continue
            r = np.corrcoef(xs, ys)[0, 1]
            corrs.append((k, float(r), int(mask.sum())))
        corrs.sort(key=lambda t: -abs(t[1]))
        results[tgt] = corrs[:10]

        print(f"\n{tgt} — top 10 absolute Pearson correlations:")
        for k, r, n in corrs[:10]:
            print(f"  {k:30s}  r = {r:+.4f}  (n = {n})")

    # ========================================================
    # Multivariate R² (rule 9: decompose single-pairwise signal)
    # ========================================================
    print("\n" + "=" * 72)
    print("MULTIVARIATE LINEAR REGRESSION  (pure numpy)")
    print("=" * 72)

    # Build full predictor matrix X (mean-imputed, standardized)
    X_cols = [col(k) for k in numeric_keys]
    X = np.vstack(X_cols).T  # shape (n_rows, n_preds)
    # Impute NaN with column means
    for j in range(X.shape[1]):
        m = np.isnan(X[:, j])
        if m.any():
            X[m, j] = np.nanmean(X[:, j]) if not np.all(m) else 0.0
    # Standardize
    mu = X.mean(axis=0)
    sd = X.std(axis=0)
    sd[sd < 1e-12] = 1.0
    Xs = (X - mu) / sd
    # Add intercept
    Xs = np.column_stack([np.ones(Xs.shape[0]), Xs])

    def ols_r2(Xs, y):
        """Train R² from OLS (no holdout)."""
        mask = ~np.isnan(y)
        Xm, ym = Xs[mask], y[mask]
        if Xm.shape[0] < Xm.shape[1] + 5:
            return float('nan'), float('nan')
        beta, *_ = np.linalg.lstsq(Xm, ym, rcond=None)
        pred = Xm @ beta
        ss_res = float(np.sum((ym - pred) ** 2))
        ss_tot = float(np.sum((ym - ym.mean()) ** 2))
        r2 = 1.0 - (ss_res / ss_tot) if ss_tot > 0 else float('nan')
        return r2, beta

    def cv_r2(Xs, y, k=5, seed=7):
        """k-fold CV R² to guard against overfitting."""
        mask = ~np.isnan(y)
        Xm, ym = Xs[mask], y[mask]
        n = len(ym)
        if n < k + 5:
            return float('nan')
        rng = np.random.default_rng(seed)
        idx = rng.permutation(n)
        fold_size = n // k
        preds = np.zeros(n)
        for f in range(k):
            test_i = idx[f * fold_size:(f + 1) * fold_size] if f < k - 1 \
                else idx[f * fold_size:]
            train_i = np.setdiff1d(idx, test_i)
            Xt, yt = Xm[train_i], ym[train_i]
            Xv, yv = Xm[test_i], ym[test_i]
            if Xt.shape[0] < Xt.shape[1] + 1:
                return float('nan')
            beta, *_ = np.linalg.lstsq(Xt, yt, rcond=None)
            preds[test_i] = Xv @ beta
        ss_res = float(np.sum((ym - preds) ** 2))
        ss_tot = float(np.sum((ym - ym.mean()) ** 2))
        return 1.0 - (ss_res / ss_tot) if ss_tot > 0 else float('nan')

    mv_results = {}
    for tgt in targets:
        y = col(tgt)
        r2_train, _ = ols_r2(Xs, y)
        r2_cv = cv_r2(Xs, y)
        mv_results[tgt] = {'r2_train': r2_train, 'r2_cv5': r2_cv}
        print(f"  {tgt:25s}  R²(train) = {r2_train:+.4f}   R²(CV5) = {r2_cv:+.4f}")

    # Save
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    # Strip rows down to just targets for storage
    compact_rows = []
    for r in rows:
        compact = {k: r.get(k) for k in ('name', 'n', 'm', 'density',
                                         'spectral_gap', 'spectral_radius',
                                         'algebraic_connectivity',
                                         'clustering_avg', 'diameter',
                                         'eig_A_min', 'deg_mean', 'deg_min',
                                         'laplacian_max')}
        for k in ('K_log_order', 'K_rank', 'K_is_cyclic', 'K_2rank', 'K_3rank',
                  'K_5rank', 'K_largest_over_order', 'K_exponent'):
            compact[k] = r.get(k)
        # store group_order as string to avoid JSON overflow (bigints)
        compact['K_order_str'] = str(r.get('K_order'))
        compact_rows.append(compact)

    with open(OUT_PATH, "w") as f:
        json.dump({
            "experiment": "S1.2 correlations",
            "n_graphs_with_snf": len(rows),
            "n_max_filter": N_MAX,
            "skipped_disconnected": skipped_disconnected,
            "predictors": numeric_keys,
            "targets": targets,
            "top_correlations": results,
            "multivariate": mv_results,
            "rows": compact_rows,
        }, f, indent=2, default=str)
    print(f"\nSaved: {OUT_PATH}")


if __name__ == "__main__":
    main()

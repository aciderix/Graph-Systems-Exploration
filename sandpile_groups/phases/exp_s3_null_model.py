"""
Experiment S1.3 — Null model for SNF rank.

Falsification rule 10: if a random-graph null model with matched basic statistics
(n, m, degree sequence) produces the same distribution of SNF invariants
(rank, is_cyclic, 2-rank, 3-rank) as the real G1 graphs, then any "signal" we
see in the correlation experiment is just reflecting n/m/degree and not the
specific families in G1.

Procedure:
  For each G1 graph G with SNF results (from exp_s2), generate a random graph
  with the SAME degree sequence via the configuration model. Compute its SNF.
  Compare the distribution of (rank, is_cyclic, p-ranks) between G1 and null.

Key tests:
  - Kolmogorov-Smirnov (pure numpy implementation) on each target.
  - Mean / median / fraction comparison.

Interpretation:
  - If null_dist ≈ G1_dist → SNF invariants are determined by degree sequence
    alone → the "novel dimension" claim is trivially wrong.
  - If they differ significantly → SNF reflects structure beyond degrees.
"""

import json
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from S1_smith_normal_form import compute_sandpile_invariants

import networkx as nx
import numpy as np
import flint


HERE = os.path.dirname(os.path.abspath(__file__))
S2_PATH = os.path.join(HERE, "..", "data", "exp_s2_correlations.json")
OUT_PATH = os.path.join(HERE, "..", "data", "exp_s3_null_model.json")


def snf_diag(int_matrix_2d):
    if not int_matrix_2d or not int_matrix_2d[0]:
        return []
    M = flint.fmpz_mat(int_matrix_2d)
    S = M.snf()
    return [abs(int(S[i, i])) for i in range(min(S.nrows(), S.ncols()))]


def graph_snf(G):
    if G.number_of_nodes() == 0 or not nx.is_connected(G):
        return None
    L = nx.laplacian_matrix(G).toarray().astype(int)
    Lr = L[:-1, :-1].tolist()
    diag = snf_diag(Lr)
    return compute_sandpile_invariants(diag)


def random_matched(G, seed):
    """Generate a random graph with the same degree sequence as G.
    Uses configuration model with simple-graph cleanup. Returns the LARGEST
    connected component if disconnected.
    """
    deg = [d for _, d in G.degree()]
    rng = np.random.default_rng(seed)
    # Need an even degree sum
    if sum(deg) % 2 == 1:
        deg[0] += 1
    # Try up to 5 times to get a simple connected graph
    for attempt in range(5):
        H = nx.configuration_model(deg, seed=int(rng.integers(0, 10**9)))
        H = nx.Graph(H)  # remove parallel edges
        H.remove_edges_from(nx.selfloop_edges(H))
        if H.number_of_nodes() == 0:
            continue
        # Largest CC
        cc = max(nx.connected_components(H), key=len)
        H = H.subgraph(cc).copy()
        H = nx.convert_node_labels_to_integers(H)
        if H.number_of_nodes() >= 3:
            return H
    return None


def ks_2samp(a, b):
    """Two-sample Kolmogorov-Smirnov statistic (pure numpy)."""
    a = np.sort(np.asarray(a, dtype=float))
    b = np.sort(np.asarray(b, dtype=float))
    n1, n2 = len(a), len(b)
    if n1 == 0 or n2 == 0:
        return float('nan'), float('nan')
    all_vals = np.sort(np.concatenate([a, b]))
    cdf_a = np.searchsorted(a, all_vals, side='right') / n1
    cdf_b = np.searchsorted(b, all_vals, side='right') / n2
    D = np.max(np.abs(cdf_a - cdf_b))
    # Asymptotic p-value
    en = math.sqrt(n1 * n2 / (n1 + n2))
    p = 2.0 * math.exp(-2.0 * (en * D) ** 2)
    p = min(1.0, max(0.0, p))
    return float(D), float(p)


def main():
    print("=" * 72)
    print("EXPERIMENT S1.3 — Null model for SNF invariants")
    print("=" * 72)

    # Load S2 results to replay exactly the same graphs
    with open(S2_PATH, "r") as f:
        s2 = json.load(f)
    print(f"Loaded S2 data: {s2['n_graphs_with_snf']} graphs")

    # We need the real G1 metric rows w/ SNF added. S2 saved sample_rows (5)
    # — not enough. We'll regenerate the subset using the same pipeline.
    from exp_s2_correlations import generate_g1_subset

    graphs = generate_g1_subset(n_max=s2['n_max_filter'])
    print(f"Regenerated {len(graphs)} graphs")

    real_invs = []
    null_invs = []
    skipped = 0
    # Cap node count to avoid the ~2000-node lobsters that blow up the
    # configuration-model SNF step (run time is dominated by a handful of
    # outliers otherwise).
    N_NULL_MAX = 600
    t0 = time.time()
    for i, (G, name, params) in enumerate(graphs):
        if G.number_of_nodes() > N_NULL_MAX:
            skipped += 1
            continue
        if not nx.is_connected(G):
            skipped += 1
            continue
        inv_r = graph_snf(G)
        if inv_r is None:
            skipped += 1
            continue
        H = random_matched(G, seed=42 * (i + 1))
        if H is None:
            skipped += 1
            continue
        # Also cap the null graph in case config model makes it huge
        if H.number_of_nodes() > N_NULL_MAX:
            skipped += 1
            continue
        inv_n = graph_snf(H)
        if inv_n is None:
            skipped += 1
            continue

        real_invs.append({
            'name': name, 'n': G.number_of_nodes(), 'm': G.number_of_edges(),
            'rank': inv_r['rank'],
            'is_cyclic': int(inv_r['is_cyclic']),
            '2rank': inv_r['p_ranks'].get('2', 0),
            '3rank': inv_r['p_ranks'].get('3', 0),
            'log_order': math.log(max(inv_r['group_order'], 1)),
        })
        null_invs.append({
            'name': name, 'n': H.number_of_nodes(), 'm': H.number_of_edges(),
            'rank': inv_n['rank'],
            'is_cyclic': int(inv_n['is_cyclic']),
            '2rank': inv_n['p_ranks'].get('2', 0),
            '3rank': inv_n['p_ranks'].get('3', 0),
            'log_order': math.log(max(inv_n['group_order'], 1)),
        })

        if (i + 1) % 25 == 0:
            print(f"  [{i+1}/{len(graphs)}] {time.time()-t0:.1f}s", flush=True)

    print(f"\nPairs computed: {len(real_invs)} (skipped {skipped})")
    print(f"Total time: {time.time() - t0:.1f}s")

    # KS tests on each target
    print("\n" + "=" * 72)
    print("KS TESTS (real vs null) — is the distribution shifted?")
    print("=" * 72)
    targets = ['rank', 'is_cyclic', '2rank', '3rank', 'log_order']
    ks_results = {}
    for tgt in targets:
        a = [r[tgt] for r in real_invs]
        b = [r[tgt] for r in null_invs]
        D, p = ks_2samp(a, b)
        m_a, m_b = float(np.mean(a)), float(np.mean(b))
        med_a, med_b = float(np.median(a)), float(np.median(b))
        frac_a_cyclic = sum(1 for r in real_invs if r['is_cyclic']) / len(real_invs)
        frac_b_cyclic = sum(1 for r in null_invs if r['is_cyclic']) / len(null_invs)
        ks_results[tgt] = {
            'D': D, 'p': p,
            'mean_real': m_a, 'mean_null': m_b,
            'median_real': med_a, 'median_null': med_b,
        }
        print(f"\n  {tgt}")
        print(f"    D = {D:.4f}, p = {p:.4g}")
        print(f"    mean:   real = {m_a:.4f},  null = {m_b:.4f}")
        print(f"    median: real = {med_a:.4f},  null = {med_b:.4f}")

    # Cyclic fraction
    frac_a_cyclic = sum(1 for r in real_invs if r['is_cyclic']) / len(real_invs)
    frac_b_cyclic = sum(1 for r in null_invs if r['is_cyclic']) / len(null_invs)
    print(f"\n  fraction cyclic: real = {frac_a_cyclic:.3f},  null = {frac_b_cyclic:.3f}")

    # Per-pair comparison: is K(H) literally the same as K(G)?
    same_rank = sum(1 for r, n in zip(real_invs, null_invs) if r['rank'] == n['rank'])
    same_cyc = sum(1 for r, n in zip(real_invs, null_invs) if r['is_cyclic'] == n['is_cyclic'])
    same_2r = sum(1 for r, n in zip(real_invs, null_invs) if r['2rank'] == n['2rank'])
    print(f"\n  per-pair match rate:")
    print(f"    rank:       {same_rank}/{len(real_invs)} ({100*same_rank/len(real_invs):.1f}%)")
    print(f"    is_cyclic:  {same_cyc}/{len(real_invs)} ({100*same_cyc/len(real_invs):.1f}%)")
    print(f"    2rank:      {same_2r}/{len(real_invs)} ({100*same_2r/len(real_invs):.1f}%)")

    # Save
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump({
            "experiment": "S1.3 null model",
            "n_pairs": len(real_invs),
            "skipped": skipped,
            "ks_results": ks_results,
            "real_summary": {
                "mean_rank": float(np.mean([r['rank'] for r in real_invs])),
                "frac_cyclic": frac_a_cyclic,
            },
            "null_summary": {
                "mean_rank": float(np.mean([r['rank'] for r in null_invs])),
                "frac_cyclic": frac_b_cyclic,
            },
            "per_pair_matches": {
                "rank": same_rank,
                "is_cyclic": same_cyc,
                "2rank": same_2r,
            },
            "real": real_invs,
            "null": null_invs,
        }, f, indent=2, default=str)
    print(f"\nSaved: {OUT_PATH}")


if __name__ == "__main__":
    main()

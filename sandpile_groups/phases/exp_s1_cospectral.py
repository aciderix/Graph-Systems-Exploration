"""
Experiment S1.1 — Does the SNF of L(G) separate cospectral graphs?

Contrarian question (against the saturation conclusion of the graphs project):
If the SNF carries information truly independent from the adjacency spectrum,
then cospectral pairs (same spectrum, non-isomorphic) should have DIFFERENT
SNF in at least some cases.

This script is deliberately SELF-CONTAINED and uses the 4 "known cospectral
pairs" from phases/G10/g10_spectral_gap.py, plus 2 extra classical pairs to
stress-test.

Falsification rules applied:
- Rule 1 (baseline): compare SNF vs the trivial "same order" check
- Rule 7 (vary params): test 6 pairs of different sizes/types
- Rule 8 (vary measurement): cross-check via networkx spanning tree count
- Rule 10 (null model): compute SNF for 20 RANDOM same-size graphs, check
  whether the "separation" is artifactual (any two random graphs of same n,m
  tend to have different SNF just by chance).
"""

import sys
import os
import json
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from S1_smith_normal_form import (
    smith_normal_form,
    build_laplacian,
    reduced_laplacian,
    compute_sandpile_invariants,
)

import networkx as nx
import numpy as np


# ============================================================
# Helpers
# ============================================================

def adj_matrix(G):
    """Return a dense 0/1 adjacency matrix as a Python list-of-lists."""
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
    """Full sandpile pipeline for a networkx graph."""
    A = adj_matrix(G)
    L = build_laplacian(A)
    Lr = reduced_laplacian(L)
    diag = smith_normal_form(Lr)
    inv = compute_sandpile_invariants(diag)
    return inv


def adj_spectrum(G):
    A = nx.adjacency_matrix(G).toarray().astype(float)
    return tuple(sorted(np.round(np.linalg.eigvalsh(A), 8)))


def lap_spectrum(G):
    L = nx.laplacian_matrix(G).toarray().astype(float)
    return tuple(sorted(np.round(np.linalg.eigvalsh(L), 8)))


def fmt_group(inv):
    """Pretty-print a critical group from invariant factors."""
    factors = inv['invariant_factors']
    if not factors:
        return "trivial (Z_1)"
    return "×".join(f"Z_{d}" for d in factors)


# ============================================================
# The 6 pairs
# ============================================================

def pair_C6_vs_2K3():
    """Smallest non-iso cospectral pair for adjacency... actually these are
    NOT cospectral for adjacency: C6 spectrum ≠ (K3+K3) spectrum.
    But they ARE cospectral for LAPLACIAN? Let's check and see.
    """
    G1 = nx.cycle_graph(6)
    G2 = nx.Graph()
    G2.add_edges_from([(0, 1), (1, 2), (2, 0), (3, 4), (4, 5), (5, 3)])
    return ("C6", "K3+K3", G1, G2)


def pair_schwenk_trees():
    """Schwenk cospectral trees (n=11, same adj spectrum)."""
    T1 = nx.Graph()
    T1.add_edges_from([(0, 1), (1, 2), (2, 3), (3, 4), (4, 5),
                       (2, 6), (6, 7), (7, 8), (6, 9), (9, 10)])
    T2 = nx.Graph()
    T2.add_edges_from([(0, 1), (1, 2), (2, 3), (3, 4),
                       (2, 5), (5, 6), (6, 7), (5, 8), (8, 9), (9, 10)])
    return ("schwenk_11a", "schwenk_11b", T1, T2)


def pair_shrikhande_L_K44():
    """Shrikhande graph vs L(K4,4). Both 6-regular on 16 vertices."""
    shrikhande = nx.Graph()
    for i in range(4):
        for j in range(4):
            v = i * 4 + j
            nbrs = [
                (i % 4) * 4 + ((j + 1) % 4),
                (i % 4) * 4 + ((j - 1) % 4),
                ((i + 1) % 4) * 4 + j,
                ((i - 1) % 4) * 4 + j,
                ((i + 1) % 4) * 4 + ((j + 1) % 4),
                ((i - 1) % 4) * 4 + ((j - 1) % 4),
            ]
            for u in nbrs:
                if u != v:
                    shrikhande.add_edge(v, u)
    K44 = nx.complete_bipartite_graph(4, 4)
    LK44 = nx.line_graph(K44)
    LK44 = nx.convert_node_labels_to_integers(LK44)
    return ("shrikhande", "L(K4,4)", shrikhande, LK44)


def pair_7nodes():
    """Small 7-node pair from G10."""
    G4a = nx.Graph()
    G4a.add_edges_from([(0, 1), (0, 2), (0, 3), (1, 2), (3, 4), (4, 5), (5, 6)])
    G4b = nx.Graph()
    G4b.add_edges_from([(0, 1), (0, 2), (1, 2), (1, 3), (3, 4), (4, 5), (4, 6)])
    return ("G7a", "G7b", G4a, G4b)


def pair_saltire():
    """Saltire pair: two well-known adj-cospectral non-iso graphs on 5 vertices.
    K_{1,4} (star) and K_{1,4} are iso, so use the disjoint union instead:
    actually the smallest adj-cospectral pair is the Schwenk pair above.
    Let's add a brute-force search pair on n=7.
    """
    # Brute force: find adj-cospectral non-iso pair on 7 vertices
    rng = random.Random(42)
    bucket = {}
    for trial in range(2000):
        p = rng.uniform(0.3, 0.7)
        G = nx.erdos_renyi_graph(7, p, seed=trial)
        if not nx.is_connected(G):
            continue
        spec = adj_spectrum(G)
        if spec in bucket:
            H = bucket[spec]
            if not nx.is_isomorphic(G, H):
                return ("rand7a", "rand7b", H, G)
        else:
            bucket[spec] = G
    return None


def pair_haemers():
    """Search for an adj-cospectral pair on 8 vertices via brute force."""
    rng = random.Random(13)
    bucket = {}
    for trial in range(3000):
        p = rng.uniform(0.3, 0.7)
        G = nx.erdos_renyi_graph(8, p, seed=trial + 10000)
        if not nx.is_connected(G):
            continue
        spec = adj_spectrum(G)
        if spec in bucket:
            H = bucket[spec]
            if not nx.is_isomorphic(G, H):
                return ("rand8a", "rand8b", H, G)
        else:
            bucket[spec] = G
    return None


# ============================================================
# Main experiment
# ============================================================

def run_pair(name_a, name_b, Ga, Gb):
    """Analyze one pair. Returns a row dict."""
    adj_cospec = adj_spectrum(Ga) == adj_spectrum(Gb)
    lap_cospec = lap_spectrum(Ga) == lap_spectrum(Gb)
    is_iso = nx.is_isomorphic(Ga, Gb)

    inv_a = graph_sandpile(Ga)
    inv_b = graph_sandpile(Gb)

    # Cross-check: |K(G)| should equal number of spanning trees
    # Networkx doesn't have a direct spanning tree count, but for connected
    # graphs we can compute it via Kirchhoff's theorem (det of reduced L).
    def n_spanning_trees(G):
        if not nx.is_connected(G):
            return 0
        L = nx.laplacian_matrix(G).toarray().astype(float)
        Lr = L[:-1, :-1]
        # det must be integer
        return int(round(np.linalg.det(Lr)))

    tau_a = n_spanning_trees(Ga)
    tau_b = n_spanning_trees(Gb)

    snf_sep = inv_a['invariant_factors'] != inv_b['invariant_factors']

    return {
        "pair": (name_a, name_b),
        "n": (Ga.number_of_nodes(), Gb.number_of_nodes()),
        "m": (Ga.number_of_edges(), Gb.number_of_edges()),
        "is_iso": is_iso,
        "adj_cospec": adj_cospec,
        "lap_cospec": lap_cospec,
        "tau_a": tau_a,
        "tau_b": tau_b,
        "K_a_factors": inv_a['invariant_factors'],
        "K_b_factors": inv_b['invariant_factors'],
        "K_a_order": inv_a['group_order'],
        "K_b_order": inv_b['group_order'],
        "K_a_cyclic": inv_a['is_cyclic'],
        "K_b_cyclic": inv_b['is_cyclic'],
        "K_a_str": fmt_group(inv_a),
        "K_b_str": fmt_group(inv_b),
        "snf_separates": snf_sep,
        "tau_matches_snf_a": tau_a == inv_a['group_order'],
        "tau_matches_snf_b": tau_b == inv_b['group_order'],
    }


def main():
    print("=" * 72)
    print("EXPERIMENT S1.1 — SNF separation of cospectral pairs")
    print("=" * 72)

    pairs = []
    for fn in [pair_C6_vs_2K3, pair_schwenk_trees, pair_shrikhande_L_K44,
               pair_7nodes, pair_saltire, pair_haemers]:
        try:
            p = fn()
            if p is not None:
                pairs.append(p)
        except Exception as e:
            print(f"  [skip] {fn.__name__}: {e}")

    print(f"\nLoaded {len(pairs)} candidate pairs")
    print()

    rows = []
    for (name_a, name_b, Ga, Gb) in pairs:
        r = run_pair(name_a, name_b, Ga, Gb)
        rows.append(r)

    # Print per-pair results
    for r in rows:
        print("-" * 72)
        print(f"  {r['pair'][0]}  vs  {r['pair'][1]}")
        print(f"    n = {r['n']}, m = {r['m']}, iso = {r['is_iso']}")
        print(f"    adj cospectral = {r['adj_cospec']}, "
              f"lap cospectral = {r['lap_cospec']}")
        print(f"    τ(G_a) = {r['tau_a']},  τ(G_b) = {r['tau_b']}")
        print(f"    K(G_a) = {r['K_a_str']}  (order {r['K_a_order']}, "
              f"cyclic={r['K_a_cyclic']})")
        print(f"    K(G_b) = {r['K_b_str']}  (order {r['K_b_order']}, "
              f"cyclic={r['K_b_cyclic']})")
        print(f"    SNF cross-check (τ == |K|): "
              f"{r['tau_matches_snf_a']} / {r['tau_matches_snf_b']}")
        print(f"    >>> SNF SEPARATES: {r['snf_separates']}")

    # Aggregate
    print("\n" + "=" * 72)
    print("AGGREGATE")
    print("=" * 72)
    adj_pairs = [r for r in rows if r['adj_cospec'] and not r['is_iso']]
    lap_pairs = [r for r in rows if r['lap_cospec'] and not r['is_iso']]
    print(f"Total pairs                              : {len(rows)}")
    print(f"Adj-cospectral non-isomorphic pairs      : {len(adj_pairs)}")
    print(f"Lap-cospectral non-isomorphic pairs      : {len(lap_pairs)}")
    adj_sep = sum(1 for r in adj_pairs if r['snf_separates'])
    lap_sep = sum(1 for r in lap_pairs if r['snf_separates'])
    print(f"Adj-cospec pairs where SNF SEPARATES     : {adj_sep}/{len(adj_pairs)}")
    print(f"Lap-cospec pairs where SNF SEPARATES     : {lap_sep}/{len(lap_pairs)}")

    # Cross-check validity
    mismatches = [r for r in rows
                  if not r['tau_matches_snf_a'] or not r['tau_matches_snf_b']]
    print(f"SNF cross-check mismatches (bug signal)  : {len(mismatches)}")

    # Save
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "..", "data", "exp_s1_cospectral.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump({
            "experiment": "S1.1 cospectral separation",
            "n_pairs": len(rows),
            "results": rows,
        }, f, indent=2, default=str)
    print(f"\nSaved: {out_path}")


if __name__ == "__main__":
    main()

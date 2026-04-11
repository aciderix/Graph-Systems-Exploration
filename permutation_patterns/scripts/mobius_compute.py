#!/usr/bin/env python3
"""
Compute the Möbius function mu(1, pi) on the permutation containment poset
for all permutations of length up to N.

Convention:
  - Poset element: a permutation tuple pi with entries 1..|pi|.
  - Canonical form: a pattern is stored as a tuple of ranks 1..k.
  - Order: tau <= pi iff tau occurs (in the pattern-sense) inside pi.
  - Bottom: (1,) in S_1.

Recurrence:
  mu((1,), (1,)) = 1
  mu((1,), pi)   = - sum_{tau in proper_patterns(pi)} mu((1,), tau)

Output: writes a JSON file with:
  - counts by n
  - histogram of mu values by n
  - extrema: perms achieving max |mu| at each n
"""

import json
import sys
from pathlib import Path
from itertools import permutations, combinations
from collections import Counter, defaultdict

OUT = Path(__file__).resolve().parent.parent / "data" / "mobius.json"

MU = {(1,): 1}  # memo


def reduce_pattern(tup):
    """Replace entries by ranks 1..k."""
    sorted_vals = sorted(tup)
    idx = {v: i + 1 for i, v in enumerate(sorted_vals)}
    return tuple(idx[v] for v in tup)


def proper_patterns(pi):
    """Set of all canonical patterns of pi with length strictly less than |pi|."""
    n = len(pi)
    pats = set()
    # Length (n-1): remove one position
    for i in range(n):
        sub = pi[:i] + pi[i+1:]
        pats.add(reduce_pattern(sub))
    # Further patterns are obtained as patterns of (n-1)-patterns, recursively.
    # But for computing mu via the direct formula, we need the FULL set.
    # Use combinations for k = 1..n-1
    for k in range(1, n):
        for idxs in combinations(range(n), k):
            sub = tuple(pi[i] for i in idxs)
            pats.add(reduce_pattern(sub))
    return pats


def compute_mu(pi):
    if pi in MU:
        return MU[pi]
    pats = proper_patterns(pi)
    val = 0
    for tau in pats:
        if tau in MU:
            val -= MU[tau]
        else:
            val -= compute_mu(tau)
    MU[pi] = val
    return val


def main():
    N_MAX = int(sys.argv[1]) if len(sys.argv) > 1 else 7

    by_n_mu_hist = {}        # n -> Counter of mu values
    by_n_extrema = {}         # n -> list of (pi, mu) with |mu| = max
    by_n_count = {}

    import time
    for n in range(1, N_MAX + 1):
        t0 = time.time()
        mu_vals = []
        for pi in permutations(range(1, n + 1)):
            m = compute_mu(pi)
            mu_vals.append((pi, m))
        t1 = time.time()

        hist = Counter(m for _, m in mu_vals)
        max_abs = max(abs(m) for _, m in mu_vals)
        extrema = [(list(p), m) for p, m in mu_vals if abs(m) == max_abs]

        by_n_count[n] = len(mu_vals)
        by_n_mu_hist[n] = dict(hist)
        by_n_extrema[n] = {"max_abs": max_abs, "count": len(extrema),
                            "examples": extrema[:20]}

        # print a concise summary per n
        top = sorted(hist.items(), key=lambda kv: -kv[1])[:12]
        print(f"n={n:<2d}  |Sn|={len(mu_vals):<7d}  "
              f"max|mu|={max_abs:<4d}  #extrema={len(extrema):<5d}  "
              f"time={t1 - t0:.2f}s")
        print(f"   hist (top): {top}")

    # Write full data
    out = {
        "n_max": N_MAX,
        "count_by_n": by_n_count,
        "histogram_by_n": {str(k): v for k, v in by_n_mu_hist.items()},
        "extrema_by_n": {str(k): v for k, v in by_n_extrema.items()},
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nSaved to {OUT}")


if __name__ == "__main__":
    main()

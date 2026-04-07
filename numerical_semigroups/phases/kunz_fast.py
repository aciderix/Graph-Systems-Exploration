"""
Fast Kunz enumerator for numerical semigroups of fixed multiplicity m.

Enumerates all integer points of the Kunz polyhedron P_m:
    k_i >= 1 for i=1..m-1
    k_r <= k_a + k_b           for a+b = r  in [1, m-1]     (no carry)
    k_r <= k_a + k_b + 1       for a+b = r + m              (carry)

Each valid tuple (k_1,...,k_{m-1}) corresponds bijectively to a numerical
semigroup S with multiplicity m, via the Apery set w_i = k_i*m + i.

The enumeration is a backtracking assignment k_1, k_2, ..., k_{m-1} with
forward-checking of the "no carry" constraints and lazy verification of
"carry" constraints at the leaves. Pruning options:
    - K_max: hard cap on k* (controls the genus range)
    - W_target: skip leaves with W(S) >= W_target (for min-hunting)
    - d_range: keep only defects in [d_min, d_max]

Usage (CLI):
    python kunz_fast.py m K_max [--d-min D] [--d-max D] [--w-max W] [--out FILE]

Compared to the tree-by-gap enumerator in N1_enumerate.py, this approach:
    - is organized by (m, d) directly (the natural axes for the Wilf frontier)
    - is unbounded in genus (bounded by k*, i.e. conductor <= K_max * m)
    - allows slicing by defect without enumerating all smaller-m semigroups.

For m=18, K_max=3: ~1M tuples in seconds.
For m=22, K_max=3: heavier but tractable (~minutes).

This is intentionally pure-Python / numpy — the hot path is the per-leaf
invariant computation, which is vectorized via numpy.
"""

import argparse
import json
import sys
import time
from typing import Callable, Iterator, Optional

import numpy as np


def invariants_from_k(k: np.ndarray, m: int) -> dict:
    """Compute (d, L, k*, r*, F, c, W, e) from a Kunz tuple k of length m-1.

    k[0] = k_1, k[1] = k_2, ..., k[m-2] = k_{m-1}.
    """
    k_star = int(k.max())
    # r* is the LARGEST residue achieving k*; residues are 1..m-1
    r_star = int(np.flatnonzero(k == k_star).max()) + 1  # +1 because k[0]=k_1

    # delta_i = k* - k_i if i <= r*, else max(0, k*-1-k_i)
    idx = np.arange(1, m)  # residues 1..m-1
    delta_le = k_star - k
    delta_gt = np.maximum(0, k_star - 1 - k)
    delta = np.where(idx <= r_star, delta_le, delta_gt)
    L = k_star + int(delta.sum())

    F = (k_star - 1) * m + r_star
    c = F + 1

    # Defect: number of decomposable residues
    # r is decomposable iff EXISTS (a,b) with a+b ≡ r (mod m) and
    # k_a + k_b + eps <= k_r.
    # Compute via pairwise sums.
    # Index convention: k[i-1] is k_i for i in 1..m-1.
    d = 0
    for r in range(1, m):
        kr = k[r - 1]
        decomposable = False
        for a in range(1, m):
            b_nocarry = r - a
            b_carry = r + m - a
            if 1 <= b_nocarry <= m - 1:
                if k[a - 1] + k[b_nocarry - 1] <= kr:
                    decomposable = True
                    break
            if 1 <= b_carry <= m - 1:
                if k[a - 1] + k[b_carry - 1] + 1 <= kr:
                    decomposable = True
                    break
        if decomposable:
            d += 1

    e = m - d  # embedding dimension
    W = e * L - c

    return {
        "m": m,
        "k": k.tolist(),
        "d": d,
        "e": e,
        "k_star": k_star,
        "r_star": r_star,
        "L": L,
        "F": F,
        "c": c,
        "W": W,
    }


def enumerate_kunz(
    m: int,
    K_max: int,
    on_leaf: Callable[[np.ndarray], None],
    stats: dict,
) -> None:
    """Backtrack over all valid Kunz tuples for multiplicity m with k* <= K_max.

    Forward-checks no-carry constraints; carry constraints are verified at the
    leaf (before invoking on_leaf).
    """
    k = np.zeros(m - 1, dtype=np.int32)  # k[i-1] = k_i

    def verify_carry() -> bool:
        # k_r <= k_a + k_b + 1 for a+b = r+m, all a,b in [1, m-1]
        for r in range(1, m):
            kr = k[r - 1]
            for a in range(max(1, r + 1), m):  # a > r so that b=r+m-a<m
                b = r + m - a
                if 1 <= b <= m - 1:
                    if kr > k[a - 1] + k[b - 1] + 1:
                        return False
        return True

    def rec(r: int) -> None:
        if r == m:
            stats["leaves_raw"] += 1
            if verify_carry():
                stats["leaves_valid"] += 1
                on_leaf(k)
            return
        # Upper bound for k_r from no-carry constraints: k_r <= k_a + k_{r-a}
        # for a=1..r-1, a<=r-a (to avoid double work) — but min over all.
        ub = K_max
        for a in range(1, r):
            b = r - a
            v = int(k[a - 1] + k[b - 1])
            if v < ub:
                ub = v
        if ub < 1:
            return
        for val in range(1, ub + 1):
            k[r - 1] = val
            rec(r + 1)

    # Increase recursion limit if needed
    sys.setrecursionlimit(max(sys.getrecursionlimit(), 10000))
    rec(1)


def run(
    m: int,
    K_max: int,
    d_min: Optional[int] = None,
    d_max: Optional[int] = None,
    w_max: Optional[int] = None,
    out_path: Optional[str] = None,
    summary_only: bool = False,
) -> dict:
    t0 = time.time()
    stats = {"leaves_raw": 0, "leaves_valid": 0, "kept": 0}

    # Accumulators per defect: min W, argmin tuple, count
    per_d: dict[int, dict] = {}
    kept_records: list[dict] = []

    def on_leaf(k: np.ndarray) -> None:
        inv = invariants_from_k(k, m)
        d = inv["d"]
        if d_min is not None and d < d_min:
            return
        if d_max is not None and d > d_max:
            return
        if w_max is not None and inv["W"] > w_max:
            return
        stats["kept"] += 1

        slot = per_d.setdefault(
            d, {"W_min": None, "argmin": None, "count": 0, "W_neg_count": 0}
        )
        slot["count"] += 1
        if inv["W"] < 0:
            slot["W_neg_count"] += 1
        if slot["W_min"] is None or inv["W"] < slot["W_min"]:
            slot["W_min"] = inv["W"]
            slot["argmin"] = inv.copy()

        if not summary_only:
            kept_records.append(inv)

    enumerate_kunz(m, K_max, on_leaf, stats)

    elapsed = time.time() - t0

    summary = {
        "m": m,
        "K_max": K_max,
        "d_min": d_min,
        "d_max": d_max,
        "w_max": w_max,
        "elapsed_sec": round(elapsed, 3),
        "leaves_raw": stats["leaves_raw"],
        "leaves_valid": stats["leaves_valid"],
        "leaves_kept": stats["kept"],
        "per_defect": {
            str(d): {
                "count": slot["count"],
                "W_min": slot["W_min"],
                "W_neg_count": slot["W_neg_count"],
                "argmin_k": slot["argmin"]["k"] if slot["argmin"] else None,
                "argmin_L": slot["argmin"]["L"] if slot["argmin"] else None,
                "argmin_c": slot["argmin"]["c"] if slot["argmin"] else None,
            }
            for d, slot in sorted(per_d.items())
        },
    }

    if out_path:
        payload = {"summary": summary}
        if not summary_only:
            payload["records"] = kept_records
        with open(out_path, "w") as f:
            json.dump(payload, f, indent=1)

    return summary


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("m", type=int)
    p.add_argument("K_max", type=int)
    p.add_argument("--d-min", type=int, default=None)
    p.add_argument("--d-max", type=int, default=None)
    p.add_argument("--w-max", type=int, default=None)
    p.add_argument("--out", type=str, default=None)
    p.add_argument("--summary-only", action="store_true")
    args = p.parse_args()

    summary = run(
        m=args.m,
        K_max=args.K_max,
        d_min=args.d_min,
        d_max=args.d_max,
        w_max=args.w_max,
        out_path=args.out,
        summary_only=args.summary_only,
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

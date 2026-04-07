"""
Internal cross-check (rule 8: vary the measurement method).

Loads numerical_semigroups/data/n1_results_*.json (where each record was
computed by N1_enumerate.py via the gap-set representation), reconstructs
each semigroup from its minimal generators using Kunz coordinates, and
recomputes (m, e, F, c, g, t, L, W) via the C extension in kunz_fast.

Two completely independent code paths:
    Path A (N1):     gap_set -> sorted gaps -> brute-force invariant loops
    Path B (kunz):   generators -> Apery set mod m -> Kunz tuple -> C kernel

Any mismatch is a bug in one of the two paths.

Usage:
    python kunz_cross_check.py --input ../data/n1_results_g20.json --sample 1000
"""

import argparse
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from kunz_fast import invariants_from_k, _C_LIB


def kunz_from_generators(gens: list[int]) -> tuple[int, list[int]]:
    """From a generating set, build the Apery set with respect to the
    multiplicity m=min(gens) and return the Kunz tuple (k_1,...,k_{m-1}).

    Standard BFS: enumerate elements of S up to a generous bound, then
    extract w_i = min{s in S : s ≡ i mod m} for i=1..m-1.
    """
    m = min(gens)
    # An upper bound on the largest Apery element: m * max(2, max(gens)).
    # Safer: m * (max(gens) + 1) covers all w_i since w_i <= m + (m-1)*max_gen.
    # We use a comfortable bound and densify by BFS.
    bound = m * (max(gens) + 2) + 50
    in_S = [False] * (bound + 1)
    in_S[0] = True
    # Iteratively close under "+ each generator".
    changed = True
    while changed:
        changed = False
        for i in range(bound + 1):
            if not in_S[i]:
                continue
            for g in gens:
                j = i + g
                if j <= bound and not in_S[j]:
                    in_S[j] = True
                    changed = True
    # Extract Apery wrt m
    apery = [None] * m
    apery[0] = 0
    for s in range(bound + 1):
        if in_S[s] and s > 0:
            r = s % m
            if apery[r] is None:
                apery[r] = s
        if all(a is not None for a in apery):
            break
    if any(a is None for a in apery):
        return m, []  # bound too small
    k = [(apery[i] - i) // m for i in range(1, m)]
    return m, k


def cross_check(records: list[dict], sample_n: int, seed: int) -> dict:
    rng = random.Random(seed)
    n = len(records)
    indices = rng.sample(range(n), min(sample_n, n))
    mismatches = []
    bound_failures = 0
    checked = 0

    for idx in indices:
        rec = records[idx]
        gens = rec.get("generators")
        if not gens:
            continue
        m, k = kunz_from_generators(gens)
        if not k:
            bound_failures += 1
            continue
        checked += 1
        inv = invariants_from_k(k, m)
        # Compare against N1's stored invariants
        diffs = []
        if inv["m"] != rec["multiplicity"]:
            diffs.append(("m", inv["m"], rec["multiplicity"]))
        if inv["e"] != rec["embedding_dimension"]:
            diffs.append(("e", inv["e"], rec["embedding_dimension"]))
        if inv["F"] != rec["frobenius"]:
            diffs.append(("F", inv["F"], rec["frobenius"]))
        if inv["c"] != rec["conductor"]:
            diffs.append(("c", inv["c"], rec["conductor"]))
        if inv["L"] != rec["left_elements"]:
            diffs.append(("L", inv["L"], rec["left_elements"]))
        if inv["W"] != rec["wilf_number"]:
            diffs.append(("W", inv["W"], rec["wilf_number"]))
        if diffs:
            mismatches.append({"idx": idx, "gens": gens, "diffs": diffs,
                               "kunz": inv, "n1": rec})

    return {
        "sample_size": len(indices),
        "checked": checked,
        "bound_failures": bound_failures,
        "mismatches": len(mismatches),
        "mismatch_examples": mismatches[:10],
        "c_extension_active": _C_LIB is not None,
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--sample", type=int, default=1000)
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()

    with open(args.input) as f:
        records = json.load(f)
    if isinstance(records, dict):
        records = records.get("records") or records.get("semigroups") or []
    print(f"Loaded {len(records)} records from {args.input}")

    report = cross_check(records, args.sample, args.seed)
    print(json.dumps(report, indent=2))

    if report["mismatches"] == 0:
        print("\n✅ All checked semigroups agree on the two independent code paths.")
        sys.exit(0)
    else:
        print(f"\n🚨 {report['mismatches']} MISMATCH(es). Investigate.")
        sys.exit(1)


if __name__ == "__main__":
    main()

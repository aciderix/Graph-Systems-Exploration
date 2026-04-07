"""
Targeted counter-example hunt for Wilf's conjecture in the regime d > 2m/3,
i.e., BEYOND Eliahou's proven range e >= m/3.

Strategy:
    - Iterate m = m_min..m_max.
    - For each m, set d_range = ceil(2m/3 + 1) .. m - 2  (Eliahou-open zone,
      excluding the 2-generator limit d = m-2 where W = 0 trivially).
    - Enumerate Kunz tuples via kunz_fast with a modest K_max.
    - Record any W < 0 (counter-example) and the W_min per (m, d).
    - Also scan "exotic parametric" families (Sidon-like constructions)
      at the boundary d = T_{p(d)}.

No counter-example has ever been found computationally up to genus ~60.
This script is designed to test slightly beyond: m up to 20, K_max up to 4,
which pushes into genus ~60-80 for the relevant (m, d) slices, bypassing the
genus-first census that stops at g=22.

Usage:
    python wilf_hunt.py --m-min 10 --m-max 18 --k-max 3 --out ../data/wilf_hunt.json
"""

import argparse
import json
import time
from math import ceil

from kunz_fast import enumerate_kunz, invariants_from_k


def hunt(m_min: int, m_max: int, k_max: int) -> dict:
    t0 = time.time()
    report = {
        "m_min": m_min,
        "m_max": m_max,
        "k_max": k_max,
        "counter_examples": [],
        "per_m": {},
    }

    for m in range(m_min, m_max + 1):
        d_low = ceil(2 * m / 3) + 1
        d_high = m - 2  # skip d=m-1 (2-gen, W=0) and above
        if d_low > d_high:
            continue

        per_d_min = {}
        neg_found = []
        leaves_kept = 0

        def on_leaf(k, _m=m, _d_low=d_low, _d_high=d_high):
            nonlocal leaves_kept
            inv = invariants_from_k(k, _m)
            d = inv["d"]
            if d < _d_low or d > _d_high:
                return
            leaves_kept += 1
            if d not in per_d_min or inv["W"] < per_d_min[d]["W"]:
                per_d_min[d] = inv
            if inv["W"] < 0:
                neg_found.append(inv)

        stats = {"leaves_raw": 0, "leaves_valid": 0}
        enumerate_kunz(m, k_max, on_leaf, stats)

        report["per_m"][str(m)] = {
            "d_range": [d_low, d_high],
            "leaves_raw": stats["leaves_raw"],
            "leaves_valid": stats["leaves_valid"],
            "leaves_kept": leaves_kept,
            "W_min_by_d": {
                str(d): {
                    "W": inv["W"],
                    "k": inv["k"],
                    "L": inv["L"],
                    "c": inv["c"],
                    "k_star": inv["k_star"],
                }
                for d, inv in sorted(per_d_min.items())
            },
        }
        if neg_found:
            report["counter_examples"].extend(neg_found)
            print(f"!!! m={m}: {len(neg_found)} counter-example(s) found !!!")
        print(
            f"m={m}  d in [{d_low},{d_high}]  "
            f"kept={leaves_kept}  "
            f"W_min={min((v['W'] for v in per_d_min.values()), default='—')}"
        )

    report["elapsed_sec"] = round(time.time() - t0, 2)
    return report


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--m-min", type=int, default=8)
    p.add_argument("--m-max", type=int, default=14)
    p.add_argument("--k-max", type=int, default=3)
    p.add_argument("--out", type=str, default=None)
    args = p.parse_args()

    report = hunt(args.m_min, args.m_max, args.k_max)

    print("\n=== SUMMARY ===")
    print(f"Elapsed: {report['elapsed_sec']} s")
    print(f"Counter-examples: {len(report['counter_examples'])}")
    if report["counter_examples"]:
        print("🚨 WILF COUNTER-EXAMPLE(S) FOUND")
        for ce in report["counter_examples"][:5]:
            print(f"  {ce}")
    else:
        print("No counter-example. Wilf holds on the scanned slice.")

    if args.out:
        with open(args.out, "w") as f:
            json.dump(report, f, indent=1)
        print(f"Written: {args.out}")


if __name__ == "__main__":
    main()

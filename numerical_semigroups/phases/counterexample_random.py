#!/usr/bin/env python3
"""
Random / heuristic counterexample search at HIGH depth (k* up to 10+).

The exhaustive enumeration becomes intractable for large m and k*, but
counterexamples to k*-saturation or the unified conjecture could hide
in deep semigroups. This script samples random valid Kunz tuples and
checks all claims.

Strategies:
  1. Random fill: assign k_i uniformly in [1, K_max], reject invalid
  2. Biased low-Wilf: bias towards high levels (large k_i) to minimize W
  3. Structured adversarial: try to construct semigroups that violate
     specific claims (e.g., high d with low L)

Usage:
    python counterexample_random.py [--m-min M] [--m-max M] [--k-max K]
                                    [--samples N] [--seed S]
"""

import argparse
import math
import os
import random
import sys
import time

# Reuse the C kernel from counterexample_hunt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from counterexample_hunt import (
    load_c_lib, invariants_c, detailed_analysis,
    W_min_predicted, p_of_d, L_of_d, ALL_CHECKS, _run_all_checks
)


def is_valid_kunz(k, m):
    """Check if a Kunz tuple satisfies all constraints."""
    n = m - 1
    # no-carry: k_r <= k_a + k_b for a+b=r, 1<=a,b<=n
    for r in range(1, m):
        kr = k[r - 1]
        for a in range(1, r):
            b = r - a
            if 1 <= b <= n:
                if kr > k[a - 1] + k[b - 1]:
                    return False
    # carry: k_r <= k_a + k_b + 1 for a+b=r+m, 1<=a,b<=n
    for r in range(1, m):
        kr = k[r - 1]
        for a in range(r + 1, m):
            b = r + m - a
            if 1 <= b <= n:
                if kr > k[a - 1] + k[b - 1] + 1:
                    return False
    return True


def random_valid_kunz(m, k_max, max_attempts=10000):
    """Generate a random valid Kunz tuple by sequential assignment with
    constraint propagation."""
    n = m - 1
    k = [0] * n

    for attempt in range(max_attempts):
        valid = True
        for pos in range(1, m):
            # Upper bound from no-carry constraints
            ub = k_max
            for a in range(1, pos):
                b = pos - a
                if 1 <= b <= n:
                    ub = min(ub, k[a - 1] + k[b - 1])
            if ub < 1:
                valid = False
                break
            k[pos - 1] = random.randint(1, ub)

        if not valid:
            continue

        # Check carry constraints
        ok = True
        for r in range(1, m):
            kr = k[r - 1]
            for a in range(r + 1, m):
                b = r + m - a
                if 1 <= b <= n:
                    if kr > k[a - 1] + k[b - 1] + 1:
                        ok = False
                        break
            if not ok:
                break

        if ok:
            return k

    return None


def biased_high_level_kunz(m, k_max, max_attempts=10000):
    """Generate a random Kunz tuple biased towards high levels (to minimize W).

    Semigroups with high levels and low defect tend to have lower Wilf numbers.
    We bias by choosing k_i close to its upper bound.
    """
    n = m - 1
    k = [0] * n

    for attempt in range(max_attempts):
        valid = True
        for pos in range(1, m):
            ub = k_max
            for a in range(1, pos):
                b = pos - a
                if 1 <= b <= n:
                    ub = min(ub, k[a - 1] + k[b - 1])
            if ub < 1:
                valid = False
                break
            # Bias: pick from top third of range
            lb = max(1, ub - max(1, ub // 3))
            k[pos - 1] = random.randint(lb, ub)

        if not valid:
            continue

        ok = True
        for r in range(1, m):
            kr = k[r - 1]
            for a in range(r + 1, m):
                b = r + m - a
                if 1 <= b <= n:
                    if kr > k[a - 1] + k[b - 1] + 1:
                        ok = False
                        break
            if not ok:
                break

        if ok:
            return k

    return None


def adversarial_high_defect(m, k_max, target_d, max_attempts=50000):
    """Try to construct a Kunz tuple with high defect and low W.

    Strategy: place some residues at level 1 (forcing them to be primitive),
    and arrange high-level residues to be decomposable.
    We want many decomposable residues (high d) with few left elements (low L).
    """
    n = m - 1
    pd = p_of_d(target_d)
    best = None
    best_W = float('inf')

    for attempt in range(max_attempts):
        k = [0] * n
        # Choose p random source residues at level 1
        p_sources = min(pd + random.randint(0, 2), n)
        sources = sorted(random.sample(range(n), p_sources))
        for s in sources:
            k[s] = 1

        # Set remaining residues at level 2 (low k* = 2 regime)
        for i in range(n):
            if k[i] == 0:
                k[i] = 2

        # Check validity
        if not is_valid_kunz(k, m):
            # Try to repair: increase violated entries
            repaired = True
            for _ in range(10):
                changed = False
                for r in range(1, m):
                    kr = k[r - 1]
                    for a in range(1, r):
                        b = r - a
                        if 1 <= b <= n:
                            if kr > k[a - 1] + k[b - 1]:
                                # Increase one of the sources or decrease target
                                k[r - 1] = min(k[r - 1], k[a - 1] + k[b - 1])
                                changed = True
                    for a in range(r + 1, m):
                        b = r + m - a
                        if 1 <= b <= n:
                            if kr > k[a - 1] + k[b - 1] + 1:
                                k[r - 1] = min(k[r - 1], k[a - 1] + k[b - 1] + 1)
                                changed = True
                if not changed:
                    break
            # Re-check
            if not is_valid_kunz(k, m):
                continue

        info = detailed_analysis(k, m)
        if info["d"] == target_d and info["W"] < best_W:
            best = list(k)
            best_W = info["W"]

    return best, best_W


def main():
    parser = argparse.ArgumentParser(description="Random counterexample search")
    parser.add_argument("--m-min", type=int, default=10)
    parser.add_argument("--m-max", type=int, default=35)
    parser.add_argument("--k-max", type=int, default=8)
    parser.add_argument("--samples", type=int, default=50000,
                        help="Samples per (m, strategy)")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    random.seed(args.seed)

    print("=" * 72)
    print("  RANDOM / HEURISTIC COUNTEREXAMPLE SEARCH")
    print(f"  m in [{args.m_min}, {args.m_max}], k* <= {args.k_max}")
    print(f"  {args.samples} samples per (m, strategy)")
    print("=" * 72)

    all_violations = []
    # Track best (lowest) W for each (m, d) across all strategies
    best_W = {}

    t_start = time.time()

    for m in range(args.m_min, args.m_max + 1):
        n_valid = 0
        m_violations = []

        # Strategy 1: Uniform random
        for i in range(args.samples):
            k = random_valid_kunz(m, args.k_max)
            if k is None:
                continue
            n_valid += 1
            info = detailed_analysis(k, m)
            v = _run_all_checks(info)
            if v is not None:
                m_violations.append(v)

            key = (m, info["d"])
            if key not in best_W or info["W"] < best_W[key]:
                best_W[key] = info["W"]

        # Strategy 2: Biased towards high levels
        for i in range(args.samples):
            k = biased_high_level_kunz(m, args.k_max)
            if k is None:
                continue
            n_valid += 1
            info = detailed_analysis(k, m)
            v = _run_all_checks(info)
            if v is not None:
                m_violations.append(v)

            key = (m, info["d"])
            if key not in best_W or info["W"] < best_W[key]:
                best_W[key] = info["W"]

        status = "OK" if not m_violations else f"*** {len(m_violations)} VIOLATION(S) ***"
        print(f"  m={m:2d}  valid={n_valid:>8,}  {status}")

        if m_violations:
            for v in m_violations[:3]:
                print(f"    {v}")
            all_violations.extend(m_violations)

    # Strategy 3: Adversarial for specific high defects
    print(f"\n  --- Adversarial high-defect search ---")
    for m in range(args.m_min, min(args.m_max, 25) + 1):
        for target_d in range(4, min(m - 1, 16)):
            k, W = adversarial_high_defect(m, min(args.k_max, 3), target_d,
                                           max_attempts=5000)
            if k is None:
                continue
            pred = W_min_predicted(m, target_d)
            key = (m, target_d)
            if key not in best_W or W < best_W[key]:
                best_W[key] = W
            if W < pred:
                v = f"  ADVERSARIAL UNIFIED: m={m}, d={target_d}, W={W} < pred={pred}"
                print(f"    {v}")
                all_violations.append(v)

        if m % 5 == 0:
            print(f"  m={m:2d} adversarial done")

    elapsed = time.time() - t_start

    # ── Compare with predicted bounds ──
    print(f"\n{'='*72}")
    print(f"  k*-SATURATION ANALYSIS: lowest W found at k*<={args.k_max}")
    print(f"{'='*72}")
    print(f"  {'m':>3s}  {'d':>3s}  {'W_obs':>6s}  {'W_pred':>7s}  {'slack':>6s}  {'status':>10s}")
    print(f"  {'-'*3}  {'-'*3}  {'-'*6}  {'-'*7}  {'-'*6}  {'-'*10}")

    for (m, d) in sorted(best_W.keys()):
        W_obs = best_W[(m, d)]
        W_pred = W_min_predicted(m, d)
        slack = W_obs - W_pred
        status = "VIOLATION" if slack < 0 else ("SHARP" if slack == 0 else "ok")
        if slack <= 2 or slack < 0:  # Only show interesting cases
            print(f"  {m:3d}  {d:3d}  {W_obs:6d}  {W_pred:7d}  {slack:+6d}  {status:>10s}")

    print(f"\n  Total time: {elapsed:.1f}s")
    print(f"  Total violations: {len(all_violations)}")

    if all_violations:
        print(f"\n  ALL VIOLATIONS:")
        for v in all_violations:
            print(f"    {v}")
    else:
        print(f"\n  *** NO COUNTEREXAMPLES FOUND ***")

    return len(all_violations)


if __name__ == "__main__":
    sys.exit(0 if main() == 0 else 1)

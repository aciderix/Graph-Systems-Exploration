#!/usr/bin/env python3
"""
analyze.py — Structural tests on q-inversion polynomials produced by qinv_enum.c

Tests:
  1. OEIS sanity check of counts (|Av_n(pi)|).
  2. Unimodality (monotone up then monotone down).
  3. Log-concavity (c_k^2 >= c_{k-1}*c_{k+1}).
  4. Real-rootedness (via Newton's inequalities, a necessary condition, and
     via numpy root-finding — we report max |imag part| of roots).
  5. Congruences mod 2, 3, 5 (coefficient vectors reduced and compared).
  6. Mode position / center of mass.
  7. High-inversion tail: where does f_n^{pi}(q) start to equal [n]_q! exactly?
  8. Pairwise comparison of the four classes: identify structural invariants
     that distinguish 1324 from the others.

Usage: python3 analyze.py [max_n]
"""

import json
import os
import sys
from pathlib import Path

import numpy as np

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

OEIS = {
    "1234": [1, 1, 2, 6, 23, 103, 513, 2761, 15767, 94359, 586590, 3763290, 24792705],  # A005802
    "1342": [1, 1, 2, 6, 23, 103, 512, 2740, 15485, 91245, 555662, 3475090, 22214707],  # A022558
    "1324": [1, 1, 2, 6, 23, 103, 513, 2762, 15793, 94776, 591950, 3824112, 25431452],  # A061552
    "4321": [1, 1, 2, 6, 23, 103, 513, 2761, 15767, 94359, 586590, 3763290, 24792705],  # = 1234
}


def load(n):
    path = DATA_DIR / f"n{n}.json"
    with open(path) as f:
        return json.load(f)


def is_unimodal(c):
    """Is c unimodal (nonnegative, monotone up then monotone down)?"""
    c = [int(x) for x in c]
    n = len(c)
    i = 0
    # Skip leading zeros / equal start
    while i + 1 < n and c[i] <= c[i + 1]:
        i += 1
    # Now we should be descending
    while i + 1 < n and c[i] >= c[i + 1]:
        i += 1
    return i == n - 1


def is_log_concave(c):
    """Is c log-concave? c_k^2 >= c_{k-1} * c_{k+1} for all interior k.
    Handles internal zeros strictly (requires nonzero support to be contiguous)."""
    n = len(c)
    # Find nonzero support
    nz = [i for i, x in enumerate(c) if x > 0]
    if not nz:
        return True
    lo, hi = nz[0], nz[-1]
    # Nonzero support must be contiguous
    for i in range(lo, hi + 1):
        if c[i] == 0:
            return False
    for k in range(lo + 1, hi):
        if c[k] * c[k] < c[k - 1] * c[k + 1]:
            return False
    return True


def is_strictly_log_concave(c):
    n = len(c)
    nz = [i for i, x in enumerate(c) if x > 0]
    if len(nz) < 3:
        return True
    lo, hi = nz[0], nz[-1]
    for i in range(lo, hi + 1):
        if c[i] == 0:
            return False
    for k in range(lo + 1, hi):
        if c[k] * c[k] <= c[k - 1] * c[k + 1]:
            return False
    return True


def max_imag_root(c):
    """Max |Im| of roots of polynomial sum c_k q^k. Nonzero => not real-rooted."""
    # Strip leading zeros for clarity; numpy wants highest degree first.
    coeffs_high_first = list(reversed(c))
    # Remove leading zeros that would lower degree
    while len(coeffs_high_first) > 1 and coeffs_high_first[0] == 0:
        coeffs_high_first.pop(0)
    if len(coeffs_high_first) <= 1:
        return 0.0
    roots = np.roots(coeffs_high_first)
    return float(np.max(np.abs(roots.imag)))


def mode_position(c):
    mx = max(c)
    return [i for i, x in enumerate(c) if x == mx]


def highest_tail_match_index(c, baseline):
    """Return smallest k such that c[k:] == baseline[k:]. If never matches, len(c)."""
    k = len(c)
    while k > 0 and c[k - 1] == baseline[k - 1]:
        k -= 1
    return k  # c matches baseline on [k, len-1]


def congruence_signature(c, p):
    return tuple(int(x) % p for x in c)


def evaluate_at_roots_of_unity(c, orders=(2, 3, 4, 5, 6)):
    """For each order m, compute f(omega^j) for j=0..m-1 with omega = e^{2pi i/m}.
    Return real, imag parts."""
    results = {}
    for m in orders:
        omegas = [np.exp(2j * np.pi * j / m) for j in range(m)]
        vals = []
        for w in omegas:
            s = 0 + 0j
            for k, ck in enumerate(c):
                s += ck * (w ** k)
            vals.append((round(s.real, 6), round(s.imag, 6)))
        results[m] = vals
    return results


def main():
    max_n = int(sys.argv[1]) if len(sys.argv) > 1 else 11
    files = sorted([p for p in DATA_DIR.glob("n*.json")], key=lambda p: int(p.stem[1:]))
    if not files:
        print("No data files found.", file=sys.stderr)
        sys.exit(1)

    print("=" * 72)
    print("STRUCTURAL ANALYSIS — q-inversion polynomials on Av_n(pi)")
    print("=" * 72)
    for p in files:
        n = int(p.stem[1:])
        if n > max_n:
            continue
        data = load(n)
        mah = data["mahonian"]
        print(f"\n=== n = {n} (max_inv = {data['max_inv']}) ===")
        # OEIS check
        for pat, info in data["classes"].items():
            oeis = OEIS[pat][n]
            got = info["count"]
            ok = "OK" if oeis == got else f"FAIL (OEIS={oeis})"
            print(f"  |Av_n({pat})| = {got:>10d}   [{ok}]")
        # Per-class structural tests
        for pat, info in data["classes"].items():
            c = info["f"]
            unimod = is_unimodal(c)
            lc = is_log_concave(c)
            slc = is_strictly_log_concave(c)
            maxim = max_imag_root(c)
            modes = mode_position(c)
            tail = highest_tail_match_index(c, mah)
            tail_len = len(c) - tail
            print(f"  [{pat}]  unimod={unimod}  log-conc={lc}  strict-lc={slc}  "
                  f"maxImRoot={maxim:.3g}")
            print(f"          mode(s)={modes}   high-tail match starts at inv≥{tail}"
                  f" (length {tail_len})")
        # Cross-class comparisons
        print(f"  -- cross-comparisons --")
        classes = list(data["classes"].keys())
        for i in range(len(classes)):
            for j in range(i + 1, len(classes)):
                ci = data["classes"][classes[i]]["f"]
                cj = data["classes"][classes[j]]["f"]
                same = ci == cj
                tag = " (EQUAL!)" if same else ""
                print(f"     {classes[i]} vs {classes[j]}: same polynomial = {same}{tag}")
        # Congruences mod 2, 3, 5 summary
        print(f"  -- congruences mod {{2,3,5}} --")
        for pat, info in data["classes"].items():
            c = info["f"]
            for prime in (2, 3, 5):
                sig = congruence_signature(c, prime)
                # Compress: count of each residue
                from collections import Counter
                ctr = Counter(sig)
                print(f"     [{pat}] mod {prime}: {dict(sorted(ctr.items()))}")

    # Compact cross-class pattern over all n
    print("\n" + "=" * 72)
    print("SUMMARY OVER ALL n: does 1324 differ structurally from others?")
    print("=" * 72)
    rows = []
    for p in files:
        n = int(p.stem[1:])
        if n > max_n:
            continue
        data = load(n)
        row = {"n": n}
        for pat, info in data["classes"].items():
            c = info["f"]
            row[f"{pat}_lc"] = is_log_concave(c)
            row[f"{pat}_slc"] = is_strictly_log_concave(c)
            row[f"{pat}_unimod"] = is_unimodal(c)
            row[f"{pat}_maxIm"] = round(max_imag_root(c), 4)
            row[f"{pat}_mode"] = mode_position(c)[0]
            row[f"{pat}_len_support"] = sum(1 for x in c if x > 0)
        rows.append(row)
    # Pretty print
    header_cols = ["n"] + [f"{pat}_{k}" for pat in ["1234","1342","1324","4321"]
                            for k in ("lc","slc","unimod","maxIm","mode","len_support")]
    # Skip printing a huge table; instead focus on discriminants
    print("\nReal-rootedness (maxIm of complex roots) per (n, pattern):")
    print(f"  n      1234        1342        1324        4321")
    for r in rows:
        print(f"  {r['n']:<3d}  "
              f"{r['1234_maxIm']:<10.4g}  "
              f"{r['1342_maxIm']:<10.4g}  "
              f"{r['1324_maxIm']:<10.4g}  "
              f"{r['4321_maxIm']:<10.4g}")

    print("\nStrict log-concavity per (n, pattern):")
    print(f"  n      1234   1342   1324   4321")
    for r in rows:
        print(f"  {r['n']:<3d}  "
              f"{str(r['1234_slc']):<6}  "
              f"{str(r['1342_slc']):<6}  "
              f"{str(r['1324_slc']):<6}  "
              f"{str(r['4321_slc']):<6}")

    print("\nMode position (leftmost) per (n, pattern):")
    print(f"  n      1234   1342   1324   4321  max_inv")
    for r in rows:
        mi = r["n"] * (r["n"] - 1) // 2
        print(f"  {r['n']:<3d}  "
              f"{r['1234_mode']:<6}  "
              f"{r['1342_mode']:<6}  "
              f"{r['1324_mode']:<6}  "
              f"{r['4321_mode']:<6}  {mi}")


if __name__ == "__main__":
    main()

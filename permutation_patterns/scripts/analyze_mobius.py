#!/usr/bin/env python3
"""
Analyze the Möbius function distribution on the permutation containment poset.

Loads data/mobius.json produced by mobius_compute.py and answers:

  1. Histogram and max|mu| by n.
  2. Sign-by-parity rule: sign(mu(1, pi)) = (-1)^(n-1)?  Find exceptions.
  3. Mass at zero: fraction of S_n with mu(1, pi) = 0.
  4. Separable check: for separable pi, mu(1, pi) in {-1, 0, 1}?
     (Separable = Av(2413, 3142).)
  5. Simple check: are extrema simple permutations?
  6. OEIS lookup of max|mu| sequence.

Also recomputes mu on the fly so we can access ALL permutations, not just
the extrema stored in mobius.json.
"""

import json
import sys
from pathlib import Path
from itertools import permutations, combinations
from collections import Counter, defaultdict

# Reuse computation from mobius_compute
sys.path.insert(0, str(Path(__file__).resolve().parent))
from mobius_compute import compute_mu, reduce_pattern, MU

DATA = Path(__file__).resolve().parent.parent / "data"


def contains_pattern(pi, pat):
    """Test if pattern 'pat' occurs in pi (standard pattern containment)."""
    n = len(pi)
    k = len(pat)
    for idxs in combinations(range(n), k):
        sub = tuple(pi[i] for i in idxs)
        if reduce_pattern(sub) == pat:
            return True
    return False


def is_separable(pi):
    """Av(2413, 3142)."""
    return not (contains_pattern(pi, (2, 4, 1, 3)) or
                contains_pattern(pi, (3, 1, 4, 2)))


def is_simple(pi):
    """A permutation is simple if it has no non-trivial interval,
    i.e. no contiguous subrange [i..j] (with j>i, (i,j) != (0,n-1))
    whose values form a contiguous integer interval.
    """
    n = len(pi)
    if n <= 1:
        return True
    if n == 2:
        return True  # convention: 12, 21 are simple
    for i in range(n):
        lo = hi = pi[i]
        for j in range(i + 1, n):
            v = pi[j]
            if v < lo: lo = v
            if v > hi: hi = v
            size = j - i + 1
            if hi - lo + 1 == size and size < n:
                return False
    return True


def sign_convention(n):
    return 1 if (n - 1) % 2 == 0 else -1


def main():
    # We'll recompute rather than load, to have access to all mu values.
    N_MAX = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    print(f"Analyzing mu(1, pi) distribution for n = 1..{N_MAX}")

    all_mu_by_n = {}  # n -> list of (pi, mu)
    for n in range(1, N_MAX + 1):
        lst = []
        for pi in permutations(range(1, n + 1)):
            lst.append((pi, compute_mu(pi)))
        all_mu_by_n[n] = lst
        print(f"  n={n}: {len(lst)} perms computed")

    print()
    print("=" * 70)
    print("HISTOGRAMS of mu(1, pi)")
    print("=" * 70)
    for n in range(1, N_MAX + 1):
        h = Counter(m for _, m in all_mu_by_n[n])
        items = sorted(h.items())
        print(f"n={n}:  #={sum(h.values())},  max|mu|={max(abs(m) for m in h)}")
        print(f"       hist: {items}")

    print()
    print("=" * 70)
    print("MASS AT ZERO")
    print("=" * 70)
    for n in range(1, N_MAX + 1):
        h = Counter(m for _, m in all_mu_by_n[n])
        zero = h.get(0, 0)
        total = sum(h.values())
        print(f"  n={n}:  mu=0: {zero}/{total}  ({100 * zero / total:.1f}%)")

    print()
    print("=" * 70)
    print("SIGN-BY-PARITY: sign(mu) = (-1)^(n-1) for non-zero mu?")
    print("=" * 70)
    for n in range(1, N_MAX + 1):
        expected_sign = sign_convention(n)
        exceptions = []
        for pi, m in all_mu_by_n[n]:
            if m != 0 and ((m > 0) != (expected_sign > 0)):
                exceptions.append((pi, m))
        print(f"  n={n}:  expected sign={expected_sign:+d},  "
              f"exceptions: {len(exceptions)}")
        if exceptions and len(exceptions) <= 12:
            for pi, m in exceptions:
                print(f"       {list(pi)} -> mu={m}")
        elif exceptions:
            print(f"       (showing first 6)")
            for pi, m in exceptions[:6]:
                print(f"       {list(pi)} -> mu={m}")

    print()
    print("=" * 70)
    print("SEPARABLE CHECK: for separable pi, mu in {-1, 0, 1}?")
    print("=" * 70)
    for n in range(1, N_MAX + 1):
        sep_mus = []
        nonsep_mus = []
        for pi, m in all_mu_by_n[n]:
            if is_separable(pi):
                sep_mus.append(m)
            else:
                nonsep_mus.append(m)
        sep_hist = Counter(sep_mus)
        violates = [m for m in sep_mus if abs(m) > 1]
        print(f"  n={n}:  #sep={len(sep_mus)}, hist={sorted(sep_hist.items())}  "
              f"(violations={len(violates)})")
        if nonsep_mus:
            nonsep_hist = Counter(nonsep_mus)
            print(f"         #nonsep={len(nonsep_mus)}, "
                  f"hist={sorted(nonsep_hist.items())}")

    print()
    print("=" * 70)
    print("EXTREMA: check if they are SIMPLE permutations")
    print("=" * 70)
    for n in range(1, N_MAX + 1):
        max_abs = max(abs(m) for _, m in all_mu_by_n[n])
        ext = [(pi, m) for pi, m in all_mu_by_n[n] if abs(m) == max_abs]
        print(f"  n={n}:  max|mu|={max_abs}, #extrema={len(ext)}")
        for pi, m in ext:
            sim = "SIMPLE" if is_simple(pi) else "not simple"
            print(f"       {list(pi)} -> mu={m:+d}  [{sim}]")

    print()
    print("=" * 70)
    print("max|mu| sequence:")
    print("=" * 70)
    seq = []
    for n in range(1, N_MAX + 1):
        max_abs = max(abs(m) for _, m in all_mu_by_n[n])
        seq.append(max_abs)
    print(f"  {seq}")
    print("  (OEIS lookup candidate)")

    print()
    print("=" * 70)
    print("Number of DISTINCT mu values by n:")
    print("=" * 70)
    for n in range(1, N_MAX + 1):
        h = Counter(m for _, m in all_mu_by_n[n])
        print(f"  n={n}:  #distinct={len(h)}, values={sorted(h)}")


if __name__ == "__main__":
    main()

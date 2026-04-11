#!/usr/bin/env python3
"""
Analyze the extended (inv, maj, des, peak, lis) polynomials for the 4 classes.

Primary questions:
  1. Log-concavity per (class, statistic, n).
  2. Unimodality per (class, statistic, n).
  3. Symmetry of the polynomial (palindromic).
  4. Where do 1324's polynomials differ structurally from the others?

Since Linusson-Verkama 2025 already covers (inv) for 1324, the new
information is in (maj, des, peak, lis).
"""

import json
from pathlib import Path
from collections import defaultdict

DATA = Path(__file__).resolve().parent.parent / "data"


def is_unimodal(c):
    nz = [i for i, x in enumerate(c) if x > 0]
    if not nz:
        return True
    lo, hi = nz[0], nz[-1]
    sub = c[lo:hi+1]
    if any(x == 0 for x in sub):
        return False
    i = 0
    while i + 1 < len(sub) and sub[i] <= sub[i+1]:
        i += 1
    while i + 1 < len(sub) and sub[i] >= sub[i+1]:
        i += 1
    return i == len(sub) - 1


def is_log_concave(c):
    nz = [i for i, x in enumerate(c) if x > 0]
    if len(nz) < 3:
        return True
    lo, hi = nz[0], nz[-1]
    for i in range(lo, hi+1):
        if c[i] == 0:
            return False
    for k in range(lo+1, hi):
        if c[k]*c[k] < c[k-1]*c[k+1]:
            return False
    return True


def lc_failures(c):
    out = []
    for k in range(1, len(c)-1):
        if c[k] and c[k-1] and c[k+1]:
            if c[k]*c[k] < c[k-1]*c[k+1]:
                out.append((k, c[k-1], c[k], c[k+1]))
    return out


def is_palindromic(c):
    nz = [i for i, x in enumerate(c) if x > 0]
    if not nz:
        return True
    lo, hi = nz[0], nz[-1]
    sub = c[lo:hi+1]
    return sub == sub[::-1]


def mode(c):
    m = max(c)
    return [i for i, x in enumerate(c) if x == m]


def main():
    files = sorted(DATA.glob("stats_n*.json"),
                   key=lambda p: int(p.stem.split("_n")[1]))
    patterns = ["1234", "1342", "1324", "4321"]
    stats_list = ["inv", "maj", "des", "peak", "lis"]

    # Summary table: for each (statistic, pattern), list the n where log-concavity fails.
    lc_status = defaultdict(list)     # (stat, pat) -> list of (n, True/False)
    unim_status = defaultdict(list)
    palindrome = defaultdict(list)
    lc_fail_details = defaultdict(list)  # (stat, pat, n) -> failures

    for p in files:
        n = int(p.stem.split("_n")[1])
        txt = p.read_text()
        if not txt.strip():
            continue  # background run not done yet
        data = json.loads(txt)
        for pat in patterns:
            info = data["classes"][pat]
            for stat in stats_list:
                c = info[stat]
                lc = is_log_concave(c)
                um = is_unimodal(c)
                pd = is_palindromic(c)
                lc_status[(stat, pat)].append((n, lc))
                unim_status[(stat, pat)].append((n, um))
                palindrome[(stat, pat)].append((n, pd))
                if not lc:
                    lc_fail_details[(stat, pat, n)] = lc_failures(c)

    print("=" * 80)
    print("LOG-CONCAVITY per (statistic, pattern) — marks n where NOT log-concave")
    print("=" * 80)
    for stat in stats_list:
        print(f"\nStatistic: {stat}")
        header = "  n    " + "  ".join(f"{pat:<8}" for pat in patterns)
        print(header)
        ns = sorted(set(n for n, _ in lc_status[(stat, patterns[0])]))
        for n in ns:
            row = f"  {n:<4}"
            for pat in patterns:
                lc_map = dict(lc_status[(stat, pat)])
                row += "  " + ("LC      " if lc_map[n] else "FAIL    ")
            print(row)

    print("\n" + "=" * 80)
    print("UNIMODALITY per (statistic, pattern) — marks n where NOT unimodal")
    print("=" * 80)
    for stat in stats_list:
        print(f"\nStatistic: {stat}")
        header = "  n    " + "  ".join(f"{pat:<8}" for pat in patterns)
        print(header)
        ns = sorted(set(n for n, _ in unim_status[(stat, patterns[0])]))
        for n in ns:
            row = f"  {n:<4}"
            for pat in patterns:
                um_map = dict(unim_status[(stat, pat)])
                row += "  " + ("UM      " if um_map[n] else "FAIL    ")
            print(row)

    print("\n" + "=" * 80)
    print("PALINDROMICITY per (statistic, pattern)")
    print("=" * 80)
    for stat in stats_list:
        print(f"\nStatistic: {stat}")
        header = "  n    " + "  ".join(f"{pat:<8}" for pat in patterns)
        print(header)
        ns = sorted(set(n for n, _ in palindrome[(stat, patterns[0])]))
        for n in ns:
            row = f"  {n:<4}"
            for pat in patterns:
                pd_map = dict(palindrome[(stat, pat)])
                row += "  " + ("PAL     " if pd_map[n] else "no      ")
            print(row)

    print("\n" + "=" * 80)
    print("LOG-CONCAVITY FAILURE DETAILS (limited to failing cases)")
    print("=" * 80)
    for (stat, pat, n), fails in sorted(lc_fail_details.items()):
        print(f"\n  [{pat}][{stat}][n={n}]: {len(fails)} failures")
        for (k, a, b, c) in fails[:5]:
            print(f"     k={k:3d}: c[k-1]={a}, c[k]={b}, c[k+1]={c}   ({b*b} vs {a*c})")
        if len(fails) > 5:
            print(f"     ... and {len(fails)-5} more")


if __name__ == "__main__":
    main()

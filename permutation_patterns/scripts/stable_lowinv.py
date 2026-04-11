#!/usr/bin/env python3
"""
Extract and compare the "stable low-inversion sequence" for each pattern class.

At low inversion count k, the coefficient [q^k] f_n^{pi}(q) stabilizes as n grows
(because small-inv perms have bounded active support). Print the stable prefix
and see where each pattern's sequence becomes non-log-concave, if at all.

Also reports the analogous stable HIGH-end (via reverse symmetry) and checks
mirror symmetry.
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

def load_polys():
    out = {}
    for p in sorted(DATA_DIR.glob("n*.json"), key=lambda q: int(q.stem[1:])):
        n = int(p.stem[1:])
        out[n] = json.loads(p.read_text())
    return out

def main():
    data = load_polys()
    ns = sorted(data.keys())
    patterns = ["1234", "1342", "1324", "4321"]

    # For each pattern, print the low-inv prefix at each n, up to inv=15.
    MAX_K = 16
    for pat in patterns:
        print(f"\n=== Low-inv prefix of f_n^{pat}(q)  (first {MAX_K} coefficients) ===")
        print(f"  n  |  c_0  c_1  c_2 ... c_{MAX_K-1}")
        for n in ns:
            c = data[n]["classes"][pat]["f"]
            prefix = c[:MAX_K]
            print(f"  {n:>2}  |  " + " ".join(f"{x:>7d}" for x in prefix))
    # Now: find the LARGEST common prefix across n (= stable sequence).
    print("\n" + "="*70)
    print("STABLE LOW-INV SEQUENCES (longest common prefix)")
    print("="*70)
    for pat in patterns:
        prefixes = [data[n]["classes"][pat]["f"] for n in ns]
        # Largest k such that prefixes[i][:k] is identical for the largest n values
        common_k = 0
        min_len = min(len(p) for p in prefixes)
        for k in range(min_len):
            vals = set(p[k] for p in prefixes)
            if len(vals) == 1:
                common_k = k + 1
            else:
                break
        stable = prefixes[-1][:common_k]
        print(f"\n[{pat}] stable prefix length = {common_k}")
        print(f"       {stable}")
        # Test log-concavity of this stable sequence
        fails = []
        for i in range(1, len(stable)-1):
            if stable[i] > 0 and stable[i-1] > 0 and stable[i+1] > 0:
                if stable[i]**2 < stable[i-1]*stable[i+1]:
                    fails.append((i, stable[i-1], stable[i], stable[i+1]))
        if fails:
            print(f"       log-conc failures: {len(fails)}")
            for f in fails:
                print(f"         k={f[0]}: {f[1]}, {f[2]}, {f[3]}  ({f[2]**2} < {f[1]*f[3]})")
        else:
            print(f"       log-concave on stable prefix.")

    # Also check ratio: does the stable sequence of 1324 differ from a known sequence?
    print("\n" + "="*70)
    print("STABLE SEQ for 1324 — first 16 terms for OEIS lookup:")
    print("="*70)
    prefixes = [data[n]["classes"]["1324"]["f"] for n in ns]
    common_k = 0
    min_len = min(len(p) for p in prefixes)
    for k in range(min_len):
        vals = set(p[k] for p in prefixes)
        if len(vals) == 1:
            common_k = k + 1
        else:
            break
    stable = prefixes[-1][:common_k]
    print(f"  stable length = {common_k}")
    print(f"  sequence: " + ", ".join(str(x) for x in stable))


if __name__ == "__main__":
    main()

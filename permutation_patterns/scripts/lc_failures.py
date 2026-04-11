#!/usr/bin/env python3
"""
Report exact log-concavity failure positions for each class and each n.

For each polynomial c, we compute the set of indices k where
  c[k]^2 < c[k-1] * c[k+1]
(strict failure), and also where c[k]^2 == c[k-1]*c[k+1] (equality).

We also measure the "severity" as log(c[k-1]*c[k+1]) - 2*log(c[k]) (positive
means log-concavity violated).

Also compare with q-factorial [n]_q! which is known to be real-rooted (hence
log-concave) since it's the product (1)(1+q)(1+q+q^2)...(1+q+...+q^{n-1}).
"""

import json
import math
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def lc_failures(c):
    failures = []
    for k in range(1, len(c) - 1):
        if c[k-1] > 0 and c[k+1] > 0 and c[k] > 0:
            lhs = c[k] * c[k]
            rhs = c[k-1] * c[k+1]
            if lhs < rhs:
                severity = math.log(rhs) - 2 * math.log(c[k])
                failures.append((k, c[k-1], c[k], c[k+1], round(severity, 5)))
    return failures


def main():
    files = sorted([p for p in DATA_DIR.glob("n*.json")], key=lambda p: int(p.stem[1:]))
    print("=" * 76)
    print("LOG-CONCAVITY FAILURES: c[k]^2 < c[k-1]*c[k+1]")
    print("=" * 76)
    for p in files:
        n = int(p.stem[1:])
        data = json.loads(p.read_text())
        print(f"\n=== n = {n} ===")
        mah = data["mahonian"]
        mfail = lc_failures(mah)
        print(f"  [Mahonian] failures: {len(mfail)}")
        for pat, info in data["classes"].items():
            c = info["f"]
            fails = lc_failures(c)
            print(f"  [{pat}] failures: {len(fails)}")
            for (k, a, b, cc, s) in fails[:8]:
                print(f"     k={k:3d}  c[k-1]={a}  c[k]={b}  c[k+1]={cc}  severity={s}")
            if len(fails) > 8:
                print(f"     ... and {len(fails)-8} more")


if __name__ == "__main__":
    main()

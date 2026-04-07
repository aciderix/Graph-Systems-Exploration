"""Micro-benchmark: serial vs OpenMP kernels at several multiplicities.

Run:
    python bench_omp.py [m_list ...]

Defaults to m in {14, 16, 18, 20}. Reports elapsed seconds and the
speedup factor, and asserts that per-defect (count, W_min) match
between the two kernels.
"""

from __future__ import annotations

import sys

import kunz_fast as kf


def compare(m: int, k_max: int = 3) -> None:
    a = kf.run_c(m, k_max)
    b = kf.run_c(m, k_max, omp_threads=0)
    ok = a["leaves_valid"] == b["leaves_valid"]
    for d in a["per_defect"]:
        ea, eb = a["per_defect"][d], b["per_defect"][d]
        if (ea["count"], ea["W_min"]) != (eb["count"], eb["W_min"]):
            ok = False
    status = "OK" if ok else "MISMATCH"
    sp = a["elapsed_sec"] / max(b["elapsed_sec"], 1e-9)
    print(f"m={m:>2}  K={k_max}  leaves={a['leaves_valid']:>12,}  "
          f"serial={a['elapsed_sec']:>7.2f}s  "
          f"omp={b['elapsed_sec']:>7.2f}s  "
          f"speedup={sp:>4.2f}x  [{status}]")


def main() -> None:
    ms = [int(x) for x in sys.argv[1:]] or [14, 16, 18, 20]
    for m in ms:
        compare(m)


if __name__ == "__main__":
    main()

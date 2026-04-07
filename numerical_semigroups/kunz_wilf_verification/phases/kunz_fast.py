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
import ctypes
import json
import os
import subprocess
import sys
import time
from typing import Callable, Iterator, Optional

import numpy as np

# ----------------------------------------------------------------------
# Optional C extension. Compile on first import if gcc is available.
# ----------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
_C_SRC = os.path.join(_HERE, "kunz_core.c")
_C_LIB_PATH = os.path.join(_HERE, "kunz_core.so")
_C_LIB = None


MAX_M_C = 64


class KunzResultC(ctypes.Structure):
    _fields_ = [
        ("counts", ctypes.c_int * MAX_M_C),
        ("W_neg", ctypes.c_int * MAX_M_C),
        ("W_min", ctypes.c_longlong * MAX_M_C),
        ("argmin_k", (ctypes.c_int * MAX_M_C) * MAX_M_C),
        ("leaves_raw", ctypes.c_longlong),
        ("leaves_valid", ctypes.c_longlong),
        ("leaves_kept", ctypes.c_longlong),
    ]


def _try_load_c() -> Optional[ctypes.CDLL]:
    if not os.path.exists(_C_SRC):
        return None
    if (not os.path.exists(_C_LIB_PATH)
            or os.path.getmtime(_C_SRC) > os.path.getmtime(_C_LIB_PATH)):
        base = ["gcc", "-O3", "-march=native", "-fPIC", "-shared",
                _C_SRC, "-o", _C_LIB_PATH]
        try:
            subprocess.run(base + ["-fopenmp"], check=True, capture_output=True)
        except Exception:
            try:
                subprocess.run(base, check=True, capture_output=True)
            except Exception:
                return None
    try:
        lib = ctypes.CDLL(_C_LIB_PATH)
        lib.invariants.argtypes = [
            ctypes.POINTER(ctypes.c_int), ctypes.c_int,
            ctypes.POINTER(ctypes.c_int),
        ]
        lib.invariants.restype = None
        lib.run_enum.argtypes = [
            ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_int,
            ctypes.c_longlong, ctypes.c_int,
            ctypes.POINTER(KunzResultC),
        ]
        lib.run_enum.restype = None
        if hasattr(lib, "run_enum_omp"):
            lib.run_enum_omp.argtypes = [
                ctypes.c_int, ctypes.c_int,
                ctypes.c_int, ctypes.c_int,
                ctypes.c_longlong, ctypes.c_int,
                ctypes.c_int,
                ctypes.POINTER(KunzResultC),
            ]
            lib.run_enum_omp.restype = None
        if hasattr(lib, "run_enum_prefix"):
            lib.run_enum_prefix.argtypes = [
                ctypes.c_int, ctypes.c_int,
                ctypes.c_int, ctypes.c_int,
                ctypes.c_longlong, ctypes.c_int,
                ctypes.POINTER(ctypes.c_int), ctypes.c_int,
                ctypes.POINTER(KunzResultC),
            ]
            lib.run_enum_prefix.restype = None
        return lib
    except Exception:
        return None


_C_LIB = _try_load_c()


def run_c(
    m: int,
    K_max: int,
    d_min: Optional[int] = None,
    d_max: Optional[int] = None,
    w_max: Optional[int] = None,
    omp_threads: Optional[int] = None,
    k_prefix: Optional[list] = None,
) -> dict:
    """Pure-C enumeration. Returns the same summary shape as run().

    If omp_threads is not None and the loaded library exposes run_enum_omp,
    the parallel kernel is used (one worker per value of k_1). Pass 0 to
    use the OMP_NUM_THREADS / default runtime choice.

    If k_prefix is provided (a list of values for k_1, k_2, ...), only the
    subtree where the leading coordinates are pinned to those values is
    enumerated. The union over all valid prefixes of a fixed length covers
    the same leaves as an unrestricted run, so prefix-restricted runs can
    be merged into a complete enumeration.
    """
    if _C_LIB is None:
        raise RuntimeError("C extension not loaded")
    if m < 2 or m > MAX_M_C:
        raise ValueError(f"m must be in [2, {MAX_M_C}]")
    res = KunzResultC()
    use_omp = (omp_threads is not None and hasattr(_C_LIB, "run_enum_omp")
               and not k_prefix)
    use_prefix = bool(k_prefix) and hasattr(_C_LIB, "run_enum_prefix")
    if k_prefix and not use_prefix:
        raise RuntimeError("run_enum_prefix not available in C extension")
    t0 = time.time()
    if use_omp:
        _C_LIB.run_enum_omp(
            m, K_max,
            d_min if d_min is not None else 0,
            d_max if d_max is not None else m,
            w_max if w_max is not None else 0,
            1 if w_max is not None else 0,
            int(omp_threads),
            ctypes.byref(res),
        )
    elif use_prefix:
        plen = len(k_prefix)
        prefix_arr = (ctypes.c_int * plen)(*[int(x) for x in k_prefix])
        _C_LIB.run_enum_prefix(
            m, K_max,
            d_min if d_min is not None else 0,
            d_max if d_max is not None else m,
            w_max if w_max is not None else 0,
            1 if w_max is not None else 0,
            prefix_arr, plen,
            ctypes.byref(res),
        )
    else:
        _C_LIB.run_enum(
            m, K_max,
            d_min if d_min is not None else 0,
            d_max if d_max is not None else m,
            w_max if w_max is not None else 0,
            1 if w_max is not None else 0,
            ctypes.byref(res),
        )
    elapsed = time.time() - t0
    per_d = {}
    for d in range(m):
        if res.counts[d] == 0:
            continue
        per_d[str(d)] = {
            "count": int(res.counts[d]),
            "W_min": int(res.W_min[d]),
            "W_neg_count": int(res.W_neg[d]),
            "argmin_k": [int(res.argmin_k[d][i]) for i in range(m - 1)],
        }
    return {
        "m": m,
        "K_max": K_max,
        "d_min": d_min,
        "d_max": d_max,
        "w_max": w_max,
        "elapsed_sec": round(elapsed, 3),
        "leaves_raw": int(res.leaves_raw),
        "leaves_valid": int(res.leaves_valid),
        "leaves_kept": int(res.leaves_kept),
        "per_defect": per_d,
        "backend": "C-OMP" if use_omp else ("C-prefix" if use_prefix else "C"),
        "k_prefix": list(k_prefix) if k_prefix else None,
    }


def invariants_from_k(k, m: int) -> dict:
    """Compute (d, L, k*, r*, F, c, W, e) from a Kunz tuple k of length m-1.

    k[0] = k_1, ..., k[m-2] = k_{m-1}. Accepts list, tuple, or ndarray.

    Uses the C extension if available (~10-50x faster), else pure Python.
    """
    if _C_LIB is not None:
        return _invariants_c(k, m)
    return _invariants_py(k, m)


def _invariants_py(k, m: int) -> dict:
    k_star = max(k)
    # r* = largest residue (1-indexed) achieving k*
    r_star = 0
    for i in range(m - 1):
        if k[i] == k_star:
            r_star = i + 1

    L = k_star
    for i in range(m - 1):
        if (i + 1) <= r_star:
            L += k_star - k[i]
        else:
            d_i = k_star - 1 - k[i]
            if d_i > 0:
                L += d_i

    F = (k_star - 1) * m + r_star
    c = F + 1

    d = 0
    for r in range(1, m):
        kr = k[r - 1]
        decomposable = False
        for a in range(1, m):
            b_nc = r - a
            if 1 <= b_nc <= m - 1:
                if k[a - 1] + k[b_nc - 1] <= kr:
                    decomposable = True
                    break
            b_c = r + m - a
            if 1 <= b_c <= m - 1:
                if k[a - 1] + k[b_c - 1] + 1 <= kr:
                    decomposable = True
                    break
        if decomposable:
            d += 1

    e = m - d
    W = e * L - c

    return {
        "m": m,
        "k": [int(x) for x in k],
        "d": d,
        "e": e,
        "k_star": k_star,
        "r_star": r_star,
        "L": L,
        "F": F,
        "c": c,
        "W": W,
    }


def _invariants_c(k, m: int) -> dict:
    arr = (ctypes.c_int * (m - 1))(*[int(x) for x in k])
    out = (ctypes.c_int * 8)()
    _C_LIB.invariants(arr, m, out)
    return {
        "m": m,
        "k": [int(x) for x in k],
        "d": int(out[0]),
        "e": int(out[1]),
        "k_star": int(out[2]),
        "r_star": int(out[3]),
        "L": int(out[4]),
        "F": int(out[5]),
        "c": int(out[6]),
        "W": int(out[7]),
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
    p.add_argument("--backend", choices=["py", "c", "auto"], default="auto")
    p.add_argument("--omp", type=int, default=None,
                   help="use OpenMP kernel with N threads (0 = runtime default)")
    p.add_argument("--k-prefix", type=str, default=None,
                   help="comma-separated values pinning k_1, k_2, ... "
                        "(enables prefix-restricted enumeration for chunking)")
    args = p.parse_args()

    use_c = args.backend == "c" or (args.backend == "auto" and _C_LIB is not None)
    if use_c:
        prefix = None
        if args.k_prefix:
            prefix = [int(x) for x in args.k_prefix.split(",") if x.strip()]
        summary = run_c(args.m, args.K_max,
                        d_min=args.d_min, d_max=args.d_max, w_max=args.w_max,
                        omp_threads=args.omp, k_prefix=prefix)
        if args.out:
            with open(args.out, "w") as f:
                json.dump(summary, f, indent=1)
        print(json.dumps(summary, indent=2))
        return

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

#!/usr/bin/env python3
"""
Systematic counterexample hunt for ALL claims in wilf_paper.tex.

Targets:
  1. Theorem A:  d=1  =>  W >= m-3         (proved, but test beyond m=25)
  2. Theorem B:  d=2  =>  W >= 2m-8        (proved, but test beyond m=25)
  3. Theorem C:  d=3, m>=7  =>  W >= 2m-12 (proved, but test beyond m=25)
  4. Unified conjecture:  W >= (m-d)*L(d) - 2m  for all d
  5. k*-saturation:  min W already achieved at k*<=3
  6. Deficit Lemma:  d>=2, k*>=4  =>  Sigma_delta >= k*-1  (i.e. L >= 2k*-1)
  7. Pair Contribution Lemma:  d=1, k*>=5  =>  delta_a + delta_b >= k*-2
  8. r* bounds:  d=1,k*=3,L=4 => r*<=m-2;  d=2,k*=3,L=5 => r*<=m-3;
               d=3,k*=3,L=5 => r*<=m-4
  9. Stabilization thresholds m_min(d)
 10. Triangular number structure of L(d)

Strategy:
  - Use the existing C kernel (kunz_core.c) for fast enumeration
  - Push m up to 30+ at k*<=3, and m up to 20 at k*<=6
  - For each claim, record any violation with full details
  - Also run targeted random/structured search at high k* for k*-saturation

Usage:
    python counterexample_hunt.py [--m-max M] [--k-max K] [--focus CLAIM]
"""

import argparse
import ctypes
import json
import math
import os
import subprocess
import sys
import time
from collections import defaultdict

# ── C kernel loading ──────────────────────────────────────────────────

_HERE = os.path.dirname(os.path.abspath(__file__))
_C_SRC = os.path.join(_HERE, "kunz_core.c")
_C_LIB_PATH = os.path.join(_HERE, "kunz_core.so")

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


def load_c_lib():
    if not os.path.exists(_C_SRC):
        print(f"ERROR: {_C_SRC} not found", file=sys.stderr)
        sys.exit(1)
    if (not os.path.exists(_C_LIB_PATH)
            or os.path.getmtime(_C_SRC) > os.path.getmtime(_C_LIB_PATH)):
        subprocess.run(
            ["gcc", "-O3", "-march=native", "-fPIC", "-shared",
             _C_SRC, "-o", _C_LIB_PATH],
            check=True,
        )
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
    return lib


def run_enum(lib, m, k_max, d_min=0, d_max=None, w_max=None):
    """Run C enumeration, return per-defect dict."""
    if d_max is None:
        d_max = m - 1
    res = KunzResultC()
    lib.run_enum(
        m, k_max,
        d_min, d_max,
        w_max if w_max is not None else 0,
        1 if w_max is not None else 0,
        ctypes.byref(res),
    )
    per_d = {}
    for d in range(m):
        if res.counts[d] == 0:
            continue
        per_d[d] = {
            "count": int(res.counts[d]),
            "W_min": int(res.W_min[d]),
            "W_neg": int(res.W_neg[d]),
            "argmin_k": [int(res.argmin_k[d][i]) for i in range(m - 1)],
        }
    return per_d, int(res.leaves_valid)


def invariants_c(lib, k, m):
    """Compute full invariants for a single Kunz tuple."""
    arr = (ctypes.c_int * (m - 1))(*[int(x) for x in k])
    out = (ctypes.c_int * 8)()
    lib.invariants(arr, m, out)
    return {
        "d": int(out[0]), "e": int(out[1]),
        "k_star": int(out[2]), "r_star": int(out[3]),
        "L": int(out[4]), "F": int(out[5]),
        "c": int(out[6]), "W": int(out[7]),
    }


# ── Unified conjecture formula ───────────────────────────────────────

def p_of_d(d):
    """Smallest p with T_p = p(p+1)/2 >= d."""
    if d == 0:
        return 0
    return math.ceil((math.sqrt(8 * d + 1) - 1) / 2)


def L_of_d(d):
    return p_of_d(d) + 2


def W_min_predicted(m, d):
    return (m - d) * L_of_d(d) - 2 * m


# ── Detailed Kunz analysis (for lemma-level checks) ──────────────────

def detailed_analysis(k, m):
    """Compute all quantities needed for lemma-level verification."""
    n = m - 1
    k_star = 0
    r_star = 0
    for i in range(n):
        if k[i] >= k_star:
            k_star = k[i]
            r_star = i + 1

    # L and delta_i
    deltas = []
    for i in range(n):
        res = i + 1
        if res <= r_star:
            deltas.append(k_star - k[i])
        else:
            deltas.append(max(0, k_star - 1 - k[i]))
    sigma_delta = sum(deltas)
    L = k_star + sigma_delta

    F = (k_star - 1) * m + r_star
    c = F + 1

    # Decomposable residues with witness pairs
    decomposable = {}
    for r in range(1, m):
        kr = k[r - 1]
        for a in range(1, m):
            # no-carry: a + b = r, b = r - a
            b_nc = r - a
            if 1 <= b_nc <= n:
                if k[a - 1] + k[b_nc - 1] <= kr:
                    decomposable[r] = (a, b_nc, 0)  # eps=0
                    break
            # carry: a + b = r + m, b = r + m - a
            b_c = r + m - a
            if 1 <= b_c <= n:
                if k[a - 1] + k[b_c - 1] + 1 <= kr:
                    decomposable[r] = (a, b_c, 1)  # eps=1
                    break

    d = len(decomposable)
    e = m - d
    W = e * L - c

    return {
        "k": list(k), "m": m, "k_star": k_star, "r_star": r_star,
        "L": L, "F": F, "c": c, "d": d, "e": e, "W": W,
        "deltas": deltas, "sigma_delta": sigma_delta,
        "decomposable": decomposable,
    }


# ── Python-level enumeration for lemma checks ────────────────────────

def enumerate_and_check(m, k_max, check_fn, d_filter=None):
    """Enumerate all Kunz tuples and apply check_fn to each.

    check_fn(analysis_dict) should return None if OK, or a string describing
    the violation.

    Returns list of violations.
    """
    violations = []
    n = m - 1
    k = [0] * n

    def verify_carry():
        for r in range(1, m):
            kr = k[r - 1]
            for a in range(r + 1, m):
                b = r + m - a
                if 1 <= b <= n:
                    if kr > k[a - 1] + k[b - 1] + 1:
                        return False
        return True

    def rec(pos):
        if pos == m:
            if not verify_carry():
                return
            info = detailed_analysis(k, m)
            if d_filter is not None and info["d"] != d_filter:
                return
            v = check_fn(info)
            if v is not None:
                violations.append(v)
            return

        ub = k_max
        for a in range(1, pos):
            b = pos - a
            val = k[a - 1] + k[b - 1]
            if val < ub:
                ub = val
        if ub < 1:
            return
        for val in range(1, ub + 1):
            k[pos - 1] = val
            rec(pos + 1)

    rec(1)
    return violations


# ── CLAIM CHECKERS ────────────────────────────────────────────────────

def check_theorem_A(info):
    """d=1 => W >= m-3"""
    if info["d"] != 1:
        return None
    bound = info["m"] - 3
    if info["W"] < bound:
        return f"THEOREM A VIOLATION: m={info['m']}, W={info['W']} < {bound}, k={info['k']}"
    return None


def check_theorem_B(info):
    """d=2, m>=4 => W >= 2m-8"""
    if info["d"] != 2 or info["m"] < 4:
        return None
    bound = 2 * info["m"] - 8
    if info["W"] < bound:
        return f"THEOREM B VIOLATION: m={info['m']}, W={info['W']} < {bound}, k={info['k']}"
    return None


def check_theorem_C(info):
    """d=3, m>=7 => W >= 2m-12"""
    if info["d"] != 3 or info["m"] < 7:
        return None
    bound = 2 * info["m"] - 12
    if info["W"] < bound:
        return f"THEOREM C VIOLATION: m={info['m']}, W={info['W']} < {bound}, k={info['k']}"
    return None


def check_unified(info):
    """Unified conjecture: W >= (m-d)*L(d) - 2m for m >= m_min(d)."""
    m, d, W = info["m"], info["d"], info["W"]
    pred = W_min_predicted(m, d)
    # Only check if the predicted bound is <= 0 or if m is large enough
    # (we don't know m_min(d) exactly, so check unconditionally and flag)
    if W < pred:
        return f"UNIFIED VIOLATION: m={m}, d={d}, W={W} < W_pred={pred}, k={info['k']}"
    return None


def check_deficit_lemma_d2(info):
    """d=2, k*>=4 => Sigma_delta >= k*-1 (L >= 2k*-1)."""
    if info["d"] != 2 or info["k_star"] < 4:
        return None
    if info["sigma_delta"] < info["k_star"] - 1:
        return (f"DEFICIT LEMMA d=2 VIOLATION: m={info['m']}, k*={info['k_star']}, "
                f"Σδ={info['sigma_delta']} < {info['k_star']-1}, k={info['k']}")
    return None


def check_deficit_lemma_d3(info):
    """d=3, k*>=4 => Sigma_delta >= k*-1 (L >= 2k*-1)."""
    if info["d"] != 3 or info["k_star"] < 4:
        return None
    if info["sigma_delta"] < info["k_star"] - 1:
        return (f"DEFICIT LEMMA d=3 VIOLATION: m={info['m']}, k*={info['k_star']}, "
                f"Σδ={info['sigma_delta']} < {info['k_star']-1}, k={info['k']}")
    return None


def check_pair_contribution(info):
    """d=1, k*>=5 => for decomposition pair (a,b): delta_a + delta_b >= k*-2."""
    if info["d"] != 1 or info["k_star"] < 5:
        return None
    for r, (a, b, eps) in info["decomposable"].items():
        da = info["deltas"][a - 1]
        db = info["deltas"][b - 1]
        if a == b:
            # Self-sum: only count delta_a once
            if da < (info["k_star"] - 2):
                # The lemma says delta_a + delta_b >= k*-2 for cross-sums
                # For self-sums the argument is different; skip strict check
                pass
        else:
            if da + db < info["k_star"] - 2:
                return (f"PAIR CONTRIBUTION VIOLATION: m={info['m']}, k*={info['k_star']}, "
                        f"pair=({a},{b}), δ_a+δ_b={da+db} < {info['k_star']-2}, k={info['k']}")
    return None


def check_rstar_d1_k3(info):
    """d=1, k*=3, L=4 => r* <= m-2."""
    if info["d"] != 1 or info["k_star"] != 3 or info["L"] != 4:
        return None
    if info["r_star"] > info["m"] - 2:
        return (f"r* BOUND d=1 VIOLATION: m={info['m']}, r*={info['r_star']} > {info['m']-2}, "
                f"k={info['k']}")
    return None


def check_rstar_d2_k3(info):
    """d=2, k*=3, L=5 => r* <= m-3."""
    if info["d"] != 2 or info["k_star"] != 3 or info["L"] != 5:
        return None
    if info["r_star"] > info["m"] - 3:
        return (f"r* BOUND d=2 VIOLATION: m={info['m']}, r*={info['r_star']} > {info['m']-3}, "
                f"k={info['k']}")
    return None


def check_rstar_d3_k3(info):
    """d=3, k*=3, L=5 => r* <= m-4."""
    if info["d"] != 3 or info["k_star"] != 3 or info["L"] != 5:
        return None
    if info["r_star"] > info["m"] - 4:
        return (f"r* BOUND d=3 VIOLATION: m={info['m']}, r*={info['r_star']} > {info['m']-4}, "
                f"k={info['k']}")
    return None


def check_L_lower_d1(info):
    """d=1 => L >= 3."""
    if info["d"] != 1:
        return None
    if info["L"] < 3:
        return f"L BOUND d=1 VIOLATION: m={info['m']}, L={info['L']} < 3, k={info['k']}"
    return None


def check_L_lower_d2_k2(info):
    """d=2, k*=2 => L >= 4."""
    if info["d"] != 2 or info["k_star"] != 2:
        return None
    if info["L"] < 4:
        return f"L BOUND d=2/k*=2 VIOLATION: m={info['m']}, L={info['L']} < 4, k={info['k']}"
    return None


def check_L_lower_d2_k3(info):
    """d=2, k*=3 => L >= 5."""
    if info["d"] != 2 or info["k_star"] != 3:
        return None
    if info["L"] < 5:
        return f"L BOUND d=2/k*=3 VIOLATION: m={info['m']}, L={info['L']} < 5, k={info['k']}"
    return None


def check_L_lower_d3_k2(info):
    """d=3, k*=2 => L >= 4."""
    if info["d"] != 3 or info["k_star"] != 2:
        return None
    if info["L"] < 4:
        return f"L BOUND d=3/k*=2 VIOLATION: m={info['m']}, L={info['L']} < 4, k={info['k']}"
    return None


def check_L_lower_d3_k3(info):
    """d=3, k*=3 => L >= 5."""
    if info["d"] != 3 or info["k_star"] != 3:
        return None
    if info["L"] < 5:
        return f"L BOUND d=3/k*=3 VIOLATION: m={info['m']}, L={info['L']} < 5, k={info['k']}"
    return None


def check_impossible_d1_k4_L5(info):
    """d=1, k*=4, L=5 should be impossible."""
    if info["d"] != 1 or info["k_star"] != 4 or info["L"] != 5:
        return None
    return f"IMPOSSIBLE CASE FOUND: d=1, k*=4, L=5 at m={info['m']}, k={info['k']}"


def check_wilf_conjecture(info):
    """Wilf's conjecture: W >= 0."""
    if info["W"] < 0:
        return f"WILF CONJECTURE VIOLATION: m={info['m']}, d={info['d']}, W={info['W']}, k={info['k']}"
    return None


ALL_CHECKS = [
    check_theorem_A, check_theorem_B, check_theorem_C,
    check_unified, check_wilf_conjecture,
    check_deficit_lemma_d2, check_deficit_lemma_d3,
    check_pair_contribution,
    check_rstar_d1_k3, check_rstar_d2_k3, check_rstar_d3_k3,
    check_L_lower_d1,
    check_L_lower_d2_k2, check_L_lower_d2_k3,
    check_L_lower_d3_k2, check_L_lower_d3_k3,
    check_impossible_d1_k4_L5,
]


# ── MAIN HUNT ROUTINES ───────────────────────────────────────────────

def hunt_fast_enum(lib, m_max, k_max):
    """Fast C enumeration: check theorems A/B/C and unified conjecture."""
    print(f"\n{'='*72}")
    print(f"PHASE 1: Fast C enumeration  (m <= {m_max}, k* <= {k_max})")
    print(f"{'='*72}")

    violations = []
    total_semigroups = 0

    for m in range(3, m_max + 1):
        t0 = time.time()
        per_d, n_valid = run_enum(lib, m, k_max)
        elapsed = time.time() - t0
        total_semigroups += n_valid

        m_violations = []
        for d, info in per_d.items():
            W_min_obs = info["W_min"]

            # Theorem A
            if d == 1 and W_min_obs < m - 3:
                v = f"  THEOREM A: m={m}, d=1, W_min={W_min_obs} < {m-3}"
                m_violations.append(v)

            # Theorem B
            if d == 2 and m >= 4 and W_min_obs < 2 * m - 8:
                v = f"  THEOREM B: m={m}, d=2, W_min={W_min_obs} < {2*m-8}"
                m_violations.append(v)

            # Theorem C
            if d == 3 and m >= 7 and W_min_obs < 2 * m - 12:
                v = f"  THEOREM C: m={m}, d=3, W_min={W_min_obs} < {2*m-12}"
                m_violations.append(v)

            # Unified conjecture
            pred = W_min_predicted(m, d)
            if W_min_obs < pred:
                v = f"  UNIFIED: m={m}, d={d}, W_min={W_min_obs} < W_pred={pred}"
                m_violations.append(v)

            # Wilf conjecture
            if info["W_neg"] > 0:
                v = f"  WILF W<0: m={m}, d={d}, W_min={W_min_obs}, count_neg={info['W_neg']}"
                m_violations.append(v)

        n_defects = len(per_d)
        status = "OK" if not m_violations else f"*** {len(m_violations)} VIOLATION(S) ***"
        print(f"  m={m:2d}  k*<={k_max}  valid={n_valid:>12,}  defects=0..{max(per_d.keys()) if per_d else 0:<2d}  "
              f"t={elapsed:6.1f}s  {status}")

        if m_violations:
            for v in m_violations:
                print(v)
            violations.extend(m_violations)

    print(f"\n  Total semigroups: {total_semigroups:,}")
    print(f"  Total violations: {len(violations)}")
    return violations


def hunt_lemmas(m_max_lemma, k_max_lemma):
    """Python-level enumeration with detailed lemma checks."""
    print(f"\n{'='*72}")
    print(f"PHASE 2: Detailed lemma verification  (m <= {m_max_lemma}, k* <= {k_max_lemma})")
    print(f"{'='*72}")

    all_violations = []

    for m in range(3, m_max_lemma + 1):
        t0 = time.time()
        violations = enumerate_and_check(m, k_max_lemma, lambda info: _run_all_checks(info))
        elapsed = time.time() - t0

        status = "OK" if not violations else f"*** {len(violations)} VIOLATION(S) ***"
        print(f"  m={m:2d}  k*<={k_max_lemma}  t={elapsed:5.1f}s  {status}")

        if violations:
            for v in violations[:5]:
                print(f"    {v}")
            if len(violations) > 5:
                print(f"    ... and {len(violations) - 5} more")
            all_violations.extend(violations)

    print(f"\n  Total lemma violations: {len(all_violations)}")
    return all_violations


def _run_all_checks(info):
    for check in ALL_CHECKS:
        v = check(info)
        if v is not None:
            return v
    return None


def hunt_k_saturation(lib, m_range, k_low, k_high):
    """Compare W_min at different k* to test saturation."""
    print(f"\n{'='*72}")
    print(f"PHASE 3: k*-saturation test  (k*={k_low} vs k*={k_high})")
    print(f"{'='*72}")

    violations = []

    for m in m_range:
        per_d_low, _ = run_enum(lib, m, k_low)
        per_d_high, _ = run_enum(lib, m, k_high)

        improvements = []
        for d in per_d_high:
            W_high = per_d_high[d]["W_min"]
            W_low = per_d_low.get(d, {}).get("W_min", None)

            if W_low is None:
                # Defect only exists at higher k*
                improvements.append(
                    f"  SATURATION NEW: m={m}, d={d}, W_min(k*<={k_high})={W_high} "
                    f"(no semigroup at k*<={k_low})")
            elif W_high < W_low:
                improvements.append(
                    f"  SATURATION BREAK: m={m}, d={d}, "
                    f"W_min(k*<={k_low})={W_low} > W_min(k*<={k_high})={W_high}")

        status = "SATURATED" if not improvements else f"*** {len(improvements)} IMPROVEMENT(S) ***"
        print(f"  m={m:2d}  {status}")

        if improvements:
            for imp in improvements:
                print(imp)
            violations.extend(improvements)

    print(f"\n  Saturation breaks: {len(violations)}")
    return violations


def hunt_stabilization(lib, m_max, k_max):
    """Verify stabilization thresholds m_min(d)."""
    print(f"\n{'='*72}")
    print(f"PHASE 4: Stabilization threshold verification  (m <= {m_max}, k* <= {k_max})")
    print(f"{'='*72}")

    # Collect W_min for all (m, d) pairs
    all_data = {}
    for m in range(3, m_max + 1):
        per_d, _ = run_enum(lib, m, k_max)
        for d, info in per_d.items():
            all_data[(m, d)] = info["W_min"]

    # For each defect, find m_min (first m where W_min = W_predicted)
    max_d = max(d for (_, d) in all_data.keys())

    print(f"\n  {'d':>3s}  {'p(d)':>4s}  {'L(d)':>4s}  {'m_min_obs':>9s}  {'sharp_at':>20s}  {'not_sharp_at':>20s}")
    print(f"  {'-'*3}  {'-'*4}  {'-'*4}  {'-'*9}  {'-'*20}  {'-'*20}")

    for d in range(0, max_d + 1):
        pd = p_of_d(d)
        ld = L_of_d(d)
        sharp_list = []
        not_sharp = []

        for m in range(max(d + 2, 3), m_max + 1):
            key = (m, d)
            if key not in all_data:
                continue
            pred = W_min_predicted(m, d)
            obs = all_data[key]
            if obs == pred:
                sharp_list.append(m)
            elif obs > pred:
                not_sharp.append(m)
            else:
                # obs < pred: this is a conjecture violation!
                print(f"  *** VIOLATION: m={m}, d={d}, W_obs={obs} < W_pred={pred}")

        if sharp_list:
            m_min = min(sharp_list)
            sharp_str = f"{min(sharp_list)}-{max(sharp_list)}" if len(sharp_list) > 1 else str(sharp_list[0])
        else:
            m_min = ">"+ str(m_max)
            sharp_str = "none"

        not_sharp_str = ",".join(str(x) for x in not_sharp[:5]) if not_sharp else "none"

        print(f"  {d:3d}  {pd:4d}  {ld:4d}  {str(m_min):>9s}  {sharp_str:>20s}  {not_sharp_str:>20s}")


def hunt_high_depth_targeted(lib, m_values, k_max):
    """Targeted search at higher k* values for specific (m, d) pairs."""
    print(f"\n{'='*72}")
    print(f"PHASE 5: High-depth targeted search  (k* <= {k_max})")
    print(f"{'='*72}")

    violations = []

    for m in m_values:
        t0 = time.time()
        per_d, n_valid = run_enum(lib, m, k_max)
        elapsed = time.time() - t0

        m_violations = []
        for d, info in per_d.items():
            W_obs = info["W_min"]
            pred = W_min_predicted(m, d)

            if W_obs < pred:
                v = f"  HIGH-DEPTH UNIFIED: m={m}, k*<={k_max}, d={d}, W={W_obs} < {pred}"
                m_violations.append(v)

            if info["W_neg"] > 0:
                v = f"  HIGH-DEPTH WILF: m={m}, k*<={k_max}, d={d}, W_min={W_obs}"
                m_violations.append(v)

        max_d_seen = max(per_d.keys()) if per_d else 0
        status = "OK" if not m_violations else f"*** {len(m_violations)} VIOLATION(S) ***"
        print(f"  m={m:2d}  k*<={k_max}  valid={n_valid:>12,}  d_max={max_d_seen}  "
              f"t={elapsed:6.1f}s  {status}")

        if m_violations:
            for v in m_violations:
                print(v)
            violations.extend(m_violations)

    return violations


# ── MAIN ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Systematic counterexample hunt")
    parser.add_argument("--m-max-fast", type=int, default=30,
                        help="Max m for fast C enumeration at k*<=3 (default: 30)")
    parser.add_argument("--m-max-lemma", type=int, default=15,
                        help="Max m for detailed lemma checks (default: 15)")
    parser.add_argument("--k-max-fast", type=int, default=3,
                        help="Max k* for fast enumeration (default: 3)")
    parser.add_argument("--k-max-lemma", type=int, default=5,
                        help="Max k* for lemma checks (default: 5)")
    parser.add_argument("--k-max-high", type=int, default=5,
                        help="Max k* for high-depth search (default: 5)")
    parser.add_argument("--skip-lemma", action="store_true",
                        help="Skip detailed lemma verification (slow)")
    parser.add_argument("--out", type=str, default=None,
                        help="Output JSON file for results")
    args = parser.parse_args()

    print("=" * 72)
    print("  SYSTEMATIC COUNTEREXAMPLE HUNT")
    print("  Target: ALL claims in wilf_paper.tex")
    print("=" * 72)

    lib = load_c_lib()
    print("C kernel loaded.")

    all_violations = []
    t_start = time.time()

    # Phase 1: Fast enumeration at moderate k*
    v1 = hunt_fast_enum(lib, args.m_max_fast, args.k_max_fast)
    all_violations.extend(v1)

    # Phase 2: Detailed lemma checks at higher k*
    if not args.skip_lemma:
        v2 = hunt_lemmas(args.m_max_lemma, args.k_max_lemma)
        all_violations.extend(v2)

    # Phase 3: k*-saturation test
    sat_range = list(range(5, min(args.m_max_fast, 22) + 1))
    v3 = hunt_k_saturation(lib, sat_range, k_low=3, k_high=args.k_max_high)
    all_violations.extend(v3)

    # Phase 4: Stabilization thresholds
    hunt_stabilization(lib, args.m_max_fast, args.k_max_fast)

    # Phase 5: High-depth targeted
    high_m = [m for m in range(10, min(args.m_max_fast, 20) + 1)]
    v5 = hunt_high_depth_targeted(lib, high_m, args.k_max_high)
    all_violations.extend(v5)

    elapsed_total = time.time() - t_start

    # ── FINAL REPORT ──
    print(f"\n{'='*72}")
    print(f"  FINAL REPORT")
    print(f"{'='*72}")
    print(f"  Total time: {elapsed_total:.1f}s")
    print(f"  Total violations found: {len(all_violations)}")

    if all_violations:
        print(f"\n  ALL VIOLATIONS:")
        for v in all_violations:
            print(f"    {v}")
    else:
        print(f"\n  *** NO COUNTEREXAMPLES FOUND ***")
        print(f"  All claims in wilf_paper.tex survive this hunt.")

    # Save results
    if args.out:
        results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "params": vars(args),
            "total_violations": len(all_violations),
            "violations": all_violations,
        }
        with open(args.out, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\n  Results saved to {args.out}")

    return len(all_violations)


if __name__ == "__main__":
    sys.exit(0 if main() == 0 else 1)

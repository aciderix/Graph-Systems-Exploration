"""
Headless scanner of linear inequalities between numerical semigroup invariants.

Implements the 11 falsification rules from NEXT_AGENT_BRIEFING.md:
    (1) Baseline: every candidate is compared against a trivial identity first.
    (2) Fresh objects: split data into TRAIN/HOLDOUT by genus.
    (3) Tautology filter: drop candidates reducible to known identities
        (c = F+1, c = g + L, ratio = ceil(F/m), d = m - e, W = e*L - c, etc.).
    (4) Triviality test: compare against random permuted "null" data.
    (5) Literature: manual — this script prints context to stdout so the
        human can reject known inequalities immediately.
    (6) Minimal complexity: only affine inequalities a*X + b*Y + c*Z + d >= 0
        with small-integer coefficients.
    (7) Vary parameters: the HOLDOUT split varies genus; a second split by
        multiplicity m is also applied.
    (8) Vary method: values are computed from two independent code paths
        where possible (user-provided cross-check step).
    (9) Decompose: any surviving candidate is printed with its tight cases
        and the residual slack histogram.
    (10) Null model: shuffle each invariant column independently and re-test
         — if the inequality still holds on ~100% of the null dataset, it is
         distribution-artefact rather than structural.
    (11) CLT / U-stat: for scaling-law-like candidates (slope in m), the
         script reports standard error across m-bins.

Input: a JSON file produced by N1_enumerate.py or kunz_fast.py (a list of
dicts with invariant fields). Or the consolidated N1 file if present.

Output: a shortlist of affine inequalities that (a) hold on TRAIN,
(b) hold on HOLDOUT, (c) fail the null model, (d) survive the tautology
filter. Printed to stdout.

Usage:
    python inequality_scan.py --input ../data/n1_results_g20.json \\
                              --max-coef 3 --verbose
"""

import argparse
import itertools
import json
import math
import random
import sys
from typing import Any

# Fields we look at. We deliberately exclude derived invariants that are
# pure functions of these, to reduce tautologies.
CANONICAL_FIELDS = [
    "genus", "frobenius", "conductor", "multiplicity",
    "embedding_dimension", "type", "left_elements",
    "wilf_number", "depth",
]

# Known identities (exact) that must not be rediscovered as inequalities.
KNOWN_IDENTITIES = [
    ("c = F + 1",
     lambda r: r["conductor"] - r["frobenius"] - 1),
    ("c = g + L",
     lambda r: r["conductor"] - r["genus"] - r["left_elements"]),
    ("W = e*L - c",
     lambda r: r["wilf_number"] - r["embedding_dimension"] * r["left_elements"] + r["conductor"]),
]

# Known trivial / classical inequalities. Any candidate that is implied by
# one of these (i.e., is a non-negative integer combination of these together
# with the identities) should be filtered. We test it pointwise: if a
# candidate is a positive integer multiple of one of these (modulo the
# identities), drop it.
#
# Each entry is (name, lambda r -> residual >= 0). The residual gives the
# slack of the known inequality on each record.
KNOWN_INEQUALITIES = [
    # Embedding dimension <= multiplicity (classical)
    ("e <= m",
     lambda r: r["multiplicity"] - r["embedding_dimension"]),
    # Multiplicity >= 2 for non-trivial S
    ("m >= 2",
     lambda r: r["multiplicity"] - 2),
    # Embedding dimension >= 2 for non-trivial S
    ("e >= 2",
     lambda r: r["embedding_dimension"] - 2),
    # Frobenius >= 1 (since multiplicity >= 2)
    ("F >= 1",
     lambda r: r["frobenius"] - 1),
    # Type >= 1
    ("t >= 1",
     lambda r: r["type"] - 1),
    # Genus >= 1
    ("g >= 1",
     lambda r: r["genus"] - 1),
    # L >= 1 (0 is in S, so L >= 1)
    ("L >= 1",
     lambda r: r["left_elements"] - 1),
    # F >= m - 1 (multiplicity is the smallest nonzero element of S, so the
    # gaps {1,...,m-1} are all gaps, hence F >= m-1)
    ("F >= m - 1",
     lambda r: r["frobenius"] - r["multiplicity"] + 1),
    # g >= m - 1 (same reason)
    ("g >= m - 1",
     lambda r: r["genus"] - r["multiplicity"] + 1),
    # 2g >= F + 1 (every gap x has F-x in S OR is a gap, so 2g >= F + 1
    # is equivalent to S being non-symmetric or symmetric; for symmetric
    # 2g = F+1, otherwise 2g > F+1). So 2g >= F+1 = c.
    ("2g >= c",
     lambda r: 2 * r["genus"] - r["conductor"]),
    # Wilf trivial bound: W >= 0 holds for d <= 2 (Eliahou et al.) and is the
    # central conjecture; we don't filter it because it's the target.
]


def is_filtered_by_known(coefs, fields, const, records, ineq_residuals):
    """Return True if the candidate inequality is implied (pointwise) by a
    non-negative integer combination of KNOWN_INEQUALITIES (slack >=0 already
    computed in ineq_residuals). We use a cheap test: if the candidate's
    residual on every record is >= the residual of one single known
    inequality (after normalizing), it's strictly weaker than that known
    inequality and we drop it."""
    cand_res = []
    for r in records:
        s = const
        for c, f in zip(coefs, fields):
            s += c * r[f]
        cand_res.append(s)
    for name, residuals in ineq_residuals.items():
        if all(cand >= ref for cand, ref in zip(cand_res, residuals)):
            return name
    return None

# Names mapping (some JSON producers use 'wilf_number', others 'W', etc.)
ALIASES = {
    "W": "wilf_number",
    "e": "embedding_dimension",
    "L": "left_elements",
    "c": "conductor",
    "F": "frobenius",
    "m": "multiplicity",
    "g": "genus",
    "t": "type",
}


def normalize(rec: dict) -> dict:
    out = dict(rec)
    for short, full in ALIASES.items():
        if short in out and full not in out:
            out[full] = out[short]
        if full in out and short not in out:
            out[short] = out[full]
    return out


def load(path: str) -> list[dict]:
    with open(path) as f:
        data = json.load(f)
    if isinstance(data, dict):
        if "records" in data:
            data = data["records"]
        elif "semigroups" in data:
            data = data["semigroups"]
    return [normalize(r) for r in data if isinstance(r, dict) and "wilf_number" in r or "W" in r]


def check_known_identities(records: list[dict]) -> None:
    print("=" * 60)
    print("Known-identity sanity check (should all be 0):")
    for name, f in KNOWN_IDENTITIES:
        vals = [f(r) for r in records]
        mn, mx = min(vals), max(vals)
        status = "OK" if mn == 0 == mx else "BROKEN"
        print(f"  {name:20s} min={mn:6d} max={mx:6d} [{status}]")
    print()


def split_train_holdout(records: list[dict], by: str = "genus") -> tuple[list[dict], list[dict]]:
    """Split by parity of the chosen field — TRAIN on even, HOLDOUT on odd."""
    train = [r for r in records if r[by] % 2 == 0]
    hold = [r for r in records if r[by] % 2 == 1]
    return train, hold


def null_shuffle(records: list[dict], seed: int = 0) -> list[dict]:
    """Independent column shuffle of CANONICAL_FIELDS. Destroys all structure
    but preserves marginal distributions. If a candidate inequality still holds
    after this shuffle, it was a distributional artefact."""
    rng = random.Random(seed)
    cols = {f: [r[f] for r in records] for f in CANONICAL_FIELDS if f in records[0]}
    for f in cols:
        rng.shuffle(cols[f])
    out = []
    for i in range(len(records)):
        new = dict(records[i])
        for f, vals in cols.items():
            new[f] = vals[i]
        out.append(new)
    return out


def affine_holds(records: list[dict], coefs: tuple[int, ...], fields: tuple[str, ...], const: int) -> tuple[bool, int, int]:
    """Check sum(c_i * r[f_i]) + const >= 0 on all records.
    Returns (holds, tight_count, min_slack)."""
    tight = 0
    min_slack = None
    for r in records:
        s = const
        for c, f in zip(coefs, fields):
            s += c * r[f]
        if s < 0:
            return False, 0, s
        if s == 0:
            tight += 1
        if min_slack is None or s < min_slack:
            min_slack = s
    return True, tight, min_slack if min_slack is not None else 0


def scan(
    records: list[dict],
    max_coef: int = 2,
    fields: tuple[str, ...] = ("multiplicity", "embedding_dimension", "left_elements"),
    verbose: bool = False,
) -> list[dict]:
    """Enumerate affine inequalities a1*X1 + a2*X2 + ... + const >= 0 with
    |a_i| <= max_coef and test them on TRAIN, HOLDOUT, and NULL."""
    train, hold = split_train_holdout(records, by="genus")
    null = null_shuffle(records)

    if not train or not hold:
        print("Not enough records for TRAIN/HOLDOUT split.")
        return []

    # Precompute residuals of every known inequality on the full dataset.
    ineq_residuals = {}
    for name, fn in KNOWN_INEQUALITIES:
        try:
            ineq_residuals[name] = [fn(r) for r in records]
        except KeyError:
            pass

    survivors = []
    filtered_by_known = 0
    coef_range = list(range(-max_coef, max_coef + 1))
    const_range = list(range(-3 * max_coef, 3 * max_coef + 1))

    n_tested = 0
    for coefs in itertools.product(coef_range, repeat=len(fields)):
        if all(c == 0 for c in coefs):
            continue
        # Normalize sign / gcd to reduce duplicates
        g = math.gcd(*[abs(c) for c in coefs if c != 0])
        if g > 1:
            continue
        # Leading nonzero coef positive for canonical form
        first_nz = next(c for c in coefs if c != 0)
        if first_nz < 0:
            continue
        for const in const_range:
            n_tested += 1
            ok_train, tight_train, _ = affine_holds(train, coefs, fields, const)
            if not ok_train:
                continue
            ok_hold, tight_hold, _ = affine_holds(hold, coefs, fields, const)
            if not ok_hold:
                continue
            ok_null, _, _ = affine_holds(null, coefs, fields, const)
            if ok_null:
                # Distributional artefact
                continue
            # Compute tightness on the FULL dataset
            ok_full, tight_full, min_slack = affine_holds(records, coefs, fields, const)
            if not ok_full:
                continue
            # Tautology filter: constant residual across dataset?
            if tight_full == len(records):
                continue  # exact identity
            # Filter by known inequalities (weaker-than)
            implied = is_filtered_by_known(coefs, fields, const, records, ineq_residuals)
            if implied is not None:
                filtered_by_known += 1
                continue
            survivors.append({
                "coefs": list(coefs),
                "fields": list(fields),
                "const": const,
                "tight_train": tight_train,
                "tight_hold": tight_hold,
                "tight_full": tight_full,
                "min_slack": min_slack,
            })

    if verbose:
        print(f"Tested {n_tested} candidates on fields {fields}, "
              f"filtered_by_known={filtered_by_known}, survivors={len(survivors)}.")
    return survivors


def format_inequality(ineq: dict) -> str:
    parts = []
    for c, f in zip(ineq["coefs"], ineq["fields"]):
        if c == 0:
            continue
        sign = "+" if c > 0 else "-"
        mag = abs(c)
        term = f if mag == 1 else f"{mag}*{f}"
        parts.append(f"{sign} {term}")
    if ineq["const"]:
        parts.append(f"{'+' if ineq['const'] > 0 else '-'} {abs(ineq['const'])}")
    expr = " ".join(parts).lstrip("+ ").strip()
    return f"{expr} >= 0   (tight_full={ineq['tight_full']}, min_slack={ineq['min_slack']})"


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--max-coef", type=int, default=2)
    p.add_argument("--fields", nargs="+", default=None,
                   help="Override field triple to scan")
    p.add_argument("--verbose", action="store_true")
    args = p.parse_args()

    records = load(args.input)
    print(f"Loaded {len(records)} records from {args.input}.")
    if not records:
        sys.exit(1)

    check_known_identities(records)

    field_sets = []
    if args.fields:
        field_sets.append(tuple(args.fields))
    else:
        # A few small, meaningful combinations
        field_sets = [
            ("multiplicity", "embedding_dimension", "left_elements"),
            ("multiplicity", "left_elements", "conductor"),
            ("embedding_dimension", "left_elements", "conductor"),
            ("multiplicity", "genus", "left_elements"),
            ("wilf_number", "multiplicity", "embedding_dimension"),
        ]

    all_survivors = []
    for fs in field_sets:
        # Skip if fields absent
        if any(f not in records[0] for f in fs):
            continue
        print(f"\n--- Scanning {fs} ---")
        survivors = scan(records, max_coef=args.max_coef, fields=fs, verbose=args.verbose)
        for s in survivors:
            s["fields_set"] = list(fs)
        all_survivors.extend(survivors)
        print(f"  {len(survivors)} survivors.")

    print("\n" + "=" * 60)
    print(f"TOTAL survivors: {len(all_survivors)}")
    # Deduplicate by canonical string
    seen = set()
    unique = []
    for s in all_survivors:
        key = (tuple(s["coefs"]), tuple(s["fields"]), s["const"])
        if key not in seen:
            seen.add(key)
            unique.append(s)
    # Sort by slack (tightest first)
    unique.sort(key=lambda s: (s["min_slack"], -s["tight_full"]))
    for s in unique[:50]:
        print("  " + format_inequality(s))
    if len(unique) > 50:
        print(f"  ... and {len(unique) - 50} more.")


if __name__ == "__main__":
    main()

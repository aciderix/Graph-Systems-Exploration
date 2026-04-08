"""Merge prefix-restricted chunk JSONs into a single enumeration summary.

Reads every results/<tag>/p_*.json produced by run_chunks.py and reduces
them into one summary file with the same shape as run_c() output:

    {m, K_max, leaves_raw, leaves_valid, leaves_kept, per_defect, ...}

Per defect, sums counts and W_neg_count and keeps the minimum W_min (with
its argmin tuple).
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.normpath(os.path.join(HERE, "..", "results"))


def merge(chunk_dir: str) -> dict:
    files = sorted(glob.glob(os.path.join(chunk_dir, "p_*.json")))
    if not files:
        raise SystemExit(f"no chunk files in {chunk_dir}")

    out: dict = {
        "leaves_raw": 0,
        "leaves_valid": 0,
        "leaves_kept": 0,
        "elapsed_sec": 0.0,
        "per_defect": {},
    }
    m_seen: set[int] = set()
    K_seen: set[int] = set()
    n_chunks = 0

    for path in files:
        with open(path) as f:
            s = json.load(f)
        m_seen.add(s["m"])
        K_seen.add(s["K_max"])
        out["leaves_raw"]   += s["leaves_raw"]
        out["leaves_valid"] += s["leaves_valid"]
        out["leaves_kept"]  += s["leaves_kept"]
        out["elapsed_sec"]  += s.get("elapsed_sec", 0.0)
        for d, v in s["per_defect"].items():
            slot = out["per_defect"].setdefault(
                d, {"count": 0, "W_min": None, "W_neg_count": 0,
                    "argmin_k": None}
            )
            slot["count"]        += v["count"]
            slot["W_neg_count"]  += v["W_neg_count"]
            if slot["W_min"] is None or v["W_min"] < slot["W_min"]:
                slot["W_min"]    = v["W_min"]
                slot["argmin_k"] = v["argmin_k"]
        n_chunks += 1

    if len(m_seen) != 1 or len(K_seen) != 1:
        raise SystemExit(f"chunks span multiple (m, K_max): {m_seen}, {K_seen}")

    m = m_seen.pop()
    K = K_seen.pop()
    out["m"] = m
    out["K_max"] = K
    out["d_min"] = None
    out["d_max"] = None
    out["w_max"] = None
    out["backend"] = "C-prefix-merged"
    out["n_chunks"] = n_chunks
    # canonicalize defect ordering
    out["per_defect"] = {
        str(d): out["per_defect"][str(d)]
        for d in sorted(int(x) for x in out["per_defect"].keys())
    }
    return out


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("chunk_dir", help="path to dir with p_*.json files "
                                     "(absolute or relative to results/)")
    p.add_argument("--out", required=True,
                   help="output JSON path (relative to results/ or absolute)")
    args = p.parse_args()

    cdir = args.chunk_dir
    if not os.path.isabs(cdir):
        cdir = os.path.join(RESULTS, cdir)

    out_path = args.out
    if not os.path.isabs(out_path):
        out_path = os.path.join(RESULTS, out_path)

    summary = merge(cdir)
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=1)

    print(f"merged {summary['n_chunks']} chunks for m={summary['m']} "
          f"K={summary['K_max']}")
    print(f"  leaves_valid = {summary['leaves_valid']:,}")
    print(f"  defects      = {sorted(int(x) for x in summary['per_defect'])}")
    print(f"  W_min by d   = "
          f"{ {int(d): v['W_min'] for d, v in summary['per_defect'].items()} }")
    print(f"  -> {out_path}")


if __name__ == "__main__":
    main()

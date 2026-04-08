"""Run a Kunz enumeration as independent prefix-restricted chunks.

Splits a full (m, K_max) enumeration over all valid (k_1, ..., k_p) prefixes
of length p (default 3), running each chunk via kunz_fast.run_c with
k_prefix= set. Each chunk's output is written to a separate JSON file under
results/<tag>_chunks/, so:

  * any chunk that finishes is durable -- a re-run skips it,
  * a killed chunk loses only its own work, not the rest,
  * the union of all chunks reproduces an unrestricted enumeration exactly.

Usage:
    python run_chunks.py m K_max [--prefix-len 3] [--workers 4] [--tag NAME]

After all chunks are present, merge_chunks.py reduces them into a single
summary file matching the format of the existing results/mNNkK.json files.
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import os
import sys
import time

import kunz_fast as kf

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.normpath(os.path.join(HERE, "..", "results"))


def valid_prefixes(K_max: int, plen: int) -> list[tuple[int, ...]]:
    """All Kunz prefixes (k_1, ..., k_plen) compatible with the no-carry
    forward checks (k_r <= k_a + k_b for a+b=r within the prefix)."""
    out: list[tuple[int, ...]] = []

    def rec(p: list[int]) -> None:
        if len(p) == plen:
            out.append(tuple(p))
            return
        r = len(p) + 1
        ub = K_max
        for a in range(1, r):
            b = r - a
            v = p[a - 1] + p[b - 1]
            if v < ub:
                ub = v
        for v in range(1, ub + 1):
            p.append(v)
            rec(p)
            p.pop()

    rec([])
    return out


def chunk_path(chunk_dir: str, prefix: tuple[int, ...]) -> str:
    return os.path.join(chunk_dir, "p_" + "_".join(str(x) for x in prefix) + ".json")


def run_one(args: tuple[int, int, tuple[int, ...], str]) -> tuple[tuple, float, bool]:
    m, K_max, prefix, path = args
    if os.path.exists(path):
        return prefix, 0.0, True  # already done
    t0 = time.time()
    summary = kf.run_c(m, K_max, k_prefix=list(prefix))
    with open(path, "w") as f:
        json.dump(summary, f, indent=1)
    return prefix, time.time() - t0, False


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("m", type=int)
    p.add_argument("K_max", type=int)
    p.add_argument("--prefix-len", type=int, default=3)
    p.add_argument("--workers", type=int, default=4)
    p.add_argument("--tag", type=str, default=None,
                   help="output dir name (default mMMkKK_chunks)")
    args = p.parse_args()

    tag = args.tag or f"m{args.m}k{args.K_max}_chunks"
    chunk_dir = os.path.join(RESULTS, tag)
    os.makedirs(chunk_dir, exist_ok=True)

    prefixes = valid_prefixes(args.K_max, args.prefix_len)
    print(f"# {len(prefixes)} prefixes of length {args.prefix_len} for K={args.K_max}")
    print(f"# chunk dir: {chunk_dir}")
    print(f"# workers:   {args.workers}")
    sys.stdout.flush()

    todo = [(args.m, args.K_max, pre, chunk_path(chunk_dir, pre)) for pre in prefixes]
    t_start = time.time()

    with cf.ProcessPoolExecutor(max_workers=args.workers) as pool:
        for prefix, dt, was_cached in pool.map(run_one, todo):
            if was_cached:
                tag = "cache"
            else:
                tag = f"{dt:7.1f}s"
            elapsed = time.time() - t_start
            print(f"  done {prefix}  {tag}   "
                  f"(wall so far {elapsed:7.1f}s)")
            sys.stdout.flush()

    print(f"all chunks present in {chunk_dir}")


if __name__ == "__main__":
    main()

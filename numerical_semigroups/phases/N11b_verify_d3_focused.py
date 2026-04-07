"""
N11b: Focused verification of Theorem C (d=3, W >= 2m-12)
Verifies on m=5..9 (485,858 semigroups) with detailed sub-claim analysis.
"""

from itertools import product
from collections import defaultdict

def is_valid_and_stats(m, kunz):
    """Check validity, compute d and stats. Returns None if invalid or d != 3."""
    n = m - 1
    # Check Kunz inequalities and find decomposable residues
    decomp = set()
    for a in range(1, m):
        for b in range(a, m):
            j = (a + b) % m
            if j == 0:
                continue
            eps = (a + b) // m
            lhs = kunz[a-1] + kunz[b-1] + eps
            if kunz[j-1] > lhs:
                return None  # invalid
            if kunz[j-1] == lhs:
                decomp.add(j)

    if len(decomp) != 3:
        return None

    e = m - 3
    k_star = min(kunz)
    r_star_idx = kunz.index(k_star)
    r_star = r_star_idx + 1

    apery = [m * kunz[j] + (j+1) for j in range(n)]
    F = max(apery) - m
    c = F + 1

    L = F // m + 1
    for j in range(1, m):
        max_t = (F - j) // m
        if max_t >= kunz[j-1]:
            L += max_t - kunz[j-1] + 1

    W = e * L - c

    # Find decomposition sources
    sources = set()
    decomp_pairs = defaultdict(list)
    for j in decomp:
        for a in range(1, m):
            for b in range(a, m):
                if (a + b) % m != j:
                    continue
                eps = (a + b) // m
                if kunz[a-1] + kunz[b-1] + eps == kunz[j-1]:
                    decomp_pairs[j].append((a, b))
                    sources.add(a)
                    sources.add(b)

    # Sum of deficits for source residues
    source_only = sources - decomp
    sum_delta = sum(k_star - 1 - kunz[s-1] for s in source_only if kunz[s-1] < k_star)

    return {
        'W': W, 'L': L, 'c': c, 'e': e,
        'k_star': k_star, 'r_star': r_star,
        'decomp': decomp, 'sources': source_only,
        'sum_delta': sum_delta, 'kunz': tuple(kunz),
        'decomp_pairs': dict(decomp_pairs)
    }


def enumerate_d3(m, max_k=None):
    """Enumerate semigroups with multiplicity m and d=3."""
    if max_k is None:
        max_k = max(m + 2, 10)
    n = m - 1
    results = []

    def recurse(idx, kv):
        if idx == n:
            stats = is_valid_and_stats(m, kv)
            if stats:
                results.append(stats)
            return
        for k in range(1, max_k + 1):
            kv.append(k)
            # Prune: check partial inequalities
            ok = True
            for a in range(1, idx + 2):
                for b in range(a, idx + 2):
                    j = (a + b) % m
                    if j == 0 or j > idx + 1:
                        continue
                    eps = (a + b) // m
                    if kv[j-1] > kv[a-1] + kv[b-1] + eps:
                        ok = False
                        break
                if not ok:
                    break
            if ok:
                recurse(idx + 1, kv)
            kv.pop()

    recurse(0, [])
    return results


def main():
    print("=" * 70)
    print("THEOREM C VERIFICATION: d=3, W >= 2m - 12")
    print("=" * 70)

    total = 0
    total_violations = 0
    tight_all = {}
    kstar_Lmin = defaultdict(lambda: float('inf'))
    kstar3_rstar_max_L5 = defaultdict(lambda: -1)
    deficit_issues = []

    for m in range(5, 10):
        sgs = enumerate_d3(m)
        count = len(sgs)
        total += count
        W_min = min(sg['W'] for sg in sgs) if sgs else None
        bound = 2 * m - 12
        viols = [sg for sg in sgs if sg['W'] < bound]
        total_violations += len(viols)
        tight = [sg for sg in sgs if sg['W'] == bound and m >= 7]

        if tight:
            tight_all[m] = tight

        # Sub-claims
        for sg in sgs:
            k = sg['k_star']
            kstar_Lmin[(m, k)] = min(kstar_Lmin[(m, k)], sg['L'])
            if k == 3 and sg['L'] == 5:
                kstar3_rstar_max_L5[(m,)] = max(kstar3_rstar_max_L5[(m,)], sg['r_star'])
            if k >= 4 and sg['sum_delta'] < k:
                deficit_issues.append((m, sg))

        print(f"m={m:2d}: {count:6d} sgs, W_min={W_min:4d}, bound={bound:4d}, "
              f"violations={len(viols)}, tight={len(tight)}")

    print(f"\nTotal: {total} semigroups, {total_violations} violations")

    # L bounds by k*
    print("\n--- L BOUNDS BY k* ---")
    for m in range(5, 10):
        parts = []
        for k in range(2, 10):
            if (m, k) in kstar_Lmin and kstar_Lmin[(m, k)] < float('inf'):
                parts.append(f"k*={k}:L>={kstar_Lmin[(m,k)]}")
        if parts:
            print(f"  m={m}: {', '.join(parts)}")

    # r* constraint for k*=3, L=5
    print("\n--- r* CONSTRAINT: k*=3, L=5 ---")
    for m in range(7, 10):
        if (m,) in kstar3_rstar_max_L5:
            print(f"  m={m}: max r* = {kstar3_rstar_max_L5[(m,)]}, m-4 = {m-4}")

    # Tight examples
    print("\n--- TIGHT EXAMPLES (W = 2m-12) ---")
    for m in sorted(tight_all):
        print(f"\n  m={m} ({len(tight_all[m])} examples):")
        for sg in tight_all[m][:6]:
            print(f"    kunz={sg['kunz']}, k*={sg['k_star']}, r*={sg['r_star']}, "
                  f"L={sg['L']}, c={sg['c']}")

    # Deficit issues for k* >= 4
    print("\n--- DEFICIT ANALYSIS (k* >= 4, Σδ < k*) ---")
    if deficit_issues:
        print(f"  {len(deficit_issues)} cases with Σδ < k*:")
        for m, sg in deficit_issues[:15]:
            print(f"    m={m}, k*={sg['k_star']}, Σδ={sg['sum_delta']}, "
                  f"r*={sg['r_star']}, L={sg['L']}, W={sg['W']}, "
                  f"bound={2*m-12}, OK={sg['W'] >= 2*m-12}")
    else:
        print("  None found.")

    print(f"\n{'PASS' if total_violations == 0 else 'FAIL'}: "
          f"W >= 2m-12 holds for all {total} semigroups with d=3, m=5..9")


if __name__ == '__main__':
    main()

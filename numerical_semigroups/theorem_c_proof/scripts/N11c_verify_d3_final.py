"""
N11c: Final verification of Theorem C (d=3, W >= 2m-12)
Uses correct convention: k* = max Kunz level (depth), r* = max residue at max level.
"""

from collections import defaultdict

def is_valid_and_stats(m, kunz):
    """Check validity, compute d and stats. Returns None if invalid or d != 3."""
    n = m - 1
    decomp = set()
    # Track which pairs witness decomposability
    witness_pairs = defaultdict(list)

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
                witness_pairs[j].append((a, b))

    if len(decomp) != 3:
        return None

    e = m - 3  # embedding dimension

    # k* = max level (depth), r* = max residue at max level
    k_star = max(kunz)
    r_star = max(i+1 for i in range(n) if kunz[i] == k_star)

    # Conductor
    c = (k_star - 1) * m + r_star + 1

    # Frobenius number
    F = (k_star - 1) * m + r_star

    # L = k* + Σδ
    sum_delta = 0
    for i in range(1, m):
        k_i = kunz[i-1]
        if i <= r_star:
            sum_delta += k_star - k_i
        else:
            sum_delta += max(0, k_star - 1 - k_i)
    L = k_star + sum_delta

    W = e * L - c

    # Find source residues (non-decomposable residues used in decomposition pairs)
    sources = set()
    for j in decomp:
        for (a, b) in witness_pairs[j]:
            if a not in decomp:
                sources.add(a)
            if b not in decomp:
                sources.add(b)

    # For deficit analysis: deficit of source j is
    # For j <= r*: delta_j = k* - k_j
    # For j > r*: delta_j = max(0, k* - 1 - k_j)
    source_deficit = 0
    for s in sources:
        k_s = kunz[s-1]
        if s <= r_star:
            source_deficit += k_star - k_s
        else:
            source_deficit += max(0, k_star - 1 - k_s)

    return {
        'W': W, 'L': L, 'c': c, 'e': e,
        'k_star': k_star, 'r_star': r_star,
        'decomp': decomp, 'sources': sources,
        'sum_delta': sum_delta, 'source_deficit': source_deficit,
        'kunz': tuple(kunz), 'witness_pairs': dict(witness_pairs)
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
    print("Convention: k* = max Kunz level (depth)")
    print("=" * 70)

    total = 0
    total_violations = 0
    tight_all = {}
    kstar_Lmin = defaultdict(lambda: float('inf'))

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

        for sg in sgs:
            k = sg['k_star']
            kstar_Lmin[(m, k)] = min(kstar_Lmin[(m, k)], sg['L'])

        print(f"m={m:2d}: {count:6d} sgs, W_min={W_min:4d}, bound={bound:4d}, "
              f"violations={len(viols)}, tight={len(tight)}")

    print(f"\nTotal: {total} semigroups, {total_violations} violations")

    # L bounds by k*
    print("\n--- MIN L BY k* (depth) ---")
    for m in range(5, 10):
        parts = []
        for k in sorted(set(k for (mm, k) in kstar_Lmin if mm == m)):
            parts.append(f"k*={k}:L>={kstar_Lmin[(m,k)]}")
        if parts:
            print(f"  m={m}: {', '.join(parts)}")

    # Tight examples
    print("\n--- TIGHT EXAMPLES (W = 2m-12) ---")
    for m in sorted(tight_all):
        print(f"\n  m={m} ({len(tight_all[m])} examples):")
        for sg in tight_all[m][:8]:
            print(f"    kunz={sg['kunz']}, k*={sg['k_star']}, r*={sg['r_star']}, "
                  f"L={sg['L']}, c={sg['c']}, e={sg['e']}, W={sg['W']}")
            # Show decomposable residues and their witnesses
            for j in sorted(sg['decomp']):
                pairs = sg['witness_pairs'].get(j, [])
                print(f"      decomp res {j}: pairs {pairs}")

    # Verify sub-claims for k*=2
    print("\n--- k*=2 ANALYSIS (d=3) ---")
    for m in range(5, 10):
        sgs_k2 = [sg for sg in enumerate_d3(m) if sg['k_star'] == 2]
        if not sgs_k2:
            print(f"  m={m}: no k*=2 cases")
            continue
        L_min = min(sg['L'] for sg in sgs_k2)
        rstar_max = max(sg['r_star'] for sg in sgs_k2)
        W_min = min(sg['W'] for sg in sgs_k2)
        print(f"  m={m}: {len(sgs_k2)} sgs, min L={L_min}, max r*={rstar_max}, "
              f"min W={W_min}, bound={2*m-12}")

    # k*=3, L analysis
    print("\n--- k*=3 ANALYSIS (d=3) ---")
    for m in range(5, 10):
        sgs_k3 = [sg for sg in enumerate_d3(m) if sg['k_star'] == 3]
        if not sgs_k3:
            print(f"  m={m}: no k*=3 cases")
            continue
        L_min = min(sg['L'] for sg in sgs_k3)
        W_min = min(sg['W'] for sg in sgs_k3)
        # For L=5 cases
        L5 = [sg for sg in sgs_k3 if sg['L'] == 5]
        if L5:
            rstar_max_L5 = max(sg['r_star'] for sg in L5)
            print(f"  m={m}: {len(sgs_k3)} sgs, min L={L_min}, min W={W_min}, "
                  f"L=5 cases: {len(L5)}, max r*|L=5={rstar_max_L5}, m-4={m-4}")
        else:
            print(f"  m={m}: {len(sgs_k3)} sgs, min L={L_min}, min W={W_min}, "
                  f"no L=5 cases")

    # k*>=4 deficit analysis
    print("\n--- k*>=4 DEFICIT ANALYSIS (d=3) ---")
    deficit_violations = 0
    for m in range(5, 10):
        for sg in enumerate_d3(m):
            if sg['k_star'] >= 4:
                # Check: does W >= 2m-12 hold even when deficit is small?
                if sg['W'] < 2 * m - 12:
                    deficit_violations += 1
                    print(f"  VIOLATION: m={m}, k*={sg['k_star']}, W={sg['W']}")
    print(f"  k*>=4 deficit violations: {deficit_violations}")

    print(f"\n{'='*70}")
    print(f"FINAL RESULT: {'PASS' if total_violations == 0 else 'FAIL'}")
    print(f"W >= 2m-12 verified on {total} semigroups with d=3, m=5..9")
    print(f"{'='*70}")


if __name__ == '__main__':
    main()

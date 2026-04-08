"""
Exhaustive analysis of witness pair configurations for d=3, k*>=4.
Goal: understand all possible source/target patterns to write a rigorous proof.
"""
from collections import defaultdict

def is_valid_and_stats(m, kunz):
    n = m - 1
    decomp = set()
    witness_pairs = defaultdict(list)
    for a in range(1, m):
        for b in range(a, m):
            j = (a + b) % m
            if j == 0:
                continue
            eps = (a + b) // m
            lhs = kunz[a-1] + kunz[b-1] + eps
            if kunz[j-1] > lhs:
                return None
            if kunz[j-1] == lhs:
                decomp.add(j)
                witness_pairs[j].append((a, b))
    if len(decomp) != 3:
        return None

    k_star = max(kunz)
    r_star = max(i+1 for i in range(n) if kunz[i] == k_star)
    c = (k_star - 1) * m + r_star + 1
    F = (k_star - 1) * m + r_star

    sum_delta = 0
    for i in range(1, m):
        k_i = kunz[i-1]
        if i <= r_star:
            sum_delta += k_star - k_i
        else:
            sum_delta += max(0, k_star - 1 - k_i)
    L = k_star + sum_delta
    e = m - 3
    W = e * L - c

    # Classify sources
    sources = set()
    for j in decomp:
        for (a, b) in witness_pairs[j]:
            sources.add(a)
            sources.add(b)
    # Sources that are themselves decomposable
    decomp_sources = sources & decomp
    pure_sources = sources - decomp

    # Compute source deficit (pure sources only)
    pure_deficit = 0
    for s in pure_sources:
        k_s = kunz[s-1]
        if s <= r_star:
            pure_deficit += k_star - k_s
        else:
            pure_deficit += max(0, k_star - 1 - k_s)

    # Classify the 3 witness pairs by structure
    # For each decomposable residue, pick the "cheapest" witness pair
    # But actually all valid pairs matter
    pair_types = []
    for j in sorted(decomp):
        for (a, b) in witness_pairs[j]:
            a_pos = "<=r*" if a <= r_star else ">r*"
            b_pos = "<=r*" if b <= r_star else ">r*"
            a_decomp = "D" if a in decomp else "P"
            b_decomp = "D" if b in decomp else "P"
            t_pos = "<=r*" if j <= r_star else ">r*"
            pair_types.append({
                'target': j, 'a': a, 'b': b,
                'a_pos': a_pos, 'b_pos': b_pos,
                'a_type': a_decomp, 'b_type': b_decomp,
                't_pos': t_pos,
                'a_level': kunz[a-1], 'b_level': kunz[b-1],
                't_level': kunz[j-1]
            })

    # Count distinct source residues
    n_pure = len(pure_sources)
    n_decomp_src = len(decomp_sources)

    return {
        'W': W, 'L': L, 'c': c, 'k_star': k_star, 'r_star': r_star,
        'decomp': sorted(decomp), 'pure_sources': sorted(pure_sources),
        'decomp_sources': sorted(decomp_sources),
        'n_pure': n_pure, 'n_decomp_src': n_decomp_src,
        'pure_deficit': pure_deficit, 'sum_delta': sum_delta,
        'pair_types': pair_types, 'kunz': tuple(kunz),
        'witness_pairs': dict(witness_pairs)
    }


def enumerate_d3(m, max_k=None):
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
    print("DEFICIT LEMMA: EXHAUSTIVE CONFIGURATION ANALYSIS")
    print("d=3, k*>=4")
    print("=" * 70)

    # Track all configuration types
    config_types = defaultdict(list)
    min_sum_delta_by_config = defaultdict(lambda: float('inf'))

    for m in range(7, 10):
        sgs = enumerate_d3(m)
        for sg in sgs:
            if sg['k_star'] < 4:
                continue

            k = sg['k_star']

            # Classify: how many pure sources, how many decomp sources?
            config_key = (sg['n_pure'], sg['n_decomp_src'])

            # Track source positions relative to r*
            pure_pos = []
            for s in sg['pure_sources']:
                pos = "<=r*" if s <= sg['r_star'] else ">r*"
                pure_pos.append(pos)

            # Are there self-sums?
            has_self_sum = False
            for j in sg['decomp']:
                for (a, b) in sg['witness_pairs'][j]:
                    if a == b:
                        has_self_sum = True

            pattern = (sg['n_pure'], sg['n_decomp_src'],
                       tuple(sorted(pure_pos)), has_self_sum)

            if sg['sum_delta'] < min_sum_delta_by_config[pattern]:
                min_sum_delta_by_config[pattern] = sg['sum_delta']
                config_types[pattern] = sg

    print(f"\nDistinct configuration patterns found:")
    for pattern in sorted(config_types.keys()):
        sg = config_types[pattern]
        n_pure, n_decomp_src, pure_pos, has_self = pattern
        print(f"\n  Pattern: {n_pure} pure sources, {n_decomp_src} decomp sources, "
              f"positions={pure_pos}, self-sum={has_self}")
        print(f"    min Σδ = {min_sum_delta_by_config[pattern]}, "
              f"k* = {sg['k_star']}, L = {sg['L']}")
        print(f"    Example: m={len(sg['kunz'])+1}, kunz={sg['kunz']}")
        print(f"    decomp={sg['decomp']}, pure_src={sg['pure_sources']}, "
              f"decomp_src={sg['decomp_sources']}")
        for j in sg['decomp']:
            pairs = sg['witness_pairs'][j]
            print(f"      target {j} (level {sg['kunz'][j-1]}): pairs {pairs}")

    # Now find the MINIMUM Σδ cases for k*>=4
    print("\n" + "=" * 70)
    print("MINIMUM Σδ CASES (k*>=4)")
    print("=" * 70)

    for m in range(7, 10):
        sgs = [sg for sg in enumerate_d3(m) if sg['k_star'] >= 4]
        if not sgs:
            continue
        sgs.sort(key=lambda s: s['sum_delta'])
        print(f"\n  m={m}: {len(sgs)} sgs with k*>=4")
        for sg in sgs[:3]:
            print(f"    kunz={sg['kunz']}, k*={sg['k_star']}, Σδ={sg['sum_delta']}, "
                  f"L={sg['L']}, W={sg['W']}")
            print(f"    pure_src={sg['pure_sources']} (deficit={sg['pure_deficit']}), "
                  f"decomp_src={sg['decomp_sources']}")
            for j in sg['decomp']:
                pairs = sg['witness_pairs'][j]
                print(f"      target {j}: pairs {pairs}")

    # Check: is Σδ >= k*-1 ALWAYS true?
    print("\n" + "=" * 70)
    print("VERIFICATION: Σδ >= k*-1 for all k*>=4?")
    print("=" * 70)
    violations = 0
    for m in range(7, 10):
        for sg in enumerate_d3(m):
            if sg['k_star'] >= 4 and sg['sum_delta'] < sg['k_star'] - 1:
                violations += 1
                print(f"  VIOLATION: m={m}, k*={sg['k_star']}, Σδ={sg['sum_delta']}")
    print(f"  Total violations of Σδ >= k*-1: {violations}")

    # Also check: is L >= 2k*-1 ALWAYS true?
    print("\n  Verification: L >= 2k*-1 for all k*>=4?")
    L_violations = 0
    for m in range(7, 10):
        for sg in enumerate_d3(m):
            if sg['k_star'] >= 4 and sg['L'] < 2*sg['k_star'] - 1:
                L_violations += 1
                print(f"  VIOLATION: m={m}, k*={sg['k_star']}, L={sg['L']}, "
                      f"bound={2*sg['k_star']-1}")
    print(f"  Total violations of L >= 2k*-1: {L_violations}")


if __name__ == '__main__':
    main()

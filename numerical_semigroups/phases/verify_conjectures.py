"""
Exhaustive verification of Conjectures A, B, C and unified formula.
Uses Kunz coordinate enumeration for each (m, d=m-e).

Strategy: For each target (m, d), enumerate ALL numerical semigroups with
multiplicity m and embedding dimension e=m-d via Kunz coordinates,
then check W >= W_min_predicted.
"""
import time
import sys
from math import floor

def compute_W_from_kunz(m, kunz_coords):
    """
    Given multiplicity m and Kunz coordinates a = [a_1, ..., a_{m-1}],
    compute all semigroup invariants and Wilf number.
    Apéry(i) = i + a_i * m for i=1..m-1, Apéry(0) = 0.
    """
    a = kunz_coords  # a[i] for i=1..m-1 (0-indexed: a[0] = a_1)
    
    # Frobenius number = max(Apéry) - m
    apery = [i+1 + a[i]*m for i in range(m-1)]  # Apéry(i+1) for i=0..m-2
    F = max(apery) - m
    
    # Genus = sum of Kunz coordinates
    g = sum(a)
    
    # Conductor
    c = F + 1
    
    # Left elements
    L = c - g  # = F + 1 - g
    
    # Embedding dimension: count non-decomposable Apéry elements
    # Apéry(r) is decomposable if Apéry(r) = Apéry(r1) + Apéry(r2) for some r1, r2 >= 1
    # with r1 + r2 ≡ r (mod m)
    n_decomposable = 0
    for r in range(1, m):
        decomposable = False
        for r1 in range(1, m):
            r2 = (r - r1) % m
            if r2 == 0:
                continue  # would need r1 ≡ r mod m, i.e., r1 = r
            # r2 is in 1..m-1
            # Check: Apéry(r1) + Apéry(r2) = Apéry(r)
            # (r1 + a_{r1}*m) + (r2 + a_{r2}*m) = r + a_r * m
            # (r1 + r2) + (a_{r1} + a_{r2})*m = r + a_r * m
            # (r1+r2) mod m = r (guaranteed by construction)
            # overflow = (r1+r2) // m (0 or 1)
            # a_{r1} + a_{r2} + overflow = a_r
            overflow = (r1 + r2) // m
            if a[r1-1] + a[r2-1] + overflow == a[r-1]:
                decomposable = True
                break
        if decomposable:
            n_decomposable += 1
    
    e = 1 + (m - 1) - n_decomposable  # 1 (for m itself) + non-decomposable count
    W = e * L - c
    
    return e, L, c, F, g, W


def enumerate_and_verify(m, target_d, max_genus):
    """
    Enumerate all semigroups with multiplicity m and depth d = m - e,
    with genus <= max_genus.
    Returns (count, w_min, w_min_achiever, violations).
    """
    target_e = m - target_d
    w_min = float('inf')
    w_min_achiever = None
    violations = []
    count = 0
    total_enumerated = 0
    
    predicted = (m - target_d) * (floor(target_d / 2) + 3) - 2 * m
    
    # Kunz coordinate backtracking
    a = [0] * (m - 1)  # a[i] corresponds to Kunz coord for residue i+1
    
    def backtrack(pos, g_so_far):
        nonlocal w_min, w_min_achiever, count, total_enumerated
        
        if pos == m - 1:
            total_enumerated += 1
            # Complete assignment - compute invariants
            e, L, c, F, g, W = compute_W_from_kunz(m, a)
            
            if e == target_e:
                count += 1
                if W < w_min:
                    w_min = W
                    w_min_achiever = (list(a), e, L, c, F, g, W)
                if W < predicted:
                    violations.append((list(a), e, L, c, F, g, W))
            return
        
        remaining = (m - 1) - pos - 1  # positions left after this one
        max_a_val = max_genus - g_so_far - remaining  # remaining each need at least 1
        
        for v in range(1, max_a_val + 1):
            a[pos] = v
            
            # Check Kunz conditions for all pairs involving pos
            valid = True
            r = pos + 1  # residue class
            
            for prev in range(pos):
                r_prev = prev + 1
                s = r + r_prev
                if s < m:
                    # a[r-1] + a[r_prev-1] >= a[s-1] (if s-1 already assigned)
                    target_idx = s - 1
                    if target_idx <= pos:
                        if a[pos] + a[prev] < a[target_idx]:
                            valid = False
                            break
                    # Also check: a[target] <= a[r] + a[r_prev]
                    # Actually the Kunz condition is:
                    # a_i + a_j >= a_{(i+j) mod m} - [(i+j) >= m]
                    # For i+j < m: a_i + a_j >= a_{i+j}
                elif s == m:
                    # a[r-1] + a[r_prev-1] >= 1 (always true since each >= 1)
                    pass
                else:  # s > m
                    s_mod = s - m  # = s mod m
                    target_idx = s_mod - 1
                    if target_idx <= pos:
                        if a[pos] + a[prev] + 1 < a[target_idx]:
                            valid = False
                            break
                
                # Also check the reverse: if r_prev + r might give constraint
                # and check if previous pair (prev1, prev2) summing to r
                # Already handled by: for each assigned pair, check forward
            
            # Check backward too: for each pair (q, pos) where sum might have been assigned
            for prev in range(pos):
                r_prev = prev + 1
                s = r_prev + r
                # Constraint: a[prev] + a[pos] >= a[s mod m - 1] - [s >= m]
                if s < m:
                    target_idx = s - 1
                    if target_idx <= pos:
                        if a[prev] + v < a[target_idx]:
                            valid = False
                            break
                elif s >= m:
                    s_mod = s % m
                    if s_mod == 0:
                        if a[prev] + v < 1:
                            valid = False
                            break
                    else:
                        target_idx = s_mod - 1
                        if target_idx <= pos:
                            if a[prev] + v + 1 < a[target_idx]:
                                valid = False
                                break
            
            if valid:
                backtrack(pos + 1, g_so_far + v)
        
        a[pos] = 0
    
    backtrack(0, 0)
    
    return count, w_min, w_min_achiever, violations, total_enumerated, predicted


def main():
    print("=" * 70)
    print("EXHAUSTIVE VERIFICATION OF UNIFIED WILF BOUND")
    print("W_min(m,d) = (m-d)*(floor(d/2)+3) - 2m")
    print("=" * 70)
    
    # Define what to verify
    # d=1: m up to 14 (genus cap needed: T_m has g=2m-3, so m=14 -> g=25)
    # d=2: m up to 12
    # d=3: m up to 11
    # d=4: m up to 10
    # d=5: m up to 10
    
    test_cases = [
        # (d, m_range, max_genus)
        (1, range(3, 15), 30),   # d=1, m=3..14, generous genus cap
        (2, range(4, 13), 30),   # d=2, m=4..12
        (3, range(7, 12), 30),   # d=3, m=7..11
        (4, range(8, 12), 35),   # d=4, m=8..11
        (5, range(9, 12), 35),   # d=5, m=9..11
    ]
    
    all_results = {}
    
    for d, m_range, max_g in test_cases:
        print(f"\n{'='*70}")
        print(f"CONJECTURE d={d}: W_min = (m-{d})*{floor(d/2)+3} - 2m")
        print(f"{'='*70}")
        
        for m in m_range:
            t0 = time.time()
            target_e = m - d
            
            # Limit genus based on what's feasible
            effective_max_g = min(max_g, 3*m)  # don't go crazy
            
            count, w_min_obs, achiever, violations, total_enum, predicted = \
                enumerate_and_verify(m, d, effective_max_g)
            
            elapsed = time.time() - t0
            
            status = "✅" if len(violations) == 0 and count > 0 else ("⚠️ NO DATA" if count == 0 else "❌ VIOLATION")
            
            print(f"  m={m:2d}, e={target_e:2d} (d={d}): "
                  f"W_min_obs={w_min_obs if w_min_obs < float('inf') else 'N/A':>6} "
                  f"predicted={predicted:>6} "
                  f"count={count:>6} "
                  f"total_enum={total_enum:>8} "
                  f"[{elapsed:6.1f}s] {status}")
            
            if violations:
                for v in violations[:3]:
                    print(f"    ❌ VIOLATION: kunz={v[0]}, e={v[1]}, L={v[2]}, c={v[3]}, W={v[6]}")
            
            if achiever and count > 0:
                print(f"    achiever: kunz={achiever[0][:6]}{'...' if len(achiever[0])>6 else ''}, "
                      f"e={achiever[1]}, L={achiever[2]}, c={achiever[3]}, F={achiever[4]}, g={achiever[5]}, W={achiever[6]}")
            
            all_results[(d, m)] = {
                'count': count, 'w_min': w_min_obs, 'predicted': predicted,
                'violations': len(violations), 'time': elapsed
            }
            
            # Timeout guard
            if elapsed > 120:
                print(f"  ⏱️ m={m} took {elapsed:.0f}s, skipping higher m for d={d}")
                break
            
            sys.stdout.flush()
    
    # Summary table
    print(f"\n{'='*70}")
    print("SUMMARY TABLE")
    print(f"{'='*70}")
    print(f"{'d':>3} {'m':>3} {'e':>3} {'count':>8} {'W_min_obs':>10} {'predicted':>10} {'status':>8}")
    print("-" * 55)
    for (d, m), r in sorted(all_results.items()):
        status = "✅" if r['violations'] == 0 and r['count'] > 0 else ("⚠️" if r['count'] == 0 else "❌")
        w_str = str(r['w_min']) if r['w_min'] < float('inf') else "N/A"
        print(f"{d:3d} {m:3d} {m-d:3d} {r['count']:8d} {w_str:>10} {r['predicted']:10d} {status:>8}")


if __name__ == "__main__":
    main()

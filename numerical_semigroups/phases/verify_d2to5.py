"""
Targeted Kunz enumeration for d=2..5.
For d >= 2, the generic minimizer has genus 2m - L(d) which is often within reach.
Key insight: generic minimizers have c=2m (F=2m-1).
"""
import time
import sys
from math import floor

def enumerate_and_check(m, target_e, max_genus):
    """Enumerate all semigroups with multiplicity m, filter for e=target_e, genus <= max_genus."""
    
    n = m - 1
    results = []
    count_total = [0]
    count_target = [0]
    a = [0] * n
    
    def is_decomposable(r, a_vals):
        r1_res = r + 1
        for i in range(n):
            i_res = i + 1
            j_res = (r1_res - i_res) % m
            if j_res == 0:
                continue
            j = j_res - 1
            overflow = (i_res + j_res) // m
            if a_vals[i] + a_vals[j] + overflow == a_vals[r]:
                return True
        return False
    
    def backtrack(pos, g_so_far):
        if pos == n:
            count_total[0] += 1
            n_decomp = 0
            for r in range(n):
                if is_decomposable(r, a):
                    n_decomp += 1
            e = 1 + n - n_decomp
            
            if e == target_e:
                count_target[0] += 1
                F = max(((i+1) + a[i]*m) for i in range(n)) - m
                c = F + 1
                g = g_so_far
                L = c - g
                W = e * L - c
                results.append((e, L, c, g, W))
            return
        
        remaining = n - pos - 1
        max_val = max_genus - g_so_far - remaining
        
        for v in range(1, max_val + 1):
            a[pos] = v
            valid = True
            r = pos + 1
            
            for prev in range(pos):
                p_res = prev + 1
                s = r + p_res
                s_mod = s % m
                if s_mod == 0:
                    pass
                else:
                    target_idx = s_mod - 1
                    if target_idx <= pos:
                        if s < m:
                            if a[prev] + v < a[target_idx]:
                                valid = False
                                break
                        else:
                            if a[prev] + v < a[target_idx] + 1:
                                valid = False
                                break
            
            if valid:
                for prev1 in range(pos):
                    for prev2 in range(prev1, pos):
                        p1_res = prev1 + 1
                        p2_res = prev2 + 1
                        s12 = p1_res + p2_res
                        s12_mod = s12 % m
                        if s12_mod == r:
                            if s12 < m:
                                if a[prev1] + a[prev2] < v:
                                    valid = False
                                    break
                            else:
                                if a[prev1] + a[prev2] < v + 1:
                                    valid = False
                                    break
                    if not valid:
                        break
            
            if valid:
                backtrack(pos + 1, g_so_far + v)
    
    t0 = time.time()
    backtrack(0, 0)
    elapsed = time.time() - t0
    return results, count_total[0], count_target[0], elapsed


def main():
    print("=" * 70)
    print("VERIFICATION: Conjectures d=2..5 (extended m range)")
    print("W_min(m,d) = (m-d)*(floor(d/2)+3) - 2m")
    print("=" * 70)
    
    # Test cases: (d, m values to test, max_genus)
    # For d=2: generic minimizer g = 2m - 4. Need genus >= 2m for safety.
    # For d=3: generic minimizer g = 2m - 4. Same.
    # For d=4,5: generic minimizer g = 2m - 5. Similar.
    
    tasks = [
        (2, [13, 14], 30),  # d=2, extend from m=12 to m=14
        (3, [13, 14], 30),  # d=3, extend from m=12 to m=14
        (4, [13, 14], 30),  # d=4, extend from m=12 to m=14
        (5, [13, 14], 30),  # d=5, extend from m=12 to m=14
    ]
    
    for d, m_vals, max_g in tasks:
        L_d = floor(d / 2) + 3
        print(f"\n{'='*60}")
        print(f"d={d}, L(d)={L_d}, predicted: W = (m-{d})*{L_d} - 2m")
        print(f"{'='*60}")
        
        for m in m_vals:
            target_e = m - d
            if target_e < 2:
                continue
            
            predicted = (m - d) * L_d - 2 * m
            
            # Adaptive genus cap: at minimum 2m+5, but cap at max_g
            eff_max_g = min(max_g, 2*m + 8)
            
            print(f"\n  m={m}, e={target_e}, max_genus={eff_max_g}")
            sys.stdout.flush()
            
            results, total, target_count, elapsed = enumerate_and_check(m, target_e, eff_max_g)
            
            if target_count == 0:
                print(f"  ⚠️ No semigroups found ({total:,} total enumerated, {elapsed:.1f}s)")
                continue
            
            w_min_obs = min(r[4] for r in results)
            violations = [r for r in results if r[4] < predicted]
            achiever = min(results, key=lambda r: r[4])
            
            status = "✅" if not violations else "❌"
            match = "EXACT" if w_min_obs == predicted else f"(above by {w_min_obs - predicted})"
            
            print(f"  Enumerated: {total:,} total, {target_count:,} with e={target_e}")
            print(f"  W_min obs: {w_min_obs}, predicted: {predicted} → {match} {status}")
            print(f"  Achiever: L={achiever[1]}, c={achiever[2]}, g={achiever[3]}, W={achiever[4]}")
            print(f"  Time: {elapsed:.1f}s")
            
            if violations:
                for v in violations[:3]:
                    print(f"  ❌ VIOLATION: L={v[1]}, c={v[2]}, g={v[3]}, W={v[4]}")
            
            sys.stdout.flush()
            
            if elapsed > 90:
                print(f"  ⏱️ Slow, skipping higher m for d={d}")
                break


if __name__ == "__main__":
    main()

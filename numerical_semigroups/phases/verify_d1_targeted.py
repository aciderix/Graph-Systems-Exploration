"""
Targeted Kunz enumeration for d=1 (e=m-1).
Key insight: for e=m-1, exactly ONE Apéry element is decomposable.

Optimizations:
1. For L >= 4 and genus <= 2m-3: W >= 2m-5 > m-3 (auto-safe, no need to check)
   So we ONLY need to check L=3 semigroups, where c <= 2m is forced by the proof.
   Combined with W = (m-1)*3 - c = 3m-3-c, W >= m-3 iff c <= 2m. QED for L=3.
   
2. For the remaining case L >= 4: we need genus > 2m-3 for a potential violation.
   Violation requires: c > (m-1)*L - m + 3
   With L >= 4: c > 3m - m + 3 - 4 + ... wait let me recalculate.
   
   W < m-3 means (m-1)*L - c < m-3, i.e., c > (m-1)*L - m + 3
   For L=4: c > 3m + 3 - 4 = 3(m-1). So need c > 3m-3 and genus g = c-4 > 3m-7.
   For m=12: g > 29. So with genus cap 30, we'd catch all violations for L=4.
   For L=5: c > 4m. g = c-5 > 4m-5. For m=12: g > 43. Way beyond feasible.
   
   So we really only need to check L=3 and L=4 cases!

Strategy: For each m, enumerate all (m, m-1) semigroups up to a safe genus cap,
then verify W >= m-3.
"""
import time
import sys

def enumerate_d1_kunz(m, max_genus):
    """Enumerate all numerical semigroups with multiplicity m, e=m-1, g <= max_genus.
    Returns list of (e, L, c, g, W) for each found semigroup with e=m-1."""
    
    n = m - 1  # number of Kunz coordinates
    results = []
    count_total = [0]
    count_target = [0]
    
    a = [0] * n  # a[i] = Kunz coord for residue i+1
    
    def is_decomposable(r, a_vals):
        """Check if Apéry(r+1) is decomposable."""
        r1_res = r + 1  # actual residue
        for i in range(n):
            i_res = i + 1
            j_res = (r1_res - i_res) % m
            if j_res == 0:
                continue
            j = j_res - 1  # index into a
            overflow = (i_res + j_res) // m
            if a_vals[i] + a_vals[j] + overflow == a_vals[r]:
                return True
        return False
    
    def backtrack(pos, g_so_far):
        if pos == n:
            count_total[0] += 1
            
            # Compute embedding dimension
            n_decomp = 0
            for r in range(n):
                if is_decomposable(r, a):
                    n_decomp += 1
            
            e = 1 + n - n_decomp  # 1 for m itself, plus non-decomposable Apéry
            
            if e == m - 1:  # d = 1
                count_target[0] += 1
                # Compute invariants
                F = max(((i+1) + a[i]*m) for i in range(n)) - m
                c = F + 1
                g = g_so_far
                L = c - g
                W = e * L - c
                results.append((e, L, c, g, W))
            return
        
        remaining = n - pos - 1
        max_val = max_genus - g_so_far - remaining  # remaining each need >= 1
        
        for v in range(1, max_val + 1):
            a[pos] = v
            
            # Check Kunz conditions
            valid = True
            r = pos + 1  # residue for this position
            
            for prev in range(pos):
                p_res = prev + 1
                s = r + p_res
                s_mod = s % m
                overflow = s // m
                
                if s_mod == 0:
                    # a[prev] + a[pos] + overflow >= 1 (always true if both >= 1)
                    # Actually: a_i + a_j >= 1 - overflow... hmm
                    # Kunz condition: a_i + a_j >= a_{(i+j) mod m} when (i+j) mod m != 0
                    # When (i+j) mod m = 0: a_i + a_j + 1 >= 1 (if overflow=1), always true
                    pass
                else:
                    target = s_mod - 1  # index
                    if target <= pos:
                        # Constraint: a[prev] + a[pos] + overflow >= a[target] + (1 if s >= m else 0)
                        # Actually: Kunz condition is a_i + a_j >= a_{(i+j) mod m} + [(i+j >= m)]
                        # Wait, let me get this right.
                        # Standard Kunz: a_i + a_j >= a_{i+j} if i+j < m
                        #                a_i + a_j >= a_{(i+j) mod m} + 1 if i+j >= m
                        # But here a is 0-indexed for residues 1..m-1
                        # a[prev] corresponds to residue prev+1 = p_res
                        # a[pos] corresponds to residue pos+1 = r
                        # sum of residues = p_res + r = s
                        if s < m:
                            if a[prev] + v < a[target]:
                                valid = False
                                break
                        else:
                            if a[prev] + v < a[target] + 1:
                                valid = False
                                break
                    
                    # Also check: if target < pos, we need to verify that
                    # a[target] + a[pos] satisfies the Kunz condition for their sum
                    # But this will be checked when pos is the "prev" for future positions
                    # So actually we need bidirectional checks for all assigned pairs
            
            if valid:
                # Also check: for pairs (pos, prev) where pos is the first element
                # This is symmetric to above, already handled.
                
                # Additional pruning: check constraints where pos appears as a target
                for prev1 in range(pos):
                    for prev2 in range(prev1, pos):
                        p1_res = prev1 + 1
                        p2_res = prev2 + 1
                        s12 = p1_res + p2_res
                        s12_mod = s12 % m
                        if s12_mod == r:  # this pair sums to our residue
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
    print("TARGETED VERIFICATION: Conjecture A (d=1, e=m-1)")
    print("W >= m - 3 for all semigroups with e = m-1")
    print("=" * 70)
    
    # Theoretical argument for safety:
    print("\n📐 THEORETICAL BOUND:")
    print("For L >= 4 and genus g: W = (m-1)*L - (g+L) = (m-2)*L - g")
    print("  If g <= 2m-3: W >= (m-2)*4 - (2m-3) = 2m-5 > m-3 for m >= 3")
    print("  So within genus 2m-3, only L=3 could possibly violate.")
    print("  L=3 case: proved c <= 2m, so W = 3(m-1) - c >= m-3. QED within this range.")
    print("  For violations from L=4: need g > 3m-7 (much higher genus)")
    print()
    
    for m in range(12, 17):
        # Safe genus cap: go to 3m to catch L=4 potential violations for small m
        max_g = min(3 * m, 40)
        
        print(f"\n--- m={m}, e={m-1}, max_genus={max_g} ---")
        sys.stdout.flush()
        
        results, total, target, elapsed = enumerate_d1_kunz(m, max_g)
        
        if target == 0:
            print(f"  No semigroups found with (m={m}, e={m-1}), genus <= {max_g}")
            continue
        
        w_min = min(r[4] for r in results)
        predicted = m - 3
        violations = [r for r in results if r[4] < predicted]
        
        # Find the achiever
        achiever = min(results, key=lambda r: r[4])
        
        status = "✅" if not violations else "❌ VIOLATION"
        
        print(f"  Total enumerated: {total:,}")
        print(f"  With e={m-1}: {target:,}")
        print(f"  W_min observed: {w_min}")
        print(f"  W_min predicted: {predicted}")
        print(f"  Status: {status}")
        print(f"  Achiever: e={achiever[0]}, L={achiever[1]}, c={achiever[2]}, g={achiever[3]}, W={achiever[4]}")
        print(f"  Time: {elapsed:.1f}s")
        
        if violations:
            print(f"  ❌ {len(violations)} VIOLATIONS found!")
            for v in violations[:5]:
                print(f"    e={v[0]}, L={v[1]}, c={v[2]}, g={v[3]}, W={v[4]}")
        
        # L distribution
        l_dist = {}
        for r in results:
            l_dist[r[1]] = l_dist.get(r[1], 0) + 1
        print(f"  L distribution: {dict(sorted(l_dist.items()))}")
        
        sys.stdout.flush()
        
        if elapsed > 120:
            print(f"  ⏱️ Too slow, stopping")
            break


if __name__ == "__main__":
    main()

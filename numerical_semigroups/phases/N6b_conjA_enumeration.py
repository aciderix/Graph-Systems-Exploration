"""
Conjecture A: For e=m-1, prove W >= m-3.
Focus: L=4 case. Need to show c <= 3m-1.

Optimized: prune during backtracking for d=1 only.
Also: early exit once we know d != 1.
"""
import time, sys
from collections import defaultdict

def enumerate_d1(m, max_genus):
    """Enumerate semigroups with multiplicity m and d=1 (e=m-1).
    Return list of (L, c, g, W, kunz_tuple, max_level, max_idx)."""
    n = m - 1
    results = []
    a = [0] * n
    
    def count_decomp():
        """Count decomposable Apéry elements."""
        nd = 0
        for r in range(n):
            r1 = r + 1
            found = False
            for i in range(n):
                i1 = i + 1
                j1 = (r1 - i1) % m
                if j1 == 0: continue
                j = j1 - 1
                ov = (i1 + j1) // m
                if a[i] + a[j] + ov == a[r]:
                    found = True
                    break
            if found:
                nd += 1
        return nd
    
    def backtrack(pos, g_so_far):
        if pos == n:
            nd = count_decomp()
            if nd != 1:  # We want d=1 exactly
                return
            e = m - 1
            F_val = max(((i+1) + a[i]*m) for i in range(n)) - m
            c = F_val + 1
            g = g_so_far
            L = c - g
            W = e * L - c
            max_i = max(range(n), key=lambda i: (i+1) + a[i]*m)
            results.append((L, c, g, W, tuple(a), a[max_i], max_i + 1))
            return
        
        remaining = n - pos - 1
        max_val = max_genus - g_so_far - remaining
        for v in range(1, max_val + 1):
            a[pos] = v
            valid = True
            r = pos + 1
            for prev in range(pos):
                p1 = prev + 1
                s = r + p1
                s_mod = s % m
                if s_mod != 0:
                    ti = s_mod - 1
                    if ti <= pos:
                        if s < m:
                            if a[prev] + v < a[ti]:
                                valid = False; break
                        else:
                            if a[prev] + v < a[ti] + 1:
                                valid = False; break
            if valid:
                for p1 in range(pos):
                    for p2 in range(p1, pos):
                        s12 = (p1+1) + (p2+1)
                        s12_mod = s12 % m
                        if s12_mod == r:
                            if s12 < m:
                                if a[p1] + a[p2] < v:
                                    valid = False; break
                            else:
                                if a[p1] + a[p2] < v + 1:
                                    valid = False; break
                    if not valid: break
            if valid:
                backtrack(pos + 1, g_so_far + v)
    
    t0 = time.time()
    backtrack(0, 0)
    return results, time.time() - t0

print("=" * 72)
print("CONJECTURE A: c <= 3m-1 when L=4, e=m-1")
print("=" * 72)

for m in range(3, 17):
    # Use tight genus cap: for L=4, g = F-3. With F ~ 3m max, g ~ 3m-3.
    max_g = min(45, 3*m + 5)
    
    print(f"\nm={m:2d} (max_genus={max_g}):", flush=True)
    results, elapsed = enumerate_d1(m, max_g)
    
    if not results:
        print(f"  No d=1 semigroups ({elapsed:.1f}s)")
        continue
    
    by_L = defaultdict(list)
    for r in results:
        by_L[r[0]].append(r)
    
    print(f"  Total d=1: {len(results)} ({elapsed:.1f}s)")
    
    for L_val in sorted(by_L.keys()):
        entries = by_L[L_val]
        c_max = max(r[1] for r in entries)
        c_min = min(r[1] for r in entries)
        w_min = min(r[3] for r in entries)
        
        if L_val == 4:
            bound = 3*m - 1
            ok = c_max <= bound
            achiever = max(entries, key=lambda r: r[1])
            kunz = achiever[4]
            ml = achiever[5]  # max level
            mi = achiever[6]  # max index (residue)
            
            print(f"  L={L_val}: n={len(entries):>5d} c∈[{c_min},{c_max}] "
                  f"c_max {'≤' if ok else '>'} {bound} W_min={w_min:>3d}≥{m-3} "
                  f"{'✅' if ok and w_min >= m-3 else '❌'}")
            print(f"        achiever: max_level={ml} at res={mi}")
            
            # Check if max_level <= 2 for ALL L=4
            all_max_levels = [r[5] for r in entries]
            max_of_max = max(all_max_levels)
            if max_of_max <= 2:
                print(f"        ⚡ ALL L=4 have max_level ≤ 2 => c ≤ 2m = {2*m}")
        else:
            w_ok = w_min >= m - 3
            print(f"  L={L_val}: n={len(entries):>5d} c∈[{c_min},{c_max}] "
                  f"W_min={w_min:>3d}≥{m-3} {'✅' if w_ok else '❌'}")
    
    if elapsed > 60:
        print("  ⏱️ Getting slow, may stop soon")
    if elapsed > 180:
        print("  ⏱️ Stopping")
        break

print("\n" + "=" * 72)
print("KEY QUESTION: Do any L=4, e=m-1 semigroups have max_level >= 3?")
print("If NOT, then c <= 2m < 3m-1 automatically, and the proof is trivial.")
print("=" * 72)

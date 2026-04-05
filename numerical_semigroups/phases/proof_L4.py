"""
Attempt to prove: For e = m-1, W >= m-3 when L >= 4.

Known:
- W = (m-1)*L - c where c = F+1
- For L >= 4: W >= m-3 iff c <= (m-1)*L - m + 3

Strategy: Study the relationship between L and c for e=m-1 semigroups.
Use our Kunz enumeration data to see if we can find a bound c <= f(L, m).

From our enumeration for m=12..16, we have the L distribution.
Let's collect (L, c, W) for all e=m-1 semigroups to find patterns.
"""
import time
import sys
from collections import defaultdict

def enumerate_d1_full(m, max_genus):
    """Return list of (L, c, g, W) for all (m, m-1) semigroups."""
    n = m - 1
    results = []
    a = [0] * n
    
    def is_decomposable(r, a_vals):
        r1_res = r + 1
        for i in range(n):
            i_res = i + 1
            j_res = (r1_res - i_res) % m
            if j_res == 0: continue
            j = j_res - 1
            overflow = (i_res + j_res) // m
            if a_vals[i] + a_vals[j] + overflow == a_vals[r]:
                return True
        return False
    
    def backtrack(pos, g_so_far):
        if pos == n:
            n_decomp = sum(1 for r in range(n) if is_decomposable(r, a))
            e = 1 + n - n_decomp
            if e == m - 1:
                F = max(((i+1) + a[i]*m) for i in range(n)) - m
                c = F + 1; g = g_so_far; L = c - g; W = e * L - c
                results.append((L, c, g, W))
            return
        remaining = n - pos - 1
        max_val = max_genus - g_so_far - remaining
        for v in range(1, max_val + 1):
            a[pos] = v
            valid = True
            r = pos + 1
            for prev in range(pos):
                p_res = prev + 1; s = r + p_res; s_mod = s % m
                if s_mod != 0:
                    ti = s_mod - 1
                    if ti <= pos:
                        if s < m:
                            if a[prev] + v < a[ti]: valid = False; break
                        else:
                            if a[prev] + v < a[ti] + 1: valid = False; break
            if valid:
                for p1 in range(pos):
                    for p2 in range(p1, pos):
                        s12 = (p1+1) + (p2+1); s12_mod = s12 % m
                        if s12_mod == r:
                            if s12 < m:
                                if a[p1] + a[p2] < v: valid = False; break
                            else:
                                if a[p1] + a[p2] < v + 1: valid = False; break
                    if not valid: break
            if valid:
                backtrack(pos + 1, g_so_far + v)
    
    backtrack(0, 0)
    return results


print("=" * 70)
print("ANALYSIS: c vs L for e=m-1 semigroups")
print("Goal: find if c <= (m-1)*L - m + 3 always holds (equivalent to W >= m-3)")
print("=" * 70)

for m in [8, 9, 10, 11, 12]:
    max_g = min(40, 3*m)
    print(f"\n--- m={m}, max_genus={max_g} ---")
    
    t0 = time.time()
    results = enumerate_d1_full(m, max_g)
    elapsed = time.time() - t0
    
    print(f"  Found {len(results)} semigroups with e={m-1} ({elapsed:.1f}s)")
    
    # For each L, find max c
    by_L = defaultdict(list)
    for L, c, g, W in results:
        by_L[L].append((c, g, W))
    
    print(f"\n  {'L':>3} | {'count':>6} | {'c_max':>6} | {'c_bound':>8} | {'W_min':>6} | {'c_max <= bound?':>15}")
    print(f"  {'-'*3}-+-{'-'*6}-+-{'-'*6}-+-{'-'*8}-+-{'-'*6}-+-{'-'*15}")
    
    for L in sorted(by_L.keys()):
        entries = by_L[L]
        c_max = max(e[0] for e in entries)
        w_min_L = min(e[2] for e in entries)
        c_bound = (m-1)*L - m + 3  # threshold: c <= this means W >= m-3
        ok = "✅" if c_max <= c_bound else "❌"
        print(f"  {L:3d} | {len(entries):6d} | {c_max:6d} | {c_bound:8d} | {w_min_L:6d} | {ok}")
    
    # Check: is c <= 2m always true? (stronger bound)
    all_c_2m = all(c <= 2*m for L, c, g, W in results)
    max_c = max(c for L, c, g, W in results)
    print(f"\n  Max c across all L: {max_c} (2m = {2*m})")
    print(f"  c <= 2m for all? {'YES ✅' if all_c_2m else 'NO ❌'}")
    
    # Is there a simple bound?
    # Try: c <= m*L/(L-1) or c <= L*m/(floor(L/2)+1)
    # Or just check c <= 2m empirically
    
    print(f"\n  L >= 4 entries:")
    for L in sorted(by_L.keys()):
        if L >= 4:
            entries = by_L[L]
            c_max = max(e[0] for e in entries)
            c_min = min(e[0] for e in entries)
            w_min_L = min(e[2] for e in entries)
            print(f"    L={L}: c in [{c_min}, {c_max}], W_min={w_min_L}, W_min>m-3? {'YES' if w_min_L >= m-3 else 'NO'}")
    
    sys.stdout.flush()

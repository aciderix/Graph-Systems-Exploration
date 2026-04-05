"""
Extend unified formula verification to d=6, 7, 8.
Predicted: L(d) = floor(d/2) + 3
  d=6: L=6, W = (m-6)*6 - 2m = 4m-36
  d=7: L=6, W = (m-7)*6 - 2m = 4m-42
  d=8: L=7, W = (m-8)*7 - 2m = 5m-56
"""
import time, sys
from math import floor

def enumerate_and_check(m, target_e, max_genus):
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
            if j_res == 0: continue
            j = j_res - 1
            overflow = (i_res + j_res) // m
            if a_vals[i] + a_vals[j] + overflow == a_vals[r]:
                return True
        return False
    
    def backtrack(pos, g_so_far):
        if pos == n:
            count_total[0] += 1
            n_decomp = sum(1 for r in range(n) if is_decomposable(r, a))
            e = 1 + n - n_decomp
            if e == target_e:
                count_target[0] += 1
                F = max(((i+1) + a[i]*m) for i in range(n)) - m
                c = F + 1; g = g_so_far; L = c - g; W = e * L - c
                results.append((e, L, c, g, W))
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
    
    t0 = time.time()
    backtrack(0, 0)
    return results, count_total[0], count_target[0], time.time() - t0

print("=" * 70)
print("VERIFICATION d=6..8: Does L(d) = floor(d/2) + 3 extend?")
print("=" * 70)

for d in range(6, 9):
    L_pred = floor(d / 2) + 3
    print(f"\n{'='*50}")
    print(f"d={d}, predicted L(d)={L_pred}")
    print(f"predicted W_min = (m-{d})*{L_pred} - 2m")
    print(f"{'='*50}")
    
    for m in range(d + 3, d + 14):  # Start from d+3 to ensure e >= 3
        target_e = m - d
        if target_e < 3: continue
        predicted = (m - d) * L_pred - 2 * m
        
        eff_max_g = min(2*m + 8, 45)
        
        print(f"  m={m:2d} e={target_e:2d}: ", end="", flush=True)
        
        results, total, tc, elapsed = enumerate_and_check(m, target_e, eff_max_g)
        
        if tc == 0:
            print(f"NO DATA ({total:,} enum, {elapsed:.1f}s)")
            if elapsed > 60: break
            continue
        
        w_min = min(r[4] for r in results)
        achiever = min(results, key=lambda r: r[4])
        match = "EXACT" if w_min == predicted else f"+{w_min-predicted}" if w_min > predicted else f"❌{w_min-predicted}"
        
        print(f"W_min={w_min:3d} pred={predicted:3d} {match:>6} "
              f"n={tc:>5} L={achiever[1]} c={achiever[2]} "
              f"[{elapsed:5.1f}s]")
        
        if elapsed > 60: 
            print(f"  ⏱️ Stopping d={d}")
            break

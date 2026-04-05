"""Quick check: d=8 should have L=6 (k=4), W = 4m-48"""
import time, sys
from math import floor

def enumerate_and_check(m, target_e, max_genus):
    n = m - 1; results = []; a = [0] * n; count = [0]
    def is_decomposable(r, a_vals):
        r1_res = r + 1
        for i in range(n):
            i_res = i + 1; j_res = (r1_res - i_res) % m
            if j_res == 0: continue
            j = j_res - 1; overflow = (i_res + j_res) // m
            if a_vals[i] + a_vals[j] + overflow == a_vals[r]: return True
        return False
    def backtrack(pos, g_so_far):
        if pos == n:
            n_decomp = sum(1 for r in range(n) if is_decomposable(r, a))
            e = 1 + n - n_decomp
            if e == target_e:
                count[0] += 1
                F = max(((i+1) + a[i]*m) for i in range(n)) - m
                c = F + 1; g = g_so_far; L = c - g; W = e * L - c
                results.append((e, L, c, g, W))
            return
        remaining = n - pos - 1; max_val = max_genus - g_so_far - remaining
        for v in range(1, max_val + 1):
            a[pos] = v; valid = True; r = pos + 1
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
            if valid: backtrack(pos + 1, g_so_far + v)
    t0 = time.time(); backtrack(0, 0); return results, count[0], time.time() - t0

d = 8
print(f"d={d}: Expected L=6, W = 4m - 48")
for m in [14, 15, 16]:
    e = m - d
    if e < 3: continue
    pred = (m-d)*6 - 2*m  # L=6 prediction
    eff_max_g = min(2*m + 8, 45)
    print(f"  m={m} e={e}: ", end="", flush=True)
    results, tc, elapsed = enumerate_and_check(m, e, eff_max_g)
    if tc == 0:
        print(f"NO DATA ({elapsed:.1f}s)"); continue
    w_min = min(r[4] for r in results)
    ach = min(results, key=lambda r: r[4])
    status = "✅" if w_min == pred else f"obs={w_min} vs pred={pred}"
    print(f"W={w_min:3d} pred={pred:3d} L={ach[1]} c={ach[2]} n={tc} [{elapsed:.1f}s] {status}")
    if elapsed > 60: break

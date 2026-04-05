"""
Check: for d=1, is L >= k* + 2 always?
If yes: W = (m-1)L - c, and c = (k*-1)m + r* + 1 <= k*m.
Then W >= (m-1)(k*+2) - k*m = k*m + 2m - k* - 2 - k*m = 2m - k* - 2.
Hmm, that gives W >= 2m - k* - 2, which needs k* <= m+1 for W >= m-3. Always true.

Actually more precisely: c = (k*-1)m + r* + 1 where 1 <= r* <= m-1.
W = (m-1)L - c >= (m-1)(k*+2) - ((k*-1)m + m - 1 + 1) = (m-1)(k*+2) - k*m
  = k*m + 2m - k* - 2 - k*m = 2m - k* - 2.
Need >= m-3, so k* <= m+1. TRUE always.

So THE KEY CLAIM is: for d=1, L >= k* + 2.
If this is true, then W >= 2m - k* - 2 >= m - 3 (since k* <= m-1).

Let's verify computationally AND look at what happens at L=3,4.
"""
import time

def enumerate_d1(m, max_genus):
    n = m - 1
    results = []
    a = [0] * n

    def count_decomp():
        nd = 0
        for r in range(n):
            r1 = r + 1
            for i in range(n):
                i1 = i + 1
                j1 = (r1 - i1) % m
                if j1 == 0: continue
                j = j1 - 1
                ov = (i1 + j1) // m
                if a[i] + a[j] + ov == a[r]:
                    nd += 1
                    break
        return nd

    def backtrack(pos, g_so_far):
        if pos == n:
            if count_decomp() != 1:
                return
            F_val = max(((i+1) + a[i]*m) for i in range(n)) - m
            c = F_val + 1
            g = g_so_far
            L = c - g
            kstar = max(a)
            results.append((L, kstar, c, g))
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

    backtrack(0, 0)
    return results

print("CHECK: L >= k* + 2 for d=1 semigroups")
print("=" * 70)

for m in range(3, 12):
    max_g = min(4*m, 44)
    t0 = time.time()
    results = enumerate_d1(m, max_g)
    elapsed = time.time() - t0

    if not results:
        continue

    # Check L vs k* + 2
    violations = [(L, ks, c, g) for (L, ks, c, g) in results if L < ks + 2]
    l5_violations = [(L, ks, c, g) for (L, ks, c, g) in results if L >= 5 and L < ks + 2]

    # Find min(L - k*) for all, and for L>=5
    diff_all = min(L - ks for (L, ks, c, g) in results)
    l5_entries = [(L, ks, c, g) for (L, ks, c, g) in results if L >= 5]
    diff_l5 = min((L - ks for (L, ks, c, g) in l5_entries), default=999)

    print(f"\nm={m:2d}: {len(results)} semigroups, time={elapsed:.1f}s")
    print(f"  min(L - k*) overall: {diff_all}")
    print(f"  min(L - k*) for L>=5: {diff_l5}")
    print(f"  L < k*+2 violations (all):  {len(violations)}")
    print(f"  L < k*+2 violations (L>=5): {len(l5_violations)}")

    if violations:
        # Show them
        for v in violations[:5]:
            L, ks, c, g = v
            W = (m-1)*L - c
            print(f"    L={L} k*={ks} L-k*={L-ks} c={c} g={g} W={W} bound={m-3}")

    if l5_violations:
        print(f"  ❌ FOUND L>=5 violation of L >= k*+2!")
        for v in l5_violations[:5]:
            L, ks, c, g = v
            W = (m-1)*L - c
            print(f"    L={L} k*={ks} c={c} g={g} W={W}")

print("\n" + "=" * 70)
print("CONCLUSION: Check if L >= k*+2 holds universally for L>=5, d=1")

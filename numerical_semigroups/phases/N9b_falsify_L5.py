"""
FALSIFICATION of the lemma argument.

The argument says: L = k*+1 forces almost all k_r >= k*-1.
Let me check this claim more carefully.

L = k* + sum_{r=1}^{m-1} contribution_r = k* + 1
So sum of contributions = 1.

For r <= r*: contribution_r = max(0, k* - k_r). So k_r >= k*-1 for contribution <= 1.
  If k_r = k*-1: contribution = 1. Exactly one such r.
  If k_r < k*-1: contribution >= 2. But total = 1, so impossible.

For r > r*: contribution_r = max(0, k*-1-k_r). So k_r >= k*-2 for contribution <= 1.
  If k_r = k*-2: contribution = 1. But then the one from r<=r* must be 0.
  If k_r < k*-2: contribution >= 2. Impossible.

So the EXACT structure for L = k*+1 is one of:
  Case A: One r0 <= r* with k_{r0} = k*-1. All other r <= r*: k_r = k*.
          All r > r*: k_r >= k*-1 (contribution 0).
  Case B: All r <= r*: k_r = k* (contribution 0).
          One r0 > r* with k_{r0} = k*-2 (contribution 1).
          All other r > r*: k_r >= k*-1 (contribution 0).

In both cases, the MINIMUM level across all residues is:
  Case A: min is k*-1 (at r0). All others >= k*-1.
  Case B: min is k*-2 (at r0). All others >= k*-1.

PROBLEM: In case B, we have one element at k*-2. My argument assumed
all >= k*-1. Let me re-examine Case B.

In Case B: k_{r0} = k*-2 for some r0 > r*.
For pairs involving r0:
  k_{r0} + k_j = (k*-2) + k_j where k_j >= k*-1 (or k* for j <= r*).
  So k_{r0} + k_j >= (k*-2) + (k*-1) = 2k*-3.
  Target: k_target <= k*. Carry: 0 or 1. Need >= k_target + carry.
  2k*-3 >= k* + 1 iff k* >= 4. So for k*>=4, still strict inequality. ✓

For self-pair (r0, r0):
  k_{r0} + k_{r0} = 2(k*-2) = 2k*-4.
  Target <= k*. Carry 0 or 1. Need 2k*-4 >= k* + carry.
  k* >= 4 + carry. So for k*>=5: strict. For k*=4: 2*2=4 >= 4+carry.
  If carry=0: 4>=4, EQUALITY possible → decomposition!
  If carry=1: 4>=5, FALSE.

So for k*=4, Case B: self-sum of the k*-2=2 level element.
2*r0 mod m. If 2*r0 < m (no carry): k_{2r0} must = 4 = 2k*-4=4. OK 4=4. Decomposable!
But wait, 2(k*-2) = 2*2 = 4 = k*. So it's exactly k_target = k*.

This could give d >= 1. Could it give d = 1 exactly?

Let me test this specific case: k*=4, r0 > r* with k_{r0}=2,
all other levels are k* or k*-1.
"""
import sys

def check_decompositions(m, kunz):
    n = m - 1
    decomp = []
    for r in range(n):
        r1 = r + 1
        found = False
        for i in range(n):
            i1 = i + 1
            j1 = (r1 - i1) % m
            if j1 == 0: continue
            j = j1 - 1
            ov = (i1 + j1) // m
            if kunz[i] + kunz[j] + ov == kunz[r]:
                found = True
                break
        if found:
            decomp.append(r1)
    return decomp

print("FALSIFICATION: Case B with k*=4, one element at level 2")
print("=" * 70)

for m in range(5, 15):
    n = m - 1
    found_problem = False

    # Case B: r* can be any residue <= m-1.
    # All r <= r*: k_r = 4. All r > r*: k_r = 3, except r0 with k_{r0} = 2.
    for rstar_idx in range(n):  # r* = rstar_idx + 1
        rstar = rstar_idx + 1
        for r0_idx in range(n):
            r0 = r0_idx + 1
            if r0 <= rstar:
                continue  # r0 > r* required

            kunz = [0] * n
            for i in range(n):
                r = i + 1
                if r <= rstar:
                    kunz[i] = 4  # k* level
                else:
                    kunz[i] = 3  # k*-1 level
            kunz[r0_idx] = 2  # the special element at k*-2

            # Verify this is a valid Kunz tuple
            valid = True
            for i in range(n):
                for j in range(i, n):
                    i1, j1 = i+1, j+1
                    s = i1 + j1
                    if s == m:
                        if kunz[i] + kunz[j] < 1:
                            valid = False; break
                    elif s < m:
                        target = s - 1
                        if kunz[i] + kunz[j] < kunz[target]:
                            valid = False; break
                    else:
                        s_mod = s % m
                        if s_mod == 0:
                            if kunz[i] + kunz[j] < 2:
                                valid = False; break
                        else:
                            target = s_mod - 1
                            if kunz[i] + kunz[j] < kunz[target] + 1:
                                valid = False; break
                if not valid:
                    break

            if not valid:
                continue

            decomp = check_decompositions(m, kunz)
            d = len(decomp)

            # Compute L
            kstar = max(kunz)
            F = max((kunz[i]*(m) + (i+1)) for i in range(n)) - m
            c = F + 1
            g = sum(kunz)
            L = c - g
            W = (m-1) * L - c

            if d == 1:
                print(f"  m={m}: FOUND d=1! r*={rstar} r0={r0} L={L} W={W} kunz={kunz}")
                print(f"    decomp at residues: {decomp}")
                found_problem = True

            # Also report if d > 0 at all
            if d > 0 and d != 1 and L == 5:  # k*+1 = 5
                pass  # not the case we care about

    if not found_problem:
        print(f"  m={m:2d}: Case B k*=4 → no d=1 found ✅")

# Also: what about more general L=k*+1 structures?
# What if not all "other" elements are at exactly k* or k*-1?
# E.g., one at k*-1, one at k*+1? No: k_r <= k* by definition.
# So k_r is between 1 and k*. The contribution analysis is correct:
# only k_r <= k*-1 (for r<=r*) or k_r <= k*-2 (for r>r*) contribute.
# And sum of contributions = 1 gives exactly the two cases A and B.

print("\n" + "=" * 70)
print("Now testing the GENERAL case: any valid Kunz tuple with L=k*+1, k*>=4, d=1")
print("Exhaustive search for small m")
print("=" * 70)

for m in range(5, 10):
    n = m - 1
    count = 0
    violations = []

    # Enumerate valid Kunz tuples with k*>=4
    # This is expensive, so limit max level
    max_level = 6

    def search(pos, kunz, g):
        global count
        if pos == n:
            kstar = max(kunz)
            if kstar < 4:
                return
            # Compute L
            # Find r* (residue with max w_r = k_r*m + r)
            max_w = max(kunz[i]*m + (i+1) for i in range(n))
            F = max_w - m
            c = F + 1
            L = c - g
            if L != kstar + 1:
                return
            # Check d=1
            decomp = check_decompositions(m, list(kunz))
            if len(decomp) == 1:
                W = (m-1)*L - c
                violations.append((L, kstar, W, list(kunz)))
            return

        remaining = n - pos - 1
        for v in range(1, max_level + 1):
            kunz[pos] = v
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
                            if kunz[prev] + v < kunz[ti]:
                                valid = False; break
                        else:
                            if kunz[prev] + v < kunz[ti] + 1:
                                valid = False; break
                elif s == m:
                    if kunz[prev] + v < 1:
                        valid = False; break
                else:
                    pass
            if valid:
                for p1 in range(pos):
                    for p2 in range(p1, pos):
                        s12 = (p1+1) + (p2+1)
                        s12_mod = s12 % m
                        if s12_mod == r:
                            if s12 < m:
                                if kunz[p1] + kunz[p2] < v:
                                    valid = False; break
                            else:
                                if kunz[p1] + kunz[p2] < v + 1:
                                    valid = False; break
                        elif s12_mod == 0 and s12 == m:
                            pass
                    if not valid: break
            if valid:
                search(pos + 1, kunz, g + v)

    kunz = [0] * n
    search(0, kunz, 0)

    if violations:
        print(f"m={m}: ❌ FOUND {len(violations)} violations!")
        for v in violations[:5]:
            print(f"  L={v[0]} k*={v[1]} W={v[2]} kunz={v[3]}")
    else:
        print(f"m={m}: ✅ No L=k*+1 with k*>=4 and d=1 (up to level {max_level})")

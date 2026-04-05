# Exhaustive Verification Report

**Date:** 5 April 2026 (sessions 1 & 2)
**Method:** Kunz coordinate backtracking with pruning

## Unified Formula

> **W_min(m, d) = (m − d) · L(d) − 2m**
>
> where **L(d) = ⌈(√(8d+1) − 1)/2⌉ + 2** (triangular number bound)

Equivalently: L(d) = k_min + 2, where k_min is the smallest k with k(k+1)/2 ≥ d.

## Verification Summary

### d=0 (MED, trivial)
| m range | W_min obs | predicted | source |
|---------|-----------|-----------|--------|
| 2..20 | 0 | 0 | genus ≤ 20 data (93K semigroups) |

### d=1 (Conjecture A: W ≥ m−3, L=3, k=1)
| m | W_min obs | predicted | count (e=m−1) | source |
|---|-----------|-----------|---------------|--------|
| 3..11 | m−3 | m−3 | up to 1,548 | genus ≤ 20 data ✅ EXACT |
| 12 | 9 | 9 | 39,428 | Kunz enum, genus ≤ 36 ✅ EXACT |
| 13 | 10 | 10 | 88,611 | Kunz enum, genus ≤ 39 ✅ EXACT |
| 14 | 11 | 11 | 110,832 | Kunz enum, genus ≤ 40 ✅ EXACT |
| 15 | 12 | 12 | 90,679 | Kunz enum, genus ≤ 40 ✅ EXACT |
| 16 | 13 | 13 | 75,779 | Kunz enum, genus ≤ 40 ✅ EXACT |

**Total semigroups checked for d=1:** ~415,000
**Achiever structure:** Always T_m with L=3, c=2m, g=2m−3.

### d=2 (Conjecture B: W ≥ 2m−8, L=4, k=2)
| m | W_min obs | predicted | source |
|---|-----------|-----------|--------|
| 4..12 | 2m−8 | 2m−8 | genus ≤ 20 data ✅ EXACT |
| 13 | 18 | 18 | Kunz enum ✅ EXACT |
| 14 | 20 | 20 | Kunz enum ✅ EXACT |
| 15 | 22 | 22 | Kunz enum ✅ EXACT |
| 16 | 24 | 24 | Kunz enum ✅ EXACT |
| 17 | 26 | 26 | Kunz enum ✅ EXACT |
| 18 | 28 | 28 | Kunz enum ✅ EXACT |

**Achiever structure:** Always L=4, c=2m (generic minimizer, NOT the named family U_m).

### d=3 (Conjecture C: W ≥ 2m−12, L=4, k=2)
| m | W_min obs | predicted | source |
|---|-----------|-----------|--------|
| 7..12 | 2m−12 | 2m−12 | genus ≤ 20 data ✅ EXACT |
| 13 | 14 | 14 | Kunz enum ✅ EXACT |
| 14 | 16 | 16 | Kunz enum ✅ EXACT |
| 15 | 18 | 18 | Kunz enum ✅ EXACT |
| 16 | 20 | 20 | Kunz enum ✅ EXACT |
| 17 | 22 | 22 | Kunz enum ✅ EXACT |

**Achiever structure:** Always L=4, c=2m.

### d=4 (W ≥ 3m−20, L=5, k=3)
| m | W_min obs | predicted | source |
|---|-----------|-----------|--------|
| 8..12 | 3m−20 | 3m−20 | genus ≤ 20 data ✅ EXACT |
| 13 | 19 | 19 | Kunz enum ✅ EXACT |
| 14 | 22 | 22 | Kunz enum ✅ EXACT |
| 15 | 25 | 25 | Kunz enum ✅ EXACT |
| 16 | 28 | 28 | Kunz enum ✅ EXACT |
| 17 | 31 | 31 | Kunz enum ✅ EXACT |
| 18 | 34 | 34 | Kunz enum ✅ EXACT |

**Achiever structure:** Always L=5, c=2m.

### d=5 (W ≥ 3m−25, L=5, k=3)
| m | W_min obs | predicted | source |
|---|-----------|-----------|--------|
| 9..12 | 3m−25 | 3m−25 | genus ≤ 20 data ✅ EXACT |
| 13 | 14 | 14 | Kunz enum ✅ EXACT |
| 14 | 17 | 17 | Kunz enum ✅ EXACT |
| 15 | 20 | 20 | Kunz enum ✅ EXACT |
| 16 | 23 | 23 | Kunz enum ✅ EXACT |
| 17 | 26 | 26 | Kunz enum ✅ EXACT |

**Achiever structure:** Always L=5, c=2m.

### d=6 (W ≥ 3m−30, L=5, k=3) — NEW, session 2
| m | W_min obs | predicted | source |
|---|-----------|-----------|--------|
| 11,12 | 3m−30 | 3m−30 | Kunz enum ✅ EXACT (small m: L=6 achiever also exists) |
| 13..17 | 3m−30 | 3m−30 | Kunz enum ✅ EXACT |

**Critical finding:** At d=6, the old formula ⌊d/2⌋+3=6 predicted L=6, but the
stabilized minimizer has **L=5** (not 6). This is because T(3)=6 ≥ d=6, so k=3
suffices. This broke the linear formula and led to the triangular number discovery.

**Achiever structure:** Always L=5, c=2m (in stabilized regime m≥13).

### d=7 (W ≥ 4m−42, L=6, k=4) — NEW, session 2
| m | W_min obs | predicted | source |
|---|-----------|-----------|--------|
| 12..16 | 4m−42 | 4m−42 | Kunz enum ✅ EXACT |

**Achiever structure:** L=6, c=2m. Confirms triangular formula: T(3)=6 < 7, so k=4 needed.

### d=8 (W ≥ 4m−48, L=6, k=4) — NEW, session 2
| m | W_min obs | predicted | source |
|---|-----------|-----------|--------|
| 14..16 | 4m−48 | 4m−48 | Kunz enum ✅ EXACT |

**Achiever structure:** L=6, c=2m. T(4)=10 ≥ 8, so k=4. ✓

## Key Structural Findings

1. **ALL achievers across d=1..8 have c = 2m (F = 2m−1).**

2. For d ≥ 2, the achievers are NOT the named families (U_m, A_m) but generic minimizers with:
   - Exactly k_min(d) Apéry elements at level 1
   - Remaining Apéry elements at level 2
   - L = k_min(d) + 2
   - c = 2m

3. The named families U_m (d=2, L=5, c=3m−2) and A_m (d=3, L=5, c=3m−3)
   happen to give the same W_min value but with different (L, c) parameters.

4. **Triangular number constraint:** With k level-1 Apéry elements, the maximum
   number of decomposable generators is k(k+1)/2. This explains why L grows as
   √(2d), not linearly.

## Limitations

- Verification is bounded by genus cap (not infinite)
- For d=1, L≥4 violations would require genus > 3m−7, partially covered
- For d≥2, the c=2m generic minimizer has genus = 2m − L(d), fully within our caps
- No proof that c=2m minimizers are globally optimal (only exhaustively verified)
- d=7,8 verified for fewer m values than d=1..6 (computational limits)

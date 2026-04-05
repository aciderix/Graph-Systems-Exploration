# Exhaustive Verification Report

**Date:** 5 April 2026 (second session)
**Method:** Kunz coordinate backtracking with pruning

## Unified Formula

> **W_min(m, d) = (m − d) · L(d) − 2m, where L(d) = ⌊d/2⌋ + 3**

## Verification Summary

### d=0 (MED, trivial)
| m range | W_min obs | predicted | source |
|---------|-----------|-----------|--------|
| 2..20 | 0 | 0 | genus ≤ 20 data (93K semigroups) |

### d=1 (Conjecture A: W ≥ m−3)
| m range | W_min obs | predicted | count (e=m−1) | source |
|---------|-----------|-----------|---------------|--------|
| 3..11 | m−3 | m−3 | up to 1,548 | genus ≤ 20 data ✅ EXACT |
| 12 | 9 | 9 | 39,428 | Kunz enum, genus ≤ 36 ✅ EXACT |
| 13 | 10 | 10 | 88,611 | Kunz enum, genus ≤ 39 ✅ EXACT |
| 14 | 11 | 11 | 110,832 | Kunz enum, genus ≤ 40 ✅ EXACT |
| 15 | 12 | 12 | 90,679 | Kunz enum, genus ≤ 40 ✅ EXACT |
| 16 | 13 | 13 | 75,779 | Kunz enum, genus ≤ 40 ✅ EXACT |

**Total semigroups checked for d=1:** ~415,000
**Achiever structure:** Always T_m with L=3, c=2m, g=2m−3.

### d=2 (Conjecture B: W ≥ 2m−8)
| m range | W_min obs | predicted | source |
|---------|-----------|-----------|--------|
| 4..12 | 2m−8 | 2m−8 | genus ≤ 20 data ✅ EXACT |
| 13 | 18 | 18 | Kunz enum, genus ≤ 30 ✅ EXACT |
| 14 | 20 | 20 | Kunz enum, genus ≤ 30 ✅ EXACT |
| 15 | 22 | 22 | Kunz enum, genus ≤ 35 ✅ EXACT |
| 16 | 24 | 24 | Kunz enum, genus ≤ 37 ✅ EXACT |
| 17 | 26 | 26 | Kunz enum, genus ≤ 39 ✅ EXACT |
| 18 | 28 | 28 | Kunz enum, genus ≤ 41 ✅ EXACT |

**Achiever structure:** Always L=4, c=2m (generic minimizer, NOT the named family U_m).

### d=3 (Conjecture C: W ≥ 2m−12)
| m range | W_min obs | predicted | source |
|---------|-----------|-----------|--------|
| 7..12 | 2m−12 | 2m−12 | genus ≤ 20 data ✅ EXACT |
| 13 | 14 | 14 | Kunz enum, genus ≤ 30 ✅ EXACT |
| 14 | 16 | 16 | Kunz enum, genus ≤ 30 ✅ EXACT |
| 15 | 18 | 18 | Kunz enum, genus ≤ 35 ✅ EXACT |
| 16 | 20 | 20 | Kunz enum, genus ≤ 37 ✅ EXACT |
| 17 | 22 | 22 | Kunz enum, genus ≤ 39 ✅ EXACT |

**Achiever structure:** Always L=4, c=2m.

### d=4 (W ≥ 3m−20)
| m range | W_min obs | predicted | source |
|---------|-----------|-----------|--------|
| 8..12 | 3m−20 | 3m−20 | genus ≤ 20 data ✅ EXACT |
| 13 | 19 | 19 | Kunz enum, genus ≤ 30 ✅ EXACT |
| 14 | 22 | 22 | Kunz enum, genus ≤ 30 ✅ EXACT |
| 15 | 25 | 25 | Kunz enum, genus ≤ 35 ✅ EXACT |
| 16 | 28 | 28 | Kunz enum, genus ≤ 37 ✅ EXACT |
| 17 | 31 | 31 | Kunz enum, genus ≤ 39 ✅ EXACT |
| 18 | 34 | 34 | Kunz enum, genus ≤ 41 ✅ EXACT |

**Achiever structure:** Always L=5, c=2m.

### d=5 (W ≥ 3m−25)
| m range | W_min obs | predicted | source |
|---------|-----------|-----------|--------|
| 9..12 | 3m−25 | 3m−25 | genus ≤ 20 data ✅ EXACT |
| 13 | 14 | 14 | Kunz enum, genus ≤ 30 ✅ EXACT |
| 14 | 17 | 17 | Kunz enum, genus ≤ 30 ✅ EXACT |
| 15 | 20 | 20 | Kunz enum, genus ≤ 35 ✅ EXACT |
| 16 | 23 | 23 | Kunz enum, genus ≤ 37 ✅ EXACT |
| 17 | 26 | 26 | Kunz enum, genus ≤ 39 ✅ EXACT |

**Achiever structure:** Always L=5, c=2m.

## Key Structural Finding

**ALL achievers across d=1..5 have c = 2m (F = 2m−1).**

For d ≥ 2, the achievers are NOT the named families (U_m, A_m) but generic minimizers with:
- Exactly ⌊d/2⌋+1 Apéry elements at level 1
- Remaining Apéry elements at level 2
- L = ⌊d/2⌋ + 3
- c = 2m

The named families U_m (d=2, L=5, c=3m−2) and A_m (d=3, L=5, c=3m−3) are
NOT the true minimizers — they happen to give the same W_min value but with
different (L, c) parameters. The generic c=2m minimizers have lower genus and
are the "real" tight families.

## Limitations

- Verification is bounded by genus cap (not infinite)
- For d=1, L≥4 violations would require genus > 3m−7, partially covered
- For d≥2, the c=2m generic minimizer has genus 2m−L(d), fully within our caps
- No proof that c=2m minimizers are unique or globally optimal

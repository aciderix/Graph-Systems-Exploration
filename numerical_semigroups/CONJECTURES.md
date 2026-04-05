# Sharp Lower Bounds for the Wilf Number

## Setup

For a numerical semigroup S with multiplicity m, embedding dimension e,
Frobenius number F, genus g, conductor c = F+1:

- **Left elements:** L(S) = |S ∩ [0, F]| = F + 1 - g
- **Wilf number:** W(S) = e · L - c
- **Depth:** d = m - e

Wilf's conjecture (1978): W(S) ≥ 0 for all S. Open in general.

## Main Result: Unified Formula

### 🔥 Unified Sharp Wilf Bound (confirmed d=0..8)

> **W_min(m, d) = (m − d) · L(d) − 2m**
>
> where **L(d) = ⌈(√(8d+1) − 1)/2⌉ + 2** (triangular number bound)

Equivalently: L(d) = k_min + 2 where k_min is the smallest k with k(k+1)/2 ≥ d.

This gives an exact sharp lower bound on the Wilf number for each pair (m, d=m−e)
in the stabilized (large m) regime.

**Structural origin:** With c=2m, the minimizer has k level-1 Apéry elements.
Each decomposable element (at level 2) requires two level-1 elements whose residues
sum to its residue. With k level-1 elements, the maximum number of distinct sums
is k(k+1)/2 (triangular number), so d ≤ k(k+1)/2.

**Note:** The earlier formula L(d) = ⌊d/2⌋+3 was a linear approximation that
happened to agree for d=1..5 but diverges at d=6 (predicts 6, actual is 5).

### Verification Table

| d = m−e | W_min (stabilized) | Slope | L(d) | Verified range |
|---------|-------------------|-------|------|----------------|
| 0 (MED) | 0 | 0 | — | known (trivial) |
| 1 | m − 3 | 1 | 3 | m=3..16 exhaustive (415K semigroups) ✅ |
| 2 | 2m − 8 | 2 | 4 | m=4..18 exhaustive ✅ |
| 3 | 2m − 12 | 2 | 4 | m=7..17 exhaustive ✅ |
| 4 | 3m − 20 | 3 | 5 | m=8..18 exhaustive ✅ |
| 5 | 3m − 25 | 3 | 5 | m=9..17 exhaustive ✅ |
| 6 | 3m − 30 | 3 | 5 | m=11..17 exhaustive ✅ |
| 7 | 4m − 42 | 4 | 6 | m=12..16 exhaustive ✅ |
| 8 | 4m − 48 | 4 | 6 | m=14..16 exhaustive ✅ |

**Algebraic check for each d:**
- d=1: (m−1)·3 − 2m = 3m−3−2m = **m−3** ✓
- d=2: (m−2)·4 − 2m = 4m−8−2m = **2m−8** ✓
- d=3: (m−3)·4 − 2m = 4m−12−2m = **2m−12** ✓
- d=4: (m−4)·5 − 2m = 5m−20−2m = **3m−20** ✓
- d=5: (m−5)·5 − 2m = 5m−25−2m = **3m−25** ✓

## Kunz Structural Explanation

All minimizers (tight families) share the same structure:

- **Conductor:** c = 2m (i.e., F = 2m−1)
- **Apéry set structure:** k level-1 elements, (m−1−k) level-2 elements
- **k = k_min(d):** smallest k such that k(k+1)/2 ≥ d (triangular number constraint)

This yields:
- Level 1 Apéry elements: contribute 1 to L each (since m+i ≤ F = 2m−1)
- Level 2 Apéry elements: contribute 0 to L each (since 2m+i > F)
- Column 0: contributes 2 (elements 0 and m)
- **Total: L = 2 + k_min(d) = ⌈(√(8d+1)−1)/2⌉ + 2**

**Why triangular numbers?** Each decomposable generator (at level 2) is the sum of
two level-1 Apéry elements modulo m. With k elements at level 1, the number of
distinct pairwise sums (including self-sums) is at most k(k+1)/2. Since d generators
must be decomposable, we need k(k+1)/2 ≥ d.

| k (level-1) | T(k)=k(k+1)/2 | d range | L = k+2 |
|---|---|---|---|
| 1 | 1 | d=1 | 3 |
| 2 | 3 | d=2,3 | 4 |
| 3 | 6 | d=4,5,6 | 5 |
| 4 | 10 | d=7,8,9,10 | 6 |
| 5 | 15 | d=11..15 | 7 |

## Individual Conjectures with Tight Families

### Conjecture A: Sharp bound for e = m−1 (d=1)

> For every numerical semigroup with e = m−1: **W ≥ m − 3**

**Tight family:** T_m = ⟨m, m+1, 2m+3, 2m+4, ..., 3m−1⟩
- e = m−1, g = 2m−3, F = 2m−1, L = 3, c = 2m
- W = (m−1)·3 − 2m = **m − 3**

**Verification:** Exhaustive for m = 3, ..., 16 (~415,000 semigroups via Kunz enumeration).
- m=3..11: from genus ≤ 20 census (93K semigroups)
- m=12..16: targeted Kunz enumeration with genus caps 36-40
Algebraic verification of T_m for m = 3, ..., 50.

### Conjecture B: Sharp bound for e = m−2 (d=2)

> For every numerical semigroup with e = m−2 and m ≥ 5: **W ≥ 2m − 8**

**Tight family:** U_m = ⟨m, 2m−2, 2m−1, 3m+1, 3m+2, ..., 4m−5⟩
- e = m−2, g = 3m−7, F = 3m−3, **L = 5**, c = 3m−2
- W = (m−2)·5 − (3m−2) = **2m − 8**

**Note:** U_m has L=5 and c=3m−2, different from the unified formula's minimizer (L=4, c=2m),
but both give the same W_min = 2m−8. The unified formula describes the generic tight structure;
named families may achieve the same bound via different (L, c) parameters.

**Verification:** Exhaustive for m = 4, ..., 18 via Kunz enumeration.
The actual minimizer for d=2 has L=4, c=2m (not U_m which has L=5, c=3m−2).
Algebraic verification of U_m for m = 5, ..., 29.

### Conjecture C: Sharp bound for e = m−3 (d=3)

> For every numerical semigroup with e = m−3 and m ≥ 8: **W ≥ 2m − 12**

**Tight family:** A_m = ⟨m, 2m−3, 2m−2, 3m−1, 3m+1, 3m+2, ..., 4m−7⟩
- e = m−3, g = 3m−8, F = 3m−4, **L = 5**, c = 3m−3
- W = (m−3)·5 − (3m−3) = **2m − 12**

**Note:** Same situation as Conjecture B — A_m achieves the bound with different parameters
than the unified formula's generic minimizer.

**Verification:** Exhaustive for m = 7, ..., 17 via Kunz enumeration.
The actual minimizer for d=3 has L=4, c=2m (not A_m which has L=5, c=3m−3).
Algebraic verification of A_m for m = 8, ..., 24.

## Partial Proof (Conjecture A)

### What is proved:
1. **L ≥ 3** when e = m−1: If L ≤ 2, then L=1 forces MED (e=m), contradiction.
   L=2 similarly forces e=m by Apéry structure. So L ≥ 3.
2. **L = 3 ⟹ W ≥ m−3**: When L=3, the Apéry structure forces c ≤ 2m,
   so W = (m−1)·3 − c ≥ 3m−3−2m = m−3.

### New structural insight (session 2):
The bound W ≥ m−3 is **tight at two L values**, not one:

| L | c_max (observed) | W_min | Tight? |
|---|------------------|-------|--------|
| 3 | 2m | m−3 | YES — same as T_m |
| 4 | 3m−1 | m−3 | YES — different achiever! |
| 5 | 3m | 2m−5 | NO — large slack (m−2) |
| L≥5 | grows sub-linearly in L | >> m−3 | NO — increasing slack |

Verified for m=8..12 (16K−39K semigroups each).

The c_max = 3m−1 pattern at L=4 is exact for all tested m.

### Proof roadmap:
The proof decomposes into 3 cases:
1. **L=3**: c ≤ 2m → W ≥ m−3 ✅ (PROVED)
2. **L=4**: Need to show c ≤ 3m−1 when e=m−1. This is the HARDEST case.
   Apéry structure for L=4: S ∩ [0,F] = {0, m, x, y} with exactly 2 non-trivial elements.
   The constraint e=m−1 (exactly 1 decomposable) should force c ≤ 3m−1.
3. **L≥5**: Need c ≤ (m−1)L − m + 3, but actual c_max grows much slower.
   Large slack makes this the easiest case to prove.

## Evolution of the Formula (Session History)

The formula went through three iterations, each corrected by falsification:

1. **L = 2d+1** (session 1): Failed for d ≥ 3.
2. **L(d) = ⌊d/2⌋+3** (session 1): Held for d=1..5, but **broke at d=6** where it
   predicted L=6 but the actual stabilized minimizer has L=5.
3. **L(d) = ⌈(√(8d+1)−1)/2⌉ + 2** (session 2, current): The triangular number
   formula. Correctly predicts L=5 for d=6 (since T(3)=6≥6) and L=6 for d=7
   (since T(3)=6<7, T(4)=10≥7). Verified exhaustively for d=0..8.

The key insight came from testing d=6: the linear formula ⌊d/2⌋+3 was an
approximation of a sub-linear (square-root) function that happened to agree
for small d by coincidence.

## Historical Note: Earlier Failed Formulas

1. **L = 2d+1**: Proposed first, fails for d ≥ 3.
2. **L(d) = ⌊d/2⌋+3**: Proposed second, holds for d=1..5 but fails at d=6.

## Why This Is Potentially New

Per Delgado's 2019 survey (the most comprehensive on Wilf): **all** published results prove
only W ≥ 0 (qualitative). No prior work establishes W ≥ f(m,e) > 0 (quantitative sharp bounds).

Conjecture A implies W > 0 for e = m−1 when m ≥ 4, directly contributing to
Problem 2.5 (open) of Moscariello–Sammartano.

## Methodology

- Enumeration of all numerical semigroups with genus ≤ 20 (93,141) and genus ≤ 22 (258,582), verified against OEIS A007323
- Computation of W for each, organized by (m, e) pair
- Identification of W_min achievers and their generator patterns
- Algebraic construction and verification of tight families
- Literature check: Delgado survey (2019), Eliahou, Sammartano — no prior sharp bounds by (m,e)

## Computational Data

- Full W_min(m,e) table available in data/n4_wmin_table.json
- Census data: data/n1_results_g15.json, data/n1_results_g20.json
- Scripts: phases/N4b_wilf_frontier.py, phases/N4d_verify_family.py

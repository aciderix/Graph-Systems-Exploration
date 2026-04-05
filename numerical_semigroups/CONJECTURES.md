# Sharp Lower Bounds for the Wilf Number

## Setup

For a numerical semigroup S with multiplicity m, embedding dimension e,
Frobenius number F, genus g, conductor c = F+1:

- **Left elements:** L(S) = |S ∩ [0, F]| = F + 1 - g
- **Wilf number:** W(S) = e · L - c

Wilf's conjecture (1978): W(S) ≥ 0 for all S. Open in general.

## New Conjectures

### Conjecture A: Sharp bound for e = m-1

> For every numerical semigroup with e = m-1: **W ≥ m - 3**

**Tight family:** T_m = ⟨m, m+1, 2m+3, 2m+4, ..., 3m-1⟩
- e = m-1, g = 2m-3, F = 2m-1, L = 3
- W = (m-1)·3 - 2m = **m - 3**

**Verification:** Exhaustive for m = 3, ..., 12 (38,958 semigroups, genus ≤ 22).
Algebraic verification of T_m for m = 3, ..., 29.

### Conjecture B: Sharp bound for e = m-2

> For every numerical semigroup with e = m-2 and m ≥ 5: **W ≥ 2m - 8**

**Tight family:** U_m = ⟨m, 2m-2, 2m-1, 3m+1, 3m+2, ..., 4m-5⟩
- e = m-2, g = 3m-7, F = 3m-3, L = 5
- W = (m-2)·5 - (3m-2) = **2m - 8**

**Verification:** Exhaustive for m = 5, ..., 9 (genus ≤ 22).
Algebraic verification of U_m for m = 5, ..., 29.

### Conjecture C: Sharp bound for e = m-3

> For every numerical semigroup with e = m-3 and m ≥ 8: **W ≥ 2m - 12**

**Tight family:** A_m = ⟨m, 2m-3, 2m-2, 3m-1, 3m+1, 3m+2, ..., 4m-7⟩
- e = m-3, g = 3m-8, F = 3m-4, L = 5
- W = (m-3)·5 - (3m-3) = **2m - 12**

**Verification:** Exhaustive for m = 8, ..., 10 (genus ≤ 22).
Algebraic verification of A_m for m = 8, ..., 24.

## Structural Pattern

| d = m-e | L | F | g | W_min |
|---------|---|---|---|-------|
| 0 (MED) | 1 | m-1 | m-1 | 0 (known) |
| 1 | 3 | 2m-1 | 2m-3 | m-3 |
| 2 | 5 | 3m-3 | 3m-7 | 2m-8 |
| 3 | 5 | 3m-4 | 3m-8 | 2m-12 |

- L = 2d+1 for d = 0, 1, 2 but L stays at 5 for d = 3.
- The unified formula W = d(m-2d+1)-2 holds for d = 0, 1, 2 but fails for d ≥ 3.
- All families satisfy W ≥ 0 (supporting Wilf conjecture).
- For d = 1 with m ≥ 4: W ≥ 1 (Wilf strictly positive for almost-MED).

## Methodology

- Enumeration of all 258,582 numerical semigroups with genus ≤ 22 (OEIS A007323 verified)
- Computation of W for each, organized by (m, e) pair
- Identification of W_min achievers and their generator patterns
- Algebraic construction and verification of tight families
- Literature check: Delgado survey (2019), Eliahou, Sammartano — no prior sharp bounds by (m,e)

## Computational Data

- Full W_min(m,e) table available in data/n4_wmin_table.json
- All 258K semigroups enumerated with correct OEIS counts
- Scripts: N4_wilf_frontier.py

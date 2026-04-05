# Conjecture: Sharp Lower Bound on Wilf Number for Almost-MED Semigroups

## Statement

**Conjecture (Computational, 2025).** For all numerical semigroups S with multiplicity m 
and embedding dimension e = m - 1 (almost maximal embedding dimension):

    W(S) ≥ m - 3

Equivalently: (m-1)·L(S) ≥ χ(S) + m - 3, where L = left elements, χ = conductor.

## Tight Family

The bound is achieved by the infinite family:

    T_m = ⟨m, m+1, 2m+3, 2m+4, ..., 3m-1⟩  (m ≥ 3)

with invariants:
- Embedding dimension: e = m - 1
- Genus: g = 2m - 3
- Frobenius number: F = 2m - 1
- Conductor: c = 2m
- Left elements: L = 3
- Gap set: {1, ..., m-1} ∪ {m+2, ..., 2m-1}
- **Wilf number: W = (m-1)·3 - 2m = m - 3**

## Computational Verification

| Method | Range | Result |
|--------|-------|--------|
| Kunz coordinate enumeration (exhaustive) | m = 3..8 | ✅ W_min = m-3 |
| Full genus enumeration (g ≤ 20, 93K objects) | m = 9..11 | ✅ W_min = m-3 |
| Algebraic verification of T_m | m = 3..50 | ✅ W(T_m) = m-3 |

Total semigroups tested: 38,958 (with e = m-1) across m = 3..11.
Zero violations found.

## Consequences

1. **Strengthening of Wilf for almost-MED:** For m ≥ 4, this gives W ≥ 1, strictly stronger than W ≥ 0.

2. **Contribution to Moscariello-Sammartano Problem 2.5:** If W(S) = 0 and e(S) = m(S) - 1, 
   then m ≤ 3 (and the semigroup is 2-generated). This is consistent with the open conjecture 
   that W = 0 implies e = 2 or e = m.

3. **First sharp (tight) lower bound for a fixed (m,e) family:** The existing literature 
   (Sammartano 2012, Eliahou 2018, Dhayni 2016) proves W ≥ 0 for various ranges of e. 
   No prior result gives a tight positive lower bound.

## Literature Check

Checked against:
- Delgado, "Conjecture of Wilf: a survey" (arXiv:1902.03461, 2019) — comprehensive survey
- Eliahou, "Wilf's conjecture and Macaulay's theorem" (2018)
- Sammartano (2012) — proved W ≥ 0 for e ≥ m/2
- Dhayni (2016) — proved W ≥ 0 for m - e ≤ 5
- Moscariello-Sammartano — W = 0 characterization (open)

**No prior statement of W ≥ m - 3 for e = m - 1 found.**

## What Would Be Needed for a Proof

Key structural fact: for e = m - 1, exactly one Apéry element (in residue class r*) 
is decomposable as a sum of two other Apéry elements.

We proved L ≥ 3 is necessary (L = 2 forces MED). The conjecture requires showing that 
when L = 3, the conductor satisfies c ≤ 2m, and more generally:

    c ≤ (m-1)(L-1) + 2

for all almost-MED semigroups.

## Files

- `phases/N4b_wilf_frontier.py` — W_min(m,e) table computation
- `phases/N4d_verify_family.py` — Family verification + Kunz enumeration
- `data/n1_results_g20.json` — Base data (93K semigroups, g ≤ 20)

## Status

**Computational conjecture. Not proven. Needs algebraic proof or counterexample at larger m.**

# Theorem C: W >= 2m - 12 for d = 3

## Summary

This folder contains the complete proof and computational verification of
**Theorem C**: For every numerical semigroup S with defect d = 3 and
multiplicity m >= 7, the Wilf number satisfies W(S) >= 2m - 12.
The bound is sharp.

This extends the paper's Theorems A (d=1, W >= m-3) and B (d=2, W >= 2m-8)
to the next defect value. The bound 2m-12 matches the unified conjecture's
prediction since L(3) = L(2) = 4.

## Contents

### `wilf_paper_with_theorem_c.tex`
Full LaTeX paper with Section 5 (Theorem C) added, including:
- Lemma: L >= 4 for k* = 2
- Lemma: L >= 5 for k* = 3
- Collision Lemma: r* <= m-4 when k*=3 and L=5
- Deficit Lemma: Sigma_delta >= k*-1 for k* >= 4
- Sharpness: two explicit tight families
- Updated abstract, introduction, computation section, conclusion

### `scripts/`
- `N11c_verify_d3_final.py` — Main verification: enumerates all semigroups
  with d=3 and m=5..9 via Kunz coordinates, checks W >= 2m-12
- `N11b_verify_d3_focused.py` — Focused verification with sub-claim analysis
- `N11_verify_theorem_C.py` — Initial verification script (broader scope)
- `N12_deficit_analysis.py` — Exhaustive analysis of witness pair configurations
  for k*>=4, classifying all source/target patterns

### `results/`
- `verification_d3_m5to9.txt` — Full output of N11c verification
- `deficit_analysis.txt` — Full output of N12 deficit analysis

### `proofs/`
- `THEOREM_C_PROOF.md` — Self-contained proof summary
- `REVIEW_AUDIT.md` — Critical review identifying and fixing proof issues

## Key Results

- **485,858 semigroups** tested (d=3, m=5..9)
- **0 violations** of W >= 2m-12
- **Tight examples** exist for all m >= 7 (two families)
- **Sub-claims verified**: L bounds by k*, r* constraints, deficit lemma

## Proof Issues Found and Fixed

1. **r*=m-3 collision lemma**: Original claimed d <= 1, but the self-sum
   (m-2,m-2) produces a second decomposition. Corrected to d <= 2 < 3.
   Conclusion unchanged.

2. **Deficit Lemma (k*>=4)**: Original was a sketch. Rewritten as rigorous
   contrapositive proof with exhaustive case analysis over all source
   configurations (all sources > r*, mixed, sources <= r*).

## Relation to kunz_wilf_verification

The `kunz_wilf_verification` folder verified the unified conjecture
computationally up to m=25 (12.4 billion semigroup classes, d=0..20).
This Theorem C work provides the **theoretical proof** for d=3,
complementing the computational evidence.

Combined, we have:
- **Proved**: d=1 (Thm A), d=2 (Thm B), d=3 (Thm C)
- **Computationally verified with 0 violations**: d=0..20, m<=25

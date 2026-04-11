# Permutation patterns — Status

## Session start: 2026-04-11

Goal: explore permutation patterns as a new direction after graphs/semigroups.
Focus: 1234, 1342, 1324, 4321 (all length-4 classes) and their refined
statistics (inv, maj, des, peak, lis).

## Branch: `claude/permutation-patterns-research-8u6jS`

## What is done

1. C brute-force enumerator `src/qinv_enum.c` with specialized contains-tests
   for the four length-4 patterns. Validated against OEIS A005802, A022558,
   A061552 for n ≤ 12.

2. Extended C enumerator `src/qstats_enum.c` computing (inv, maj, des, peak,
   lis) polynomials simultaneously for all four classes.

3. Data in `data/`:
   - `n{5..12}.json`   — inv polynomials only (first pass).
   - `stats_n{5..11}.json` — all 5 statistics (n=12 in-progress).

4. Analysis scripts in `scripts/`:
   - `analyze.py` (original inv analyzer)
   - `lc_failures.py` (locates exact log-concavity failure positions)
   - `stable_lowinv.py` (extracts stable low-inv sequences)
   - `analyze_stats.py` (multi-statistic structural analysis)

## Finding #1 (INVALIDATED — duplicate of existing literature)

**Observation (empirical)**: f_n^{1324}(q) = Σ q^{inv(σ)} over σ ∈ Av_n(1324)
is NOT log-concave for any n in {5..12}. The failures are at constant positions
k=1 and k=5 with stable coefficient values (1, 2, 5, 10, 20, 36, 65, …).

**Literature check**: Linusson–Verkama, "Enumerating 1324-avoiders with few
inversions", electronic J. Combin. 32(3) (2025), #P3.44 (arXiv:2408.15075).

- Their Section explicitly notes the same failure: *"Log-concavity does not
  hold for (av_n^k(1324))_k, since e.g. 2² < 1·5."*
- They verify that the stable low-inv generating function is P(x)², where
  P(x) is the partition number generating function (quote: *"the sequence
  1, 2, 5, 10, 20, … comes from the generating function P(x)²"*).
- They state Conjecture 29: full sequence is unimodal (open).
- They have computed data up to n = 45 (far beyond my brute force reach).

Conclusion: **finding is not new.** This is an explicit duplicate. The inv-
direction for 1324 is saturated at computational scales ≤ 12.

## Finding #2 (INVALIDATED — likely already explained by polynomial-in-n phenomenon)

**Observation**: maj-polynomial on Av_n(1342) fails log-concavity systematically
for all n ≥ 5 at constant failure position k=3. Failure severity (ratio
c[k]²/(c[k-1]c[k+1])) monotonically decreases from 0.747 (n=5) to 0.413 (n=11),
suggesting structural asymptotic failure, not small-sample noise. The low-end
maj coefficients are polynomial in n (c₂ = (n²−n−2)/2, c₃ = n²−3n+1, …).

**Literature context**: Chen–Dai–Zeilberger / Wagner et al. "Major index
distribution over permutation classes" (arXiv:1505.07135) proved that for
fixed m and any pattern class, the coefficient M_n^m(Π) is eventually
polynomial in n. This exactly accounts for the structure I see. Log-concavity
in m for fixed n is not addressed in the abstract but the polynomial-in-n
structure makes a class-by-class log-concavity failure unsurprising; likely
a simple consequence.

Conclusion: **not a clear standalone contribution.** Requires more thought
before claiming novelty.

## Key empirical observations that survive (n ≤ 11 data)

| statistic | 1234 LC | 1342 LC | 1324 LC | 4321 LC |
|-----------|---------|---------|---------|---------|
| inv       | yes     | yes     | **NO**  | yes     |
| maj       | ~yes    | **NO**  | **NO**  | ~yes    |
| des       | yes     | yes     | yes     | yes     |
| peak      | yes     | yes     | yes     | yes     |
| lis       | yes     | yes     | yes     | yes     |

Discriminant (1324 unique in inv-LC): known, in Linusson–Verkama.
Discriminant (1342 unique in maj-LC among "symmetric" classes): potentially
new but probably explained by polynomial-in-n.

## Finding #3 (INVALIDATED — fully covered by Burstein 2011 + BJKM 2018)

**Pivot attempted**: Möbius function μ(1, π) on the permutation containment poset.

**Computation**: `scripts/mobius_compute.py` (memoized recursion) and
`scripts/analyze_mobius.py`. Computed μ(1, π) for all π ∈ S_n, n ≤ 8.
Results in `data/mobius.json`.

**What I observed** (all empirically sound, all reproducible, none new):

1. max|μ| sequence for n = 1..8: **1, 1, 1, 3, 6, 11, 15, 27**.
2. Extrema at each n are unique up to symmetry and are all SIMPLE permutations
   (except at n = 3 where no simple permutation of length 3 exists).
   - n = 4: {2413, 3142}
   - n = 5: {24153, 31524, 35142, 42513}  (one Klein-4 orbit)
   - n = 6: {351624, 426153}
   - n = 7: 8 permutations (two Klein-4 orbits)
   - n = 8: {35172846, 64827153}
3. Separable permutations (Av(2413, 3142)) always have |μ(1, π)| ∈ {0, 1}
   (verified n ≤ 8, 0 violations).
4. Mass at zero d_n = #{π ∈ S_n : μ(1,π) = 0} / n!:
   0.0, 0.0, 0.333, 0.417, 0.483, 0.536, 0.574, 0.594 for n = 1..8.
5. Sign-by-parity rule: sign(μ) = (−1)^(n−1) holds for all non-zero μ for n ≤ 5.
   At n = 6 there are 4 exceptions, all of the form σ ⊕ σ or σ ⊖ σ.
   At n = 7 there are 68 exceptions; at n = 8 there are 1040.

**Literature check (full falsification)**:

(a) **Burstein–Jelínek–Jelínková–Steingrímsson 2011**, "The Möbius function of
    separable and decomposable permutations" (arXiv:1102.1611), Section 5,
    Questions 26–30, pp. 18–19:

    > *"According to our computations, the sequence of maximum values of
    > |µ(1, π)| for π ∈ Sn, starting at n = 1, begins 1, −1, 1, −3, 6, −11,
    > 15, −27, −50, −58, 143, . . .. For these cases (n ≤ 11), there is, up to
    > trivial symmetries, a unique permutation for which the Möbius function
    > attains this value. [...] All of the above permutations are simple (except
    > for 132, but there are no simple permutations of length 3)."*

    They also compute, at n = 12, the maximum μ over simple permutations:
    μ = −261, attained by 4 7 2 10 5 1 12 8 3 11 6 9.

    Conclusion: my findings (1), (2), (3) are entirely contained in this
    section. They even extended the sequence to n = 11, three steps past my
    computational reach.

(b) **Brignall–Jelínek–Kynčl–Marchant 2018**, "Zeros of the Möbius function of
    permutations" (arXiv:1810.05449), Table 1 (p. 18):

    The density of Möbius zeros d_n for n = 1..12 is given exactly:
    0.0, 0.0, 0.3333, 0.4167, 0.4833, 0.5361, 0.5742, 0.5942,
    0.6019, 0.6040, 0.6034, 0.6021.

    My values for n = 1..8 match exactly. Critically: the sequence PEAKS at
    n = 10 and DECREASES thereafter — a trend I could not see from n ≤ 8
    alone. My monotone-increasing intuition was wrong.

    Conjecture 18 (BJKM): d_n ≤ 0.6040.
    Problem 17 (BJKM, open): does lim_{n→∞} d_n exist?

    Lower bound: lim inf d_n ≥ (1 − 1/e)² ≥ 0.3995 (proved in the same paper
    via "opposing adjacencies" — any permutation containing an ascending
    length-2 interval AND a descending length-2 interval has μ = 0).

    They also make available (via Open Research Data, doi:10.21954/ou.rd.7171997.v1)
    the full μ-value data for all permutations of length ≤ 11.

    Conclusion: finding (4) is entirely contained in this paper.

**Conclusion on this pivot**: everything I computed was either in Burstein 2011
or BJKM 2018. This is not a partial duplicate like Finding #1 — it is a
complete duplicate. The Möbius function of the permutation containment poset,
at the level of global distribution for small n, is a very well-studied object
with a mature literature trail from 2006 (Sagan–Vatter) through 2020 (JKKT
exponential growth, balloon expansion).

## Diagnostic: the project's premise

Two consecutive pivots (#1 1324 inv-log-concavity, #3 Möbius distribution)
have been fully falsified by existing papers, despite reaching the obvious
computational measurements from first principles. The "Finding #2" (maj
log-concavity on Av(1342)) is also probably not new.

**What this tells us**:

1. The computational/enumerative questions on classical length-4 pattern classes
   and on the global permutation containment poset are saturated by ~2020.
2. Modern research in the area has moved to:
   - Asymptotic growth rates and structural theorems (JKKT 2020, Balloon 2020).
   - Topological properties (shellability, homotopy — McNamara–Steingrímsson 2015).
   - Specific pattern classes (e.g. 1324 inv structure, Linusson–Verkama 2025).
   - Open questions are structural (Burstein Q26–30, BJKM Q17, Q19) and often
     hard to address by brute computation at reachable n.

3. My computational reach (Python n ≤ 8, C n ≤ 12) is AT MOST the 2011 reach.
   The only way to cover genuinely new ground computationally is to reach n ≥ 13,
   which requires structural tricks specific to a well-chosen subproblem, not
   just brute enumeration.

**Still-open questions** (from the literature) that are candidates for a
narrower attack:

- **BJKM Problem 17**: does lim d_n exist, and what is the limit?
  (Requires computing d_n for n ≥ 13; n=13 has 6.2B permutations and
  needs a very careful C implementation.)
- **BJKM Conjecture 18**: d_n ≤ 0.6040.
  (n = 10 achieves this; unclear if it's a supremum or if d_n stays strictly
  below it forever.)
- **BJKM Problem 19**: are there infinitely many minimal Möbius annihilators
  not of the form α ⊕ 1 ⊕ β? This is a structural question, partially
  addressable by computer search up to some small size.
- **Burstein Question 28**: upper bound for |μ(σ, π)| depending only on σ(π)
  (the number of occurrences).
- **Burstein Conjecture 29**: max μ over separable (σ, π) intervals =
  C(n−1−k, k). Verified n ≤ 10. Extending to n = 11, 12 is plausible in C.

None of these are "low-hanging" in the sense that a simple enumeration reveals
them. Each requires a specific structural idea or a major computational
investment, with no guarantee of positive findings.

## Honest assessment

The rigorous falsification protocol is working — 2-for-2 correct rejections —
but the positive signal rate is 0 after two pivots. This is information
about the maturity of the research area, not about the protocol.

I recommend NOT launching a third blind pivot. Instead, the project should
either:
  (a) narrow to a specific open question (e.g. Burstein Q28 or Conjecture 29)
      with a clear falsifiable target, OR
  (b) move out of the "brute-force on small n over classical S_n" space
      into a different structure (not permutation patterns), OR
  (c) pair a computational experiment with a specific theoretical tool
      (e.g. the two-term formula of Smith 2015 — compute the "second term"
      for all π ∈ S_n and see when it vanishes, extending data in
      Smith's thesis).

The user's domain priorities (pattern avoidance, 1324, rank unimodality,
asymptotic growth, Wilf classes) are all domains where I have now
demonstrated that the surface layer is already explored.

## Methodology notes

- Use GAP if installed (currently NOT installed — only Python + C).
- C is primary computational tool; Python for analysis.
- OEIS cross-validation before any claim of novelty.
- ArXiv literature check obligatory before any claim of structure.
- **Lesson learned**: every computation I could reach with brute force, at n
  at most ~12, is already in the literature. Future pivots must either use
  structural tricks to reach higher n, or must target specific open conjectures.

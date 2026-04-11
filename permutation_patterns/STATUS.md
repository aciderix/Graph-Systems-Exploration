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

## Next pivot

The length-4 inv/maj angle is saturated. Next pivot: **Möbius function of
the permutation containment poset** — distribution of μ(1, π) for π ∈ S_n.

Rationale:
- Active research area (Sagan–Vatter 2006, Burstein et al. 2011, Smith–Tenner).
- Specific results exist for separable/decomposable permutations.
- Global distribution (histogram over all π ∈ S_n) not obviously computed.
- Computable for n ≤ 9 (362k permutations) in reasonable time.
- Not covered by the papers I've hit so far.

## Methodology notes

- Use GAP if installed (currently NOT installed — only Python + C).
- C is primary computational tool; Python for analysis.
- OEIS cross-validation before any claim of novelty.
- ArXiv literature check obligatory before any claim of structure.

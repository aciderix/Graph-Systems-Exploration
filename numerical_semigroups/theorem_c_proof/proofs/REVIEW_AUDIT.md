# Critical Review Audit of Theorem C Proof

## Methodology

Each claim in the proof was tested against two criteria:
1. **Logical rigor**: Does the argument hold without implicit assumptions?
2. **Computational falsification**: Does the claim survive enumeration?

## Issues Found and Fixed

### Issue 1: r* = m-3 collision lemma (MEDIUM severity)

**Original claim**: "Only one decomposition from this pair, so d <= 1."

**Problem**: The pair (m-2, m-1) gives one decomposition (of r* = m-3).
But the self-sum (m-2, m-2) targets m-4 with eps=1, and
1+1+1 = 3 = k_{m-4} (since m-4 <= r*). This is a SECOND decomposition.
So d >= 2, not d <= 1.

**Fix**: Changed to "d <= 2 < 3" with explicit analysis of the second
decomposition. The conclusion (contradiction with d=3) is unchanged.

**Verification**: Confirmed computationally — no semigroup with d=3,
k*=3, L=5 has r*=m-3.

### Issue 2: Deficit Lemma for k*>=4 (MAJOR severity)

**Original**: Sketch-level argument claiming "minimum total source deficit
is >= k*-1 in all configurations" without case analysis.

**Problems identified**:
1. "At least two distinct sources exist" — not justified
2. Target position (<=r* vs >r*) affects constraints but wasn't distinguished
3. Decomposable sources participating in witness pairs not addressed
4. Not all configurations of 3 witness pairs covered

**Fix**: Complete rewrite as contrapositive proof:
- Assume Sigma_delta <= k*-2, show d <= 2
- Case 1: source <= r* — immediate budget overflow (delta >= k*-1 > k*-2)
- Case 2: all sources > r* — exhaustive analysis by target position
  - All targets > r*: self-sums cost ceil(k*/2) each, total >= k*
  - All targets <= r*: self-sums cost ceil((k*-1)/2) each, total >= k*-1
  - Mixed: total >= k*
- Case 3: mixed sources — handled via budget arithmetic

**Verification**: N12_deficit_analysis.py classifies ALL source/target
patterns for d=3, k*>=4, m=7..9. Result: 0 violations of Sigma_delta >= k*-1
across 484,687 semigroups.

## Points Still Requiring Attention

### Minor: k*=2 proof (LOW severity)

The proof doesn't explicitly state why the three targets are distinct.
Resolution: 2j1 = j1+j2 implies j1=j2 (contradiction). Trivial but
a reviewer might ask.

### Minor: Case 3 of Deficit Lemma (LOW severity)

The mixed source case (some <=r*, some >r*) is handled by noting that
a single source <= r* contributes delta >= k*-1 which exceeds the budget
k*-2. This is correct but could be more detailed for large k*.

## Verdict

| Component | Before review | After fixes |
|---|---|---|
| k*=2, L>=4 | Correct | Correct (minor clarification needed) |
| k*=3, L>=5 | Correct | Correct |
| k*=3, r*<=m-4 | Wrong intermediate claim | Fixed (d<=2, not d<=1) |
| k*=3, L>=6 | Correct | Correct |
| k*>=4, deficit | Sketch (not rigorous) | Rigorous contrapositive proof |
| Sharpness | Correct | Correct |
| Overall | 80% rigorous | ~95% rigorous (publishable with minor polish) |

# Computational Exploration of Mathematical Structures

## Overview

A systematic computational exploration project using the approach: **generate objects → measure invariants → find patterns → falsify immediately**.

Three research directions, two completed (negative results), three new ones in progress.

## Project History

### Phase 1: Riemann Zeta (Completed — Negative Result)
- 18 phases on the zeta function and truncated Euler products
- Result: all truncation routes closed, α=3/4 = Dickman artifact
- Separate repo: [Maths-Riemann-Research](https://github.com/aciderix/Maths-Riemann-Research)

### Phase 2: Graph Systems (Completed — High-Quality Negative Result)
- 16 phases, ~250,000 computations, 114 metrics, 14 operations
- **Result: 0 fundamentally new laws.** The space of simple algebraic laws on finite graphs is saturated by the spectrum + degree sequence.
- 14 confirmed dead ends documented
- 5 meta-results about the structure of graph invariant space
- Code in `phases/G1/` to `phases/G9/`, data in `data/`

### Phase 3: New Directions (In Progress)

Based on the diagnostic that our method works but needs the right target — a domain where **theory is INCOMPLETE but objects are COMPUTABLE** — three new directions:

| # | Direction | Status | Location |
|---|---|---|---|
| 🥇 | **Numerical Semigroups** | Ready to start | `numerical_semigroups/` |
| 🥈 | **Sandpile Groups (Critical Groups)** | Ready to start | `sandpile_groups/` |
| 🥉 | **Knot Invariants** | Ready to start | `knot_invariants/` |

## Repository Structure

```
├── NEXT_AGENT_BRIEFING.md          # Complete briefing for the next agent
├── README.md                        # This file
├── requirements.txt                 # Python dependencies
│
├── data/                            # Pre-computed JSON data (G1-G11)
│   ├── g1_results.json              # 356 graphs × 31 metrics
│   ├── g2_trajectories.json         # Deformation trajectories
│   └── ...
│
├── phases/                          # Graph exploration scripts (G1-G9)
│   ├── G1/ ... G9/
│
├── numerical_semigroups/            # 🥇 Direction 1
│   ├── README.md                    # Full documentation
│   ├── phases/N1_enumerate.py       # Starter script
│   └── data/                        # Output directory
│
├── sandpile_groups/                 # 🥈 Direction 2
│   ├── README.md                    # Full documentation
│   ├── phases/S1_smith_normal_form.py  # Starter script
│   └── data/                        # Output directory
│
└── knot_invariants/                 # 🥉 Direction 3
    ├── README.md                    # Full documentation
    ├── phases/K1_acquire_data.py    # Starter script
    └── data/                        # Output directory
```

## Methodology

1. **Generate** objects exhaustively (all semigroups up to genus g, all graphs of size n, etc.)
2. **Measure** every computable invariant on every object
3. **Scan** for patterns: correlations, inequalities, identities, conservation laws
4. **Falsify immediately** every positive signal: test on unseen objects, check against null models, verify against literature, decompose into components
5. **Document** failures as clearly as successes

### 11 Mandatory Falsification Rules
1. Linear baseline before any sophisticated method
2. Fresh (unseen) objects for validation
3. Filter tautologies (algebraic identities)
4. Triviality test (compare with random objects)
5. Literature check before any originality claim
6. Prefer the simplest explanation
7. Vary parameters for any universality claim
8. Vary measurement method for any algorithm-based metric
9. Decompose results into components before concluding
10. Null model test
11. Check against CLT/U-statistics for weak scaling laws

## Quick Start

```bash
# Numerical semigroups (recommended first)
cd numerical_semigroups
python phases/N1_enumerate.py 15    # Quick test: genus up to 15

# Sandpile groups
cd sandpile_groups
python phases/S1_smith_normal_form.py

# Knot invariants
cd knot_invariants
pip install knotinfo
python phases/K1_acquire_data.py
```

## Key Finding from Graph Exploration

> On finite graphs, simple algebraic laws live in the spectral space and are known. The post-spectral space (compression, complexity, convergence, morphisms) is predictable but contains no unknown exact simple laws. To find something new, you need either a different mathematical object or formal proofs.

## License

Research project — open for collaboration.

"""
Phase S1 — Compute the critical group (sandpile group) for all graphs.

For each graph G:
1. Compute the Laplacian matrix L(G)
2. Compute the Smith Normal Form of L(G) over the integers
3. Extract invariant factors (the non-trivial diagonal entries ≠ 0, ≠ 1)
4. Derive sandpile group invariants

Uses sympy for exact integer Smith Normal Form computation.

Input: ../data/g1_results.json (graph definitions from Graph Systems Exploration)
Output: ../data/s1_results.json
"""

import json
import sys
import numpy as np
from collections import Counter

# ============================================================
# Smith Normal Form (pure integer implementation)
# ============================================================

def smith_normal_form(M):
    """
    Compute the Smith Normal Form of an integer matrix M.
    Returns the diagonal entries (invariant factors).
    
    Uses row and column operations over Z.
    """
    # Work with a copy
    A = [list(row) for row in M]
    m = len(A)
    n = len(A[0]) if m > 0 else 0
    
    pivot = 0
    
    for col in range(min(m, n)):
        if pivot >= m:
            break
        
        # Find nonzero entry in column col, row >= pivot
        found = False
        for row in range(pivot, m):
            if A[row][col] != 0:
                # Swap rows
                A[pivot], A[row] = A[row], A[pivot]
                found = True
                break
        
        if not found:
            continue
        
        # Eliminate in column and row using the pivot
        changed = True
        while changed:
            changed = False
            
            # Make pivot positive
            if A[pivot][col] < 0:
                A[pivot] = [-x for x in A[pivot]]
            
            # Row elimination
            for row in range(m):
                if row == pivot:
                    continue
                if A[row][col] != 0:
                    if A[row][col] % A[pivot][col] == 0:
                        factor = A[row][col] // A[pivot][col]
                        for j in range(n):
                            A[row][j] -= factor * A[pivot][j]
                    else:
                        # Use extended GCD
                        g, s, t = extended_gcd(A[pivot][col], A[row][col])
                        # New pivot row = s * pivot_row + t * row
                        # New other row = -(A[row][col]//g) * pivot_row + (A[pivot][col]//g) * row
                        a_pc = A[pivot][col]
                        a_rc = A[row][col]
                        new_pivot = [s * A[pivot][j] + t * A[row][j] for j in range(n)]
                        new_row = [-(a_rc // g) * A[pivot][j] + (a_pc // g) * A[row][j] for j in range(n)]
                        A[pivot] = new_pivot
                        A[row] = new_row
                        changed = True
            
            # Column elimination
            for c in range(n):
                if c == col:
                    continue
                if A[pivot][c] != 0:
                    if A[pivot][c] % A[pivot][col] == 0:
                        factor = A[pivot][c] // A[pivot][col]
                        for row in range(m):
                            A[row][c] -= factor * A[row][col]
                    else:
                        g, s, t = extended_gcd(A[pivot][col], A[pivot][c])
                        a_pc = A[pivot][col]
                        a_cc = A[pivot][c]
                        for row in range(m):
                            new_col_val = s * A[row][col] + t * A[row][c]
                            new_c_val = -(a_cc // g) * A[row][col] + (a_pc // g) * A[row][c]
                            A[row][col] = new_col_val
                            A[row][c] = new_c_val
                        changed = True
        
        pivot += 1
    
    # Extract diagonal
    diag = []
    for i in range(min(m, n)):
        diag.append(abs(A[i][i]))
    
    # Ensure divisibility chain: d_i | d_{i+1}
    # (The algorithm above should produce this, but let's enforce it)
    for i in range(len(diag) - 1):
        if diag[i] != 0 and diag[i+1] != 0:
            if diag[i+1] % diag[i] != 0:
                g = gcd_int(diag[i], diag[i+1])
                diag[i+1] = (diag[i] * diag[i+1]) // g
                diag[i] = g
    
    return diag


def extended_gcd(a, b):
    """Extended Euclidean algorithm. Returns (g, s, t) with g = s*a + t*b."""
    if a == 0:
        return b, 0, 1
    g, s, t = extended_gcd(b % a, a)
    return g, t - (b // a) * s, s


def gcd_int(a, b):
    """GCD of two integers."""
    while b:
        a, b = b, a % b
    return abs(a)


# ============================================================
# Graph construction (from G1 data or from scratch)
# ============================================================

def build_laplacian(adj_matrix):
    """Build the Laplacian matrix L = D - A from an adjacency matrix."""
    n = len(adj_matrix)
    L = [[0] * n for _ in range(n)]
    for i in range(n):
        deg = sum(adj_matrix[i])
        L[i][i] = deg
        for j in range(n):
            if i != j:
                L[i][j] = -adj_matrix[i][j]
    return L


def reduced_laplacian(L):
    """Remove last row and column to get the reduced Laplacian."""
    n = len(L)
    return [[L[i][j] for j in range(n - 1)] for i in range(n - 1)]


# ============================================================
# Sandpile group invariants
# ============================================================

def compute_sandpile_invariants(invariant_factors):
    """
    Given the invariant factors of the reduced Laplacian's SNF,
    compute all sandpile group invariants.
    """
    # Filter out 0s and 1s
    nontrivial = [d for d in invariant_factors if d > 1]
    
    if not nontrivial:
        return {
            'invariant_factors': [],
            'group_order': 1,
            'rank': 0,
            'is_cyclic': True,
            'largest_factor': 1,
            'exponent': 1,
            'p_ranks': {},
            'factor_entropy': 0.0,
            'num_nontrivial_factors': 0,
        }
    
    group_order = 1
    for d in nontrivial:
        group_order *= d
    
    rank = len(nontrivial)
    is_cyclic = (rank == 1)
    largest_factor = max(nontrivial)
    
    # Exponent = LCM of all factors
    exponent = nontrivial[0]
    for d in nontrivial[1:]:
        exponent = lcm(exponent, d)
    
    # p-ranks for small primes
    primes = [2, 3, 5, 7, 11, 13]
    p_ranks = {}
    for p in primes:
        p_rank = sum(1 for d in nontrivial if d % p == 0)
        if p_rank > 0:
            p_ranks[str(p)] = p_rank
    
    # Entropy of factor distribution
    total = sum(nontrivial)
    if total > 0:
        probs = [d / total for d in nontrivial]
        import math
        factor_entropy = -sum(p * math.log2(p) for p in probs if p > 0)
    else:
        factor_entropy = 0.0
    
    return {
        'invariant_factors': nontrivial,
        'group_order': group_order,
        'rank': rank,
        'is_cyclic': is_cyclic,
        'largest_factor': largest_factor,
        'exponent': exponent,
        'p_ranks': p_ranks,
        'factor_entropy': factor_entropy,
        'num_nontrivial_factors': rank,
        'order_over_exponent': group_order / exponent if exponent > 0 else 0,
    }


def lcm(a, b):
    return abs(a * b) // gcd_int(a, b)


# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    print("Phase S1: Computing sandpile groups (critical groups) for graphs")
    print("=" * 60)
    
    # Try to load G1 data
    try:
        with open('../../data/g1_results.json', 'r') as f:
            g1_data = json.load(f)
        print(f"Loaded {len(g1_data)} graphs from G1 data")
    except FileNotFoundError:
        print("G1 data not found. Generating standard graph families...")
        g1_data = None
    
    # If no G1 data, generate standard families
    # For now, demonstrate with small examples
    if g1_data is None:
        print("\nGenerating example graphs...")
        # This would be replaced by proper graph generation
        # using NetworkX or custom code
        print("TODO: Generate graphs from families")
        sys.exit(1)
    
    # For each graph in G1, we need the adjacency matrix
    # G1 stores metrics but not matrices — we need to regenerate
    print("\nNOTE: G1 data contains metrics, not adjacency matrices.")
    print("Need to regenerate graphs from family + params to compute SNF.")
    print("This script provides the SNF + invariant computation framework.")
    print("The next step is to regenerate the 356 graphs and feed them here.")
    
    # Demo with small known graphs
    print("\n--- Demo: Known small graphs ---\n")
    
    demos = [
        ("K4 (complete 4)", [
            [0,1,1,1],
            [1,0,1,1],
            [1,1,0,1],
            [1,1,1,0]
        ]),
        ("C5 (cycle 5)", [
            [0,1,0,0,1],
            [1,0,1,0,0],
            [0,1,0,1,0],
            [0,0,1,0,1],
            [1,0,0,1,0]
        ]),
        ("K3,3 (complete bipartite)", [
            [0,0,0,1,1,1],
            [0,0,0,1,1,1],
            [0,0,0,1,1,1],
            [1,1,1,0,0,0],
            [1,1,1,0,0,0],
            [1,1,1,0,0,0]
        ]),
    ]
    
    for name, adj in demos:
        L = build_laplacian(adj)
        Lr = reduced_laplacian(L)
        diag = smith_normal_form(Lr)
        inv = compute_sandpile_invariants(diag)
        
        print(f"{name}:")
        print(f"  SNF diagonal: {diag}")
        print(f"  K(G) = {'×'.join(f'Z_{d}' for d in inv['invariant_factors']) or 'trivial'}")
        print(f"  |K(G)| = {inv['group_order']} (= spanning trees)")
        print(f"  Cyclic: {inv['is_cyclic']}")
        print(f"  Exponent: {inv['exponent']}")
        print(f"  p-ranks: {inv['p_ranks']}")
        print()

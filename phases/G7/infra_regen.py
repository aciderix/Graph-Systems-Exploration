"""
INFRASTRUCTURE — Régénération des 356 graphes + sauvegarde pickle
================================================================
Reproduit exactement le generate_all_graphs() de G1 avec seed=42.
Sauvegarde les objets graphes pour réutilisation par les pistes.
"""
import networkx as nx
import numpy as np
import pickle
import json
import time
import warnings
warnings.filterwarnings('ignore')

def generate_all_graphs():
    graphs = []
    
    # 1. ERDŐS-RÉNYI
    for n in [50, 100, 200, 500]:
        for p in [0.01, 0.02, 0.05, 0.1, 0.2, 0.5]:
            G = nx.erdos_renyi_graph(n, p, seed=42)
            graphs.append((G, 'erdos_renyi', {'n': n, 'p': p}))
    
    # 2. BARABÁSI-ALBERT
    for n in [50, 100, 200, 500]:
        for m_ba in [1, 2, 3, 5, 10]:
            G = nx.barabasi_albert_graph(n, m_ba, seed=42)
            graphs.append((G, 'barabasi_albert', {'n': n, 'm': m_ba}))
    
    # 3. WATTS-STROGATZ
    for n in [50, 100, 200, 500]:
        for k in [4, 6, 10]:
            for p in [0.0, 0.01, 0.05, 0.1, 0.3, 1.0]:
                G = nx.watts_strogatz_graph(n, k, p, seed=42)
                graphs.append((G, 'watts_strogatz', {'n': n, 'k': k, 'p': p}))
    
    # 4. LATTICES
    for n in [50, 100, 200]:
        graphs.append((nx.cycle_graph(n), 'cycle', {'n': n}))
    
    for side in [7, 10, 15, 20]:
        G = nx.convert_node_labels_to_integers(nx.grid_2d_graph(side, side))
        graphs.append((G, 'grid_2d', {'side': side, 'n': side*side}))
    
    for side in [5, 8, 12]:
        G = nx.convert_node_labels_to_integers(nx.triangular_lattice_graph(side, side))
        graphs.append((G, 'triangular_lattice', {'side': side}))
    
    # 5. TREES
    for n in [50, 100, 200, 500]:
        G = nx.random_labeled_tree(n, seed=42)
        graphs.append((G, 'random_tree', {'n': n}))
    
    for r in [2, 3, 4]:
        for h in [3, 4, 5]:
            n_tree = sum(r**i for i in range(h+1))
            if n_tree <= 1500:
                G = nx.balanced_tree(r, h)
                graphs.append((G, 'balanced_tree', {'r': r, 'h': h, 'n': n_tree}))
    
    for n in [20, 50, 100, 200]:
        graphs.append((nx.star_graph(n-1), 'star', {'n': n}))
    
    for n in [20, 50, 100, 200]:
        graphs.append((nx.path_graph(n), 'path', {'n': n}))
    
    # 6. COMPLETE
    for n in [10, 20, 50, 100]:
        graphs.append((nx.complete_graph(n), 'complete', {'n': n}))
    
    # 7. COMPLETE BIPARTITE
    for n1 in [10, 25, 50]:
        for n2 in [10, 25, 50]:
            graphs.append((nx.complete_bipartite_graph(n1, n2), 'complete_bipartite', {'n1': n1, 'n2': n2}))
    
    # 8. RANDOM REGULAR
    for n in [50, 100, 200]:
        for d in [3, 4, 6, 10]:
            if d < n:
                try:
                    G = nx.random_regular_graph(d, n, seed=42)
                    graphs.append((G, 'random_regular', {'n': n, 'd': d}))
                except:
                    pass
    
    # 9. RANDOM GEOMETRIC
    for n in [50, 100, 200, 500]:
        for radius in [0.1, 0.15, 0.2, 0.3]:
            G = nx.random_geometric_graph(n, radius, seed=42)
            graphs.append((G, 'random_geometric', {'n': n, 'radius': radius}))
    
    # 10. SBM
    for n_per_block in [25, 50]:
        for k_blocks in [2, 4]:
            for p_in in [0.3, 0.5]:
                for p_out in [0.01, 0.05, 0.1]:
                    sizes = [n_per_block] * k_blocks
                    probs = [[p_in if i==j else p_out for j in range(k_blocks)] for i in range(k_blocks)]
                    G = nx.stochastic_block_model(sizes, probs, seed=42)
                    graphs.append((G, 'stochastic_block', {'n_per_block': n_per_block, 'k': k_blocks, 'p_in': p_in, 'p_out': p_out}))
    
    # 11. POWERLAW CLUSTER
    for n in [50, 100, 200, 500]:
        for m_plc in [2, 3, 5]:
            for p in [0.1, 0.5, 0.9]:
                try:
                    G = nx.powerlaw_cluster_graph(n, m_plc, p, seed=42)
                    graphs.append((G, 'powerlaw_cluster', {'n': n, 'm': m_plc, 'p': p}))
                except:
                    pass
    
    # 12. CIRCULANT
    for n in [50, 100, 200]:
        for offsets in [[1,2], [1,3], [1,5], [1,2,5], [1,n//4]]:
            G = nx.circulant_graph(n, offsets)
            graphs.append((G, 'circulant', {'n': n, 'offsets': offsets}))
    
    # 13. NEWMAN-WATTS-STROGATZ
    for n in [50, 100, 200]:
        for k in [4, 6]:
            for p in [0.01, 0.05, 0.1, 0.3]:
                G = nx.newman_watts_strogatz_graph(n, k, p, seed=42)
                graphs.append((G, 'newman_watts_strogatz', {'n': n, 'k': k, 'p': p}))
    
    # 14. CAVEMAN
    for l in [5, 10, 20]:
        for k in [5, 10]:
            if l * k <= 500:
                G = nx.connected_caveman_graph(l, k)
                graphs.append((G, 'connected_caveman', {'l': l, 'k': k, 'n': l*k}))
    
    # 15. DUAL BARABÁSI-ALBERT
    for n in [100, 200, 500]:
        for m1 in [1, 2]:
            for m2 in [1, 2]:
                for p_dba in [0.3, 0.5, 0.7]:
                    try:
                        G = nx.dual_barabasi_albert_graph(n, m1, m2, p_dba, seed=42)
                        graphs.append((G, 'dual_barabasi_albert', {'n': n, 'm1': m1, 'm2': m2, 'p': p_dba}))
                    except:
                        pass
    
    # 16. RANDOM LOBSTER
    for n in [50, 100, 200]:
        for p1 in [0.3, 0.5, 0.8]:
            for p2 in [0.1, 0.3, 0.5]:
                G = nx.random_lobster(n, p1, p2, seed=42)
                graphs.append((G, 'random_lobster', {'n_backbone': n, 'p1': p1, 'p2': p2}))
    
    return graphs

# === EXTREME GRAPHS (from G6) ===
def generate_extreme_graphs():
    graphs = {}
    for n in [5,10,20,50,100,200]:
        graphs[f"star_{n}"] = nx.star_graph(n-1)
        graphs[f"clique_{n}"] = nx.complete_graph(n)
        graphs[f"path_{n}"] = nx.path_graph(n)
        graphs[f"cycle_{n}"] = nx.cycle_graph(n)
    for d in [3,4,5,6,7]:
        graphs[f"bintree_d{d}"] = nx.balanced_tree(2, d)
    for n in [10,25,50]:
        graphs[f"barbell_{n}"] = nx.barbell_graph(n, 1)
        graphs[f"lollipop_{n}"] = nx.lollipop_graph(n, n)
        graphs[f"wheel_{n}"] = nx.wheel_graph(n)
        graphs[f"ladder_{n}"] = nx.ladder_graph(n)
    for n1,n2 in [(2,50),(5,100),(1,200)]:
        graphs[f"Kbip_{n1}_{n2}"] = nx.complete_bipartite_graph(n1, n2)
    for n in range(4, 31, 2):
        graphs[f"ER_tiny_N{n}"] = nx.erdos_renyi_graph(n, 0.3, seed=42)
    graphs["petersen"] = nx.petersen_graph()
    graphs["dodecahedron"] = nx.dodecahedral_graph()
    graphs["icosahedron"] = nx.icosahedral_graph()
    try: graphs["tutte"] = nx.tutte_graph()
    except: pass
    for n in [20,50]:
        G = nx.path_graph(n)
        for i in range(n):
            G.add_edge(i, n + i)
        graphs[f"caterpillar_{n}"] = G
    # Unequal cliques
    for n1,n2 in [(5,95),(3,197)]:
        G = nx.Graph()
        G.add_edges_from([(i,j) for i in range(n1) for j in range(i+1,n1)])
        G.add_edges_from([(n1+i,n1+j) for i in range(n2) for j in range(i+1,n2)])
        G.add_edge(0, n1)
        graphs[f"unequal_{n1}_{n2}"] = G
    # Almost disconnected
    for n in [50,100]:
        G1 = nx.erdos_renyi_graph(n, 0.15, seed=42)
        G2 = nx.erdos_renyi_graph(n, 0.15, seed=43)
        G = nx.disjoint_union(G1, G2)
        G.add_edge(0, n)
        graphs[f"almost_discon_{n}"] = G
    return graphs

# === NULL RANDOM GRAPHS (for trivality test) ===
def generate_null_random(n_samples=50):
    """Generate random graphs with same N,M as typical graphs for null comparison."""
    np.random.seed(42)
    nulls = {}
    for n in [50, 100, 200]:
        for density in [0.05, 0.1, 0.2]:
            for i in range(5):
                G = nx.erdos_renyi_graph(n, density, seed=42+i*100)
                nulls[f"null_ER_n{n}_d{density}_i{i}"] = G
    return nulls

if __name__ == "__main__":
    t0 = time.time()
    
    print("=" * 60)
    print("REGENERATING ALL GRAPHS")
    print("=" * 60)
    
    all_graphs = generate_all_graphs()
    print(f"Main dataset: {len(all_graphs)} graphs generated")
    
    extreme = generate_extreme_graphs()
    print(f"Extreme graphs: {len(extreme)} generated")
    
    nulls = generate_null_random()
    print(f"Null random: {len(nulls)} generated")
    
    # Save as pickle
    data = {
        'main': all_graphs,  # list of (G, name, params)
        'extreme': extreme,   # dict name -> G
        'null': nulls,        # dict name -> G
    }
    
    with open('/tmp/all_graphs.pkl', 'wb') as f:
        pickle.dump(data, f)
    
    print(f"\nTotal time: {time.time()-t0:.1f}s")
    print(f"Saved to /tmp/all_graphs.pkl")
    
    # Quick stats
    from collections import Counter
    families = Counter(g[1] for g in all_graphs)
    print(f"\n{len(families)} families:")
    for fam, cnt in sorted(families.items(), key=lambda x: -x[1]):
        print(f"  {fam:30s} {cnt:>4d}")

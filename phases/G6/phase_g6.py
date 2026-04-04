import numpy as np
import json
np.random.seed(42)

try:
    import networkx as nx
except ImportError:
    import subprocess; subprocess.check_call(["pip","install","networkx","-q"])
    import networkx as nx

def S_norm(G):
    N = len(G)
    if N < 3: return None
    L = nx.normalized_laplacian_matrix(G).toarray()
    eigs = np.linalg.eigvalsh(L)
    eigs_pos = eigs[eigs > 1e-10]
    if len(eigs_pos) == 0: return 0.0
    p = eigs_pos / eigs_pos.sum()
    S = -np.sum(p * np.log2(p + 1e-30))
    return S / np.log2(N)

def rho_k(G):
    N = len(G)
    if N < 3 or G.number_of_edges() == 0: return None
    A = nx.adjacency_matrix(G).toarray().astype(float)
    rho = max(abs(np.linalg.eigvalsh(A)))
    km = 2*G.number_of_edges()/N
    return rho/km if km > 0 else None

def test(name, G):
    if not nx.is_connected(G):
        G = G.subgraph(max(nx.connected_components(G), key=len)).copy()
    N = len(G)
    s = S_norm(G)
    r = rho_k(G)
    return {"name": name, "N": N, "S_norm": round(s,4) if s else None, "rho_k": round(r,4) if r else None}

all_results = []

# ===== SECTION 1: EXTREME STRUCTURES =====
print("=" * 60)
print("SECTION 1: STRUCTURES EXTRÊMES")
print("=" * 60)

graphs = {}
for n in [5,10,20,50,100,200]:
    graphs[f"star_{n}"] = nx.star_graph(n-1)
    graphs[f"clique_{n}"] = nx.complete_graph(n)
    graphs[f"path_{n}"] = nx.path_graph(n)
    graphs[f"cycle_{n}"] = nx.cycle_graph(n)

for d in [3,4,5,6,7]:
    T = nx.balanced_tree(2, d)
    graphs[f"bintree_d{d}"] = T

for n in [10,25,50]:
    graphs[f"barbell_{n}"] = nx.barbell_graph(n, 1)
    graphs[f"lollipop_{n}"] = nx.lollipop_graph(n, n)
    graphs[f"wheel_{n}"] = nx.wheel_graph(n)
    graphs[f"ladder_{n}"] = nx.ladder_graph(n)

for n1,n2 in [(2,50),(5,100),(1,200)]:
    graphs[f"Kbip_{n1}_{n2}"] = nx.complete_bipartite_graph(n1, n2)

# Small N < 30
for n in range(4, 31, 2):
    graphs[f"ER_tiny_N{n}"] = nx.erdos_renyi_graph(n, 0.3, seed=42)

# Named graphs
graphs["petersen"] = nx.petersen_graph()
graphs["dodecahedron"] = nx.dodecahedral_graph()
graphs["icosahedron"] = nx.icosahedral_graph()
try: graphs["tutte"] = nx.tutte_graph()
except: pass

# Caterpillar
for n in [20,50]:
    G = nx.path_graph(n)
    for i in range(n):
        G.add_edge(i, n + i)
    graphs[f"caterpillar_{n}"] = G

print(f"Testing {len(graphs)} extreme graphs...")
for name, G in graphs.items():
    all_results.append(test(name, G))

# ===== SECTION 2: PATHOLOGICAL =====
print("\n" + "=" * 60)
print("SECTION 2: PATHOLOGIQUES")
print("=" * 60)

# Unequal cliques connected by bridge
for n1,n2 in [(5,95),(3,197)]:
    G = nx.Graph()
    G.add_edges_from([(i,j) for i in range(n1) for j in range(i+1,n1)])
    G.add_edges_from([(n1+i,n1+j) for i in range(n2) for j in range(i+1,n2)])
    G.add_edge(0, n1)
    graphs[f"unequal_{n1}_{n2}"] = G
    all_results.append(test(f"unequal_{n1}_{n2}", G))

# Almost-disconnected ER
for n in [50,100]:
    G1 = nx.erdos_renyi_graph(n, 0.15, seed=42)
    G2 = nx.erdos_renyi_graph(n, 0.15, seed=43)
    G = nx.disjoint_union(G1, G2)
    G.add_edge(0, n)
    all_results.append(test(f"almost_discon_{n}", G))

# Sierpinski
for k in [3,4,5]:
    try:
        G = nx.sierpinski_graph(k, 3)
        all_results.append(test(f"sierpinski_k{k}", G))
    except: pass

print(f"Added pathological graphs")

# ===== SECTION 3: DESTRUCTION =====
print("\n" + "=" * 60)
print("SECTION 3: DESTRUCTION (suppression massive d'arêtes)")
print("=" * 60)

destruction = []
bases = {
    "ER_100": nx.erdos_renyi_graph(100, 0.1, seed=42),
    "BA_100": nx.barabasi_albert_graph(100, 3, seed=42),
    "WS_100": nx.watts_strogatz_graph(100, 10, 0.3, seed=42),
    "grid_10": nx.grid_2d_graph(10, 10),
}

for bname, Gb in bases.items():
    Gb = nx.convert_node_labels_to_integers(Gb)
    se0 = S_norm(Gb) if nx.is_connected(Gb) else None
    for frac in [0.3, 0.5, 0.7, 0.8, 0.9, 0.95]:
        G = Gb.copy()
        edges = list(G.edges())
        nr = int(len(edges)*frac)
        if nr >= len(edges)-1: continue
        rm = [edges[i] for i in np.random.choice(len(edges), nr, replace=False)]
        G.remove_edges_from(rm)
        if not nx.is_connected(G):
            G = G.subgraph(max(nx.connected_components(G), key=len)).copy()
        if len(G) < 3: continue
        se = S_norm(G)
        destruction.append({
            "base": bname, "frac": frac, "N": len(G),
            "S_norm": round(se,4) if se else None,
            "S_base": round(se0,4) if se0 else None
        })

print(f"Tested {len(destruction)} destruction scenarios")

# ===== SECTION 4: TRIVIALITÉ TEST =====
print("\n" + "=" * 60)
print("SECTION 4: TEST DE TRIVIALITÉ — S/log2(N) pour matrices ALÉATOIRES")
print("=" * 60)

print("\nQ: Est-ce que S/log2(N) ≈ 0.97 pour N'IMPORTE QUELLE matrice?")
print("   Si oui → LOI 1 est un artefact mathématique, pas une propriété des graphes.\n")

for N in [10, 20, 50, 100, 200]:
    random_S = []
    for _ in range(20):
        M = np.random.randn(N,N)
        M = (M + M.T)/2
        eigs = np.linalg.eigvalsh(M)
        eigs_abs = np.abs(eigs)
        eigs_abs = eigs_abs[eigs_abs > 1e-10]
        p = eigs_abs / eigs_abs.sum()
        S = -np.sum(p * np.log2(p + 1e-30))
        random_S.append(S / np.log2(N))
    
    # Graph Laplacian for comparison
    G = nx.erdos_renyi_graph(N, 0.1, seed=42)
    if nx.is_connected(G):
        graph_S = S_norm(G)
    else:
        graph_S = None
    
    # Uniform on [0, 2] (Laplacian-like range)
    unif_S = []
    for _ in range(20):
        eigs_u = np.random.uniform(0.01, 2.0, N)
        p = eigs_u / eigs_u.sum()
        S = -np.sum(p * np.log2(p + 1e-30))
        unif_S.append(S / np.log2(N))
    
    print(f"N={N:>4}: Random matrix = {np.mean(random_S):.4f}±{np.std(random_S):.4f} | "
          f"Uniform[0,2] = {np.mean(unif_S):.4f}±{np.std(unif_S):.4f} | "
          f"Graph Laplacian = {graph_S:.4f}" if graph_S else f"N={N:>4}: skip")

# ===== FINAL VERDICT =====
print("\n" + "=" * 60)
print("🔬 VERDICT FINAL — FALSIFICATION")
print("=" * 60)

valid = [r for r in all_results if r["S_norm"] is not None]
broken = [r for r in valid if r["S_norm"] < 0.80]
weak = [r for r in valid if 0.80 <= r["S_norm"] < 0.90]

print(f"\n📊 LOI 1 — S/log₂(N) ≈ 0.97:")
print(f"  Total graphes testés: {len(valid)}")
print(f"  Cassés (< 0.80): {len(broken)}")
print(f"  Faibles (0.80-0.90): {len(weak)}")
smin = min(valid, key=lambda x: x["S_norm"])
smax = max(valid, key=lambda x: x["S_norm"])
print(f"  Minimum: {smin['S_norm']} → {smin['name']} (N={smin['N']})")
print(f"  Maximum: {smax['S_norm']} → {smax['name']} (N={smax['N']})")

if broken:
    print(f"\n  🔥 CONTRE-EXEMPLES (S < 0.80):")
    for r in sorted(broken, key=lambda x: x["S_norm"]):
        print(f"    {r['name']:30s} N={r['N']:>4}  S/log2(N) = {r['S_norm']}")

if weak:
    print(f"\n  ⚠️  CAS FAIBLES (0.80-0.90):")
    for r in sorted(weak, key=lambda x: x["S_norm"]):
        print(f"    {r['name']:30s} N={r['N']:>4}  S/log2(N) = {r['S_norm']}")

# Destruction verdict
dest_broken = [d for d in destruction if d["S_norm"] is not None and d["S_norm"] < 0.80]
dest_weak = [d for d in destruction if d["S_norm"] is not None and 0.80 <= d["S_norm"] < 0.90]
print(f"\n📊 LOI 1 sous destruction:")
print(f"  Scénarios: {len(destruction)}")
print(f"  Cassés: {len(dest_broken)}, Faibles: {len(dest_weak)}")
if dest_broken:
    print(f"  🔥 Cassés:")
    for d in dest_broken:
        print(f"    {d['base']} -{d['frac']:.0%} → S={d['S_norm']} (N={d['N']})")

# LOI 4
valid4 = [r for r in all_results if r["rho_k"] is not None]
print(f"\n📊 LOI 4 — ρ(A)/⟨k⟩:")
print(f"  Total: {len(valid4)}")
print(f"  Range: [{min(r['rho_k'] for r in valid4):.4f}, {max(r['rho_k'] for r in valid4):.4f}]")
regulars = [r for r in valid4 if any(k in r["name"] for k in ["clique","cycle","petersen","dodecahedron","icosahedron"])]
print(f"  Graphes réguliers testés: {len(regulars)}")
reg_exact = [r for r in regulars if abs(r["rho_k"] - 1.0) < 0.001]
print(f"  ρ/⟨k⟩ = 1.000 ± 0.001: {len(reg_exact)}/{len(regulars)}")
if len(reg_exact) < len(regulars):
    print(f"  ⚠️ Exceptions:")
    for r in regulars:
        if abs(r["rho_k"] - 1.0) >= 0.001:
            print(f"    {r['name']}: ρ/⟨k⟩ = {r['rho_k']}")

# Save
with open("/tmp/g6_results.json", "w") as f:
    json.dump({"graphs": all_results, "destruction": destruction}, f, indent=2)
print("\n✅ Saved to /tmp/g6_results.json")

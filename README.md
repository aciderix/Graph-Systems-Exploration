# Graph Systems Exploration

**Exploration computationnelle systématique des graphes finis — 16 phases, ~250 000 calculs, 0 loi fondamentalement nouvelle.**

Ce projet est un résultat négatif de haute qualité. Son apport principal est **méthodologique** : un pipeline de découverte-falsification automatisé qui a démontré empiriquement que l'espace des lois algébriques simples sur les graphes finis est saturé — y compris dans les directions post-spectrales (compression, complexité algorithmique, exposants de convergence, morphismes).

---

## Table des matières

1. [Philosophie et objectif](#philosophie-et-objectif)
2. [Résumé exécutif](#résumé-exécutif)
3. [Phases G1→G11 : exploration initiale](#phases-g1g11--exploration-initiale)
4. [Phases G12→G16 : exploration post-spectrale](#phases-g12g16--exploration-post-spectrale)
5. [Les 5 grandes découvertes (toutes négatives)](#les-5-grandes-découvertes-toutes-négatives)
6. [Leçons apprises — règles de travail](#leçons-apprises--règles-de-travail)
7. [Pistes futures réalistes](#pistes-futures-réalistes)
8. [Structure des données](#structure-des-données)
9. [Stack technique](#stack-technique)

---

## Philosophie et objectif

### Origine

Ce projet est né d'un pivot. Le travail précédent (18 phases) explorait la **fonction zêta de Riemann** et les produits d'Euler tronqués. Conclusion : toutes les routes par troncature sont fermées, α = 3/4 est un artefact de la convergence de Dickman. Archives : [`Maths-Riemann-Research`](https://github.com/aciderix/Maths-Riemann-Research).

### Philosophie fondamentale

> **Se comporter comme un système exploratoire cherchant à cartographier un espace inconnu et en extraire des lois fondamentales — PAS comme un mathématicien cherchant une preuve.**

Concrètement :
- **Penser comme une machine, pas comme un humain** — pas d'intuition non testée
- **Couverture maximale** — tester même les pistes improbables
- **Refuser les explications faciles** — remettre en question chaque résultat
- **Falsifier systématiquement** — une loi n'est intéressante que si elle survit à la tentative de destruction
- **Documenter les échecs aussi clairement que les succès**

### Objectif

Trouver un **invariant ou une loi fondamentale sur les graphes** qui soit :
1. **Non trivial** (pas un artefact, pas dérivable en 3 lignes)
2. **Survivant à la falsification** (tient sur graphes extrêmes, frais, pathologiques)
3. **Absent de la littérature** (pas une redécouverte)
4. **Théoriquement explicable** (pas du surapprentissage)

**Résultat après 16 phases : 0/4 satisfait. Le résultat négatif lui-même est informatif — et renforcé par 5 phases post-spectrales qui convergent vers la même conclusion.**

---

## Résumé exécutif

```
356 graphes × 21 familles × 114 métriques (31 standard + 83 non-standard)
+ 4 processus dynamiques (Kuramoto, SIR, chaleur, coopération)
+ 8 opérations classiques × 6 opérations exotiques
+ 7 paires de graphes cospectraux
+ Lois de conservation (SVD null-space)
+ Lois de transformation (régression symbolique)
+ Compression gap (zlib/bzip2/lzma × adj/spectre/bfs)
+ Eigenvectors analysis (IPR, skew, level spacing)
+ Trajectory invariants (contraction itérative)
+ Graphes pondérés + localisation d'Anderson
+ Familles paramétriques + morphismes fonctoriels
+ Complexité computationnelle des invariants
+ Exposants de fluctuation (graphons) + scaling laws
+ Falsification systématique à chaque étape
= ~250 000 calculs individuels
= 0 loi fondamentalement nouvelle
```

### Le théorème empirique

> **Sur les graphes finis, les lois algébriques simples vivent dans l'espace spectral, et l'espace spectral est entièrement défriché. L'espace non-spectral est prédictible mais sans lois exactes simples.**

---

## Phases G1→G11 : exploration initiale

### Phase G1 — Génération massive + mesures baseline

**356 graphes** de **21 familles** :

| Famille | Nb | Tailles | Paramètres variés |
|---|---|---|---|
| erdos_renyi | 24 | 50-500 | p ∈ {0.01, 0.02, 0.05, 0.1, 0.2} |
| barabasi_albert | 20 | 50-500 | m ∈ {1, 2, 3, 5} |
| watts_strogatz | 72 | 50-500 | k ∈ {4,6,10}, p ∈ {0.01..1.0} |
| newman_watts_strogatz | 24 | 50-200 | k ∈ {4,10}, p ∈ {0.01..1.0} |
| random_geometric | 16 | 50-500 | r ∈ {0.1,0.15,0.2,0.3} |
| stochastic_block | 24 | 50-200 | 2-5 blocs, p_in/p_out variés |
| connected_caveman | 6 | 25-200 | cliques de 5-20 |
| powerlaw_cluster | 36 | 50-500 | m ∈ {2,3,5}, p ∈ {0..1} |
| dual_barabasi_albert | 36 | 100-500 | m1,m2,p variés |
| random_regular | 12 | 50-200 | d ∈ {3,5,10} |
| balanced_tree | 9 | 15-1365 | r ∈ {2,3}, h ∈ {3,4,5} |
| circulant | 15 | 50-200 | offsets variés |
| random_lobster | 27 | ~100-2237 | p1,p2 ∈ {0.3,0.5,0.8} |
| complete, complete_bipartite, grid_2d, triangular_lattice, star, path, cycle, random_tree | 31 | 10-500 | — |

**31 métriques** : structure (n, m, density), degrés (mean, std, min, max, skew, kurtosis), composantes, clustering (avg, transitivity, triangles), distances (avg_path, diameter), assortativity, spectre (A: radius, gap, min; L: algebraic_connectivity, max, ratio, norm_gap), topologie (girth), communautés, wiener_index.

**Fichier** : `data/g1_results.json` (349 KB)

### Phase G2 — Déformations contrôlées

5 types × 13 niveaux × 12 graphes de base. Tracking continu de toutes métriques.

| Déformation | Description |
|---|---|
| edge_addition | Ajout aléatoire (0% à 100% des manquantes) |
| edge_removal | Suppression aléatoire (0% à 90%) |
| rewiring | Remplacement d'arêtes (conservation du degré) |
| node_removal | Suppression aléatoire de nœuds |
| degree_attack | Suppression ciblée des plus hauts degrés |

**Résultats clés** : transition small-world (2% rewiring caveman → diamètre ÷ 1.5), BA(m=1) s'effondre à 2% de suppression ciblée.

**Fichier** : `data/g2_trajectories.json` (314 KB)

### Phase G3 — Percolation fine

14 graphes × 3 modes d'attaque (aléatoire, degré, betweenness) × 50-200 points par courbe.

**Résultat** : le seuil critique se détecte par le pic du SLC (second largest component). Standard en physique statistique.

**Fichier** : `data/g3_results.json` (263 KB)

### Phase G4 — Chasse aux invariants

~50 000 combinaisons algébriques (produits, ratios, puissances de toutes paires de métriques). PCA sur 302 graphes connectés :
- PC1 (48%) = axe densité/connectivité
- PC2 (24%) = axe clustering
- 72% de variance en 2 dimensions

### Phase G5 — Synthèse croisée

Validation des 6 lois candidates identifiées en G1-G4.

### Phase G6 — Falsification hardcore

**68 graphes extrêmes** + 24 scénarios de destruction + tests de trivialité.

| Loi | Statut post-falsification |
|---|---|
| Entropie spectrale S/log₂(N) → 0.97 | ❌ 70% triviale (concentration entropique) |
| 3 régimes de vulnérabilité | ⚠️ Descriptif, connu (Albert-Barabási 2000) |
| C × L universel | ❌ Varie de 0 à 5.6 — pas de constante |
| ρ(A)/⟨k⟩ signature d'hétérogénéité | ✅ Vraie mais connue (Perron-Frobenius) |
| Transition de percolation par pic SLC | ⚠️ Standard depuis 30 ans |
| λ₂ × D borné | ❌ Borne classique |

**Verdict : 0/6 véritablement nouvelle.**

**Fichier** : `data/g6_results.json`

### Phase G7 — 83 nouvelles métriques non-standard

Pistes explorées : Forman-Ricci, Ollivier-Ricci, compression spectrale, entropie de Von Neumann, homologie persistante (TDA), réponse dynamique (chaleur, marches aléatoires).

| Piste | Nb métriques | Résultat |
|---|---|---|
| Courbure de Ricci | ~15 | Corrélation forte avec métriques classiques |
| Entropie Von Neumann | ~5 | Redondant avec spectral entropy |
| TDA (persistance) | ~10 | 3 survivantes, toutes issues de frameworks connus |
| Compression spectrale | ~8 | spec_complexity_per_node intéressant... |
| Réponse dynamique | ~15 | Déterminée par le spectre Laplacien |

**Fichiers** : `data/g7_*.json`

### Phase G8 — Approfondissement des survivantes

| Sous-phase | Sujet | Verdict |
|---|---|---|
| G8.5 | Stabilité de spec_complexity_per_node | **CASSÉ** : stable seulement si spectre complexe, diverge sur star/complete |
| G8.6 | Transition de betti0_mean_persistence | **PAS DE TRANSITION** : amplitude 20%, seuil erratique |
| G8.7 | Processus dynamiques (Kuramoto, SIR, chaleur, coopération) | Kuramoto ↔ compression spectrale r=0.955 — **MAIS** médiatisé par le spectral gap (connu depuis Arenas 2008) |
| G8.8 | ML classifier (standard vs nouvelles métriques) | Standard (72.3%) **écrase** nouvelles (47.2%) |

**Fichiers** : `data/g8_*.json`

### Phase G9 — Lois de conservation sous transformations

**Le changement de paradigme** : au lieu de mesurer des propriétés, chercher des **quantités conservées** quand on transforme un graphe (analogue de Noether).

```
91 graphes × 8 opérations × 29 métriques
→ 221 lois brutes
→ 50 après filtrage tautologies
→ 21 lois nonlinéaires (SVD null-space)
→ 11 survivent la falsification sur 86 graphes frais
→ 8 lois DISTINCTES
```

**Opérations testées** : complement, line_graph, square, power3, corona_K1, subdivision, cart_K2, double.

**Top 3** :

| # | Opération | σ_test | Description |
|---|---|---|---|
| 1 | G□K₂ | 0.018 | Combinaison de density, ST_log, ρ(A), tri_per_m, avg_deg |
| 2 | Corona | 0.024 | Combinaison de Δmax, transitivity, λ_max/Δmax |
| 3 | G□K₂ | 0.030 | Combinaison de Δmax, λ_max/Δmax, transitivity, density |

**Verdict** : les lois sont **réelles** (tiennent sur graphes frais) mais **dérivables** algébriquement. Les spectres sous produit cartésien et corona sont connus exactement (Hammack-Imrich-Klavžar, Barik-Pati-Sarma 2007). La SVD a trouvé des conséquences, pas des découvertes.

**Fichiers** : `data/g9_conservation_laws.json`, `phases/G9/`

### Phase G10 — La faille spectrale

**Idée** : le spectre ne détermine PAS le graphe (graphes cospectraux existent). Donc il existe de l'information non-spectrale. Explorer cette faille.

**G10.1 — Paires cospectrales** : 7 paires vérifiées (Shrikhande↔L(K₄₄), brute-force, GM-switching).

| Métrique | Sépare les paires | Connu ? |
|---|---|---|
| Betweenness (max, std, entropy) | 86% | ✅ Oui |
| Closeness (mean, std) | 86% | ✅ Oui |
| Clustering (avg, std) | 71% | ✅ Oui |
| Diamètre, rayon | 57% | ✅ Oui |

**Découverte inattendue** : Le Laplacien, Laplacien normalisé, et signless Laplacien séparent aussi les paires adjacence-cospectrales (71%). Le "spectre" n'est pas un mur unique — c'est une **hiérarchie de murs** (adjacence < Laplacien < normalisé < ...).

**G10.2 — Opérations exotiques × métriques non-spectrales** :

6 opérations (kcore, clique graph, Mycielskian, betweenness contraction, local complement, neighborhood intersection) × 80 graphes × 24 métriques non-spectrales.

**Verdict** : 57 lois SVD + 20 directes → après filtrage : 0 loi non-triviale et nouvelle. Le Mycielskian a des propriétés exactes (radius=2, deg_min+1) mais connues.

**Méta-résultat** : L'information non-spectrale existe (sépare les graphes cospectraux) mais **n'obéit pas à des lois de conservation** sous les transformations.

**Fichiers** : `data/g10_spectral_gap.json`, `data/g10_exotic_ops.json`, `phases/G10/`

### Phase G11 — Lois de transformation (régression symbolique)

**Idée** (suggérée par un LLM externe) : au lieu de chercher F(T(G)) ≈ const, chercher F(T(G)) = Φ(F(G)) — des lois dynamiques, pas des invariants.

```
64 graphes × 7 opérations × 14 métriques cibles
→ Baseline linéaire (Ridge) : 24/25 paires R² > 0.9
→ Régression symbolique (brute-force depth 1-2)
→ 7 "non-triviales" (naive R² < 0.5, symbolic R² > 0.7)
→ Falsification sur 48 graphes frais
→ 6/7 survivent
```

**Loi exacte trouvée** :
```
avg_path(complement(G)) = density(G) + 1    [R² = 1.0000]
```

**Mais trivialement dérivable** : le complément d'un graphe sparse a diamètre ≤ 2, donc avg_path = 1×(1−d) + 2×d = 1+d. ∎

**Les 5 autres survivantes** : R² de 0.86 à 0.99 sur graphes frais, mais soit dérivables (complement), soit approximatives et cassant sur les graphes extrêmes (Mycielskian).

**Verdict** : ChatGPT avait raison que le non-spectral n'est pas "sans loi" — mais les lois de transformation trouvées sont soit **triviales** (dérivables) soit **approximatives** (R² < 1, cassent sur extrêmes). Pas de zone intermédiaire contenant des lois exactes + non-triviales + inconnues.

**Fichier** : `data/g11_transformation_laws.json`, `phases/G11/`

---

## Phases G12→G16 : exploration post-spectrale

Après G11, la conclusion était claire : l'espace spectral est saturé. Les phases G12-G16 explorent systématiquement les directions **post-spectrales** : compression, eigenvectors, trajectoires, graphes pondérés, familles paramétriques, morphismes, complexité computationnelle et convergence vers les graphons.

### Phase G12 — Trois propositions alternatives

Trois axes explorés en parallèle pour attaquer l'espace non-spectral.

| Proposition | Approche | Verdict |
|---|---|---|
| **Eigenvectors** | IPR (Inverse Participation Ratio), entropie, level spacing, skew divergence | 🔴 7/7 cospectraux séparés mais **trivial par construction**. IPR localisation BA = Pastor-Satorras 2016, level spacing GOE = Evangelou 1992, correspondance degré-eigenvector = Hata & Nakao 2017 |
| **Compression** | Compressibilité zlib de différents encodages (adj rows, spectre, BFS order) | 🟢 7/7 cospectraux séparés, R² < 0.43 vs (n, m, densité) → **info structurelle au-delà de la taille** |
| **Trajectoires** | Contraction itérative : retirer le nœud de plus haut degré, mesurer les invariants à chaque pas | 🟠 `avg_deg_half_life_frac` : intra-CV=0.02, discrimination=55. Stable pour BA/WS, mais original = pas de littérature directe |

### Phase G13 — Approfondissement 4 fronts

Tests de robustesse et falsification sur les 3 propositions + graphes pondérés.

**13a — IPR Skew Scaling :** R² = 0.62 avec stats de degrés → non-trivial. Mais CV = 0.56–1.46 sur 10 instances → **trop instable pour un invariant**. Des exposants β par famille existent (BA: +0.52, grid: +0.68) avec R² > 0.9, mais les valeurs ponctuelles fluctuent trop.

**13b — Compression Gap :** Découverte du `compression_gap = ratio_adj_rows − ratio_adj_spectrum`. Mesure littéralement **combien d'information structurelle n'est PAS dans le spectre**.

| Famille | Gap | Interprétation |
|---|---|---|
| Complete / Star | ≈ −0.02 | Quasi-entièrement spectral |
| Grid / Cycle | −0.19 à −0.21 | Info spatiale non-spectrale |
| BA / ER | −0.32 à −0.33 | Hétérogénéité locale |
| WS / Random Regular | **−0.37 à −0.38** | Le spectre capture le MOINS |

**13c — Half_life_frac :** CV = 0.00–0.06 (excellent) mais R² = **0.87 avec avg_degree** → **largement trivial**. Les 13% résiduels viennent de la topologie fine (ponts, clustering) — insuffisant pour un invariant indépendant.

**13d — Graphes pondérés :** Profil de sensibilité aux poids = **localisation d'Anderson** (1958). Path/Cycle : IPR ×15–21 (explosion). Mais c'est le phénomène le plus étudié en physique de la matière condensée. Les poids **réduisent** la discrimination inter-familles. Von Neumann entropy baisse de 3–7% uniformément — pas discriminant.

### Phase G14 — Compression Gap : approfondissement

4 axes sur le candidat le plus prometteur.

**14a — Scaling law :** `gap ≈ a − b·ln(n)` avec b ≈ −0.026 ± 0.003 pour BA, WS et Random Regular (R² > 0.88). Apparente universalité du taux logarithmique.

| Famille | b (taux) | R² | Comportement |
|---|---|---|---|
| BA(3) / WS(6,0.3) / RR(4) | −0.026 ± 0.003 | >0.88 | Diverge ↓ |
| ER(0.15) / Path | ≈ −0.004 | <0.45 | Converge |
| Star / Complete / Barbell | ≈ +0.02 | >0.71 | → 0 (spectre capture tout) |

**14b — Relation fonctionnelle :** R²=0.95 avec 18 métriques, mais pas de formule fermée simple. Les métriques de distance (diamètre, avg_path, betweenness) ont r ≈ 0 → le gap est **totalement indépendant de la structure de distances**. Ironiquement, les meilleurs prédicteurs sont spectraux.

**14c — Falsification extrêmes :** Le gap résiste (R²=0.11 vs densité → pas un proxy). `Config model ≈ BA` → **la distribution de degrés détermine le gap**, pas le câblage détaillé. **Anomalie unique** : Hypercube(6) a un gap **positif** (+0.03) — le spectre est PLUS compressible que la structure complète.

**14d — Cross-connexions :** gap ↔ IPR_skew : r = −0.22 (**indépendants**). gap ↔ hlf : r = +0.44. Le fingerprint 3D (gap, skew, hlf) sépare les 9 familles avec distance min = 0.20.

### Phase G15 — Test critique : universalité du taux b

**Résultat : le taux universel est MORT. Trois coups fatals simultanés.**

**15a — b dépend de ⟨k⟩ :**

| Famille | corr(b, ⟨k⟩) | R² |
|---|---|---|
| BA | +0.09 | 0.01 |
| **WS** | **−0.96** | **0.92** |
| **RR** | **−0.92** | **0.84** |
| **ER** | **−0.98** | **0.96** |

L'apparente universalité venait du fait qu'on testait toujours à ⟨k⟩ similaire (~4-6).

**15b — b dépend de l'algorithme de compression :** Spread cross-algorithme = **66%** (zlib vs bzip2 vs lzma). Le taux n'est PAS une propriété intrinsèque du graphe — c'est un **artefact de la méthode de mesure**.

**15c — ln(n) vient de la convergence spectrale :** Le ratio spectral chute 3× plus vite que le ratio adj avec ln(n). Le gap croît uniquement parce que le spectre devient plus compressible à grand n — artefact de la convergence spectrale (Wigner, résultats analogues BA/WS).

### Phase G16 — Quatre pivots radicaux

Changement d'objet et de type de question.

**16a — Familles paramétriques G(p)→métrique :**
- 0/13 métriques avec forme universelle ER↔WS
- Transitions de phase détectées = seuils connus (connectivité ER, rewiring WS)
- Dérivées couplées density↔avg_deg↔spectral_radius = trivial (quasi le même nombre pour ER)
- **Verdict : les courbes metric(param) ne révèlent rien au-delà de la théorie existante**

**16b — Morphismes fonctoriels :**
- Subdivision : max_deg préservé exactement → trivial (ne change pas les degrés existants)
- Line graph : energy(L(G)) ~ m(G) R²=0.96 → trivial (L(G) a m(G) nœuds)
- Complement : max_deg(Ḡ) ~ n → trivial (= n-1-min_deg(G))
- **Verdict : 0 invariant fonctoriel non-trivial**

**16c — Complexité computationnelle :**
- PR_iters, BFS_90, mix_time, power_iters : R² < 0.13 avec (n, avg_deg) → **pas prédit par les métriques simples**
- F-ratio > 100 pour la séparation inter-familles → info topologique dans la complexité
- Mais CV = 0.2–0.4 pour stochastiques → trop bruitée
- mix_time ≠ 1/λ₂ (R²=0.33) → la borne théorique est lâche, mais connu (Levin, Peres & Wilmer 2009)
- **Verdict : la complexité encode de l'info au-delà du spectre, mais c'est du Markov chain theory — connu**

**16d — Graphons / Exposants de fluctuation α :**
- std(metric) ~ n^{−α} est bien défini (R² > 0.9) pour la plupart des métriques
- α **N'EST PAS universel** : IPR va de −0.31 (BA, diverge) à +2.58 (ER, converge vite)
- **Ratios α(m₁)/α(m₂) quasi-constants** : α(clustering)/α(transitivity) = 0.972 ± 0.062 (CV=6%)
- Mais **trivial** : clustering et transitivity mesurent la densité de triangles → mêmes fluctuations sous CLT
- L'espace des α est quasi-1D : chaque famille a une "vitesse de convergence" qui détermine tous les α
- Conséquence du CLT pour fonctionnelles de graphes (Janson 2004, Penrose 2003)
- **Verdict : exposants bien définis mais théoriquement expliqués**

---

## Les 5 grandes découvertes (toutes négatives)

### 1. Les lois exactes sur graphes finis = spectrales = connues

114 métriques testées, 83 non-standard (Ricci, TDA, compression, Von Neumann, dynamique). Toutes celles qui forment des lois exactes sont **spectralement déterminées** et déjà dans la littérature.

### 2. L'espace non-spectral est "sans loi exacte simple"

Les métriques non-spectrales (betweenness, clustering, diamètre...) séparent les graphes cospectraux — donc elles portent de l'information — mais cette information ne forme **pas de lois de conservation** sous les transformations de graphes. Elle est prédictible (R² > 0.9 en régression linéaire) mais pas compressible en formules fermées.

### 3. La hiérarchie spectrale

Le "spectre" n'est pas un objet unique. Il y a une hiérarchie :
```
Spectre d'adjacence < Spectre Laplacien < Spectre Laplacien normalisé < Spectre signless Laplacien
```
Chaque niveau sépare des graphes que le précédent ne distingue pas. Cette hiérarchie est connue en théorie spectrale mais notre contribution est de l'avoir **mesurée quantitativement** sur des paires cospectrales.

### 4. La compression ne produit pas de loi de scaling intrinsèque (G12-G15)

Le compression gap (ratio_adj − ratio_spectre) est un **outil descriptif valide** : non réductible à la densité, sépare les familles et les cospectraux, indépendant des métriques de distance. Mais toute tentative de loi de scaling échoue :
- Le taux logarithmique dépend de ⟨k⟩ (R² = 0.84–0.96)
- Le taux dépend de l'algorithme de compression (spread 66%)
- Le ln(n) vient de la convergence spectrale (Wigner), pas d'une propriété structurelle intrinsèque

**Leçon** : les métriques basées sur la compression algorithmique mesurent un mélange structure + algorithme. Elles ne sont pas intrinsèques au graphe.

### 5. L'exploration post-spectrale converge aussi vers le connu (G16)

Les 4 pivots radicaux (familles paramétriques, morphismes, complexité, graphons) convergent tous :
- **Familles paramétriques** : transitions de phase = seuils de connectivité connus
- **Morphismes** : seuls les invariants triviaux sont préservés
- **Complexité computationnelle** : encode de l'info non-spectrale mais = Markov chain theory
- **Graphons/α** : exposants bien définis mais expliqués par le CLT pour fonctionnelles de graphes (Janson 2004)

**Méta-leçon** : même en changeant l'objet (familles, morphismes) et le type de question (complexité, convergence), on retombe sur de la théorie existante. L'espace des graphes finis est profondément défriché.

---

## Leçons apprises — règles de travail

### Principes de falsification (OBLIGATOIRES pour tout futur travail)

1. **Falsifier au fur et à mesure, pas à la fin** — G1-G5 ont produit 6 "lois" ; G6 les a toutes tuées. Coût évitable.
2. **Toujours tester contre le null le plus stupide** — l'entropie spectrale (LOI 1) était 70% artefact. Un test contre matrices aléatoires l'aurait montré immédiatement.
3. **Baseline linéaire obligatoire** — avant toute régression symbolique, vérifier si une Ridge simple ne fait pas aussi bien. (G11 : 24/25 cas, la linéaire suffit.)
4. **Graphes frais obligatoires** — toute loi doit être testée sur des graphes non vus pendant la découverte.
5. **Filtrer les tautologies** — deg_sum = lap_trace = 2m, adj_trace_sq = 2m, adj_trace_cube = 6×triangles sont des identités, pas des découvertes.
6. **Vérifier la littérature** — avant de crier victoire, chercher si le résultat existe déjà. (Toutes nos "meilleures" lois étaient connues.)

### Principes méthodologiques

7. **Mesurer des métriques standard ne révèle que des phénomènes standard** — la leçon la plus chère de G1-G6.
8. **Le spectre encode presque tout** — la leçon la plus profonde de G7-G11. Tant qu'on mesure des choses déterminées par les eigenvalues, on redécouvre des conséquences.
9. **La régression symbolique ≠ la linéaire + 5%** — sur nos données, la puissance d'expression supplémentaire n'apporte presque rien (G11).
10. **Un résultat négatif n'est intéressant que s'il survit à la tentative de le contourner** — on a essayé 3 contournements (G9, G10, G11). Ils convergent.
11. **Ne pas recalculer ce qui existe** — les JSON contiennent les métriques pré-calculées. Ne régénérer les graphes QUE si on calcule quelque chose de nouveau sur l'objet graphe lui-même.
12. **Copier en /tmp/ avant les opérations lourdes** — le FUSE mount de /agent/ est lent pour git et les gros I/O.

### Principes de falsification post-spectrale (ajoutés G12-G16)

13. **Un signal non-trivial ≠ une loi** — le compression gap a R² < 0.43 vs densité et sépare les cospectraux, mais son scaling est un artefact. Exiger les 4 critères simultanément (non-trivial, résistant, absent de la littérature, explicable).
14. **Tester la dépendance aux paramètres** — une "universalité" apparente peut venir du fait qu'on teste à ⟨k⟩ ou n similaires. Varier systématiquement les paramètres de la famille.
15. **Tester la dépendance à la méthode** — si le résultat change avec l'algorithme de compression, la discrétisation, ou l'encodage, c'est un artefact de mesure, pas une propriété du graphe.
16. **Décomposer avant de célébrer** — le "taux universel b" n'existait que parce que le spectre converge 3× plus vite que la structure. Décomposer tout résultat en ses composantes.
17. **Le CLT explique les scaling laws "faibles"** — si std(metric) ~ n^{-α} et les ratios α(m₁)/α(m₂) sont constants, vérifier si les métriques sont des U-statistiques du même ordre (Janson 2004).
18. **Config model = test ultime** — si config_model(même degré seq) donne le même résultat que BA/ER, la propriété dépend de la distribution de degrés, pas du câblage. Pas nouveau.

### Principes de comportement pour l'agent

19. **Ne pas se comporter comme un cheerleader** — chaque résultat positif doit être attaqué immédiatement.
20. **Explorer des chemins inconnus et contre-intuitifs** — les réponses sont là où aucun humain n'irait chercher.
21. **Résultats dans le chat, pas dans des fichiers de rapport** — sauf pour les très longs contenus.
22. **Vérifier l'inédit de chaque claim** avant de l'exploiter.
23. **Ne pas écouter aveuglément les suggestions d'autres LLMs** — les filtrer avec la même rigueur que nos propres idées. (ChatGPT a suggéré la régression symbolique comme "game changer" — résultat : marginal.)

---

## Pistes futures réalistes

### ❌ Ce qui ne marchera PAS (et pourquoi)

| Piste | Raison de l'échec | Prouvé en |
|---|---|---|
| Plus de métriques sur graphes finis statiques | L'espace spectral est saturé | G1-G11 |
| Algorithme génétique de métriques | Combine des quantités spectrales → espace fermé | G4, G7 |
| PCA / réduction dimensionnelle | Métriques corrélées, c'est connu | G4 |
| Régression symbolique plus profonde | Gain marginal sur la linéaire | G11 |
| Hypergraphes / complexes simpliciaux (naïvement) | Même piège G1-G11 sur objet différent | — |
| **Compression comme invariant** | Dépend de l'algo (66% spread), pas intrinsèque | **G14-G15** |
| **IPR skew comme invariant** | CV = 0.56–1.46, trop instable | **G13** |
| **Half_life_frac comme invariant** | R² = 0.87 avec avg_degree, trivial | **G13** |
| **Graphes pondérés (aléatoires)** | Localisation d'Anderson 1958, ultra-connu | **G13** |
| **Lois de scaling via compression** | ln(n) = convergence spectrale, b dépend de ⟨k⟩ | **G15** |
| **Morphismes fonctoriels** | Seuls invariants triviaux préservés | **G16** |
| **Familles paramétriques metric(p)** | Transitions = seuils de connectivité connus | **G16** |
| **Exposants de fluctuation α** | CLT pour U-statistiques (Janson 2004) | **G16** |

### ⚠️ Ce qui POURRAIT encore marcher (avec des réserves fortes)

> **Note après G16 :** Les pistes A-D de la version précédente ont été partiellement ou totalement explorées. Les scaling laws (A) sont des artefacts ou du CLT. Les graphes pondérés (B) donnent Anderson 1958. Les transitions de phase (C) sont aux seuils connus. Les opérations non-standard (D) ne donnent que des invariants triviaux. La piste E (changer le type de question) reste la seule direction viable, reformulée ci-dessous.

#### Piste 1 — Preuves formelles guidées par le numérique

**Idée** : passer de l'exploration computationnelle aux mathématiques. Utiliser nos ~250K calculs comme guide pour formuler et prouver des théorèmes. Par exemple : prouver que le compression gap est borné inférieurement par une fonction de la distribution de degrés.

**Pourquoi c'est différent** : on sort du paradigme "mesurer et chercher des patterns" pour entrer dans "prouver des implications structurelles". Nos données orientent la preuve.

**Risques** : nécessite des compétences de mathématicien, pas seulement de calcul brut.

#### Piste 2 — Graphes réels (réseaux biologiques, sociaux, technologiques)

**Idée** : les modèles théoriques (ER, BA, WS) sont des approximations. Les vrais réseaux ont des propriétés que les modèles ne capturent pas (motifs, communautés hiérarchiques, corrélations temporelles).

**Pourquoi c'est différent** : les graphes réels ne sont pas générés par un processus simple. La complexité de leur formation pourrait produire des invariants que les modèles ne montrent pas.

**Risques** : overfitting sur des datasets spécifiques. Difficulté de généralisation.

#### Piste 3 — Information quantique sur graphes

**Idée** : entropie de Von Neumann, intrication dans les graphes d'états quantiques, marches quantiques.

**Pourquoi c'est différent** : les marches quantiques ont un comportement fondamentalement différent des marches classiques (interférences). Les invariants associés pourraient être inaccessibles à la théorie classique.

**Risques** : domaine actif et bien publié — risque de redécouverte. La Von Neumann entropy classique a déjà été testée (G7, redondante).

---

## Structure des données

```
Graph-Systems-Exploration/
├── README.md                          # Ce fichier
├── NEXT_AGENT_BRIEFING.md             # Briefing technique complet pour le prochain agent
├── requirements.txt                   # Dépendances Python
│
├── phases/                            # Scripts Python de chaque phase
│   ├── G1/phase_g1.py                # Génération de 356 graphes + 31 métriques
│   ├── G2/phase_g2.py                # Déformations contrôlées
│   ├── G3/phase_g3.py                # Percolation fine
│   ├── G4/phase_g4.py                # Chasse aux invariants (50K combinaisons)
│   ├── G5/phase_g5.py                # Synthèse croisée
│   ├── G6/phase_g6.py                # Falsification hardcore
│   ├── G7/*.py                        # 83 nouvelles métriques non-standard
│   ├── G8/g8_5_6.py, g8_7_8_v2.py   # Approfondissement des survivantes
│   ├── G9/g9_conservation_laws.py    # Lois de conservation (SVD)
│   ├── G10/g10_spectral_gap.py       # Faille spectrale + ops exotiques
│   │   └── g10_exotic_ops.py
│   └── G11/g11_transformation_laws.py # Lois de transformation (régression)
│
└── data/                              # Résultats JSON
    ├── g1_results.json                # 356 graphes × 31 métriques (349 KB)
    ├── g2_trajectories.json           # Trajectoires de déformation (314 KB)
    ├── g3_results.json                # Courbes de percolation (263 KB)
    ├── g6_results.json                # Falsification 68 graphes extrêmes
    ├── g7_*.json                      # 83 nouvelles métriques sur 356 graphes
    ├── g8_*.json                      # Résultats G8.5, G8.6, G8.7, G8.8
    ├── g9_conservation_laws.json      # 8 lois de conservation (réelles mais dérivables)
    ├── g10_spectral_gap.json          # 7 paires cospectrales + analyse
    ├── g10_exotic_ops.json            # 6 ops exotiques × 80 graphes
    └── g11_transformation_laws.json   # 6 lois de transformation survivantes
```

### Format des données

**g1_results.json** : liste de 356 objets
```json
{
  "name": "erdos_renyi",
  "params": {"n": 50, "p": 0.01},
  "n": 50, "m": 15, "density": 0.012,
  "deg_mean": 0.6, "deg_std": 0.63,
  "spectral_radius": ..., "algebraic_connectivity": ...,
  ...
}
```

Les JSON contiennent les métriques pré-calculées. Ne régénérer les graphes QUE pour calculer quelque chose de nouveau sur l'objet graphe lui-même.

---

## Stack technique

| Outil | Usage |
|---|---|
| Python 3.12 | Langage principal |
| NetworkX ≥ 3.0 | Génération et analyse de graphes |
| NumPy ≥ 1.24 | Calcul vectorisé, algèbre linéaire |
| SciPy ≥ 1.10 | Eigenvalues, statistiques, sparse matrices |

**Note** : scikit-learn et les packages nécessitant une compilation C ne fonctionnent pas toujours sur Alpine Linux (sandbox). Préférer les implémentations en pur numpy quand possible. PySR fonctionne mais les résultats ne justifient pas la complexité d'installation.

---

## Historique du projet

- **Origine** : Pivot depuis le projet Riemann (18 phases, résultat négatif sur la troncature zêta)
- **G1-G6** : Exploration classique — 31 métriques standard → 6 lois candidates → toutes cassées/connues
- **G7-G8** : Nouvelles métriques (83 non-standard) → redondantes avec le spectre ou fragiles
- **G9** : Changement de paradigme — lois de conservation → 8 lois réelles mais dérivables
- **G10** : Faille spectrale — le non-spectral existe mais est "sans loi de conservation"
- **G11** : Lois de transformation — prédictibles mais triviales ou approximatives
- **G12** : Trois propositions post-spectrales (eigenvectors, compression, trajectoires)
- **G13** : Approfondissement 4 fronts — compression gap découvert, half_life trivial, Anderson 1958
- **G14** : Compression gap deep dive — scaling, fonctionnel, falsification, cross-connexions
- **G15** : Test critique — universalité du taux logarithmique TUÉE (dépend de ⟨k⟩, algo, convergence spectrale)
- **G16** : 4 pivots radicaux — familles paramétriques, morphismes, complexité, graphons → tous convergent vers le connu

**Contribution principale** : un pipeline de découverte-falsification automatisé, et la démonstration empirique que l'espace des lois simples sur les graphes finis est saturé — **y compris dans les directions post-spectrales** (compression, complexité algorithmique, exposants de convergence, morphismes fonctoriels).

---

## Licence

MIT

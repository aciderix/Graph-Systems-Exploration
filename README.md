# Graph Systems Exploration

**Exploration computationnelle systématique des graphes finis — 11 phases, ~200 000 calculs, 0 loi fondamentalement nouvelle.**

Ce projet est un résultat négatif de haute qualité. Son apport principal est **méthodologique** : un pipeline de découverte-falsification automatisé qui a démontré empiriquement que l'espace des lois algébriques simples sur les graphes finis est saturé.

---

## Table des matières

1. [Philosophie et objectif](#philosophie-et-objectif)
2. [Résumé exécutif](#résumé-exécutif)
3. [Phases G1→G11 : le parcours complet](#phases-g1g11--le-parcours-complet)
4. [Les 3 grandes découvertes (toutes négatives)](#les-3-grandes-découvertes-toutes-négatives)
5. [Leçons apprises — règles de travail](#leçons-apprises--règles-de-travail)
6. [Pistes futures réalistes](#pistes-futures-réalistes)
7. [Structure des données](#structure-des-données)
8. [Stack technique](#stack-technique)

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

**Résultat après 11 phases : 0/4 satisfait. Le résultat négatif lui-même est informatif.**

---

## Résumé exécutif

```
356 graphes × 21 familles × 114 métriques (31 standard + 83 non-standard)
+ 4 processus dynamiques (Kuramoto, SIR, chaleur, coopération)
+ 8 opérations classiques × 6 opérations exotiques
+ 7 paires de graphes cospectraux
+ Lois de conservation (SVD null-space)
+ Lois de transformation (régression symbolique)
+ Falsification systématique à chaque étape
= ~200 000 calculs individuels
= 0 loi fondamentalement nouvelle
```

### Le théorème empirique

> **Sur les graphes finis, les lois algébriques simples vivent dans l'espace spectral, et l'espace spectral est entièrement défriché. L'espace non-spectral est prédictible mais sans lois exactes simples.**

---

## Phases G1→G11 : le parcours complet

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

## Les 3 grandes découvertes (toutes négatives)

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

### Principes de comportement pour l'agent

13. **Ne pas se comporter comme un cheerleader** — chaque résultat positif doit être attaqué immédiatement.
14. **Explorer des chemins inconnus et contre-intuitifs** — les réponses sont là où aucun humain n'irait chercher.
15. **Résultats dans le chat, pas dans des fichiers de rapport** — sauf pour les très longs contenus.
16. **Vérifier l'inédit de chaque claim** avant de l'exploiter.
17. **Ne pas écouter aveuglément les suggestions d'autres LLMs** — les filtrer avec la même rigueur que nos propres idées. (ChatGPT a suggéré la régression symbolique comme "game changer" — résultat : marginal.)

---

## Pistes futures réalistes

### ❌ Ce qui ne marchera PAS (et pourquoi)

| Piste | Raison de l'échec prévisible |
|---|---|
| Plus de métriques sur graphes finis statiques | L'espace spectral est saturé (prouvé G1-G11) |
| Algorithme génétique de métriques | Combine des quantités spectrales → reste dans l'espace fermé |
| PCA / réduction dimensionnelle | Déjà fait en G4. Les métriques sont corrélées, c'est connu |
| Régression symbolique plus profonde | G11 montre gain marginal sur la linéaire |
| Hypergraphes / complexes simpliciaux (naïvement) | Risque de refaire G1-G11 version 2.0 (même piège, objets différents) |

### ⚠️ Ce qui POURRAIT marcher (avec des réserves)

#### Piste A — Lois de SCALING (n → ∞)

**Idée** : au lieu de chercher F(G) = const, chercher comment F(G_n) évolue quand on grandit G dans une famille donnée. Les lois de scaling sont le pain quotidien de la physique statistique mais restent peu explorées systématiquement sur les graphes.

**Pourquoi c'est différent** : une loi de scaling n'est pas un invariant — c'est un **exposant**. "diameter ∝ n^α" est une loi même si diameter change avec n.

**Risques** : beaucoup d'exposants de scaling sont déjà connus (diamètre ER = O(log n), BA = O(log n/log log n), etc.).

**Test de faisabilité** : générer des séquences de graphes de même famille avec n croissant, mesurer les exposants, vérifier contre la littérature.

#### Piste B — Graphes pondérés continus

**Idée** : les poids sur les arêtes introduisent un continuum. Le spectre du Laplacien pondéré ne détermine plus aussi facilement la structure.

**Pourquoi c'est différent** : on sort de l'espace "graphe fini non pondéré" qui est saturé. Les poids brisent certaines symétries spectrales.

**Risques** : espace de recherche plus grand = plus de chances de surapprentissage. Besoin de contraintes claires sur les poids.

#### Piste C — Transitions de phase dans les ensembles contraints

**Idée** : fixer une propriété (nombre d'arêtes, séquence de degrés, etc.) et faire varier une autre contrainte. Chercher des seuils critiques dans l'espace des graphes satisfaisant les contraintes.

**Pourquoi c'est différent** : les transitions de phase dans les graphes aléatoires contraints sont un domaine actif avec des résultats ouverts (ex : seuil de satisfaisabilité de k-SAT sur graphes aléatoires).

**Risques** : computationnellement coûteux (échantillonner uniformément sous contraintes est NP-dur en général).

#### Piste D — Opérations NON-STANDARD dont la théorie spectrale est inconnue

**Idée** : les opérations testées en G9 (produit cartésien, corona, line graph, etc.) ont toutes une théorie spectrale exacte connue. D'où nos "lois dérivables". Il faudrait des opérations **sans formule spectrale connue**.

**Exemples** :
- Rewiring conditionnel (réécrire les arêtes selon une règle basée sur le spectre local)
- Contraction par métrique (fusionner les nœuds les plus proches en betweenness)
- Évolution stochastique (appliquer une dynamique et observer le graphe à l'équilibre)

**Risques** : si l'opération est trop stochastique, les métriques résultantes seront bruitées → pas de loi exacte possible.

#### Piste E — La vraie sortie : changer le TYPE de question

**L'insight le plus profond de G1-G11** : on cherchait des réponses dans un espace de questions épuisé. La question "quelle est la valeur de M(G) ?" et même "comment M change sous T ?" restent dans le cadre "mesure sur objet fixe".

**Questions radicalement différentes** :
- **Information-théorétiques** : quelle est la quantité minimale d'information nécessaire pour reconstruire un graphe à partir de ses métriques ? (Taux de compression optimale)
- **Algorithmiques** : existe-t-il une propriété de graphe calculable en O(n) qui sépare les graphes cospectraux ? (Complexité computationnelle des invariants)
- **Catégoriques** : quels sont les foncteurs entre la catégorie des graphes et la catégorie des espaces métriques qui préservent une structure intéressante ?

Ce sont des questions que la force brute ne peut pas résoudre — elles nécessitent une approche théorique guidée par les résultats computationnels qu'on a accumulés.

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

**Contribution principale** : un pipeline de découverte-falsification automatisé, et la démonstration empirique que l'espace des lois simples sur les graphes finis est saturé.

---

## Licence

MIT

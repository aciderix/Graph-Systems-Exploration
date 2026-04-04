# BRIEFING COMPLET — Projet Exploration Systématique des Graphes

## Destinataire : Prochain agent de travail

**Date :** 5 avril 2025
**Auteur :** Agent précédent (Tasklet)
**Repo GitHub :** https://github.com/aciderix/Graph-Systems-Exploration
**Token GitHub :** `[TOKEN REDACTED — ask owner]`

---

## TABLE DES MATIÈRES

1. [Contexte et philosophie du projet](#1-contexte-et-philosophie-du-projet)
2. [Ce qui a été fait (Phases G1-G6)](#2-ce-qui-a-été-fait-phases-g1-g6)
3. [Résultats concrets et données](#3-résultats-concrets-et-données)
4. [Ce qui a ÉCHOUÉ — leçons apprises](#4-ce-qui-a-échoué--leçons-apprises)
5. [Direction recommandée : Option 2 — Nouvelles métriques](#5-direction-recommandée--option-2--nouvelles-métriques)
6. [Ressources techniques](#6-ressources-techniques)
7. [Principes de travail OBLIGATOIRES](#7-principes-de-travail-obligatoires)

---

## 1. Contexte et philosophie du projet

### Origine

Ce projet est né d'un pivot. Le travail précédent (18 phases) explorait la **fonction zêta de Riemann** et les produits d'Euler tronqués, cherchant des chemins vers RH (Riemann Hypothesis). Conclusion après 18 phases : toutes les routes par troncature sont fermées. Le phénomène "α = 3/4" s'est révélé être un artefact de la convergence de Dickman, pas un invariant fondamental.

### Pivot vers les graphes

L'idée : transposer la **démarche expérimentale systématique** (pas les outils mathématiques) vers la théorie des graphes. Mêmes principes — exploration exhaustive, zéro biais, falsification impitoyable — mais sur un terrain où les structures sont plus accessibles computationnellement.

### Philosophie fondamentale

> **Tu ne dois pas te comporter comme un mathématicien cherchant une preuve, mais comme un système exploratoire cherchant à cartographier un espace inconnu et en extraire des lois fondamentales.**

Concrètement :
- **Penser comme une machine, pas comme un humain** — pas d'intuition non testée
- **Couverture maximale** — tester même les pistes improbables
- **Refuser les explications faciles** — remettre en question chaque résultat
- **Falsifier systématiquement** — une loi n'est intéressante que si elle survit à la tentative de destruction
- **Documenter les échecs aussi clairement que les succès**

---

## 2. Ce qui a été fait (Phases G1-G6)

### Phase G1 — Génération massive + mesures baseline

**356 graphes** générés couvrant **21 familles** :

| Famille | Nb graphes | Tailles (N) | Paramètres variés |
|---|---|---|---|
| erdos_renyi | 24 | 50-500 | p ∈ {0.01, 0.02, 0.05, 0.1, 0.2} |
| barabasi_albert | 20 | 50-500 | m ∈ {1, 2, 3, 5} |
| watts_strogatz | 72 | 50-500 | k ∈ {4,6,10}, p ∈ {0.01,0.05,0.1,0.3,0.5,1.0} |
| newman_watts_strogatz | 24 | 50-200 | k ∈ {4,10}, p ∈ {0.01,0.05,0.1,0.3,0.5,1.0} |
| random_geometric | 16 | 50-500 | r ∈ {0.1,0.15,0.2,0.3} |
| stochastic_block | 24 | 50-200 | 2-5 blocs, p_in/p_out variés |
| connected_caveman | 6 | 25-200 | cliques de 5-20 |
| powerlaw_cluster | 36 | 50-500 | m ∈ {2,3,5}, p ∈ {0,0.3,0.5,0.8,1} |
| dual_barabasi_albert | 36 | 100-500 | m1,m2,p variés |
| random_regular | 12 | 50-200 | d ∈ {3,5,10} |
| balanced_tree | 9 | 15-1365 | r ∈ {2,3}, h ∈ {3,4,5} |
| circulant | 15 | 50-200 | offsets variés |
| random_lobster | 27 | ~100-2237 | p1,p2 ∈ {0.3,0.5,0.8} |
| complete | 4 | 10-100 | — |
| complete_bipartite | 9 | 20-100 | n1/n2 variés |
| grid_2d | 4 | 49-400 | 7×7 à 20×20 |
| triangular_lattice | 3 | 21-91 | — |
| star | 4 | 20-200 | — |
| path | 4 | 20-200 | — |
| cycle | 3 | 50-200 | — |
| random_tree | 4 | 50-500 | — |

**31 métriques mesurées par graphe :**

| Catégorie | Métriques |
|---|---|
| Structure | n, m, density |
| Degrés | deg_mean, deg_std, deg_min, deg_max, deg_median, deg_skew, deg_kurtosis |
| Composantes | num_components, largest_cc_frac |
| Clustering | clustering_avg, transitivity, num_triangles |
| Distances | avg_shortest_path, diameter |
| Corrélations | assortativity |
| Spectre (A) | spectral_radius, spectral_gap, eig_A_min |
| Spectre (L) | algebraic_connectivity, laplacian_max, spectral_ratio, norm_lap_gap |
| Topologie | girth |
| Communautés | modularity, num_communities |
| Global | wiener_index |

**Fichier :** `g1_results.json` (349 KB, liste de 356 dictionnaires)

### Phase G2 — Déformations contrôlées

5 types de déformation × 13 niveaux (0% à 100%) × 12 graphes de base :

| Déformation | Description |
|---|---|
| edge_addition | Ajout aléatoire d'arêtes (0% à 100% des arêtes possibles manquantes) |
| edge_removal | Suppression aléatoire (0% à 90% des arêtes) |
| rewiring | Remplacement d'arêtes (conservation du degré) |
| node_removal | Suppression aléatoire de nœuds |
| degree_attack | Suppression ciblée des nœuds de plus haut degré |

Tracking continu de TOUTES les métriques à chaque niveau.

**Résultats clés :**
- Transition small-world détectée : 2% de rewiring dans caveman divise le diamètre par 1.5
- Seuils de percolation identifiés pour chaque famille
- BA(m=1) s'effondre après suppression de 2% des hubs

**Fichier :** `g2_trajectories.json` (314 KB)

### Phase G3 — Percolation fine

14 graphes × 3 modes d'attaque × 50-200 points par courbe :

| Mode | Cible |
|---|---|
| random | Nœuds aléatoires |
| degree | Plus hauts degrés d'abord |
| betweenness | Plus haute centralité d'intermédiarité d'abord |

Métriques trackées : taille LCC (largest connected component), taille SLC (second largest component), nombre de composantes.

**Résultat principal :** Le seuil critique se détecte précisément par le pic du SLC. Les graphes à queue lourde (BA) ont des seuils très bas sous attaque ciblée.

**Fichier :** `g3_results.json` (263 KB)

### Phase G4 — Chasse aux invariants

~50 000 combinaisons algébriques testées systématiquement :
- Produits, ratios, puissances de toutes paires de métriques
- Recherche de quantités à faible coefficient de variation (CV)
- PCA sur l'espace des 302 graphes connectés

**Résultat PCA :**
- PC1 (48%) = axe densité/connectivité
- PC2 (24%) = axe clustering
- 72% de variance expliquée par 2 dimensions

### Phase G5 — Synthèse croisée

Validation des 6 lois candidates identifiées en G1-G4. Tests de robustesse.

### Phase G6 — FALSIFICATION (la plus importante)

**68 graphes extrêmes testés** + 24 scénarios de destruction + tests de trivialité.

Graphes extrêmes testés : étoiles, cliques, paths, cycles, arbres binaires, barbells, lollipops, roues, bipartites complets, caterpillars, Petersen, dodécaèdre, icosaèdre, Tutte, Sierpinski, graphes très petits (N=4 à 30), cliques inégales reliées par un pont, graphes almost-disconnected.

---

## 3. Résultats concrets et données

### Les 6 lois candidates et leur statut post-falsification

#### LOI 1 — Entropie spectrale normalisée S/log₂(N) → 0.97

**Statut : ❌ QUASI-TRIVIALE (70%)**

| N | Matrice aléatoire | Uniforme[0,2] | Graphe Laplacien |
|---|---|---|---|
| 50 | 0.944 | 0.950 | 0.970 |
| 100 | 0.952 | 0.958 | 0.987 |
| 200 | 0.959 | 0.963 | 0.995 |

Le gros de l'effet (~0.95) est de la **concentration entropique** — n'importe quelle distribution de N nombres donne S/log₂(N) → 1 quand N → ∞. Le surplus graphe (~0.02) est réel mais trop faible pour être une "loi".

Contre-exemples : path_5 (0.759), ER_tiny_N4 (0.703), mais uniquement pour N ≤ 10.

#### LOI 2 — Trois régimes de vulnérabilité

**Statut : ⚠️ DESCRIPTIF (vrai mais connu)**

| Régime | Ratio attaque/aléatoire | Exemples |
|---|---|---|
| VULNÉRABLE (< 0.3) | Hub-dependent | BA_m1 (0.12), caveman (0.20) |
| MODÉRÉ (0.3-0.7) | Mixte | ER (0.43-0.61) |
| ROBUSTE (> 0.7) | Homogène | Régulier (0.90-0.98), WS_low (1.00!) |

Le déterminant est le **CV des degrés**, pas κ. Mais c'est essentiellement "les graphes hétérogènes sont fragiles" — connu depuis Albert-Barabási 2000.

#### LOI 3 — C × L n'est PAS universel

**Statut : ❌ CONNU** — varie de 0 à 5.6, pas de constante.

#### LOI 4 — ρ(A)/⟨k⟩ = signature spectrale d'hétérogénéité

**Statut : ✅ VRAIE mais CONNUE**

- **15/15 graphes réguliers à ρ/⟨k⟩ = 1.000 exact** (cycles, cliques, Petersen, dodécaèdre, icosaèdre, k-réguliers)
- Range totale : [1.000, 7.106] (Kbip_1_200)
- Les étoiles donnent ρ/⟨k⟩ → √N, les BA donnent ~2-3

C'est essentiellement le théorème de Perron-Frobenius : pour un graphe k-régulier, la plus grande valeur propre de A est exactement k.

#### LOI 5 — Transition de percolation détectable par pic du SLC

**Statut : ⚠️ STANDARD** — utilisé en physique statistique depuis 30 ans.

#### LOI 6 — λ₂ × D borné mais non constant

**Statut : ❌ CONNU** — borne classique.

### Verdict global

> **0 résultat véritablement nouveau sur 6.** Le travail est propre et exhaustif, mais les métriques classiques ne révèlent que des phénomènes classiques. Pour trouver quelque chose de nouveau, il faut **inventer de nouvelles métriques**.

---

## 4. Ce qui a ÉCHOUÉ — leçons apprises

### Erreur 1 : Mesurer des métriques standard sur des graphes standard

On a mesuré 31 métriques connues. Résultat prévisible : on a retrouvé des phénomènes connus. Pour trouver du nouveau, il faut des **observables nouvelles**.

### Erreur 2 : Surinterpréter LOI 1

L'entropie spectrale normalisée "quasi-universelle" semblait révolutionnaire. Le test de trivialité (comparaison avec matrices aléatoires) a montré que c'est un artefact de concentration. **Toujours tester contre le null le plus stupide possible.**

### Erreur 3 : Ne pas falsifier assez tôt

Les phases G1-G5 ont produit des "lois" non testées. La falsification (G6) a tué 5 sur 6. Il faut falsifier au fur et à mesure, pas à la fin.

### Leçon centrale

> Les graphes sont un espace bien exploré. Pour trouver quelque chose de nouveau, il faut soit :
> - Explorer un **sous-espace** peu étudié (graphes dynamiques, hyperboliques, produits tensoriels)
> - Inventer de **nouvelles observables** (métriques non-standard, transformées, analogies physiques)
> - Les deux à la fois

---

## 5. Direction recommandée : Option 2 — Nouvelles métriques

### Objectif

Inventer des métriques **non standards** — des quantités qu'aucun article ne mesure — et voir si elles révèlent des structures cachées.

### 10 pistes concrètes à explorer

#### Piste A — Métriques de "tension" et "courbure" locale

**Idée :** Traiter le graphe comme une surface discrète. Définir une "courbure de Ricci discrète" locale (Ollivier-Ricci ou Forman-Ricci) et étudier sa distribution.

**Pourquoi c'est prometteur :** La courbure de Ricci discrète est récente (2009-2015) et peu explorée systématiquement. Elle pourrait révéler des invariants de "forme" invisibles aux métriques spectrales.

**Implémentation :** Bibliothèque `GraphRicciCurvature` en Python, ou calcul direct de la distance de Wasserstein-1 entre distributions de voisinage.

**Mesures à faire :**
- Distribution de la courbure de Ricci sur toutes les arêtes
- Moyenne, variance, skewness, kurtosis
- Corrélation courbure ↔ centralité
- Comportement sous déformation

#### Piste B — Entropie de Von Neumann et température du graphe

**Idée :** Traiter la matrice densité ρ = L/trace(L) (Laplacien normalisé par la trace) comme un état quantique. L'entropie de Von Neumann S_VN = -trace(ρ log ρ) est une mesure d'intrication.

**Pourquoi c'est différent de LOI 1 :** LOI 1 utilisait l'entropie de Shannon sur le spectre. L'entropie de Von Neumann est une quantité physique avec une interprétation en termes de "température" du graphe — et ses propriétés sous opérations de graphes (union, produit) sont non triviales.

**Mesures :**
- S_VN pour tous les 356 graphes
- Comportement sous ajout/suppression d'arêtes
- Relation avec d'autres métriques
- Subadditivité pour des sous-graphes

#### Piste C — Transformée en ondelettes sur graphes

**Idée :** Décomposer les signaux sur graphes en échelles spatiales via les ondelettes spectrales de graphes (SGWT, Hammond 2011). Mesurer l'énergie à chaque échelle.

**Pourquoi c'est prometteur :** Permet de détecter des structures multi-échelles. Deux graphes peuvent avoir les mêmes métriques globales mais des signatures très différentes à certaines échelles.

**Implémentation :** Bibliothèque `PyGSP` (Graph Signal Processing).

**Mesures :**
- Spectre en ondelettes pour un signal constant/aléatoire
- Concentration d'énergie par bande de fréquence
- Ratio hautes/basses fréquences comme métrique structurelle

#### Piste D — Distance de Gromov-Hausdorff entre graphes

**Idée :** Définir une distance entre graphes basée sur la géométrie métrique, pas sur l'isomorphisme. Construire un "atlas" de l'espace des graphes avec cette distance.

**Pourquoi :** Permet de voir quels graphes sont "proches" structurellement, même s'ils ont des tailles différentes.

**Implémentation :** Approximation via les distributions de distances (persistance topologique) ou via les embeddings spectraux.

#### Piste E — Homologie persistante (TDA)

**Idée :** Calculer les groupes d'homologie du complexe de Vietoris-Rips associé au graphe à différentes échelles. Les "barres de persistance" révèlent les trous topologiques stables.

**Pourquoi c'est prometteur :** La TDA (Topological Data Analysis) est puissante mais rarement appliquée systématiquement aux familles classiques de graphes. Les diagrammes de persistance pourraient servir de signature.

**Implémentation :** `ripser`, `gudhi`, ou `giotto-tda`.

**Mesures :**
- Nombre de barres en dimension 0, 1, 2
- Entropie de persistance
- Durée de vie maximale en dimension 1 (trous)

#### Piste F — Métriques de "réponse" dynamique

**Idée :** Au lieu de mesurer le graphe statiquement, le perturber et mesurer la **réponse**. Injecter un signal (chaleur, marche aléatoire) et mesurer comment il se propage.

**Mesures :**
- Temps de mixing d'une marche aléatoire
- Profil de diffusion de chaleur à t = 1, 10, 100
- "Résistance effective" entre paires de nœuds
- Spectre du noyau de chaleur H(t) = exp(-tL)
- Trace de H(t) = somme des exp(-t λ_i) comme "fonction de partition"

**Le lien avec la physique :** La trace de H(t) est la fonction de partition d'un système quantique sur le graphe. La dérivée -d/dt log trace(H(t)) est "l'énergie" à température 1/t.

#### Piste G — Non-linéarités et chaos sur graphes

**Idée :** Itérer une dynamique non-linéaire (ex : f(x) = x² mod 1, ou logistique) sur les nœuds du graphe couplés par les arêtes. Mesurer l'exposant de Lyapunov, le temps de synchronisation.

**Pourquoi :** Les graphes réguliers se synchronisent, les graphes hétérogènes divergent. Le seuil de synchronisation est un **invariant dynamique** non trivial.

**Mesures :**
- Seuil de couplage pour synchronisation
- Exposant de Lyapunov maximal
- Dimension de l'attracteur

#### Piste H — Théorie des jeux sur graphes

**Idée :** Simuler des jeux évolutionnaires (Prisoner's Dilemma, Hawk-Dove) sur les graphes. Mesurer l'équilibre de coopération.

**Pourquoi :** Le taux de coopération à l'équilibre est une propriété émergente du graphe qui dépend de la topologie de manière non triviale.

#### Piste I — Produits tensoriels et opérations sur graphes

**Idée :** Étudier comment les métriques se comportent sous les opérations : produit cartésien G□H, produit tensoriel G×H, produit lexicographique, complément, line graph.

**Pourquoi :** Les invariants qui sont multiplicatifs ou additifs sous ces opérations sont rares et importants. En trouver de nouveaux serait significatif.

#### Piste J — Métriques d'information et compression

**Idée :** Mesurer la "complexité" d'un graphe par la taille de sa description compressée (Kolmogorov approximée). Utiliser la compressibilité de la matrice d'adjacence (via gzip, zlib) comme proxy.

**Pourquoi :** La complexité de Kolmogorov est l'ultime mesure de structure. Un graphe aléatoire est incompressible, un graphe structuré est compressible. Le ratio compression pourrait être un invariant non trivial.

**Mesures :**
- Taille compressée de la matrice d'adjacence (gzip)
- Ratio de compression
- Corrélation avec les autres métriques

### Priorités recommandées

| Priorité | Piste | Raison |
|---|---|---|
| **1** | F (Réponse dynamique) | Facile à implémenter, riche en observables, physique claire |
| **2** | A (Courbure de Ricci) | Récente, peu explorée systématiquement, invariant géométrique |
| **3** | B (Von Neumann) | Extension naturelle de LOI 1 mais NON triviale |
| **4** | E (TDA / Homologie persistante) | Puissante, signatures robustes |
| **5** | J (Compression) | Ultra-simple à implémenter, résultat immédiat |

Les pistes C, D, G, H, I sont des extensions naturelles si les 5 premières donnent des résultats.

### Protocole de travail recommandé

Pour CHAQUE nouvelle métrique :

```
1. DÉFINIR précisément la métrique (formule, pas de flou)
2. IMPLÉMENTER et calculer sur les 356 graphes existants
3. CORRÉLER avec les 31 métriques connues
   → Si corrélation > 0.95 avec une métrique connue → SKIP (redondant)
4. VARIER sous déformation (données G2 existantes)
   → Chercher des transitions de phase NOUVELLES
5. FALSIFIER immédiatement
   → Tester sur graphes extrêmes (G6 dataset)
   → Tester contre le null aléatoire
   → Si ça ne survit pas → documenter l'échec et passer à la suivante
6. Si SURVIE → caractériser (universalité, bornes, dépendance en N)
```

---

## 6. Ressources techniques

### Fichiers sur le repo GitHub

```
Graph-Systems-Exploration/
├── README.md                    # Vue d'ensemble du projet
├── requirements.txt             # Dépendances Python
├── phases/
│   ├── G1/
│   │   ├── phase_g1.py         # Script de génération (16 KB)
│   │   └── results.json        # 356 graphes × 31 métriques (349 KB)
│   ├── G2/
│   │   ├── phase_g2.py         # Script de déformation (12 KB)
│   │   └── results.json        # Trajectoires de déformation (314 KB)
│   ├── G3/
│   │   ├── phase_g3.py         # Script de percolation (11 KB)
│   │   └── results.json        # Courbes de percolation (263 KB)
│   ├── G4/
│   │   └── phase_g4.py         # Chasse aux invariants (14 KB)
│   └── G5/
│       └── phase_g5.py         # Synthèse croisée (12 KB)
└── data/
    ├── g1_results.json          # Copie des résultats G1
    ├── g2_trajectories.json     # Copie des résultats G2
    └── g3_results.json          # Copie des résultats G3
```

### Fichiers sur /agent/home/graphs/

```
/agent/home/graphs/
├── phase_g1.py through phase_g6.py   # Tous les scripts
├── g1_results.json                     # Données G1
├── g2_trajectories.json               # Données G2
├── g3_results.json                     # Données G3
├── g6_results.json                     # Données de falsification
└── NEXT_AGENT_BRIEFING.md             # Ce document
```

### Stack technique

| Outil | Usage |
|---|---|
| Python 3.12 | Langage principal |
| NetworkX ≥ 3.0 | Génération et analyse de graphes |
| NumPy ≥ 1.24 | Calcul vectorisé, algèbre linéaire |
| SciPy ≥ 1.10 | Eigenvalues, statistiques, sparse matrices |
| mpmath ≥ 1.3 | Haute précision (30 décimales) si nécessaire |
| matplotlib ≥ 3.7 | Visualisations |

**Bibliothèques additionnelles recommandées pour la suite :**

| Bibliothèque | Piste | Usage |
|---|---|---|
| `GraphRicciCurvature` | A | Courbure de Ricci discrète |
| `PyGSP` | C | Ondelettes sur graphes |
| `gudhi` ou `giotto-tda` | E | Homologie persistante |
| `POT` | D | Optimal transport (Gromov-Wasserstein) |

### Format des données JSON

**g1_results.json :** Liste de 356 objets :
```json
{
  "name": "erdos_renyi",
  "params": {"n": 50, "p": 0.01},
  "n": 50, "m": 15, "density": 0.012,
  "deg_mean": 0.6, "deg_std": 0.63, "deg_min": 0, "deg_max": 2,
  "clustering_avg": 0.0, "avg_shortest_path": 1.67, "diameter": 3,
  "spectral_radius": ..., "algebraic_connectivity": ...,
  ...
}
```

**g2_trajectories.json :** Trajectoires de déformation par graphe × type × niveau.

**g3_results.json :** Courbes de percolation (fraction supprimée → taille LCC, SLC, nb composantes).

**g6_results.json :**
```json
{
  "graphs": [{"name": "star_5", "N": 5, "S_norm": 0.8277, "rho_k": 2.236}, ...],
  "destruction": [{"base": "ER_100", "frac": 0.95, "N": 5, "S_norm": 0.759}, ...]
}
```

---

## 7. Principes de travail OBLIGATOIRES

### Pour l'utilisateur (Djdk)

1. **Travail sérieux, rigoureux, sans approximations** — chaque résultat vérifiable et reproductible
2. **Vigilance maximale sur les formules** — vérifier chaque formule, croiser les résultats
3. **Étape par étape** — génération → transformation → mesure → analyse → falsification
4. **Penser comme une machine** — exploration exhaustive, pas de biais théorique
5. **Couverture maximale** — tester même les pistes improbables
6. **Falsifier dès que possible** — pas attendre la fin
7. **Objectif : lois structurelles fortes** — invariants, seuils universels, mécanismes fondamentaux
8. **Ne pas créer de fichiers de rapport** — présenter les résultats dans la conversation
9. **Compresser et sauvegarder** dans `/agent/home/` et sur le repo GitHub

### Leçons du travail précédent

- **NE PAS surinterpréter** — tester contre le null le plus simple
- **NE PAS mesurer que des métriques connues** — inventer des observables
- **FALSIFIER au fur et à mesure** — pas à la fin
- **Le test de trivialité est OBLIGATOIRE** — comparer avec une matrice aléatoire ou un graphe aléatoire de mêmes paramètres
- **Documenter honnêtement** — les échecs sont aussi précieux que les succès

### Contexte historique (Riemann)

Si le prochain agent a besoin de contexte sur le travail Riemann :
- Archive complète : `/agent/home/Maths-Riemann-Research.tar.gz` (8.7 MB)
- Repo : https://github.com/aciderix/Maths-Riemann-Research
- Phases 15-18 : `/agent/home/phase15/`, `phase16/`, `phase17/`, `/agent/home/research/`
- Conclusion : toutes les routes par troncature sont fermées. α = 3/4 est un artefact.

---

## RÉSUMÉ EXÉCUTIF

**Où on en est :** 6 phases d'exploration systématique, 356 graphes, 21 familles, 31 métriques, 6 lois candidates — toutes cassées ou connues après falsification.

**Ce qui reste :** La cartographie est solide mais les métriques classiques sont épuisées. Le prochain pas est d'**inventer de nouvelles observables** (courbure de Ricci, entropie de Von Neumann, réponse dynamique, TDA, compression) et de les tester sur le même dataset.

**Le signal le plus prometteur :** La piste F (métriques de réponse dynamique) est la plus riche car elle transforme le graphe de statique à dynamique — c'est là que les transitions de phase vraiment nouvelles peuvent émerger.

**L'objectif ultime :** Trouver un invariant ou une loi qui (a) est NON TRIVIAL, (b) SURVIT à la falsification, (c) n'est PAS dans la littérature, et (d) a une EXPLICATION théorique.

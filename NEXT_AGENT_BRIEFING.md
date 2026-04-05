# BRIEFING COMPLET — Projet Exploration Computationnelle

## Destinataire : Prochain agent de travail

**Date :** 5 avril 2026
**Auteur :** Agent précédent (Tasklet)
**Repo GitHub :** https://github.com/aciderix/Graph-Systems-Exploration
**Token GitHub :** `[TOKEN_REMOVED]`

---

## RÉSUMÉ EN 30 SECONDES

Ce projet a deux phases historiques (résultats négatifs de haute qualité) et trois nouvelles directions de recherche.

**Phase Riemann (terminée) :** 18 phases sur la fonction zêta → toutes les routes par troncature fermées, α=3/4 = artefact Dickman.

**Phase Graphes (terminée) :** 16 phases, ~250 000 calculs, 114 métriques, 14 opérations → **0 loi fondamentalement nouvelle**. L'espace des lois algébriques simples sur les graphes finis est saturé.

**Nouvelles directions (à explorer) :**
1. 🥇 **Semigroupes numériques** — `numerical_semigroups/`
2. 🥈 **Groupes critiques (sandpile)** — `sandpile_groups/`
3. 🥉 **Invariants de nœuds** — `knot_invariants/`

---

## RÈGLES DE COMPORTEMENT — OBLIGATOIRES

### Philosophie
> Se comporter comme un système exploratoire cherchant à cartographier un espace inconnu — PAS comme un mathématicien cherchant une preuve.

- Explorer des chemins **inconnus, inattendus, contre-intuitifs**
- Penser comme une **machine**, pas comme un humain
- **Résultats dans le chat**, pas dans des fichiers de rapport (sauf très longs contenus)
- Ne pas se comporter comme un cheerleader — **attaquer chaque résultat positif immédiatement**
- **Falsifier systématiquement** et immédiatement
- Documenter les échecs aussi clairement que les succès
- Ne pas écouter aveuglément les suggestions d'autres LLMs
- **Copier en `/tmp/` avant les opérations lourdes** (FUSE mount `/agent/` est lent)
- Utiliser **pur numpy** (sklearn ne compile pas sur Alpine)

### 11 règles de falsification OBLIGATOIRES
1. **Baseline linéaire** avant toute méthode sophistiquée
2. **Objets frais** (non vus) pour toute validation
3. **Filtrage des tautologies** (identités algébriques triviales)
4. **Test de trivialité** (comparaison avec objets aléatoires)
5. **Vérification littérature** avant toute claim d'originalité
6. **Complexité minimale** : si une explication simple existe, la préférer
7. **Varier les paramètres** pour toute claim d'universalité
8. **Varier la méthode de mesure** pour toute métrique basée sur un algorithme
9. **Décomposer le résultat** en ses composantes avant de conclure
10. **Test null model** : si un modèle nul donne le même résultat, c'est artefactuel
11. **Vérifier contre le CLT/U-statistics** pour tout scaling law faible

---

## CONTEXTE : POURQUOI CES 3 DIRECTIONS ?

### Le diagnostic
| Projet précédent | Problème | Leçon |
|---|---|---|
| Riemann | Trop **dur** — patterns à échelle calculable connus depuis 150 ans | Ne pas attaquer des problèmes où le calcul ne peut pas atteindre les échelles utiles |
| Graphes | Trop **saturé** — l'espace est dominé par spectre + degrés | Ne pas attaquer des espaces théoriquement clos |

### Le sweet spot
La méthode (générer → mesurer → patterns → falsifier) nécessite :
> **Un domaine où la théorie est INCOMPLÈTE mais les objets sont CALCULABLES.**

### Analyse critique des suggestions LLM externes (session précédente)
- **Gemini** proposait pseudospectres, sheaf Laplacians, marches quantiques → des domaines existants habillés en "ruptures"
- **ChatGPT** proposait Kolmogorov structurelle → incalculable (théorème de Rice), artefactuel en pratique
- Les deux font la même erreur : "changer l'objet suffit" — mais le projet graphes a montré que chaque enrichissement converge vers le connu **si le domaine est théoriquement saturé**

---

## 🥇 DIRECTION 1 : SEMIGROUPES NUMÉRIQUES

**Répertoire :** `numerical_semigroups/`
**Priorité :** HAUTE — meilleur rapport effort/chance de résultat

### Qu'est-ce que c'est ?
Un semigroupe numérique S est un sous-ensemble de ℕ contenant 0, fermé par addition, avec un nombre fini de trous.

### Pourquoi c'est le bon choix
| Critère | Score |
|---|---|
| Objets calculables | ✅ Tous les semigroupes par genus jusqu'à g≈60-70 |
| Théorie incomplète | ✅ **Conjecture de Wilf (1978) OUVERTE** |
| Invariants non-saturés | ✅ ~30 invariants, relations pas toutes connues |
| Conjecturation automatique faite ? | ❌ **NON** — Graffiti/AGX n'ont pas touché ce domaine |
| FunSearch/AlphaEvolve ? | ❌ NON — pas de compétition DeepMind |
| Publiable | ✅ Experimental Mathematics, Semigroup Forum |

### Cible principale : Conjecture de Wilf
**Énoncé :** W(S) = e(S)·l(S) − c(S) ≥ 0 pour tout semigroupe numérique S.
- e(S) = embedding dimension, l(S) = left elements, c(S) = conductor
- Vérifiée jusqu'à genus ~60, pas prouvée
- **Un contre-exemple serait une publication majeure**
- Même sans contre-exemple : nouvelles inégalités entre invariants = publiable

### Plan
1. **N1 :** Énumérer par genus (g=1 à 50+), calculer ~25 invariants → `data/n1_results.json`
2. **N2 :** Scan systématique : corrélations, inégalités candidates, identités
3. **N3 :** Falsification sur genus supérieurs + littérature
4. **N4 :** Formalisation des conjectures survivantes

### Script de démarrage
`phases/N1_enumerate.py` — énumération par arbre + calcul d'invariants. **Tester d'abord sur genus 15 pour vérifier contre OEIS A007323.**

### Bibliographie essentielle
- Rosales & García-Sánchez (2009). *Numerical Semigroups*. Springer.
- Kaplan (2017). "Counting numerical semigroups by genus and some cases of Wilf."
- Fromentin & Hivert (2016). "Exploring the tree of numerical semigroups."
- Bras-Amorós (2008). "Fibonacci-like behavior of the number of numerical semigroups of a given genus."
- Delgado & García-Sánchez (2016). *numericalsgps* — GAP package.

### Dépendances
```
numpy
# Optionnel : gap-system pour vérification croisée
```

---

## 🥈 DIRECTION 2 : GROUPES CRITIQUES (SANDPILE)

**Répertoire :** `sandpile_groups/`
**Priorité :** MOYENNE — réutilise l'infrastructure graphes, accède à l'info non-spectrale

### Qu'est-ce que c'est ?
Le groupe critique K(G) d'un graphe G est un groupe abélien fini calculé via la Smith Normal Form du Laplacien. Son ordre = nombre d'arbres couvrants, mais sa **structure de groupe** (facteurs invariants) contient de l'information **non-spectrale**.

### Pourquoi c'est pertinent
- C'est littéralement l'information non-spectrale que le projet graphes cherchait
- Les eigenvalues réelles du Laplacien → déterminant = |K(G)|
- Mais la décomposition en facteurs invariants (divisibilité entière) n'est PAS dans le spectre
- **Réutilise les 356 graphes de G1** et les 7 paires cospectrales de G10

### Problèmes ouverts ciblés
1. **Pour quels graphes K(G) est cyclique ?** → pas de caractérisation générale
2. **K(grille n×m) ?** → inconnu en général
3. **Distribution de K(G) pour graphes aléatoires** → conjectures de Melanie Wood (2017+)

### Plan
1. **S1 :** Calculer SNF + facteurs invariants pour les 356 graphes de G1
2. **S2 :** Comparer les graphes cospectraux de G10 — la SNF les sépare-t-elle ?
3. **S3 :** Scan systématique : relations entre invariants du sandpile group et du graphe
4. **S4 :** Grilles n×m : patterns dans les facteurs

### Script de démarrage
`phases/S1_smith_normal_form.py` — framework SNF + calcul d'invariants. Démo incluse avec K4, C5, K3,3.

### ⚠️ Attention technique
La SNF nécessite de l'arithmétique entière exacte. Utiliser `sympy.matrices.normalforms` ou l'implémentation custom fournie (pas numpy float).

### Bibliographie
- Biggs (1999). "Chip-firing and the critical group of a graph."
- Wood (2017). "The distribution of sandpile groups of random graphs."
- Corry & Perkinson (2018). *Divisors and Sandpiles*. AMS.
- Stanley (2016). "Smith normal form in combinatorics."

### Dépendances
```
networkx
numpy
sympy  # Pour SNF exacte
```

---

## 🥉 DIRECTION 3 : INVARIANTS DE NŒUDS

**Répertoire :** `knot_invariants/`
**Priorité :** EXPLORATOIRE — plus riche mais plus dur

### Qu'est-ce que c'est ?
Les nœuds mathématiques (plongements de S¹ dans ℝ³) ont des dizaines d'invariants de types très différents (polynomiaux, géométriques, homologiques). Contrairement aux graphes, **aucun invariant unique ne domine**.

### Pourquoi c'est intéressant
- Espace d'invariants RICHE et NON saturé par un seul
- Question à un million de dollars : le Jones polynomial détecte-t-il l'unknot ?
- Base KnotInfo : ~13 000 nœuds × ~80 invariants pré-calculés
- DeepMind (2021, Nature) a montré que le ML trouve des relations sur les nœuds → mais la falsification systématique n'a pas été faite

### Plan
1. **K1 :** Acquérir les données KnotInfo (package Python `knotinfo` ou scraping)
2. **K2 :** Scan systématique : PCA, corrélations, le spectre domine-t-il ici ?
3. **K3 :** Recherche de lois : inégalités, identités sur les évaluations polynomiales
4. **K4 :** Falsification + littérature

### Script de démarrage
`phases/K1_acquire_data.py` — acquisition de données (stub + instructions pour package complet)

### ⚠️ Risques
- Courbe d'apprentissage en topologie
- Certains invariants (Khovanov) sont exponentiels à calculer
- Les relations "faciles" entre invariants classiques sont peut-être déjà connues

### Dépendances
```
knotinfo    # Package Python pour la base de données
snappy      # Volume hyperbolique (optionnel)
numpy
```

---

## HISTORIQUE DU PROJET GRAPHES (pour référence)

### Résumé exécutif
16 phases, ~250K calculs, 0 loi nouvelle. L'espace des graphes finis est saturé par le spectre + degrés.

### Les 5 méta-résultats
1. Lois exactes simples = spectrales = connues
2. L'espace non-spectral est prédictible mais sans lois exactes
3. Le spectre est une hiérarchie : Adjacence < Laplacien < normalisé < signless
4. La compression ne produit pas de loi intrinsèque (dépend de l'algo à 66%)
5. Toute direction post-spectrale converge vers de la théorie existante

### 14 impasses confirmées
Métriques non-standard, algo génétique, PCA, régression symbolique, hypergraphes naïfs, compression naïve, half_life_frac (≈avg_degree), graphes pondérés (Anderson 1958), familles paramétriques (0 universalité), morphismes fonctoriels (trivial), complexité algo (Markov theory), graphons/α (CLT), IPR skew scaling (artefact densité), compression gap scaling (artefact algo+densité).

### Données disponibles
| Fichier | Contenu |
|---|---|
| `data/g1_results.json` | 356 graphes × 31 métriques |
| `data/g2_trajectories.json` | Trajectoires de déformation |
| `data/g3_results.json` | Courbes de percolation |
| `data/g6_results.json` | 68 graphes extrêmes |
| `data/g7_*.json` | 83 nouvelles métriques |
| `data/g8_*.json` | Résultats G8 |
| `data/g9_conservation_laws.json` | 8 lois de conservation |
| `data/g10_*.json` | Spectral gap + ops exotiques |
| `data/g11_transformation_laws.json` | 6 lois de transformation |

### Scripts
Dans `phases/G1/` à `phases/G9/`. Autonomes et reproductibles.

---

## HISTORIQUE DU PROJET RIEMANN (pour référence)

- 18 phases sur la fonction zêta et les produits d'Euler tronqués
- Résultat : toutes les routes par troncature fermées, α = 3/4 = artefact Dickman
- Archive : `/agent/home/Maths-Riemann-Research.tar.gz`
- Repo : https://github.com/aciderix/Maths-Riemann-Research

---

## STACK TECHNIQUE

| Outil | Usage |
|---|---|
| Python 3.12 | Langage principal |
| NetworkX ≥ 3.0 | Graphes (direction 2 principalement) |
| NumPy ≥ 1.24 | Algèbre linéaire |
| SciPy ≥ 1.10 | Eigenvalues, stats |
| SymPy | Smith Normal Form exacte (direction 2) |

**⚠️ scikit-learn ne compile PAS sur Alpine Linux.** Préférer pur numpy.
**⚠️ Copier en /tmp/ avant les opérations lourdes** (FUSE mount /agent/ est lent).
**⚠️ Ne pas recalculer ce qui existe dans les JSON** — ne régénérer que pour du NOUVEAU.

---

## UTILISATEUR

- Pseudonyme : Wkwk / Karim
- Email : tipovi1368@availors.com
- Attentes : exploration de chemins **inconnus, inattendus, contre-intuitifs**
- Exigence : résultats dans le chat, pas de cheerleading, falsification immédiate
- A consulté d'autres LLMs (ChatGPT, Gemini) — leurs suggestions doivent être filtrées avec la même rigueur

---

## RECOMMANDATION DE DÉMARRAGE

**Commencer par les semigroupes numériques (Direction 1).** C'est le territoire le plus vierge avec le meilleur rapport effort/chance de résultat. Le script N1 est prêt à tourner.

Séquence recommandée :
1. Lancer `N1_enumerate.py` avec genus=15 pour vérifier (devrait matcher OEIS A007323)
2. Monter à genus=40-50 (quelques minutes de calcul)
3. Scanner les invariants pour des patterns
4. Falsifier immédiatement tout candidat

Si les semigroupes s'avèrent aussi saturés → passer aux sandpile groups (Direction 2), qui réutilise l'infrastructure graphes existante.

Les nœuds (Direction 3) sont le backup le plus riche mais le plus coûteux en apprentissage.

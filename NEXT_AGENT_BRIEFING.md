# BRIEFING COMPLET — Projet Graph Systems Exploration

## Destinataire : Prochain agent de travail

**Date :** 5 avril 2025 (mis à jour avril 2026)
**Auteur :** Agent précédent (Tasklet)
**Repo GitHub :** https://github.com/aciderix/Graph-Systems-Exploration

---

## RÉSUMÉ EN 30 SECONDES

11 phases d'exploration computationnelle sur les graphes finis. ~200 000 calculs. 114 métriques (31 standard + 83 non-standard). 14 opérations de transformation. Lois de conservation ET de transformation cherchées. Falsification systématique à chaque étape. **Résultat : 0 loi fondamentalement nouvelle.** L'espace des lois algébriques simples sur les graphes finis est saturé.

---

## PHILOSOPHIE OBLIGATOIRE

> **Se comporter comme un système exploratoire cherchant à cartographier un espace inconnu — PAS comme un mathématicien cherchant une preuve.**

- Penser comme une machine, pas comme un humain
- Couverture maximale — tester même les pistes improbables
- Refuser les explications faciles
- Falsifier systématiquement — une loi n'est intéressante que si elle survit à la destruction
- Documenter les échecs aussi clairement que les succès
- **Ne pas créer de fichiers de rapport** — afficher les résultats dans le chat
- **Vérifier l'inédit de chaque claim** avant de l'exploiter

---

## CE QUI A ÉTÉ FAIT (G1→G11)

### Tableau synthétique

| Phase | Quoi | Volume | Verdict |
|---|---|---|---|
| G1 | 356 graphes, 21 familles, 31 métriques | 11 036 mesures | Base de données |
| G2 | 5 déformations × 13 niveaux × 12 graphes | ~780 trajectoires | Transitions connues |
| G3 | Percolation fine (3 modes × 14 graphes) | ~4 200 points | Standard |
| G4 | Combinaisons algébriques + PCA | ~50 000 combos | Rien de nouveau |
| G5 | Validation croisée 6 lois | 6 candidats | — |
| G6 | Falsification : 68 graphes extrêmes | 24 scénarios | **6/6 cassées ou connues** |
| G7 | 83 nouvelles métriques non-standard | 29 548 mesures | 3 survivantes → frameworks connus |
| G8.5 | Stabilité spec_complexity_per_node | — | **CASSÉ** (star/complete) |
| G8.6 | Transition betti0_mean_persistence | — | **PAS de transition propre** |
| G8.7 | 4 processus dynamiques | 30 graphes × 4 | Kuramoto r=0.955 avec spectre → **CONNU** |
| G8.8 | ML classifier | 27 vs 83 features | Standard écrase (72% vs 47%) |
| G9 | Lois de conservation (SVD null-space) | 91 graphes × 8 ops × 29 métriques | **8 lois réelles mais dérivables** |
| G10 | Faille spectrale + ops exotiques | 80 graphes × 6 ops × 24 métriques | **0 loi non-spectrale** |
| G11 | Lois de transformation (régression) | 64 graphes × 7 ops × 14 cibles | **6 survivantes, triviales ou approx** |

### Les 3 méta-résultats

1. **Les lois exactes simples = spectrales = connues** (G1-G9)
2. **L'espace non-spectral est prédictible mais sans lois exactes** (G10-G11)
3. **Le spectre est une hiérarchie** : adjacence < Laplacien < normalisé < signless (G10)

---

## CE QUI A ÉCHOUÉ — LEÇONS CRITIQUES

### Erreurs commises (à NE PAS répéter)

| Erreur | Phase | Leçon |
|---|---|---|
| Mesurer des métriques standard | G1-G5 | Résultats connus garantis |
| Falsifier trop tard | G1-G5 → G6 | Falsifier **immédiatement** à chaque découverte |
| Ne pas tester contre le null stupide | G1 (LOI 1) | L'entropie spectrale = 70% artefact de concentration |
| Surinterpréter les corrélations | G8.7 | Kuramoto r=0.955 → médiatisé par le spectral gap |
| Recalculer les JSON existants | G11 | Les JSON contiennent les métriques ; ne régénérer que si calcul NOUVEAU |
| Écouter aveuglément les suggestions d'autres LLMs | G11 | Régression symbolique = marginal sur la linéaire |
| Utiliser sklearn sur Alpine | G11 | Ne compile pas ; préférer pur numpy |

### Règles de falsification OBLIGATOIRES

1. **Baseline linéaire** avant toute méthode sophistiquée
2. **Graphes frais** (non vus) pour toute validation
3. **Filtrage des tautologies** (deg_sum=2m, trace identities, etc.)
4. **Test de trivialité** (comparaison avec graphes/matrices aléatoires)
5. **Vérification littérature** avant toute claim d'originalité
6. **Complexité minimale** : si une explication simple existe, la préférer

---

## DONNÉES DISPONIBLES

### Fichiers JSON (dans data/)

| Fichier | Contenu | Taille |
|---|---|---|
| g1_results.json | 356 graphes × 31 métriques | 349 KB |
| g2_trajectories.json | Trajectoires de déformation | 314 KB |
| g3_results.json | Courbes de percolation | 263 KB |
| g6_results.json | 68 graphes extrêmes | — |
| g7_*.json | 83 nouvelles métriques sur 356 graphes | — |
| g8_*.json | Résultats G8.5-G8.8 | — |
| g9_conservation_laws.json | 8 lois de conservation | — |
| g10_spectral_gap.json | 7 paires cospectrales | — |
| g10_exotic_ops.json | 6 ops exotiques × 80 graphes | — |
| g11_transformation_laws.json | 6 lois de transformation | — |

### Format type (g1_results.json)

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

### Scripts (dans phases/)

Chaque phase a ses scripts Python dans `phases/Gx/`. Ils sont autonomes et reproductibles.

---

## PISTES FUTURES — ÉVALUATION HONNÊTE

### ❌ DEAD ENDS (NE PAS RETENTER)

| Piste | Raison |
|---|---|
| Plus de métriques sur graphes finis statiques | Espace spectral saturé |
| Algorithme génétique de métriques | Combine des quantités spectrales → espace fermé |
| PCA / réduction dimensionnelle | Fait en G4, résultat connu |
| Régression symbolique plus profonde | Gain marginal sur linéaire (G11) |
| Hypergraphes naïvement | Même piège G1-G11 sur objet différent |

### ⚠️ PISTES VIABLES (avec réserves)

#### A. Lois de scaling (n → ∞)
- Chercher des **exposants** (F(G_n) ∝ n^α) au lieu d'invariants
- Beaucoup d'exposants connus → vérifier littérature d'abord
- Faisable computationnellement

#### B. Graphes pondérés continus
- Les poids brisent les symétries spectrales
- Espace de recherche plus grand → risque de surapprentissage
- Besoin de contraintes claires sur les poids

#### C. Transitions de phase sous contraintes
- Fixer une propriété, faire varier une autre
- Domaine actif (seuil k-SAT, etc.)
- Computationnellement coûteux

#### D. Opérations sans théorie spectrale connue
- Rewiring conditionnel, contraction par métrique, évolution stochastique
- Si trop stochastique → bruit → pas de loi exacte

#### E. Changer le TYPE de question
- Information-théorique : compression optimale des graphes
- Algorithmique : complexité des invariants
- Catégorique : foncteurs préservant la structure

---

## STACK TECHNIQUE

| Outil | Usage |
|---|---|
| Python 3.12 | Langage principal |
| NetworkX ≥ 3.0 | Graphes |
| NumPy ≥ 1.24 | Algèbre linéaire |
| SciPy ≥ 1.10 | Eigenvalues, stats |

**⚠️ scikit-learn ne compile pas toujours sur Alpine Linux.** Préférer pur numpy.
**⚠️ Copier en /tmp/ avant les opérations lourdes** (git, gros I/O) — le FUSE mount de /agent/ est lent.

---

## CONTEXTE HISTORIQUE

### Projet Riemann (précédent)
- 18 phases sur la fonction zêta et les produits d'Euler tronqués
- Résultat : toutes les routes par troncature fermées, α = 3/4 = artefact Dickman
- Archive : `/agent/home/Maths-Riemann-Research.tar.gz`
- Repo : https://github.com/aciderix/Maths-Riemann-Research

### Utilisateur
- Pseudonyme : Djdn / Karim
- Email : tedimat142@availors.com
- Attentes : exploration de chemins **inconnus, inattendus, contre-intuitifs**
- Exigence : ne pas penser comme un humain mais comme une machine
- A consulté d'autres LLMs (ChatGPT) pendant le projet — leurs suggestions doivent être filtrées avec la même rigueur que les nôtres

---

## RÉSUMÉ EXÉCUTIF FINAL

**Où on en est :** 11 phases, ~200K calculs, 0 loi nouvelle. L'espace des graphes finis statiques est un espace clos.

**Ce qui a de la valeur :** Le pipeline de falsification lui-même (méthodologie) + la démonstration empirique de la saturation spectrale.

**Pour trouver quelque chose de nouveau :** Il faut changer l'OBJET (pas la méthode) ou changer le TYPE de question (pas juste "quelle métrique sur quel graphe").

**L'objectif reste :** Un invariant ou une loi qui est (1) non trivial, (2) résistant à la falsification, (3) absent de la littérature, (4) théoriquement explicable.

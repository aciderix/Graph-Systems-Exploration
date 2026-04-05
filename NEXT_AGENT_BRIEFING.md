# BRIEFING COMPLET — Projet Graph Systems Exploration

## Destinataire : Prochain agent de travail

**Date :** 5 avril 2025 (mis à jour avril 2026)
**Auteur :** Agent précédent (Tasklet)
**Repo GitHub :** https://github.com/aciderix/Graph-Systems-Exploration

---

## RÉSUMÉ EN 30 SECONDES

16 phases d'exploration computationnelle sur les graphes finis. ~250 000 calculs. 114 métriques (31 standard + 83 non-standard). 14 opérations de transformation. Lois de conservation ET de transformation cherchées. Puis 5 phases post-spectrales : compression, eigenvectors, trajectoires, graphes pondérés, familles paramétriques, morphismes, complexité computationnelle, graphons. Falsification systématique à chaque étape. **Résultat : 0 loi fondamentalement nouvelle.** L'espace des lois algébriques simples sur les graphes finis est saturé — y compris dans les directions post-spectrales.

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
| G12 | 3 propositions post-spectrales | Eigenvectors + compression + trajectoires | Compression gap seul candidat viable |
| G13 | Approfondissement 4 fronts | IPR skew + gap + hlf + pondérés | IPR instable, hlf trivial (R²=0.87 avg_deg), Anderson 1958 |
| G14 | Compression gap deep dive | Scaling + fonctionnel + falsification + cross | Gap = outil descriptif, scaling = mirage |
| G15 | Test critique universalité b | b vs ⟨k⟩, algo, décomposition | **b dépend de ⟨k⟩ (R²=0.92), algo (66% spread), et convergence spectrale** |
| G16 | 4 pivots radicaux | Paramétrique + morphismes + complexité + graphons | **Tout converge vers le connu** |

### Les 5 méta-résultats

1. **Les lois exactes simples = spectrales = connues** (G1-G9)
2. **L'espace non-spectral est prédictible mais sans lois exactes** (G10-G11)
3. **Le spectre est une hiérarchie** : adjacence < Laplacien < normalisé < signless (G10)
4. **La compression ne produit pas de loi intrinsèque** — dépend de l'algorithme et du degré moyen (G12-G15)
5. **L'exploration post-spectrale converge aussi vers le connu** — familles paramétriques, morphismes, complexité computationnelle et graphons retombent tous sur de la théorie existante (G16)

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
| Croire à l'universalité sans varier les paramètres | G15 | b≈−0.026 "universel" → dépend de ⟨k⟩ (R²=0.92). Toujours tester sur ⟨k⟩ variés |
| Utiliser la compression comme métrique intrinsèque | G15 | Le résultat change de 66% entre zlib/bzip2/lzma. Pas intrinsèque au graphe |
| Confondre "sépare les familles" et "nouveau" | G13 | half_life sépare bien mais R²=0.87 avec avg_degree = trivial |
| Chercher des invariants fonctoriels par force brute | G16 | Seuls les invariants triviaux sont préservés (max_deg sous subdivision) |
| Croire que le CLT n'explique pas les scaling laws | G16 | α(clustering)/α(transitivity)≈1.0 = conséquence triviale du CLT (Janson 2004) |

### Règles de falsification OBLIGATOIRES

1. **Baseline linéaire** avant toute méthode sophistiquée
2. **Graphes frais** (non vus) pour toute validation
3. **Filtrage des tautologies** (deg_sum=2m, trace identities, etc.)
4. **Test de trivialité** (comparaison avec graphes/matrices aléatoires)
5. **Vérification littérature** avant toute claim d'originalité
6. **Complexité minimale** : si une explication simple existe, la préférer
7. **Varier les paramètres de famille** (⟨k⟩, p, m) pour toute claim d'universalité
8. **Varier la méthode de mesure** (algo de compression, encodage, discrétisation) pour toute métrique basée sur un algorithme
9. **Décomposer le résultat** en ses composantes avant de conclure (ex: gap = adj_slope − spec_slope)
10. **Test config_model** : si config_model(même degré seq) donne le même résultat, c'est la distribution de degrés qui drive, pas la topologie fine
11. **Vérifier contre le CLT/U-statistics** pour tout scaling law faible

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

| Piste | Raison | Prouvé en |
|---|---|---|
| Plus de métriques sur graphes finis statiques | Espace spectral saturé | G1-G11 |
| Algorithme génétique de métriques | Combine des quantités spectrales → espace fermé | G4, G7 |
| PCA / réduction dimensionnelle | Fait en G4, résultat connu | G4 |
| Régression symbolique plus profonde | Gain marginal sur linéaire | G11 |
| Hypergraphes naïvement | Même piège G1-G11 sur objet différent | — |
| **Compression comme invariant/loi** | Dépend de l'algo (66% spread zlib/bzip2/lzma), pas intrinsèque | **G15** |
| **IPR skew scaling** | CV=0.56–1.46, trop instable ; littérature (Pastor-Satorras 2016) | **G12-G13** |
| **Half_life_frac** | R²=0.87 avec avg_degree, trivial | **G13** |
| **Graphes pondérés (poids aléatoires)** | Localisation d'Anderson (1958), ultra-connu | **G13** |
| **Scaling laws via compression** | ln(n) = convergence spectrale ; b dépend de ⟨k⟩ | **G14-G15** |
| **Morphismes fonctoriels** | Seuls les invariants triviaux (max_deg sous subdivision) sont préservés | **G16** |
| **Familles paramétriques metric(p)** | Transitions = seuils de connectivité connus, 0/13 universalité | **G16** |
| **Exposants de fluctuation α / ratios** | CLT pour U-statistiques (Janson 2004), trivial | **G16** |
| **Complexité computationnelle comme invariant** | Signal existe mais = Markov chain theory (Levin, Peres & Wilmer 2009) | **G16** |

### ⚠️ PISTES VIABLES (après filtrage G12-G16)

> **Note :** Les pistes A (scaling), B (pondérés), C (transitions) et D (opérations) de la version précédente ont été explorées et fermées en G12-G16. Restent 3 directions, toutes nécessitant un changement de paradigme.

#### 1. Preuves formelles guidées par le numérique
- Utiliser les ~250K calculs comme guide pour formuler et **prouver** des théorèmes
- Exemple : prouver que le compression gap est borné inférieurement par f(distribution de degrés)
- Risque : nécessite des compétences mathématiques, pas du calcul brut

#### 2. Graphes réels (réseaux biologiques, sociaux, technologiques)
- Les modèles théoriques (ER, BA, WS) sont des approximations trop propres
- Les vrais réseaux ont motifs, hiérarchies, corrélations temporelles
- Risque : overfitting sur datasets spécifiques, difficulté de généralisation

#### 3. Information quantique sur graphes
- Marches quantiques, intrication dans les graphes d'états, quantum entanglement entropy
- Les interférences quantiques produisent des invariants inaccessibles à la théorie classique
- Risque : domaine actif, bien publié — la Von Neumann entropy classique est déjà testée (G7, redondante)

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

**Où on en est :** 16 phases, ~250K calculs, 0 loi nouvelle. L'espace des graphes finis statiques est un espace clos — **y compris dans les directions post-spectrales** (compression, complexité, graphons, morphismes).

**Ce qui a de la valeur :** Le pipeline de falsification lui-même (méthodologie) + la démonstration empirique de la saturation spectrale + la démonstration que les approches post-spectrales convergent aussi vers le connu.

**Ce qui reste :** Preuves formelles guidées par les données, graphes réels, ou information quantique. Toutes requièrent un changement de paradigme — pas plus de calcul brut.

**L'objectif reste :** Un invariant ou une loi qui est (1) non trivial, (2) résistant à la falsification, (3) absent de la littérature, (4) théoriquement explicable.

**Le théorème empirique renforcé :**
> Sur les graphes finis, les lois algébriques simples vivent dans l'espace spectral et sont connues. L'espace post-spectral (compression, complexité, convergence, morphismes) est prédictible mais ne contient pas de lois exactes simples inconnues. Pour trouver du nouveau, il faut soit changer l'objet (graphes réels, quantiques), soit passer aux preuves formelles.

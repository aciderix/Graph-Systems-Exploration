# Semigroupes Numériques — Exploration Computationnelle

## Qu'est-ce qu'un semigroupe numérique ?

Un **semigroupe numérique** S est un sous-ensemble de ℕ contenant 0, fermé par addition, avec un nombre fini de "trous" (gaps).

**Exemple :** S = ⟨3, 5, 7⟩ = {0, 3, 5, 6, 7, 8, 9, 10, …} — les trous sont {1, 2, 4}.

## Invariants principaux (~30 connus)

| Invariant | Définition | Calculable ? |
|---|---|---|
| **genus** g(S) | Nombre de gaps (entiers ∉ S) | ✅ O(F) |
| **Frobenius number** F(S) | Plus grand gap | ✅ O(F) |
| **multiplicity** m(S) | Plus petit élément non-nul | ✅ O(1) |
| **embedding dimension** e(S) | Nombre de générateurs minimaux | ✅ O(F) |
| **type** t(S) | Nombre de pseudo-Frobenius numbers | ✅ O(F) |
| **conductor** c(S) | F(S) + 1 | ✅ O(1) |
| **ratio** r(S) | ⌈F(S)/m(S)⌉ | ✅ O(1) |
| **Apéry set** Ap(S,m) | {w₀, w₁, ..., w_{m-1}} avec wᵢ = min{s∈S : s≡i mod m} | ✅ O(m²) |
| **delta set** Δ(S) | Distances consécutives entre longueurs de factorisation | ✅ |
| **catenary degree** c(S) | Distance max dans le graphe de factorisation | ✅ |
| **tame degree** | Variante de catenary pour certains éléments | ✅ |
| **elasticity** ρ(S) | max L(s) / min L(s) sur les factorisations | ✅ |
| **Betti numbers** | Rangs des modules de syzygies | ✅ |
| **Kunz coordinates** | Coordonnées dans le polyèdre de Kunz | ✅ |
| **Wilf number** W(S) | e(S)·l(S) − c(S), où l(S)=|S ∩ [0,c(S))| | ✅ |

## Conjectures ouvertes ciblées

### 1. Conjecture de Wilf (1978) — PRINCIPALE
**Énoncé :** Pour tout semigroupe numérique S, W(S) = e(S)·l(S) − c(S) ≥ 0.

- Vérifiée computationnellement jusqu'à genus ~60
- Prouvée pour e(S) ≤ 4, pour m(S) ≤ 2·e(S), et d'autres cas partiels
- **Pas de preuve générale, pas de contre-exemple**
- Un contre-exemple serait une publication majeure

### 2. Nouvelles inégalités entre invariants
- Appliquer une approche type Graffiti/AGX (jamais fait systématiquement)
- Chercher des relations f(g, F, m, e, t, ...) ≥ 0 ou = 0

### 3. Structure du graphe de Kunz
- Les semigroupes de multiplicity m correspondent aux points entiers d'un cône
- Relations entre la géométrie du cône et les invariants : peu explorées

### 4. Asymptotique
- Proportion de semigroupes de genus g satisfaisant une propriété P quand g → ∞
- Beaucoup de résultats partiels, peu de résultats exacts

## Plan d'attaque (phases)

### Phase N1 : Énumération + Invariants
- Énumérer tous les semigroupes numériques par genus (g=1 à g=50+)
- Calculer tous les invariants sur chacun
- Stocker en JSON dans data/

### Phase N2 : Scan systématique
- Chercher des corrélations, identités, inégalités entre invariants
- Baseline : modèles linéaires et quadratiques
- Tester les inégalités connues + chercher des nouvelles

### Phase N3 : Falsification
- Chaque candidat-loi testé sur genus supérieurs (non vus)
- Vérification littérature immédiate
- Test contre null model (semigroupe aléatoire uniforme)

### Phase N4 : Conjectures survivantes
- Formalisation
- Preuve ou contre-exemple

## Bibliographie de départ

- Wilf, H. (1978). "A circle-of-lights algorithm for the 'money-changing problem'."
- Rosales, J.C. & García-Sánchez, P.A. (2009). *Numerical Semigroups*. Springer.
- Kaplan, N. (2017). "Counting numerical semigroups by genus and some cases of a question of Wilf."
- Delgado, M., García-Sánchez, P.A. (2016). *numericalsgps* — GAP package.
- Fromentin, J. & Hivert, F. (2016). "Exploring the tree of numerical semigroups."
- Bras-Amorós, M. (2008). "Fibonacci-like behavior of the number of numerical semigroups of a given genus."

## Dépendances techniques

```
# Pas besoin de NetworkX ici — pur combinatoire
numpy
# Optional: gap (système de calcul algébrique) pour vérification
```

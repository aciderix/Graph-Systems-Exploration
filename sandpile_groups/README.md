# Sandpile Groups (Groupes Critiques) — Exploration Computationnelle

## Qu'est-ce que le groupe critique ?

Pour un graphe G connecté, le **groupe critique** (ou sandpile group, Jacobian, chip-firing group) K(G) est un groupe abélien fini dont l'ordre = nombre d'arbres couvrants (théorème de Kirchhoff).

**Calcul :** K(G) = facteurs invariants de la Smith Normal Form du Laplacien L(G), en supprimant le facteur 0.

**Exemple :** Pour le cycle C₅, L a SNF = diag(1,5,5,5,0), donc K(C₅) = ℤ₅ × ℤ₅ × ℤ₅ ≅ ℤ₅³. Non : en fait K(C₅) = ℤ₅ (un seul facteur non-trivial après réduction). L'important c'est que la structure de groupe va AU-DELÀ du spectre.

## Pourquoi c'est le bon objet ?

1. **C'est l'information non-spectrale formalisée** — Les eigenvalues réelles du Laplacien donnent le déterminant = |K(G)|, mais PAS la structure de groupe (facteurs invariants = divisibilité entière).
2. **Réutilise l'infrastructure graphes** existante du projet.
3. **Problèmes ouverts genuins** — pas de saturation théorique.

## Invariants à calculer

| Invariant | Définition | Lié au spectre ? |
|---|---|---|
| **|K(G)|** = spanning trees | det(L̃) (cofacteur du Laplacien) | ✅ Oui (Kirchhoff) |
| **Facteurs invariants** d₁ \| d₂ \| ... \| dₖ | Smith Normal Form | ❌ **NON** |
| **Rang** (nombre de facteurs) | dim du groupe | ❌ NON (sauf bornes) |
| **Cyclicité** (K(G) cyclique ?) | 1 seul facteur invariant | ❌ NON |
| **Plus grand facteur** dₖ | "période" du groupe | ❌ NON |
| **Exposant** exp(K(G)) | LCM des facteurs | ❌ NON |
| **p-rank** pour chaque premier p | dim_{F_p} K(G)/pK(G) | ❌ NON |
| **Entropie de la distribution des facteurs** | H = −Σ pᵢ log pᵢ | ❌ NON |
| **Sylow subgroup structure** | Décomposition en p-groupes | ❌ NON |

## Problèmes ouverts ciblés

### 1. Cyclicité — Pour quels graphes K(G) est cyclique ?
- Connu pour certaines familles (complets, roues, certains circulants)
- **Pas de caractérisation générale**
- Conjecture computationnelle possible

### 2. K(G) pour les grilles n×m
- Le groupe critique de la grille rectangulaire est **INCONNU** en général
- Résultats partiels pour n=2, n=3
- Attaquable par calcul direct pour petites grilles

### 3. Distribution de K(G) pour graphes aléatoires
- Melanie Wood (2017+) : conjectures sur la distribution des p-Sylow
- Analogie avec les corps de nombres (heuristique de Cohen-Lenstra)
- Des données computationnelles massives seraient utiles

### 4. Relations K(G) ↔ structure topologique
- Quelles propriétés du graphe contrôlent les facteurs invariants ?
- Le spectre ne suffit pas → qu'est-ce qui manque ?

## Plan d'attaque

### Phase S1 : Infrastructure
- Réutiliser les 356 graphes de G1 (21 familles)
- Calculer la SNF du Laplacien pour chacun → facteurs invariants
- Stocker en JSON avec tous les invariants du sandpile group

### Phase S2 : Comparaison spectre vs SNF
- Identifier les graphes cospectraux de G10
- Comparer leurs groupes critiques → la SNF les sépare-t-elle ?
- Quantifier : combien d'information non-spectrale dans les facteurs ?

### Phase S3 : Scan systématique
- Chercher des relations entre invariants du sandpile group et invariants du graphe
- Focus sur les relations qui NE PASSENT PAS par le spectre
- Falsification immédiate

### Phase S4 : Grilles et familles paramétriques
- Calculer K(grid(n,m)) pour n,m = 2..20
- Chercher des patterns dans les facteurs invariants
- Comparer avec les résultats partiels de la littérature

## Bibliographie de départ

- Lorenzini, D. (1991). "Arithmetical graphs."
- Bak, P., Tang, C. & Wiesenfeld, K. (1987). "Self-organized criticality." (sandpile original)
- Biggs, N. (1999). "Chip-firing and the critical group of a graph."
- Corry, S. & Perkinson, D. (2018). *Divisors and Sandpiles*. AMS.
- Wood, M.M. (2017). "The distribution of sandpile groups of random graphs."
- Stanley, R. (2016). "Smith normal form in combinatorics."

## Dépendances techniques

```
networkx   # Réutiliser l'infrastructure graphes existante
numpy      # Algèbre linéaire
scipy      # Smith Normal Form (via scipy.linalg ou implémentation custom)
sympy      # SNF exacte en entiers (sympy.matrices.normalforms)
```

**Note :** La SNF nécessite de l'arithmétique entière exacte. `numpy` travaille en float. Utiliser `sympy` pour la SNF exacte, ou implémenter l'algorithme sur les entiers.

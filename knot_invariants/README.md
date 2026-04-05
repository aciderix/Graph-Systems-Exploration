# Knot Invariants — Exploration Computationnelle

## Qu'est-ce qu'un nœud mathématique ?

Un **nœud** est un plongement du cercle S¹ dans ℝ³ (ou S³), considéré à isotopie ambiante près. Deux nœuds sont "les mêmes" si on peut déformer l'un en l'autre sans couper.

## Pourquoi les nœuds ?

1. **Espace d'invariants riche et NON dominé par un seul** — contrairement aux graphes, aucun invariant ne "capture tout"
2. **Questions ouvertes majeures** — Jones polynomial détecte-t-il l'unknot ? (million-dollar level)
3. **Base de données existante** — KnotInfo (~13 000 nœuds, ~80 invariants pré-calculés)
4. **Le pipeline mesurer → patterns → falsifier s'applique directement**

## Invariants principaux

| Invariant | Type | Calculable ? | Difficulté |
|---|---|---|---|
| **Crossing number** c(K) | Entier | ✅ (tabulé) | Facile |
| **Unknotting number** u(K) | Entier | ⚠️ (NP-hard en général) | Dur |
| **Bridge number** br(K) | Entier | ✅ | Moyen |
| **Braid index** | Entier | ✅ | Moyen |
| **Signature** σ(K) | Entier | ✅ | Facile |
| **Determinant** det(K) | Entier | ✅ | Facile |
| **Alexander polynomial** Δ(K) | Polynôme | ✅ | Facile |
| **Jones polynomial** V(K) | Polynôme Laurent | ✅ | O(2^n) théorique |
| **HOMFLY polynomial** P(K) | Polynôme 2-var | ✅ | Moyen-dur |
| **Khovanov homology** | Groupes gradués | ⚠️ | Dur (expo) |
| **Knot Floer homology** | Groupes | ⚠️ | Très dur |
| **Hyperbolic volume** vol(K) | Réel | ✅ (SnapPy) | Facile |
| **Genus** g(K) | Entier | ✅ | Moyen |
| **Slice genus** g₄(K) | Entier | ⚠️ | Dur |
| **Concordance invariants** (τ, s, ε) | Entiers | ⚠️ | Dur |
| **Thurston-Bennequin** tb(K) | Entier | ✅ | Moyen |

## Problèmes ouverts ciblés

### 1. Le polynôme de Jones détecte-t-il l'unknot ?
- **Conjecture :** Si V(K) = 1, alors K est le nœud trivial
- Pas de contre-exemple connu parmi les ~13 000 nœuds tabulés
- Une exploration systématique pourrait trouver des "presque contre-exemples" ou renforcer la conjecture

### 2. Relations inconnues entre invariants
- Le volume hyperbolique est-il déterminé par le Jones polynomial ? (Conjecture du volume)
- Quelles combinaisons d'invariants classiques déterminent un nœud ?
- Corrélations non-triviales entre invariants de type différent (polynomiaux vs géométriques)

### 3. Patterns dans les invariants de Khovanov
- L'homologie de Khovanov est STRICTEMENT plus forte que Jones
- La structure "extra" est-elle corrélée à des invariants géométriques ?

### 4. Machine learning pour la classification
- DeepMind a montré (2021) que le ML peut découvrir des relations entre invariants de nœuds
- Mais la falsification systématique n'a pas été faite

## Plan d'attaque

### Phase K1 : Acquisition des données
- Télécharger KnotInfo (https://www.indiana.edu/~knotinfo/)
- Parser la base de données (~13 000 nœuds, ~80 invariants)
- Stocker en JSON dans data/

### Phase K2 : Scan systématique
- Matrice de corrélation entre tous les invariants numériques
- PCA pour identifier les axes principaux
- Comparer avec la PCA des graphes (G4) — le spectre domine-t-il aussi ici ?

### Phase K3 : Recherche de lois
- Inégalités entre invariants (type Graffiti)
- Identités exactes sur les invariants polynomiaux évalués à des points spéciaux
- Relations entre invariants classiques et quantiques

### Phase K4 : Falsification
- Test sur nœuds non vus (crossings élevés)
- Comparaison avec nœuds virtuels / links
- Vérification littérature

## Outils techniques

| Outil | Usage |
|---|---|
| **KnotInfo** | Base de données (téléchargement direct) |
| **SnapPy** (Python) | Volume hyperbolique, invariants géométriques |
| **SageMath** | Polynômes de Jones/Alexander/HOMFLY, homologie |
| **regina** | 3-manifolds, genus |
| **numpy** | Analyse numérique |

## Bibliographie de départ

- Livingston, C. & Moore, A.H. "KnotInfo: Table of Knot Invariants." https://www.indiana.edu/~knotinfo/
- Jones, V.F.R. (1985). "A polynomial invariant for knots via von Neumann algebras."
- Khovanov, M. (2000). "A categorification of the Jones polynomial."
- Davies, A. et al. (2021). "Advancing mathematics by guiding human intuition with AI." Nature.
- Adams, C. (2004). *The Knot Book*. AMS.
- Cromwell, P. (2004). *Knots and Links*. Cambridge.

## Risques et limites

- **Courbe d'apprentissage** : la topologie des nœuds est plus abstraite que la théorie des graphes
- **Coût computationnel** : certains invariants (Khovanov, knot Floer) sont exponentiels
- **Saturation possible** : les relations "faciles" entre invariants classiques sont probablement connues
- **Avantage** : les invariants quantiques (Jones, HOMFLY, Khovanov) vivent dans un espace bien plus riche que le spectre des graphes — la saturation est moins probable

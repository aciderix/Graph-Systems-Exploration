# Rapport de lecture : positionnement du papier par rapport a la litterature existante

**Auteur du rapport** : Claude (agent 1 — preuves & integration)
**Date** : 2026-04-08
**Sources lues** :
- `refs/particular-cases.tex` — Delgado, *Conjecture of Wilf: A Survey* (arXiv:1902.03461, 2019)
- `refs/arXiv-1610.08726v1` — Dhayni, *Wilf's conjecture for numerical semigroups* (Palestine J. Math., 2018)
- `refs/arXiv-1703.01761v1` — Eliahou, *Wilf's conjecture and Macaulay's theorem* (JEMS, 2018)
- `refs/arXiv-1710.03623v1` — Eliahou & Fromentin, *Near-misses in Wilf's conjecture* (Semigroup Forum, 2018)
- `refs/wilfmultiplicity.tex` — Bruns, Garcia-Sanchez, O'Neill, *Wilf's conjecture in fixed multiplicity* (arXiv:1903.04342, 2020)

**Methode** : recherches ciblees par mots-cles (sharp, tight, attain, optimal, lower bound, W >= f(m), defect, m-e, m-nu) dans les sources TeX, lecture contextuelle des passages pertinents.

---

## 1. Etat de l'art : resultats d'existence (W >= 0)

### 1.1 Par deficit (= m - e dans notre notation)

| Reference | Resultat | Traduction (notre notation) |
|-----------|----------|-----------------------------|
| Dobbs & Matthews 2006 | MED => Wilf | d = 0 => W >= 0 |
| Sammartano 2012 [Th. 18] | 2e >= m => Wilf | d <= m/2 => W >= 0 |
| **Dhayni 2018 [Th. 4.9]** | **m - nu <= 5 => Wilf** | **d <= 5 => W >= 0** |
| Dhayni 2018 [Th. 4.12] | (2 + 1/q)e >= m => Wilf | condition mixte deficit/profondeur |
| **Eliahou 2018 [Th. 3.19 Delgado]** | **3e >= m => Wilf** | **d <= 2m/3 => W >= 0** |
| Delgado 2019 [Rem. 3.20] | e >= m - 10 => Wilf | d <= 10 => W >= 0 |

**Consequence directe** : nos Theoremes A (d=1), B (d=2), C (d=3) en tant qu'enonces "W >= 0 pour deficit d" sont des **cas particuliers triviaux** de Dhayni 2018 (d <= 5) et a fortiori d'Eliahou 2018 (3e >= m).

### 1.2 Par multiplicite

| Reference | Resultat |
|-----------|----------|
| Sammartano 2012 [Cor. 19] | m <= 8 => Wilf |
| Dhayni 2018 [Cor. 4.10] | m <= 9 => Wilf |
| Eliahou 2018 | m <= 12 => Wilf (consequence de 3e >= m et e >= 4) |
| **Bruns et al. 2020** | **m <= 18 => Wilf** (via polytopes de Kunz + algorithme) |

### 1.3 Par profondeur / conducteur

| Reference | Resultat |
|-----------|----------|
| Kaplan 2012 | c <= 2m => Wilf |
| **Eliahou 2018 (JEMS)** | **c <= 3m => Wilf** |
| Eliahou 2018 (JEMS) | W_0(S) >= 0 pour q <= 3 (ou q = ceil(c/m)) |

### 1.4 Verifications computationnelles

| Reference | Portee |
|-----------|--------|
| Fromentin & Hivert 2016 | genre <= 60 (33.5 x 10^9 semi-groupes) |
| Delgado-Eliahou-Fromentin 2023 | genre <= 100 |
| Eliahou 2024 | genre <= 120 (si m | c) |
| Bruns et al. 2020 | m <= 18 (toute profondeur, via Kunz) |
| **Notre travail** | m <= 25, k* <= 4 (23.7 x 10^9 semi-groupes via Kunz) |

---

## 2. Question cruciale : des bornes sharp existent-elles dans la litterature ?

### 2.1 Recherche dans Dhayni 2018

Le papier de Dhayni prouve W >= 0 pour m - nu <= 5. Sa methode (comptage dans des intervalles de longueur m de l'ensemble d'Apery) produit en fait des bornes intermediaires plus fortes, mais elle ne les extrait jamais.

**Exemple concret** (d = 1, ligne 387 de `arXiv-1610.08726v1`) :

```
>= 2(m-3) - (m-2) + rho = m - 4 + rho >= 0
```

Le calcul montre W >= m - 4 + rho >= m - 4 (voire m - 3 quand rho >= 1), mais Dhayni conclut simplement ">= 0". **Aucune borne sharp n'est enoncee.**

Pour d = 2 et d = 3, les calculs sont plus longs (lignes 400-490) mais la conclusion est identique : ">= 0", sans extraction de borne quantitative.

**Verdict** : Dhayni ne donne PAS de borne W >= f(m) pour f croissant. Pas de familles tendues.

### 2.2 Recherche dans Eliahou 2018 (JEMS)

Le theoreme principal (3e >= m => Wilf) est prouve via la theorie de Macaulay sur les fonctions de Hilbert et un matching dans un graphe associe a l'ensemble d'Apery. La conclusion est W(S) >= W_0(S) >= 0 pour q <= 3.

Pour q = 4, Eliahou montre que W_0(S) peut etre negatif (5 contre-exemples sur 33.5 x 10^9 semi-groupes, tous avec W_0 = -1).

**Important** : Eliahou definit W_0(S) = |P cap L| * |L| - q * d_q + rho, et montre W(S) >= W_0(S). Il ne cherche pas le minimum de W(S) parametre par le deficit d = m - e.

**Verdict** : pas de borne sharp parametree par le deficit. L'angle d'attaque est totalement different (profondeur q, pas deficit d).

### 2.3 Recherche dans Eliahou & Fromentin 2018 (Near-misses)

Ce papier est le plus proche de notre approche. Eliahou & Fromentin :
- Etudient le minimum de W_0(S) pour q = 4 fixe
- Conjecturent (Conjecture 1) : W_0(S) >= -C(n,3) ou n = |P cap L|
- Conjecturent (Conjecture 2) : le minimum est atteint quand P cap L subset S_1, X_2 = vide, X_3 = 2X_1, etc.
- Mentionnent (ligne 525) que leur borne inferieure "might well be optimal"

**Mais** : leur parametrage est par (q, n), PAS par le deficit d = m - e. Ils ne donnent aucune borne de la forme W >= f(m, d).

**Verdict** : pas de recouvrement direct avec nos resultats. Cependant, une connexion conceptuelle existe — nos deux approches cherchent des minimums de W sous des contraintes differentes.

### 2.4 Recherche dans Bruns et al. 2020

Ce papier utilise les **polytopes de Kunz** (exactement notre methode computationnelle) pour verifier Wilf pour m <= 18. Leur algorithme :
- Enumere les faces du polyedre de Kunz
- Pour chaque face, verifie si W >= 0 via un systeme d'inegalites lineaires
- Resultat : toutes les regions testees sont vides (aucune violation)

Ils prouvent m <= 18 => Wilf, mais ne calculent pas le minimum de W, ne cherchent pas de bornes sharp, et ne parametrent pas par le deficit.

**Verdict** : methode identique a la notre, mais objectif different (existence vs. bornes quantitatives). Notre enumeration va plus loin (m <= 25) mais n'est pas methodologiquement nouvelle.

---

## 3. Synthese : ce qui est nouveau et ce qui ne l'est pas

### Ce qui N'EST PAS nouveau

1. **W >= 0 pour d = 1, 2, 3** — cas particulier trivial de Dhayni 2018 (d <= 5) et Eliahou 2018 (3e >= m)
2. **La methode Kunz** — deja deployee par Bruns et al. pour m <= 18
3. **La verification computationnelle massive** — Fromentin & Hivert ont verifie 33.5 x 10^9 semi-groupes en 2016, notre 23.7 x 10^9 est du meme ordre

### Ce qui EST (probablement) nouveau

1. **Les bornes sharp explicites** :
   - W >= m - 3 pour d = 1 (avec m >= 4)
   - W >= 2m - 8 pour d = 2 (avec m >= 5)
   - W >= 2m - 12 pour d = 3 (avec m >= 5)
   
   Aucun des 5 papiers lus ne contient d'enonce de cette forme. Dhayni a les ingredients dans ses calculs mais ne les extrait pas.

2. **Les familles tendues** (tight families) atteignant ces bornes :
   - d = 1 : deux familles (k* = 2, c = 2m, L = 3 et k* = 3, c = 3m-1, L = 4)
   - d = 2 : famille a k* = 2, c = 2m, L = 4
   - d = 3 : famille a k* = 3
   
   Aucune reference ne mentionne de telles familles.

3. **La conjecture unifiee** W_min(m,d) = (m-d) * L(d) - 2m avec L(d) = ceil((sqrt(8d+1)-1)/2) + 2, indexee par les nombres triangulaires.

4. **Les seuils de stabilisation** m_min(d) et leur non-monotonie.

5. **L'observation de k*-saturation** : le minimum de W est capture par k* <= 3 pour tous les deficits testes.

---

## 4. Piege de notation

La litterature utilise `d` pour la dimension de plongement (= notre `e`).

| Concept | Notre papier | Litterature standard |
|---------|-------------|---------------------|
| Multiplicite | m | m |
| Dimension de plongement | e | d ou nu |
| **Deficit** | **d = m - e** | **m - d** ou **m - nu** |
| Profondeur | k* | q = ceil(c/m) |
| Conducteur | c | c ou chi |

**Attention** : "semigroups satisfying m - d <= 5" chez Delgado signifie "deficit <= 5" chez nous.

---

## 5. Implications pour le papier

### 5.1 Reformulation necessaire

Le papier doit etre **radicalement recentre**. Il ne peut plus pretendre prouver Wilf pour petit deficit (c'est deja fait). Il doit annoncer :

> **Sharp lower bounds for the Wilf number of numerical semigroups, parametrized by defect, with explicit attaining families.**

### 5.2 Citations manquantes (critiques)

Les references suivantes DOIVENT etre ajoutees des l'introduction :

- Dhayni 2018 — Palestine J. Math. 7(2):385-396
- Eliahou 2018 — JEMS 20(9):2105-2129 (DOI: 10.4171/JEMS/807)
- Eliahou & Fromentin 2018 — Semigroup Forum (DOI: 10.1007/s00233-018-9926-5)
- Bruns, Garcia-Sanchez, O'Neill 2020 — Int. J. Algebra Comput. (arXiv:1903.04342)
- Sammartano 2012 — Semigroup Forum 85:439-447
- Delgado 2019 — in Numerical Semigroups, Springer INdAM Series 40:39-62
- Delgado, Eliahou, Fromentin 2023 — verification genre 100 (arXiv:2310.07742)
- GAP / NumericalSgps package

### 5.3 Correction de la conjecture unifiee

Comme note par Moscariello : pour m = d + 2 (e = 2), W_min(m,d) est negatif alors que W(S) = 0. La conjecture doit etre enoncee avec l'hypothese **m >= m_0(d)** ou la borne est non-triviale et sharp.

### 5.4 Reponse suggeree a Moscariello

Points a aborder honnetement :
1. Reconnaitre que W >= 0 pour petit deficit est connu (Dhayni, Eliahou)
2. Preciser que l'apport est la **borne quantitative sharp** W >= f(m,d) avec familles tendues
3. Corriger la conjecture avec m >= m_0(d)
4. Demander : "les bornes sharp explicites figurent-elles dans Dhayni 2018 ou ailleurs ?" — un expert du domaine saura repondre immediatement
5. Mentionner Python + C/OpenMP comme outils (pas GAP, mais compatible)

---

## 6. Papiers restant a verifier

Un seul papier cite par Delgado pourrait potentiellement contenir des bornes sharp et n'a pas ete lu :

- **Moscariello & Sammartano 2015** — "On a conjecture by Wilf about the Frobenius number", Math. Zeitschrift. Leur Th. 1 donne une condition pour Wilf en termes de ceil(m/e), mais le survey de Delgado ne mentionne pas de bornes quantitatives dans ce papier.

Le papier de Dhayni reste le plus dangereux : ses calculs intermediaires contiennent presque nos bornes. Il faudrait verifier qu'elle ne les enonce pas dans sa these (Dhayni 2017, these de doctorat, Universite d'Angers, [Th. 2.3.13]).

---

## 7. Conclusion

**Niveau de confiance que les bornes sharp sont nouvelles : 85%.**

Raisons de confiance (85%) :
- 5 papiers lus, aucun ne contient W >= f(m) avec f croissant
- Le survey de Delgado (2019) est exhaustif et ne mentionne aucune borne sharp
- Eliahou & Fromentin (les plus proches) parametrent par (q, n), pas par d

Raisons de doute (15%) :
- La these de Dhayni (non lue) pourrait contenir les bornes
- Moscariello & Sammartano 2015 (non lu en detail)
- Des papiers post-2020 non couverts par le survey pourraient exister

**Recommandation** : demander directement a Moscariello (qui a deja repondu positivement) si les bornes sharp par deficit sont connues. C'est la verification la plus rapide et la plus fiable.

---

*Rapport genere a partir de la lecture directe des sources TeX des papiers de reference.*

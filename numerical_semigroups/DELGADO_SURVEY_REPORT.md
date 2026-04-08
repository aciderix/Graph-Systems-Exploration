# Rapport de lecture : Delgado, *Conjecture of Wilf — A Survey* (2019)

**Auteur du rapport** : Claude (agent Claude Code)
**Date** : 2026-04-08
**Source** : `numerical_semigroups/Delgado survey.tex` (dump pdf2tex de 16 178 lignes)
**Outil utilisé** : `numerical_semigroups/extract_delgado.py` (extracteur custom — 1 355 fragments `\put`, 325 blocs picture, → `Delgado_survey_extracted.txt` 1 499 lignes)
**Méthode** : aucun chargement du fichier complet en contexte ; extraction texte plat puis recherches ciblées par mots-clés.

---

## TL;DR

Les Théorèmes A (défaut 1), B (défaut 2) et C (défaut 3) du papier `wilf_paper.tex`, en tant qu'**énoncés d'existence** ("Wilf est vrai pour les semi-groupes de défaut petit"), sont **complètement subsumés par des résultats publiés entre 2017 et 2020**.

L'apport potentiellement encore original du papier se limite à :

1. **Les valeurs numériques explicites** des bornes inférieures sharp (`W ≥ m−3`, `W ≥ 2m−8`, `W ≥ 2m−12`) — sous réserve de vérification dans les papiers de Dhayni et d'Eliahou.
2. **Les familles tendues explicites** atteignant ces bornes.
3. **La vérification computationnelle massive** (23,7 G de semi-groupes), uniquement comme support empirique indépendant — la méthode (énumération de polytopes de Kunz) est l'approche standard du domaine, déjà déployée par Bruns–García-Sánchez–O'Neil.

L'objection technique de Moscariello sur la conjecture unifiée (formule donnant `W_min` négatif pour petite multiplicité) reste à corriger indépendamment.

---

## ⚠ Piège de notation à connaître absolument

| Concept | Notre papier | Delgado (et la littérature standard) |
|---|---|---|
| Multiplicité | `m` | `m` |
| Dimension de plongement | `e` | **`d`** (= `\|P(S)\|`) |
| Défaut (= notre `d`) | `d = m − e` | **`m − d`** |
| Profondeur | `k*` | `q = ⌈χ/m⌉` |
| Conducteur | `c` | `χ` (chi) |
| Petits éléments | `L` | `L` |
| Genre | `g` | `Ω` (omega) |

**Exemple critique** :
- "défaut ≤ 5" dans notre notation = `m − e ≤ 5` = `m − d ≤ 5` chez Delgado.
- "Théorème : `m − d ≤ 5` ⟹ Wilf" chez Delgado = "défaut ≤ 5 ⟹ Wilf" chez nous.

Toute lecture du survey sans cette traduction conduit à des contresens immédiats.

---

## Résultats préexistants qui couvrent nos Théorèmes A, B, C

### 1. Dhayni 2018 — borne directe sur le défaut

**Référence** : Mariam Dhayni, *Wilf's conjecture for numerical semigroups*, **Palestine Journal of Mathematics 7(2):385–396, 2018**.

Citée dans Delgado en deux endroits :

- **Proposition 3.18** (= [Dhayni 2018, Th. 4.12]) : "Let S be a numerical semigroup with `2 + d ≥ m`. Then S is Wilf."
  → traduction : `2 + e ≥ m`, soit `m − e ≤ 2`, soit **défaut ≤ 2 ⟹ Wilf**.
  → couvre nos Théorèmes A et B.

- **[Dhayni 2018, Th. 4.9]** (mentionné comme corollaire dans la discussion de Théorème 3.19, ligne 814 de l'extrait) : "semigroups satisfying `m − d ≤ 5` are Wilf"
  → traduction : **défaut ≤ 5 ⟹ Wilf**.
  → couvre nos Théorèmes A, B **et C** d'un seul coup.

### 2. Eliahou 2017 — borne plus large via théorie des graphes

**Référence** : Shalom Eliahou, *A graph-theoretic approach to Wilf's conjecture*, slides présentées à la rencontre des sociétés mathématiques catalane/espagnole/suédoise (Umeå, 2017). Matériel ensuite publié dans :
- Eliahou, *Wilf's conjecture and Macaulay's theorem*, **J. Eur. Math. Soc. (JEMS) 20(9):2105–2129, 2018**.
- Eliahou & Fromentin, *Near-misses in Wilf's conjecture*, **Semigroup Forum, 2018**.

**Théorème 3.19 du survey** : "Let S be a numerical semigroup with `3·d(S) ≥ m(S)`. Then S is Wilf."
→ traduction : `3·e ≥ m`, soit `e ≥ m/3`, soit **défaut ≤ 2m/3 ⟹ Wilf**.

Conséquences :
- défaut = 1, 2, 3 : trivialement satisfait pour tout `m ≥ 5`.
- **Tous nos Théorèmes A, B, C sont des cas particuliers triviaux** d'Eliahou 2017.
- Comme conséquence également notée dans le survey : un semi-groupe non-Wilf doit avoir `m > 12`.

### 3. Remarque 3.20 du survey — extension explicite

**Remarque 3.20 (Delgado)** : "If `d(S) ≥ m(S) − 10`, then S is Wilf."
→ traduction : **défaut ≤ 10 ⟹ Wilf** (preuve : combiner Théorème 3.19 + Proposition 3.17).

→ Cette borne **dépasse de loin** notre Théorème C (défaut = 3).

### 4. Petite multiplicité : Bruns–García-Sánchez–O'Neil 2020

**Référence** : Winfried Bruns, Pedro García-Sánchez, Christopher O'Neill, *On the geometry of numerical semigroups*, ~2020.

**Proposition 3.17 du survey** : "Let S be a numerical semigroup with `m ≤ 16`. Then S is Wilf."

**Point critique** : leur preuve "involves computational methods, combined with geometrical ones, such as the use of **Kunz polytopes**".

→ **C'est exactement notre méthode.** L'énumération des coordonnées de Kunz (que nous utilisons pour la vérification 23,7 G) est l'outil standard du domaine, déjà déployé pour vérifier Wilf jusqu'à `m = 16`.

→ Notre vérification massive n'est donc pas méthodologiquement nouvelle. Sa valeur résiduelle est :
- vérification indépendante avec une implémentation différente
- exploration de paramètres `(m, K)` au-delà de ce qui était publié

mais ce n'est **pas** un apport méthodologique original.

### 5. Autres bornes de multiplicité (chronologie)

- **Sammartano [31, Cor. 19]** (~2012) : `m ≤ 8` ⟹ Wilf
- **Dhayni [13, Cor. 4.10]** (2018) : `m ≤ 9` ⟹ Wilf
- **Eliahou [15]** (2017) : `m ≤ 12` ⟹ Wilf
- **Bruns–García-Sánchez–O'Neil [7]** (~2020) : `m ≤ 16` ⟹ Wilf

---

## Bornes quantitatives explicites — ce qui n'est PAS dans le survey

Dans le matériel de Delgado que j'ai pu lire (extraction complète, recherche par mots-clés `sharp`, `tight`, `attained`, `equality`, `W(S) ≥`, `Eliahou number`), **je n'ai trouvé aucune borne explicite de la forme `W ≥ f(m, d)`** avec famille tendue exhibée.

Le survey est presque entièrement orienté **existence** ("est Wilf / n'est pas Wilf"), pas **bornes quantitatives**.

### Conclusion provisoire pour l'originalité

Si nos formules
- `W ≥ m − 3` (défaut 1)
- `W ≥ 2m − 8` (défaut 2)
- `W ≥ 2m − 12` (défaut 3)

et nos **familles tendues** correspondantes ne sont pas explicitement énoncées dans :

1. Dhayni 2018 (Palest. J. Math.) — papier source de [Dhayni Th. 4.9]
2. Eliahou 2018 (JEMS, *Wilf's conjecture and Macaulay's theorem*)
3. Eliahou & Fromentin 2018 (*Near-misses in Wilf's conjecture*)
4. Bruns–García-Sánchez–O'Neil 2020

…alors **c'est notre seul apport potentiellement original**, et il faut centrer le papier dessus.

**Tâche restant à faire AVANT d'envoyer quoi que ce soit** : récupérer et lire ces 4 papiers, et confirmer qu'aucun ne contient les bornes explicites avec familles tendues.

---

## État de chaque claim du papier

| Claim de notre papier | Statut réel |
|---|---|
| Théorème A : défaut 1 ⟹ Wilf | Déjà prouvé. Dhayni 2018 (Th. 4.9, Th. 4.12), Eliahou 2017 (Th. 3.19) |
| Théorème B : défaut 2 ⟹ Wilf | Déjà prouvé. Mêmes références |
| Théorème C : défaut 3 ⟹ Wilf | Déjà prouvé. Dhayni [13, Th. 4.9] (défaut ≤ 5), Eliahou Th. 3.19 |
| Conjecture unifiée `W_min(m,d)` | Bugguée pour petite `m` (objection Moscariello, contre-exemple `m = d+2`). Doit être reformulée avec hypothèse `m ≥ m₀(d)` |
| Vérification Kunz 23,7 G de semi-groupes | Méthode standard du domaine ; déjà déployée par Bruns et al. avec GAP + `numericalsgps`. Valeur uniquement comme **vérification indépendante**, pas comme méthode nouvelle |
| Borne explicite `W ≥ m−3` (défaut 1) avec familles tendues | **Possiblement nouveau** — à vérifier dans Dhayni 2018 et Eliahou 2018 |
| Borne explicite `W ≥ 2m−8` (défaut 2) avec familles tendues | **Possiblement nouveau** — idem |
| Borne explicite `W ≥ 2m−12` (défaut 3) avec familles tendues | **Possiblement nouveau** — idem |

---

## Recommandations concrètes

### 1. Avant tout

**Récupérer et lire intégralement** :

- [13] **Dhayni 2018** — *Wilf's conjecture for numerical semigroups*, Palest. J. Math. 7(2):385–396, 2018. (Open access via Palestine J. Math.)
- [16] **Eliahou 2018** — *Wilf's conjecture and Macaulay's theorem*, JEMS 20(9):2105–2129, 2018. (DOI: 10.4171/JEMS/807, probable preprint arXiv)
- [17] **Eliahou & Fromentin 2018** — *Near-misses in Wilf's conjecture*, Semigroup Forum, 2018. (DOI: 10.1007/s00233-018-9926-5)
- [7] **Bruns, García-Sánchez, O'Neill** — papier ~2020 sur la géométrie des semi-groupes numériques (chercher sur arXiv).

Pour chacun, vérifier si les bornes inférieures explicites de `W` (et pas seulement l'existence Wilf) sont énoncées ou démontrées en passant.

### 2. Outils de vérification indépendante

**Installer GAP + le package `numericalsgps`**.
- Pourra servir à valider quelques exemples de notre énumération Kunz.
- Pourra aussi être cité dans le papier comme "vérification indépendante avec l'outil de référence du domaine".
- Référence : la base GAP couvre le genre jusqu'à 120 selon Moscariello.

### 3. Reformulation du papier

Si après lecture des 4 papiers ci-dessus les **bornes explicites** sont effectivement nouvelles, recadrer le papier comme suit :

- **Titre/abstract** : ne pas annoncer "preuve de Wilf pour défaut petit" (déjà connu), mais **"sharp lower bounds for the Wilf number for small defect, with attaining families"**.
- **Introduction** : citer explicitement Dhayni 2018, Eliahou 2017/2018, Bruns et al. ; positionner le papier comme une **précision quantitative** d'un résultat d'existence connu.
- **Conjecture unifiée** : ajouter l'hypothèse `m ≥ m₀(d)` qui élimine le contre-exemple `m = d+2, e = 2`.
- **Section computation** : présenter comme **vérification indépendante avec implémentation Python**, en accord avec GAP.

Si après lecture les bornes explicites ne sont **pas** nouvelles, le papier devient sans contribution publiable et il faut reconsidérer son utilité (notes pédagogiques internes ?).

### 4. Réponse à Moscariello

Reconnaître honnêtement :

- Avoir lu son survey et identifié les références [13], [15], [16], [17], [7].
- Avoir compris que l'existence Wilf pour défaut petit est déjà connue.
- Demander confirmation/infirmation : **"est-ce que les bornes inférieures sharp explicites avec familles tendues figurent dans Dhayni 2018 ou Eliahou 2018 ?"** — c'est exactement le genre de question qu'un mathématicien du domaine pourra trancher en quelques secondes.
- Mentionner avoir installé GAP+numericalsgps pour vérification croisée.
- Ne **pas** prétendre originalité méthodologique sur l'enumeration Kunz.

---

## Annexe — extraits clés du survey, références complètes

### Théorème 3.19 de Delgado (= Eliahou 2017)

> Let S be a numerical semigroup with `3·d(S) ≥ m(S)`. Then S is Wilf.

Commentaire du survey :
> Previous result implies that semigroups of multiplicity up to 12 are Wilf [...]. A non-Wilf semigroup S must satisfy `d(S) ≥ 4` by Theorem 3.2. As it must also satisfy `3·d(S) < m(S)`, it follows that if S is non Wilf, then `m(S) > 12`.

### Proposition 3.18 de Delgado (= Dhayni 2018, Th. 4.12)

> Let S be a numerical semigroup with `2 + d ≥ m`. Then S is Wilf.

### Référence à Dhayni Th. 4.9 (générale, défaut ≤ 5)

> Two other simple consequences of Theorem 3.19 follow. The first is a generalization of a result of Dhayni [13, Th. 4.9], who proved that semigroups satisfying `m − d ≤ 5` are Wilf.

### Remarque 3.20 de Delgado

> If `d(S) ≥ m(S) − 10`, then S is Wilf.

(Preuve : `m ≤ 16` ⟹ Prop. 3.17 ; `m ≥ 16` ⟹ `m − 10 ≥ m/3` ⟹ Théorème 3.19.)

### Proposition 3.17 (= Bruns–García-Sánchez–O'Neill)

> Let S be a numerical semigroup with `m ≤ 16`. Then S is Wilf.

Commentaire du survey :
> A big breakthrough was obtained by Bruns, García-Sánchez and O'Neil, who achieved multiplicity 16. Their proof involves computational methods, combined with geometrical ones, such as **the use of Kunz polytopes**.

### Liste des références citées dans ce rapport

- **[7]** Bruns, García-Sánchez, O'Neill (~2020).
- **[13]** Mariam Dhayni. *Wilf's conjecture for numerical semigroups*. Palest. J. Math. 7(2):385–396, 2018.
- **[15]** Shalom Eliahou. *A graph-theoretic approach to Wilf's conjecture*. Slides Umeå 2017.
- **[16]** Shalom Eliahou. *Wilf's conjecture and Macaulay's theorem*. JEMS 20(9):2105–2129, 2018. DOI: 10.4171/JEMS/807.
- **[17]** Eliahou & Fromentin. *Near-misses in Wilf's conjecture*. Semigroup Forum, 2018. DOI: 10.1007/s00233-018-9926-5.
- **[31]** Sammartano (référence à compléter — survey utilise [31, Cor. 19] pour `m ≤ 8`).

---

## Limites de ce rapport

1. **Extraction imparfaite** : le dump pdf2tex contient des espaces parasites intra-mot ("in v olv ed"), et environ 1 355 fragments seulement. Certains passages techniques (formules, indices) sont mal préservés. Une lecture manuelle du PDF original (si disponible) compléterait utilement.
2. **Pas de lecture des papiers cités** : ce rapport résume uniquement le **survey** de Delgado. Les preuves originales sont dans les papiers cités, et seule leur lecture permettrait de confirmer/infirmer si les bornes quantitatives sharp y figurent.
3. **Pas d'accès GAP/`numericalsgps`** : aucune vérification croisée n'a été faite avec l'outil de référence du domaine. C'est une étape à faire indépendamment.

---

*Rapport généré automatiquement pour servir de point d'entrée à la décision sur l'orientation du papier.*

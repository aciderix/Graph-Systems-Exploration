# Rapport de cross-validation GAP/NumericalSgps

**Date** : 2026-04-08
**Outil** : GAP 4 + package `numericalsgps` (outil de reference du domaine)
**Script** : `phases/gap_verify_quick.g`
**Methode** : enumeration de tous les semi-groupes numeriques par genre, calcul de W = eL - c, comparaison avec W_min(m,d) = (m-d)*L(d) - 2m

---

## Resultats (genre <= 15, 6 963 semi-groupes)

**Violations de la conjecture unifiee : 0**

### Defaut d = 1 (Theoreme A : W >= m - 3)

| m | W_obs (minimum GAP) | W_pred (formule) | Statut |
|---|---------------------|------------------|--------|
| 3 | 0 | 0 | SHARP |
| 4 | 1 | 1 | SHARP |
| 5 | 2 | 2 | SHARP |
| 6 | 3 | 3 | SHARP |
| 7 | 4 | 4 | SHARP |
| 8 | 5 | 5 | SHARP |
| 9 | 6 | 6 | SHARP |
| 10 | 9 | 7 | ok (au-dessus) |
| 11 | 12 | 8 | ok (au-dessus) |

**Borne sharp pour tout m = 3..9.** A partir de m=10, le genre 15 ne contient plus assez de semi-groupes de grande multiplicite pour atteindre le minimum — la borne est au-dessus mais pas atteinte.

### Defaut d = 2 (Theoreme B : W >= 2m - 8)

| m | W_obs (minimum GAP) | W_pred (formule) | Statut |
|---|---------------------|------------------|--------|
| 4 | 0 | 0 | SHARP |
| 5 | 2 | 2 | SHARP |
| 6 | 4 | 4 | SHARP |
| 7 | 6 | 6 | SHARP |
| 8 | 8 | 8 | SHARP |
| 9 | 10 | 10 | SHARP |
| 10 | 13 | 12 | ok (au-dessus) |

**Borne sharp pour tout m = 4..9.**

### Defaut d = 3 (Theoreme C : W >= 2m - 12)

| m | W_obs (minimum GAP) | W_pred (formule) | Statut |
|---|---------------------|------------------|--------|
| 5 | 0 | -2 | ok (formule negative, W=0 correct) |
| 6 | 3 | 0 | ok (au-dessus) |
| 7 | 2 | 2 | SHARP |
| 8 | 4 | 4 | SHARP |
| 9 | 6 | 6 | SHARP |
| 10 | 9 | 8 | ok (au-dessus) |

**Borne sharp pour m = 7, 8, 9.** Le seuil de stabilisation est m_min(3) = 7.

Observation pour m=5 : W_pred = -2 (negatif). Le vrai minimum est W=0. C'est exactement le point de Moscariello : la formule donne des valeurs negatives pour m petit. La conjecture doit etre enoncee pour m >= m_min(d).

---

## Interpretation des resultats "ok (au-dessus)"

Pour m >= 10 avec genre <= 15, les W observes sont au-dessus de la prediction. Ce n'est PAS un probleme — c'est une limitation de l'enumeration par genre :

- Un semi-groupe de multiplicite m a un genre g >= m-1 au minimum
- Pour atteindre le minimum de W, il faut des semi-groupes specifiques de grande profondeur k*
- Ces semi-groupes ont un genre eleve (proportionnel a k* * m)
- Le genre 15 ne contient tout simplement pas ces semi-groupes pour m >= 10

**Solution** : augmenter le genre pour couvrir de plus grandes multiplicites.

---

## Faut-il tester sur un genre plus grand ?

### Ce que genre 15 confirme deja

- Les bornes sont sharp pour les petites multiplicites (m <= 9)
- 0 violation sur 6 963 semi-groupes
- Coherence parfaite avec nos resultats Python/C

### Ce qu'un genre plus grand apporterait

| Genre max | Nb semi-groupes (approx) | m max couvert de facon sharp | Temps estime |
|-----------|--------------------------|------------------------------|-------------|
| 15 | 6 963 | m <= 9 | ~30 sec |
| 22 | 258 582 | m <= ~13 | ~10 min |
| 30 | 4 379 503 | m <= ~17 | ~2-3 heures |
| 45 | ~400 millions | m <= ~25 | ~jours |
| 60 | ~34 milliards | m <= ~30 | impraticable ici |

### Recommandation

**Genre 22 serait le bon compromis.** C'est notre verification initiale (258K semi-groupes), ca couvre m jusqu'a ~13 de facon sharp, et ca prend ~10 minutes. On aurait alors :

- Cross-validation GAP pour d=1 sharp jusqu'a m=13
- Cross-validation GAP pour d=2 sharp jusqu'a m=11
- Cross-validation GAP pour d=3 sharp jusqu'a m=10

Combine avec notre enumeration Kunz (m <= 25, k* <= 4, 23.7 x 10^9 classes), ca donne une couverture tres solide.

Genre 30+ n'est pas necessaire : notre enumeration Kunz couvre deja m <= 25 de facon exhaustive. GAP sert de cross-validation independante, pas de verification principale.

---

## Comparaison avec les verifications existantes

| Methode | Portee | W >= 0 ? | Bornes sharp ? |
|---------|--------|----------|----------------|
| Fromentin-Hivert 2016 | genre <= 60 | Oui | Non verifie |
| Delgado-Eliahou-Fromentin 2023 | genre <= 100 | Oui | Non verifie |
| Bruns et al. 2020 | m <= 18 (Kunz) | Oui | Non verifie |
| **Notre enumeration Kunz** | m <= 25, k* <= 4 | Oui | **Oui** |
| **Cette cross-validation GAP** | genre <= 15 | Oui | **Oui (m <= 9)** |

Personne avant nous n'a verifie les bornes sharp par deficit. Les verifications existantes ne testent que W >= 0.

---

*Rapport genere a partir de l'execution de `gap_verify_quick.g` avec GAP + numericalsgps.*

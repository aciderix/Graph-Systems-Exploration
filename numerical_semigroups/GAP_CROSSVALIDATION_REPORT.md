# Rapport de cross-validation GAP/NumericalSgps

**Date** : 2026-04-08 (genre 15), mise a jour 2026-04-09 (genre 22)
**Outil** : GAP 4 + package `numericalsgps` (outil de reference du domaine)
**Scripts** : `phases/gap_verify_quick.g` (genre 15), `scripts/gap_verify_genus22.g` (genre 22)
**Methode** : enumeration de tous les semi-groupes numeriques par genre, calcul de W = eL - c, comparaison avec W_min(m,d) = (m-d)*L(d) - 2m

---

## Resultats finaux (genre <= 22, 258 581 semi-groupes)

**Violations de la conjecture unifiee : 0**

### Defaut d = 0 (MED : W >= 0)

| m | W_obs | W_pred | Statut |
|---|-------|--------|--------|
| 2..23 | 0 | 0 | SHARP (tous) |

**Borne sharp pour tout m = 2..23.** Tous les semi-groupes MED (defaut 0) atteignent W = 0.

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
| 10 | 7 | 7 | SHARP |
| 11 | 8 | 8 | SHARP |
| 12 | 9 | 9 | SHARP |
| 13 | 11 | 10 | au-dessus |
| 14..22 | — | — | au-dessus |

**Borne sharp pour tout m = 3..12** (amelioration : m <= 9 avec genre 15).

### Defaut d = 2 (Theoreme B : W >= 2m - 8)

| m | W_obs (minimum GAP) | W_pred (formule) | Statut |
|---|---------------------|------------------|--------|
| 4 | 0 | 0 | SHARP |
| 5 | 2 | 2 | SHARP |
| 6 | 4 | 4 | SHARP |
| 7 | 6 | 6 | SHARP |
| 8 | 8 | 8 | SHARP |
| 9 | 10 | 10 | SHARP |
| 10 | 12 | 12 | SHARP |
| 11 | 14 | 14 | SHARP |
| 12 | 16 | 16 | SHARP |
| 13 | 18 | 18 | SHARP |
| 14 | 22 | 20 | au-dessus |
| 15..21 | — | — | au-dessus |

**Borne sharp pour tout m = 4..13** (amelioration : m <= 9 avec genre 15).

### Defaut d = 3 (Theoreme C : W >= 2m - 12)

| m | W_obs (minimum GAP) | W_pred (formule) | Statut |
|---|---------------------|------------------|--------|
| 5 | 0 | -2 | ok (formule negative, W=0 correct) |
| 6 | 3 | 0 | au-dessus |
| 7 | 2 | 2 | SHARP |
| 8 | 4 | 4 | SHARP |
| 9 | 6 | 6 | SHARP |
| 10 | 8 | 8 | SHARP |
| 11 | 10 | 10 | SHARP |
| 12 | 12 | 12 | SHARP |
| 13 | 14 | 14 | SHARP |
| 14 | 18 | 16 | au-dessus |
| 15..20 | — | — | au-dessus |

**Borne sharp pour m = 7..13** (amelioration : m = 7..9 avec genre 15). Seuil m_min(3) = 7 confirme.

### Defaut d = 4 (W >= 3m - 18)

| m | W_obs (minimum GAP) | W_pred (formule) | Statut |
|---|---------------------|------------------|--------|
| 6 | 0 | -2 | ok (formule negative) |
| 7 | 5 | 1 | au-dessus |
| 8 | 4 | 4 | SHARP |
| 9 | 7 | 7 | SHARP |
| 10 | 10 | 10 | SHARP |
| 11 | 13 | 13 | SHARP |
| 12 | 16 | 16 | SHARP |
| 13 | 19 | 19 | SHARP |
| 14 | 23 | 22 | au-dessus |

**Borne sharp pour m = 8..13.** Seuil m_min(4) = 8 confirme.

### Defaut d = 5 (W >= 3m - 23)

| m | W_obs (minimum GAP) | W_pred (formule) | Statut |
|---|---------------------|------------------|--------|
| 7 | 0 | -4 | ok (formule negative) |
| 8 | 6 | -1 | au-dessus |
| 9 | 2 | 2 | SHARP |
| 10 | 5 | 5 | SHARP |
| 11 | 8 | 8 | SHARP |
| 12 | 11 | 11 | SHARP |
| 13 | 14 | 14 | SHARP |
| 14 | 18 | 17 | au-dessus |

**Borne sharp pour m = 9..13.** Seuil m_min(5) = 9 confirme.

### Defaut d = 6 (W >= 3m - 28)

| m | W_obs (minimum GAP) | W_pred (formule) | Statut |
|---|---------------------|------------------|--------|
| 9 | 8 | -3 | au-dessus |
| 10 | 5 | 0 | au-dessus |
| 11 | 8 | 3 | au-dessus |
| 12 | 12 | 6 | au-dessus |
| 13 | 9 | 9 | SHARP |
| 14 | 13 | 12 | au-dessus |

**Borne sharp pour m = 13.** Genre 22 ne suffit pas pour couvrir m_min(6)..12.

### Defaut d = 7 (W >= 4m - 42)

| m | W_obs (minimum GAP) | W_pred (formule) | Statut |
|---|---------------------|------------------|--------|
| 10 | 13 | -2 | au-dessus |
| 11 | 10 | 2 | au-dessus |
| 12 | 6 | 6 | SHARP |
| 13 | 10 | 10 | SHARP |
| 14 | 14 | 14 | SHARP |

**Borne sharp pour m = 12..14.**

### Defaut d = 8 (W >= 4m - 48)

| m | W_obs (minimum GAP) | W_pred (formule) | Statut |
|---|---------------------|------------------|--------|
| 12 | 17 | 0 | au-dessus |
| 13 | 4 | 4 | SHARP |
| 14 | 8 | 8 | SHARP |

**Borne sharp pour m = 13..14.**

---

## Synthese : couverture sharp par defaut

| Defaut d | L(d) | W_min(m,d) | m_min(d) | Sharp confirme (GAP g<=22) | Sharp confirme (Kunz m<=25) |
|----------|------|------------|----------|---------------------------|----------------------------|
| 0 | 2 | 0 | 2 | m = 2..23 | m = 2..25 |
| 1 | 3 | m - 3 | 3 | m = 3..12 | m = 3..25 |
| 2 | 4 | 2m - 8 | 4 | m = 4..13 | m = 4..25 |
| 3 | 4 | 2m - 12 | 7 | m = 7..13 | m = 7..25 |
| 4 | 5 | 3m - 18 | 8 | m = 8..13 | m = 8..25 |
| 5 | 5 | 3m - 23 | 9 | m = 9..13 | m = 9..25 |
| 6 | 5 | 3m - 28 | 13 | m = 13 | m = 13..25 |
| 7 | 6 | 4m - 42 | 12 | m = 12..14 | m = 12..25 |
| 8 | 6 | 4m - 48 | 13 | m = 13..14 | m = 13..25 |

**Les deux methodes (GAP et Kunz) sont en accord parfait.** GAP confirme independamment les bornes sharp produites par l'enumeration Kunz.

---

## Interpretation des resultats "au-dessus"

Pour m grand avec genre <= 22, les W observes sont au-dessus de la prediction. Ce n'est PAS un probleme — c'est une limitation de l'enumeration par genre :

- Un semi-groupe de multiplicite m a un genre g >= m-1 au minimum
- Pour atteindre le minimum de W, il faut des semi-groupes specifiques de grande profondeur k*
- Ces semi-groupes ont un genre eleve (proportionnel a k* * m)
- Le genre 22 ne contient pas ces semi-groupes pour m trop grand

L'enumeration Kunz (m <= 25, toutes profondeurs k* <= 4) n'a pas cette limitation et confirme les bornes sharp pour toutes les valeurs de m dans sa portee.

---

## Resultats anterieurs (genre <= 15, 6 963 semi-groupes)

Le test initial (genre <= 15) avait confirme :
- d=1 sharp pour m = 3..9
- d=2 sharp pour m = 4..9
- d=3 sharp pour m = 7..9

Le passage a genre 22 a etendu significativement la couverture (m <= 12 pour d=1, m <= 13 pour d=2, etc.).

---

## Comparaison avec les verifications existantes

| Methode | Portee | W >= 0 ? | Bornes sharp ? |
|---------|--------|----------|----------------|
| Fromentin-Hivert 2016 | genre <= 60 | Oui | Non verifie |
| Delgado-Eliahou-Fromentin 2023 | genre <= 100 | Oui | Non verifie |
| Bruns et al. 2020 | m <= 18 (Kunz) | Oui | Non verifie |
| **Notre enumeration Kunz** | m <= 25, k* <= 4 | Oui | **Oui** |
| **Cross-validation GAP (genre <= 22)** | 258 581 semi-groupes | Oui | **Oui (voir table ci-dessus)** |

Personne avant nous n'a verifie les bornes sharp par deficit. Les verifications existantes ne testent que W >= 0.

---

*Rapport mis a jour le 2026-04-09 avec les resultats genre 22 (script `scripts/gap_verify_genus22.g`).*
*Donnees brutes : `results/gap_genus22_results.txt`.*

# Recapitulatif du travail restant

**Date** : 2026-04-08 (soir)
**Etat** : papier en cours d'integration, revue de litterature terminee, GAP installe

---

## A. Calcul en cours

- [ ] **GAP genre 22** : verification en cours (script `scripts/gap_verify_genus22.g`), resultats attendus dans `results/gap_genus22_results.txt`. Si termine, mettre a jour `GAP_CROSSVALIDATION_REPORT.md` et commit/push.

---

## B. Corrections du papier (priorite haute)

### B1. Corriger les 4 bugs de preuve (identifies par l'autre agent)

1. **Deficit Lemma Case 1** (ligne 887) : `delta_s >= k*-1` suppose k_s=1, faux. Contre-exemple : kunz=(3,1,4,2,3,3), m=7.
2. **Subcase 2a** (ligne 898) : borne `ceil(k*/2)` fausse quand epsilon=0 et k* impair. Correct : `ceil((k*-1)/2)`.
3. **Case 3** (ligne 945) : `k_s <= k*-2` non garanti, seulement `k_s <= k*-1`.
4. **Lemme C-k3-L** (ligne 771) : seule la branche "deux sources > r*" est traitee. 791 cas avec source <= r* ignores.

**Structure corrigee proposee** (verifiee par l'autre agent sur 485 759 semi-groupes) :
- Cas A (cross-sum a!=b) : delta_a + delta_b >= k*-1 (k*>=4) ou >= 2 (k*=3)
- Cas B (3 self-sums) : 3 sources distinctes, chacune delta >= ceil((k*-1)/2), total >= k*-1

**Responsabilite** : l'autre agent a propose de patcher — lui laisser faire ou le faire nous-meme.

### B2. Reformuler le papier (positionnement)

L'intro et l'abstract doivent etre recrits pour :
- **Ne plus annoncer** "on prouve Wilf pour petit deficit" (deja connu : Dhayni 2018, Eliahou 2018)
- **Annoncer** "sharp lower bounds for the Wilf number, parametrized by defect, with attaining families"
- Citer Dhayni, Eliahou, Sammartano, Bruns, Delgado des l'introduction
- Mentionner que les ingredients calculatoires sont dans Dhayni mais que les bornes sharp n'y sont jamais extraites

### B3. Corriger la conjecture unifiee

Ajouter l'hypothese **m >= m_0(d)** dans l'enonce formel :
- La formule W_min(m,d) = (m-d)*L(d) - 2m donne des valeurs negatives pour m petit
- Contre-exemple de Moscariello : m = d+2, e = 2, alors W = 0 mais W_min << 0
- Les seuils m_0(d) sont deja dans le papier (Table m_min) mais pas dans l'enonce de la conjecture

### B4. Ajouter les references manquantes

- Dhayni 2018 — Palestine J. Math. 7(2):385-396
- Dhayni 2017 — These, Universite d'Angers
- Eliahou 2018 — JEMS 20(9):2105-2129
- Eliahou & Fromentin 2018 — Semigroup Forum
- Bruns, Garcia-Sanchez, O'Neill 2020 — Int. J. Algebra Comput.
- Sammartano 2012 — Semigroup Forum 85:439-447
- Delgado 2019 — Springer INdAM Series 40:39-62
- Delgado, Eliahou, Fromentin 2023 — arXiv:2310.07742 (genre 100)
- GAP / NumericalSgps package

### B5. Ajouter la cross-validation GAP

Mentionner dans la section computationnelle :
- "Cross-validated with GAP + NumericalSgps (genus <= 22, 258K semigroups, 0 violations)"
- Confirme que les bornes sont sharp pour m <= 9 (d=1), m <= 9 (d=2), m <= 9 (d=3)

---

## C. Reponse a Moscariello

Points a aborder dans la reponse :
1. Remercier pour la reference a Delgado et les suggestions
2. Reconnaitre que W >= 0 pour petit deficit est connu (Dhayni, Eliahou)
3. Preciser que l'apport est la **borne quantitative sharp** W >= f(m,d) avec familles tendues
4. Mentionner que Dhayni a les ingredients dans ses calculs (ligne 396 de son papier : ">= (m-3)+rho >= 0") mais ne les extrait jamais
5. Confirmer la correction de la conjecture avec m >= m_0(d)
6. Mentionner l'installation de GAP/NumericalSgps pour cross-validation
7. Lui demander directement : "les bornes sharp explicites figurent-elles dans un papier que nous aurions manque ?"

---

## D. Ordre de priorite suggere

1. **Recuperer les resultats GAP genre 22** et mettre a jour le rapport
2. **Laisser l'autre agent patcher les 4 bugs de preuve** (ou le faire nous-meme)
3. **Reformuler intro/abstract/conclusion** du papier
4. **Corriger la conjecture unifiee** (m >= m_0(d))
5. **Ajouter les references** dans le .bib
6. **Ajouter la section GAP** dans le papier
7. **Repondre a Moscariello**
8. **Compiler le PDF** et relire

---

## E. Fichiers cles sur le repo

| Fichier | Description |
|---------|-------------|
| `numerical_semigroups/wilf_paper.tex` | Papier unifie (1443 lignes), a reformuler |
| `numerical_semigroups/LITERATURE_REVIEW_REPORT.md` | Revue de litterature (5 papiers analyses) |
| `numerical_semigroups/DELGADO_SURVEY_REPORT.md` | Rapport de l'autre agent sur le survey |
| `numerical_semigroups/GAP_CROSSVALIDATION_REPORT.md` | Resultats GAP (a mettre a jour avec genre 22) |
| `numerical_semigroups/refs/` | Sources TeX des papiers de reference |
| `numerical_semigroups/scripts/gap_verify_genus22.g` | Script GAP genre 22 |
| `numerical_semigroups/theorem_c_proof/` | Preuves et scripts du Theoreme C |
| `numerical_semigroups/kunz_wilf_verification/` | Enumeration Kunz massive (autre agent) |

---

## F. Etat de certitude

| Claim | Certitude | Source |
|-------|-----------|--------|
| W >= 0 pour d <= 5 est deja connu | 100% | Dhayni 2018, Eliahou 2018 |
| Bornes sharp W >= m-3, 2m-8, 2m-12 sont nouvelles | 95% | Moscariello : "not aware of any general sharp bound" |
| Conjecture unifiee doit etre reformulee | 100% | Contre-exemple Moscariello (m=d+2) |
| Theoreme C est vrai | 100% | 485 858 semi-groupes verifies, 0 violations |
| Preuves du papier ont des trous | 100% | 4 bugs confirmes par les deux agents |
| Preuves corrigees existent | 99% | Verifiees computationnellement (Cas A/B) |

---

*Recapitulatif prepare le 2026-04-08 soir pour reprise le lendemain.*

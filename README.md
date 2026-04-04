# Graph Systems Exploration

**Exploration systématique des graphes comme systèmes dynamiques déformables**

Objectif : cartographier l'espace des graphes, identifier des transitions de phase, des invariants robustes et des structures émergentes universelles.

## Approche

Pas de biais théorique. Exploration exhaustive, orientée machine :
- Génération massive et diverse
- Déformation contrôlée
- Mesure systématique
- Détection automatique de patterns

## Phases

### Phase G1 — Génération + Mesures Baseline
- **356 graphes** de 21 familles (Erdős-Rényi, Barabási-Albert, Watts-Strogatz, grids, arbres, réguliers, géométriques, SBM, caveman, circulants, lobster, bipartite…)
- 20+ métriques par graphe (composantes, degrés, distances, clustering, spectre, robustesse)
- Résultats : `phases/G1/results.json`

### Phase G2 — Déformations Contrôlées
- 5 types de déformation × 13 niveaux × 12 graphes de base
- Suivi continu de toutes les métriques sous déformation
- Détection de transitions de phase (small-world, percolation)
- Résultats : `phases/G2/results.json`

### Phase G3 — Percolation Fine
- 14 graphes × 3 modes d'attaque (aléatoire, ciblé degré, ciblé betweenness)
- 50-200 points par courbe de percolation
- Détection précise des seuils critiques (pic du 2ème composant)
- Résultats : `phases/G3/results.json`

### Phase G4 — Chasse aux Invariants
- ~50 000 combinaisons algébriques testées
- Recherche systématique de quantités stables sous déformation
- Analyse PCA de l'espace des graphes

### Phase G5 — Synthèse Croisée
- Validation croisée des 6 lois candidates
- Tests de robustesse et d'universalité
- Classement final

## 🏆 Résultats Principaux

### 6 Lois Extraites

| # | Loi | Force |
|---|-----|-------|
| 1 | **Entropie spectrale normalisée S/log₂(N) → 0.97** (quasi-universel, stable sous déformation) | ⭐⭐⭐⭐⭐ |
| 2 | **Trois régimes de vulnérabilité** (CV des degrés détermine la robustesse, pas κ) | ⭐⭐⭐⭐ |
| 3 | C × L n'est PAS universel (contrairement à l'intuition small-world) | ⭐⭐ |
| 4 | **ρ(A)/⟨k⟩ = signature spectrale d'hétérogénéité** (= 1.000 ssi régulier) | ⭐⭐⭐⭐ |
| 5 | **Transition de percolation détectable par pic du SLC** (non universel en amplitude) | ⭐⭐⭐ |
| 6 | λ₂ × D borné mais non constant | ⭐⭐ |

### Phénomènes Surprenants

1. **BA(m=1) est ultra-fragile** : 2% de suppression ciblée brise le graphe en 30 composants
2. **2% de rewiring dans caveman** divise le diamètre par 1.5 — transition small-world brutale
3. **L'entropie spectrale est insensible à la structure locale** — ne "voit" pas le clustering
4. **WS(p=0.01) résiste mieux aux attaques ciblées qu'aléatoires** — unique dans notre dataset

### Architecture de l'Espace des Graphes (PCA)
- PC1 (48%) = axe densité/connectivité
- PC2 (24%) = axe clustering
- 72% de variance expliquée par 2 dimensions

## Stack Technique

- Python 3.12 + NetworkX + NumPy + SciPy
- mpmath pour haute précision quand nécessaire
- Résultats sérialisés en JSON

## Licence

MIT

### Phase G6 — Falsification Hardcore

**Objectif :** Détruire nos propres lois. Tester contre graphes extrêmes, pathologiques, bruit extrême, et le null le plus stupide.

- **68 graphes extrêmes** (étoiles, cliques, paths, bipartites, arbres dégénérés, N=4 à 500)
- **24 scénarios de destruction** (suppression 30% à 99% des arêtes)
- **Test de trivialité** (comparaison avec matrices aléatoires)

**Verdict :**

| LOI | Statut post-falsification |
|---|---|
| LOI 1 (entropie spectrale) | ❌ 70% triviale — effet de concentration |
| LOI 2 (vulnérabilité) | ⚠️ Descriptif, connu |
| LOI 3 (C × L) | ❌ Connu |
| LOI 4 (ρ/⟨k⟩) | ✅ Vraie, mais connue (Perron-Frobenius) |
| LOI 5 (SLC) | ⚠️ Standard |
| LOI 6 (λ₂ × D) | ❌ Connu |

**0 résultat véritablement nouveau sur 6.**

→ Voir `NEXT_AGENT_BRIEFING.md` pour la direction recommandée : **inventer de nouvelles métriques**.

## Next Steps

Voir le document complet : [`NEXT_AGENT_BRIEFING.md`](NEXT_AGENT_BRIEFING.md)

Direction recommandée : **Option 2 — Nouvelles métriques non-standard**

Priorités :
1. Métriques de réponse dynamique (diffusion de chaleur, marches aléatoires)
2. Courbure de Ricci discrète (Ollivier/Forman)
3. Entropie de Von Neumann
4. Homologie persistante (TDA)
5. Complexité par compression

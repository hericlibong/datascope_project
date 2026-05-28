# Refonte UI — Adoption du Claude Design System

> Spec source : `DESIGN.md` (généré via `npx getdesign@latest add claude`) — à committer à la racine du projet.
> Branche cible : `feature/claude-design-refonte` (depuis `feature/ui-notebook-layout`).
> Estimation : 5 à 7 jours-homme, livrable phase par phase.

---

## 1. Contexte & objectif

Datascope utilise actuellement une identité visuelle « dashboard data tech » (dark navy + cyan/violet, glassmorphism, dégradés radiaux). L'app est une **assistance éditoriale** pour journalistes — le registre actuel est en décalage avec l'usage. La refonte vise à adopter le langage visuel de Claude (Anthropic) : **canvas cream + accent coral + typo éditoriale serif**, plus aligné avec un outil de rédaction.

## 2. Décisions arrêtées

| Point | Décision |
|---|---|
| Stack | **Inchangée** : Flask + Jinja2 + CSS vanilla. Pas de React/Tailwind/Next. |
| Fonts | **Google Fonts CDN** : EB Garamond (display) + Inter (body) + JetBrains Mono (code). |
| Dark mode | **Abandonné**. Cream-first, aligné spec Claude. |
| Bootstrap | **Suppression totale** (Phase 3). |
| Branche | `feature/claude-design-refonte` ← `feature/ui-notebook-layout`. |
| Commits | **Un commit par phase** (5 commits prévus). |
| Doc | Ce fichier unique consolidé. |

## 3. Évaluation de l'existant

**Forces**
- `app.css` déjà tokenisé en variables CSS (`--ds-*`) → re-tokenisation = remplacement de valeurs.
- Structure 3-colonnes (`ds-shell`) déjà en place dans `base.html`.
- Partials propres (`_partials/analyze_*`, `_partials/results_*`).
- Sémantique HTML correcte (`<header>`, `<main>`, `<aside>`, `aria-*`).

**Frictions**
- Bootstrap CDN encore chargé (`base.html:14,60`) « for now (Phase 1) ».
- `style.css` (163 l.) coexiste avec `app.css` (530 l.) — héritage refonte précédente.
- `!important` dans `app.css:441-444` pour combattre Bootstrap.
- Bug latent `app/__init__.py:22` : `app.context_processor` non appelé comme décorateur (`inject_admin_email` jamais enregistré). **Hors scope refonte** — à signaler ailleurs.

## 4. Tokens cibles (extraits de `DESIGN.md`)

### Couleurs
```
--ds-canvas              #faf9f5   /* page floor — cream tinted */
--ds-surface-soft        #f5f0e8
--ds-surface-card        #efe9de   /* feature cards */
--ds-surface-dark        #181715   /* code blocks, footer ponctuel */
--ds-surface-dark-elev   #252320

--ds-ink                 #141413   /* titres + texte principal */
--ds-body                #3d3d3a
--ds-muted               #6c6a64
--ds-muted-soft          #8e8b82

--ds-primary             #cc785c   /* coral — CTA primaire */
--ds-primary-active      #a9583e
--ds-primary-disabled    #e6dfd8

--ds-hairline            #e6dfd8   /* borders 1px sur cream */
--ds-hairline-soft       #ebe6df

--ds-on-primary          #ffffff
--ds-on-dark             #faf9f5

--ds-success             #5db872
--ds-warning             #d4a017
--ds-error               #c64545
```

### Typo
```
--ds-font-serif    'EB Garamond', Garamond, 'Times New Roman', serif
--ds-font-sans     'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif
--ds-font-mono     'JetBrains Mono', ui-monospace, monospace
```

| Usage | Famille | Taille | Poids | Tracking |
|---|---|---|---|---|
| display-xl (h1 hero) | serif | 64px | 400 | -1.5px |
| display-lg | serif | 48px | 400 | -1px |
| display-md (h2) | serif | 36px | 400 | -0.5px |
| display-sm (h3) | serif | 28px | 400 | -0.3px |
| title-md | sans | 18px | 500 | 0 |
| body-md | sans | 16px | 400 | 0 (line-height 1.55) |
| caption | sans | 13px | 500 | 0 |
| button | sans | 14px | 500 | 0 |

### Espacement (base 4px)
`4 · 8 · 12 · 16 · 24 · 32 · 48 · 96`

### Border-radius
`xs:4 · sm:6 · md:8 · lg:12 · xl:16 · pill:9999`

### Depth
**« Color-block first, shadow rare »** — contraste de surfaces (cream ↔ dark) plutôt qu'ombres. Box-shadow réservée à des hovers ponctuels (`0 1px 3px rgba(20,20,19,0.08)`).

---

## 5. Plan d'exécution

### Phase 0 — Préparation
- [x] 0.1 Créer la branche `feature/claude-design-refonte` depuis `feature/ui-notebook-layout`
- [x] 0.2 Committer `DESIGN.md` à la racine (référence permanente)
- [x] 0.3 Audit de `style.css` → encore utilisé par 4 pages (`about/guide/feedback/login`), suppression reportée en 4.6
- [x] 0.4 Ajouter les `<link>` Google Fonts dans `base.html` (EB Garamond + Inter + JetBrains Mono)
- [x] 0.5 Commit : `chore(ui): prepare claude design refonte (fonts + design spec)`

### Phase 1 — Re-tokenisation `app.css`
- [x] 1.1 Réécrire le bloc `:root` avec les tokens Claude (couleurs + typo + spacing)
- [x] 1.2 Retirer les `radial-gradient` du `body`, passer en cream plat
- [x] 1.3 Smoke test : `/login` répond 200, `app.css` servi correctement
- [x] 1.4 Commit : `ui(claude): re-tokenize app.css with cream/coral palette`

### Phase 2 — Composants visuels
- [x] 2.1 Boutons : `ds-btn` cream/hairline, `ds-btn--primary` coral plein + hover active, `ds-btn--ghost` transparent
- [x] 2.2 Cards & panels : fond `surface-card`, hairline 1px, suppression box-shadow (color-block first)
- [x] 2.3 Header : suppression `backdrop-filter` et `rgba(11,18,32,0.72)`, header cream plat + hairline bottom
- [x] 2.4 Typo : `.ds-title` en serif 28px tracking -0.3px, `.ds-brand__name` en serif 1.35rem, `.ds-kpi__value` en serif éditorial
- [x] 2.5 Inputs / textarea : background canvas + border hairline + focus coral (`!important` gardé jusqu'à Phase 3 / drop Bootstrap)
- [x] 2.6 Drawers mobile : fond canvas opaque, scrim warm-ink (rgba 20,20,19,0.55)
- [x] 2.7 Alertes : variants warning (amber), error (rouge Claude), success (vert Claude), tints alpha 8-10%
- [x] 2.8 Commit : `ui(claude): refit components to warm-editorial visual language`

> Notes Phase 2 :
> - Footer passé en `surface-soft` (au lieu du dark `rgba(11,18,32,0.65)`) — cohérence cream-first. Footer dark Claude réservé aux pages produit, pas pertinent pour Datascope.
> - Suppression des aliases legacy reportée **fin de Phase 3** (après drop Bootstrap), pour éviter casse de `style.css` qui pourrait encore référencer indirectement.
> - Le focus `!important` sur inputs reste — sera retiré en 3.1 quand `form-control` Bootstrap disparaît des templates.

### Phase 3 — Dé-bootstrapification
- [ ] 3.1 Remplacer `form-control`, `form-label`, `alert-info`, `mt-3` etc. dans les 10 templates par des classes `ds-*` natives
- [ ] 3.2 Réécrire les popovers Bootstrap en JS vanilla (ou supprimer si non utilisés)
- [ ] 3.3 Retirer `<link>` Bootswatch et `<script>` Bootstrap de `base.html`
- [ ] 3.4 Commit : `ui(claude): drop bootstrap, finalize ds-* primitives`

> Note : `style.css` ne peut pas être supprimé en Phase 3 — il est encore référencé par les 4 pages secondaires (`page-content`, `card-static`, `login-card`). Suppression déplacée en Phase 4.6.

### Phase 4 — Pages secondaires
- [ ] 4.1 `about.html`
- [ ] 4.2 `guide.html`
- [ ] 4.3 `login.html`
- [ ] 4.4 `feedback.html`
- [ ] 4.5 `admin_users.html` + `admin_feedbacks.html`
- [ ] 4.6 Supprimer `static/style.css` + son `<link>` dans `base.html`
- [ ] 4.7 Commit : `ui(claude): apply design to secondary and admin pages`

### Phase 5 — Polish & QA
- [ ] 5.1 Contrastes WCAG AA (vérifier coral `#cc785c` sur cream `#faf9f5` — peut être limite)
- [ ] 5.2 Tester drawers mobile, menu langue, focus-visible, navigation clavier
- [ ] 5.3 Diff visuel manuel sur 3 pages clés : analyze, results, login
- [ ] 5.4 Vérifier rendu du filtre `markdown` Jinja sur les résultats
- [ ] 5.5 Commit : `ui(claude): a11y polish and visual QA fixes`

---

## 6. Critères de succès

- Aucun appel Bootstrap dans `base.html` ni dans aucun template.
- `style.css` supprimé, `app.css` reste seul fichier de styles applicatifs.
- Toutes les pages rendues utilisent les tokens `--ds-*` mis à jour.
- Pages analyze + results visuellement cohérentes avec la spec Claude (cream/coral/serif).
- Aucune régression fonctionnelle (formulaires, upload, export markdown, auth, switch langue).
- Lighthouse perf ≥ celui d'avant refonte.

## 7. Hors scope (à traiter ailleurs)

- Bug `app/__init__.py:22` (`app.context_processor` non décorateur).
- Persistance JSON → DB (users.json, feedbacks.json).
- Refactor backend `routes.py` (354 lignes, plusieurs `eval()` à remplacer par `json.loads`).
- Migration vers un framework JS (non requis par la spec).

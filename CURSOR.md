# Documentation du projet

Ce fichier décrit la structure et les conventions du blog personnel de David Pilato, accessible sur [david.pilato.fr](https://david.pilato.fr).

## Stack technique

- **Générateur** : [Hugo](https://gohugo.io)
- **Thème** : [Dream](https://g1en.site/hugo-theme-dream/) avec des personnalisations locales
- **Hébergement** : GitHub Pages
- **Stockage PDF** : Google Cloud Storage (`gs://dadoonet-talks/slides/`)

## Structure du projet

```shell
.
├── archetypes/          # Templates pour créer du contenu (posts, talks)
├── content/
│   ├── about/           # Pages "À propos" (multiples fichiers .md combinés)
│   ├── posts/           # Articles de blog
│   └── talks/
│       ├── YYYY/        # Talks par année (YYYY-MM-DD-conference-name/)
│       └── templates/   # Templates d'abstracts multilingues
├── data/                # Données JSON/TOML (icons, countries, socials)
├── layouts/
│   ├── about/           # Layout personnalisé pour la page About
│   ├── partials/        # Fragments réutilisables (pdf.html, author.html...)
│   ├── shortcodes/      # Shortcodes personnalisés (speakerdeck, x)
│   └── talks/           # Templates spécifiques aux talks (single, template)
├── static/
│   ├── speakers/        # Photos des co-speakers (prenom_nom.jpg)
│   └── ...              # Autres assets statiques (favicon, images)
├── themes/dream/        # Thème Hugo (submodule git)
└── hugo.toml            # Configuration principale
```

---

## Talks (`content/talks/`)

Les talks sont organisés par année dans des sous-dossiers : `content/talks/YYYY/YYYY-MM-DD-conference-name/`

### Structure d'un talk

Chaque talk est un dossier contenant :

- `index.md` : Le fichier principal avec le frontmatter et l'abstract
- `cover.*` : Image de couverture (png, jpg, jpeg, avif, webp...) - détectée automatiquement

### Frontmatter d'un talk

```yaml
---
title: "Titre du talk"
conference: 
  name: "Nom de la conférence"
  city: "Ville"
  country: "Pays"
  country_code: "fr"          # Code ISO du pays (fr, us, online...)
  url: "https://..."          # URL de l'événement (optionnel)
  latitude: "48.856614"       # Coordonnées pour la carte (optionnel)
  longitude: "2.352222"

# Speakers - Format moderne (liste d'auteurs)
authors:
  - author: David Pilato
    avatar: /about/david_pilato.png
    link: "https://linkedin.com/in/dadoonet"  # Optionnel
  - author: "Co-speaker Name"
    avatar: /speakers/cospeaker.jpg           # Optionnel
    link: "https://..."                       # Optionnel

# OU format legacy (un seul auteur - rétro-compatible)
# author: David Pilato
# avatar: /about/david_pilato.png

date: YYYY-MM-DD
talk-lang: fr                 # Langue de la présentation (fr ou en)
nolastmod: true               # Ne pas afficher la date de modification
draft: false                  # true = non publié

# Optionnel - Slides PDF
pdf: "YYYY/YYYY-MM-DD-conference-name.pdf"  # Chemin relatif sur GCS

# Optionnel - Image de couverture explicite
cover: "cover.png"            # Par défaut, cherche cover.*

# Optionnel - Template de talk (pour la sidebar "Played X times")
talk: "AI Search"             # Regroupe les talks sur le même sujet

# Optionnel - Vidéo YouTube
youtube: "dQw4w9WgXcQ"        # ID de la vidéo

# Optionnel - Ressources complémentaires
links:
  - title: "Titre du lien"
    url: "https://..."
    description: "Description du lien"

# Optionnel - Tweets/Posts X
x:
  - user: "dadoonet"
    id: "1234567890"

# Optionnel - Nombre de participants
attendees: 200

# Optionnel - Alias d'URL
aliases:
  - /WlpZdt
---
```

### Co-speakers

Les images des co-speakers sont stockées dans `static/speakers/`. Utiliser le format `prenom_nom.jpg` ou `.png`.

Exemple avec plusieurs speakers :

```yaml
authors:
  - author: David Pilato
    avatar: /about/david_pilato.png
  - author: Tugdual Grall
    avatar: /speakers/tugdual_grall.jpg
    link: "https://linkedin.com/in/tgrall"
```

### Sidebar "Played X times"

Quand plusieurs talks partagent la même valeur `talk:` dans le frontmatter, une sidebar apparaît à droite listant toutes les occurrences de ce talk. Cela permet de voir toutes les conférences où le même sujet a été présenté.

**Exemple** : `talk: "ES|QL"` regroupera tous les talks portant sur ES|QL.

Si une page template existe pour ce talk (voir section Templates ci-dessous), un lien vers la page template est affiché.

### Sidebar "At this conference"

Quand plusieurs talks ont le même `conference.name`, une seconde sidebar apparaît listant tous les talks donnés à cette conférence. Utile pour les conférences où vous avez présenté plusieurs sessions.

### Créer un nouveau talk

```sh
hugo new talks/YYYY/YYYY-MM-DD-conference-name/index.md
```

Puis uploader le PDF sur GCS :

```sh
gsutil cp YYYY-MM-DD-conference-name.pdf gs://dadoonet-talks/slides/YYYY/YYYY-MM-DD-conference-name.pdf
```

---

## Templates de talks (`content/talks/templates/`)

Les templates permettent de centraliser les abstracts multilingues d'un talk récurrent. Ils sont affichés sur une page dédiée avec statistiques et liste de toutes les occurrences.

### Structure d'un template

```shell
content/talks/templates/
├── _index.md                 # Page liste des templates
├── esql/
│   └── index.md              # Template ES|QL
├── serverless/
│   └── index.md              # Template Serverless
└── ...
```

### Frontmatter d'un template

```yaml
---
title: "Elasticsearch Query Language: ES|QL"
layout: "template"            # OBLIGATOIRE - utilise layouts/talks/template.html
talk: ES|QL                   # OBLIGATOIRE - doit correspondre aux talks
date: 2024-09-17              # Date de création du template (souvent 1ère occurrence)
nolastmod: true
draft: false

# Versions multilingues de l'abstract
versions:
  - label: "EN"               # Label affiché dans l'onglet
    flag: "gb"                # Code du drapeau (gb, fr, us...)
    title: "English Title"
    abstract: |
      English abstract text...
  - label: "FR"
    flag: "fr"
    title: "Titre en français"
    abstract: |
      Texte de l'abstract en français...

# Optionnel - Ressources liées au talk
links:
  - title: "Demo code"
    url: "https://github.com/..."
    description: "Description"
---
```

### Créer un nouveau template

1. Créer le dossier `content/talks/templates/nom-du-talk/`
2. Créer `index.md` avec le frontmatter ci-dessus
3. S'assurer que `talk:` correspond à la valeur utilisée dans les talks individuels

La page template affiche :

- Statistiques (nombre de présentations, vidéos disponibles, dates)
- Onglets pour chaque version linguistique avec vue "Talk" et "Raw" (pour copier-coller dans les CFP)
- Liste chronologique de toutes les conférences avec cards visuelles

---

## Page About (`content/about/`)

La page About utilise un layout personnalisé qui combine plusieurs fichiers Markdown.

### Structure

```shell
content/about/
├── index.md              # Page principale (frontmatter minimal)
├── 10-me.md              # Section "Who am I?"
├── 20-details.md         # Section détails additionnels
└── david_pilato.png      # Avatar principal
```

### Fonctionnement

Le layout `layouts/about/single.html` :

1. Affiche d'abord les liens sociaux (depuis `data/socials.toml`)
2. Charge tous les fichiers `*.md` du dossier, triés par nom (d'où les préfixes 10-, 20-)
3. Affiche chaque fichier comme une section avec son titre (`title` du frontmatter)

### Exemple de fichier section

```yaml
---
title: Who am I?
---

Contenu Markdown de la section...
```

---

## Posts (`content/posts/`)

Les articles de blog sont dans `content/posts/YYYY-MM-DD-title/`

### Structure d'un post

- `index.md` : Contenu avec frontmatter
- Images et assets directement dans le dossier

### Frontmatter d'un post

```yaml
---
title: "Titre de l'article"
description: "Description courte"
author: David Pilato
avatar: /about/david_pilato.png
tags:
  - tag1
  - tag2
categories:
  - category
series:
  - serie
date: YYYY-MM-DD
nolastmod: true
cover: image.png              # Image de couverture (optionnel)
draft: false
---

Contenu avant le "more"...

<!--more-->

Suite du contenu...
```

### Créer un nouveau post

```sh
hugo new posts/YYYY-MM-DD-something-awesome/index.md
```

---

## Shortcodes personnalisés

### Embed X (Twitter)

```hugo
{{</* x user="dadoonet" id="1234567890" */>}}
```

### Embed Speakerdeck

```hugo
{{</* speakerdeck "slide_id" "wide" */>}}
```

Le second paramètre (`wide`) est optionnel et change le ratio d'aspect.

### Figure (Hugo natif)

```hugo
{{</* figure src="image.png" caption="Légende" */>}}
```

### YouTube (Hugo natif)

```hugo
{{</* youtube VIDEO_ID */>}}
```

### Référence interne

```hugo
{{</* ref "YYYY-MM-DD-post-name" */>}}
```

---

## Taxonomies

Le site utilise plusieurs taxonomies définies dans `hugo.toml` :

- `categories` : Catégories d'articles
- `tags` : Tags/mots-clés
- `series` : Séries d'articles liés
- `cities` : Villes (pour les talks)
- `languages` : Langues des présentations

---

## Développement local

### Installation des dépendances

```sh
[[ -f package-lock.json || -f npm-shrinkwrap.json ]] && npm ci || true
```

### Lancer le serveur de développement

```sh
hugo server --buildFuture --buildDrafts -D
```

- `--buildFuture` : Inclut les contenus datés dans le futur
- `--buildDrafts` / `-D` : Inclut les brouillons

### Build production

```sh
hugo
```

### Mettre à jour le thème

```sh
git submodule update --rebase --remote
```

---

## Layouts personnalisés

### Single talk

Dans `layouts/talks/single.html`, template principal pour l'affichage d'un talk individuel. Gère :

- L'affichage des informations de conférence avec drapeau du pays
- L'affichage des speakers (un ou plusieurs avec avatars)
- L'embed du PDF avec navigation
- La vidéo YouTube
- Les liens/ressources
- Les embeds X
- La sidebar "Played X times" (talks similaires avec lien vers template)
- La sidebar "At this conference" (autres talks à la même conférence)
- La navigation prev/next

### Talk templates

Dans `layouts/talks/template.html`, template pour les pages de templates de talks. Affiche :

- Statistiques du talk (nombre de présentations, vidéos, dates)
- Onglets pour chaque version linguistique
- Vue "Talk" (abstract formaté) et "Raw" (pour CFP)
- Liste chronologique des conférences avec cards
- Navigation entre templates

### About page

In `layouts/about/single.html`, template pour la page About. Combine les liens sociaux avec les fichiers Markdown du dossier `content/about/`.

Template pour la page About. Combine les liens sociaux avec les fichiers Markdown du dossier `content/about/`.

### Author partial

In `layouts/partials/author.html`, gère l'affichage des speakers. Supporte :

- Format moderne : `authors` (liste d'auteurs avec avatar et lien)
- Format legacy : `author` + `avatar` (un seul auteur)

### PDF partial

In `layouts/partials/pdf.html`, affiche un viewer PDF interactif avec les slides. Utilise pdf.js pour le rendu.

### Country flag partial

In `layouts/partials/countryFlag.html`, affiche le drapeau du pays basé sur le `country_code`.

### Lang label partial

In `layouts/partials/langLabel.html`, affiche un badge indiquant la langue du talk (`talk-lang: fr` ou `en`).

### Slides label partial

In `layouts/partials/slidesLabel.html`, affiche un badge si le talk a des slides PDF disponibles.

### Video label partial

In `layouts/partials/videoLabel.html`, affiche un badge si le talk a une vidéo YouTube disponible.

### X embed partial

In `layouts/partials/x-embed.html`, embed de posts X (Twitter).

---

## Conventions de nommage

- **Talks** : `YYYY-MM-DD-conference-name-optional-details`
  - Exemples : `2024-04-18-devoxx-france-2024`, `2024-09-12-chti-jug-esql`
- **Posts** : `YYYY-MM-DD-title-in-kebab-case`
- **BBL (Brown Bag Lunch)** : Inclure `-bbl-` et `-private-event` si c'est un événement privé
  - Exemple : `2024-05-23-bbl-talan-private-event`

---

## Configuration (`hugo.toml`)

Points clés de la configuration :

- `baseURL` : `https://david.pilato.fr`
- `theme` : dream
- `params.talks.pdf_base_url` : URL de base pour les PDFs sur GCS
- `params.showTableOfContents` : Table des matières activée
- `params.imageZoomableInPost` : Zoom sur les images au clic
- `params.showPrevNextPost` : Navigation entre talks/posts

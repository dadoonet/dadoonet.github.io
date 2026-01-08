# Documentation du projet

Ce fichier décrit la structure et les conventions du blog personnel de David Pilato, accessible sur [david.pilato.fr](https://david.pilato.fr).

## Stack technique

- **Générateur** : [Hugo](https://gohugo.io)
- **Thème** : [Dream](https://g1en.site/hugo-theme-dream/) avec des personnalisations locales
- **Hébergement** : GitHub Pages
- **Stockage PDF** : Google Cloud Storage (`gs://dadoonet-talks/slides/`)

## Structure du projet

```
.
├── archetypes/          # Templates pour créer du contenu (posts, talks)
├── content/
│   ├── about/           # Pages "À propos"
│   ├── posts/           # Articles de blog
│   └── talks/           # Présentations (passées et futures)
├── data/                # Données JSON/TOML (icons, countries, socials)
├── layouts/             # Templates Hugo personnalisés
│   ├── partials/        # Fragments réutilisables (pdf.html, x-embed.html...)
│   ├── shortcodes/      # Shortcodes personnalisés (speakerdeck, x)
│   └── talks/           # Templates spécifiques aux talks
├── static/              # Assets statiques (favicon, images)
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
author: David Pilato
avatar: /about/david_pilato.png
date: YYYY-MM-DD
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

### Sidebar "Played X times"

Quand plusieurs talks partagent la même valeur `talk:` dans le frontmatter, une sidebar apparaît à droite listant toutes les occurrences de ce talk. Cela permet de voir toutes les conférences où le même sujet a été présenté.

**Exemple** : `talk: "AI Search"` regroupera tous les talks portant sur l'IA et la recherche.

### Créer un nouveau talk

```sh
hugo new talks/YYYY/YYYY-MM-DD-conference-name/index.md
```

Puis uploader le PDF sur GCS :
```sh
gsutil cp YYYY-MM-DD-conference-name.pdf gs://dadoonet-talks/slides/YYYY/YYYY-MM-DD-conference-name.pdf
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

### `layouts/talks/single.html`
Template principal pour l'affichage d'un talk individuel. Gère :
- L'affichage des informations de conférence avec drapeau du pays
- L'embed du PDF avec navigation
- La vidéo YouTube
- Les liens/ressources
- Les embeds X
- La sidebar "Played X times" (talks similaires)
- La navigation prev/next

### `layouts/partials/pdf.html`
Affiche un viewer PDF interactif avec les slides. Utilise pdf.js pour le rendu.

### `layouts/partials/countryFlag.html`
Affiche le drapeau du pays basé sur le `country_code`.

### `layouts/partials/x-embed.html`
Embed de posts X (Twitter).

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

- `baseURL` : https://david.pilato.fr
- `theme` : dream
- `params.talks.pdf_base_url` : URL de base pour les PDFs sur GCS
- `params.showTableOfContents` : Table des matières activée
- `params.imageZoomableInPost` : Zoom sur les images au clic
- `params.showPrevNextPost` : Navigation entre talks/posts


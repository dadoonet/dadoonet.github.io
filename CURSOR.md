# Project Documentation

This file describes the structure and conventions of David Pilato's personal blog, accessible at [david.pilato.fr](https://david.pilato.fr).

## Tech Stack

- **Generator**: [Hugo](https://gohugo.io)
- **Theme**: [hugo-theme-devrel](https://github.com/dadoonet/hugo-theme-devrel) (DevRel overlay) → imports [Dream](https://g1en.site/hugo-theme-dream/)
- **Hosting**: GitHub Pages
- **PDF Storage**: Google Cloud Storage (`gs://dadoonet-talks/slides/`)

## Project Structure

```shell
.
├── content/
│   ├── about/           # "About" pages (multiple .md files combined)
│   ├── posts/           # Blog articles
│   └── talks/
│       ├── YYYY/        # Talks by year (YYYY-MM-DD-conference-name/)
│       └── templates/   # Multilingual abstract templates
├── data/                # Personal data (socials)
├── static/
│   ├── speakers/        # Co-speaker photos (firstname_lastname.jpg)
│   └── ...              # Favicon, CNAME, etc.
├── go.mod               # Hugo module → github.com/dadoonet/hugo-theme-devrel
└── hugo.toml            # Site identity + integrations
```

Layouts, archetypes, and theme CSS live in the [devrel](https://github.com/dadoonet/hugo-theme-devrel) module (not in this repo).

---

## Talks (`content/talks/`)

Talks are organized by year in subfolders: `content/talks/YYYY/YYYY-MM-DD-conference-name/`

### Talk Structure

Each talk is a folder containing:

- `index.md`: The main file with frontmatter and abstract
- `cover.*`: Cover image (png, jpg, jpeg, **avif**, webp...) - automatically detected

### Talk Frontmatter

```yaml
---
title: "Talk Title"
conference: 
  name: "Conference Name"
  city: "City"
  country: "Country"
  country_code: "fr"          # ISO country code (fr, us, online...)
  url: "https://..."          # Event URL (optional)
  latitude: "48.856614"       # Coordinates for the map (optional)
  longitude: "2.352222"

# Speakers - Modern format (list of authors)
authors:
  - author: David Pilato
    avatar: /about/david_pilato.avif
    link: "https://linkedin.com/in/dadoonet"  # Optional
  - author: "Co-speaker Name"
    avatar: /speakers/cospeaker.avif           # Optional
    link: "https://..."                       # Optional

# OR legacy format (single author - backward compatible)
# author: David Pilato
# avatar: /about/david_pilato.avif

date: YYYY-MM-DD
talk-lang: fr                 # Presentation language (fr or en)
nolastmod: true               # Don't display modification date
draft: false                  # true = unpublished

# Optional - PDF Slides (relative to params.talks.pdf_base_url)
pdf: "YYYY/YYYY-MM-DD-conference-name.pdf"

# Optional - Explicit cover image
cover: "cover.avif"            # By default, looks for cover.*

# Optional - Talk template (for "Played X times" sidebar)
talk: "AI Search"             # Groups talks on the same topic

# Optional - YouTube video
youtube: "dQw4w9WgXcQ"        # Video ID

# Optional - Additional resources
links:
  - title: "Link Title"
    url: "https://..."
    description: "Link description"

# Optional - Social posts (X, Bluesky, LinkedIn)
social:
  - "https://x.com/dadoonet/status/1234567890"
  - "https://bsky.app/profile/klf37.bsky.social/post/3muol6taevk2h"
  - "https://www.linkedin.com/embed/feed/update/urn:li:activity:7501648269345812481"

# Optional - Number of attendees
attendees: 200

# Optional - URL alias
aliases:
  - /WlpZdt
---
```

### Co-speakers

Co-speaker images are stored in `static/speakers/`. Use the format `firstname_lastname.avif`.

### "Played X times" Sidebar

When multiple talks share the same `talk:` value in the frontmatter, a sidebar appears listing all occurrences. If a template page exists under `content/talks/templates/`, a link is shown.

### Creating a New Talk

```sh
hugo new talks/YYYY/YYYY-MM-DD-conference-name/index.md
```

Then upload the PDF to GCS:

```sh
gsutil cp YYYY-MM-DD-conference-name.pdf gs://dadoonet-talks/slides/YYYY/YYYY-MM-DD-conference-name.pdf
```

---

## Talk Templates (`content/talks/templates/`)

```yaml
---
title: "Elasticsearch Query Language: ES|QL"
layout: "template"            # REQUIRED
talk: ES|QL                   # REQUIRED - must match the talks
nolastmod: true
draft: false
versions:
  - label: "EN"
    flag: "gb"
    title: "English Title"
    abstract: |
      English abstract text...
---
```

Satellite pages (layouts provided by the theme):

| Path | Front matter |
|------|----------------|
| `content/talks/all/_index.md` | `layout: "all"` |
| `content/talks/map/_index.md` | `layout: "map"` |
| `content/talks/videos/_index.md` | `layout: "videos"` |
| `content/talks/templates/_index.md` | `layout: "templates"` |

The talks map is derived from `conference.latitude` / `longitude` on talk pages.

---

## About Page (`content/about/`)

```shell
content/about/
├── index.md              # Main page (minimal frontmatter)
├── 10-me.md              # "Who am I?" section
├── 20-details.md         # Additional details section
└── david_pilato.avif     # Main avatar
```

Social links come from `data/socials.toml`. Numbered `*.md` files are rendered as sections in name order.

---

## Posts (`content/posts/`)

```shell
content/posts/YYYY-MM-DD-title/index.md
```

```sh
hugo new posts/YYYY-MM-DD-something-awesome/index.md
```

---

## Configuration (`hugo.toml`)

- `baseURL`, identity (`author`, `avatar`, `email`, Utterances)
- Module import: `github.com/dadoonet/hugo-theme-devrel` (pulls Dream)
- `params.talks.pdf_base_url`: GCS slides prefix
- `params.search.enabled`: Pagefind UI (`/search` + Ctrl/Cmd+K)
- Taxonomies: categories, tags, series, cities, languages

### Updating the theme

```sh
hugo mod get -u github.com/dadoonet/hugo-theme-devrel
hugo mod tidy
```

### Search index

```sh
npm ci
hugo --minify --buildFuture
npx pagefind --site public
```

---

## Local Development

```sh
hugo mod tidy
hugo server --buildFuture --buildDrafts -D
```

### Production Build

```sh
hugo
```

---

## Naming Conventions

- **Talks**: `YYYY-MM-DD-conference-name-optional-details`
- **Posts**: `YYYY-MM-DD-title-in-kebab-case`
- **BBL**: Include `-bbl-` and `-private-event` when private

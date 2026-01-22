# Project Documentation

This file describes the structure and conventions of David Pilato's personal blog, accessible at [david.pilato.fr](https://david.pilato.fr).

## Tech Stack

- **Generator**: [Hugo](https://gohugo.io)
- **Theme**: [Dream](https://g1en.site/hugo-theme-dream/) with local customizations
- **Hosting**: GitHub Pages
- **PDF Storage**: Google Cloud Storage (`gs://dadoonet-talks/slides/`)

## Project Structure

```shell
.
├── archetypes/          # Templates for creating content (posts, talks)
├── content/
│   ├── about/           # "About" pages (multiple .md files combined)
│   ├── posts/           # Blog articles
│   └── talks/
│       ├── YYYY/        # Talks by year (YYYY-MM-DD-conference-name/)
│       └── templates/   # Multilingual abstract templates
├── data/                # JSON/TOML data (icons, countries, socials)
├── layouts/
│   ├── about/           # Custom layout for the About page
│   ├── partials/        # Reusable fragments (pdf.html, author.html...)
│   ├── shortcodes/      # Custom shortcodes (speakerdeck, x)
│   └── talks/           # Talk-specific templates (single, template)
├── static/
│   ├── speakers/        # Co-speaker photos (firstname_lastname.jpg)
│   └── ...              # Other static assets (favicon, images)
├── themes/dream/        # Hugo theme (git submodule)
└── hugo.toml            # Main configuration
```

---

## Talks (`content/talks/`)

Talks are organized by year in subfolders: `content/talks/YYYY/YYYY-MM-DD-conference-name/`

### Talk Structure

Each talk is a folder containing:

- `index.md`: The main file with frontmatter and abstract
- `cover.*`: Cover image (png, jpg, jpeg, avif, webp...) - automatically detected

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
    avatar: /about/david_pilato.png
    link: "https://linkedin.com/in/dadoonet"  # Optional
  - author: "Co-speaker Name"
    avatar: /speakers/cospeaker.jpg           # Optional
    link: "https://..."                       # Optional

# OR legacy format (single author - backward compatible)
# author: David Pilato
# avatar: /about/david_pilato.png

date: YYYY-MM-DD
talk-lang: fr                 # Presentation language (fr or en)
nolastmod: true               # Don't display modification date
draft: false                  # true = unpublished

# Optional - PDF Slides
pdf: "YYYY/YYYY-MM-DD-conference-name.pdf"  # Relative path on GCS

# Optional - Explicit cover image
cover: "cover.png"            # By default, looks for cover.*

# Optional - Talk template (for "Played X times" sidebar)
talk: "AI Search"             # Groups talks on the same topic

# Optional - YouTube video
youtube: "dQw4w9WgXcQ"        # Video ID

# Optional - Additional resources
links:
  - title: "Link Title"
    url: "https://..."
    description: "Link description"

# Optional - X Tweets/Posts
x:
  - user: "dadoonet"
    id: "1234567890"

# Optional - Number of attendees
attendees: 200

# Optional - URL alias
aliases:
  - /WlpZdt
---
```

### Co-speakers

Co-speaker images are stored in `static/speakers/`. Use the format `firstname_lastname.jpg` or `.png`.

Example with multiple speakers:

```yaml
authors:
  - author: David Pilato
    avatar: /about/david_pilato.png
  - author: Tugdual Grall
    avatar: /speakers/tugdual_grall.jpg
    link: "https://linkedin.com/in/tgrall"
```

### "Played X times" Sidebar

When multiple talks share the same `talk:` value in the frontmatter, a sidebar appears on the right listing all occurrences of that talk. This allows seeing all conferences where the same topic was presented.

**Example**: `talk: "ES|QL"` will group all talks about ES|QL.

If a template page exists for this talk (see Templates section below), a link to the template page is displayed.

### "At this conference" Sidebar

When multiple talks have the same `conference.name`, a second sidebar appears listing all talks given at that conference. Useful for conferences where you presented multiple sessions.

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

Templates allow centralizing multilingual abstracts for a recurring talk. They are displayed on a dedicated page with statistics and a list of all occurrences.

### Template Structure

```shell
content/talks/templates/
├── _index.md                 # Templates list page
├── esql/
│   └── index.md              # ES|QL template
├── serverless/
│   └── index.md              # Serverless template
└── ...
```

### Template Frontmatter

```yaml
---
title: "Elasticsearch Query Language: ES|QL"
layout: "template"            # REQUIRED - uses layouts/talks/template.html
talk: ES|QL                   # REQUIRED - must match the talks
nolastmod: true
draft: false

# Multilingual versions of the abstract
versions:
  - label: "EN"               # Label displayed in the tab
    flag: "gb"                # Flag code (gb, fr, us...)
    title: "English Title"
    abstract: |
      English abstract text...
  - label: "FR"
    flag: "fr"
    title: "Titre en français"
    abstract: |
      French abstract text...

# Optional - Resources related to the talk
links:
  - title: "Demo code"
    url: "https://github.com/..."
    description: "Description"
---
```

### Creating a New Template

1. Create the folder `content/talks/templates/talk-name/`
2. Create `index.md` with the frontmatter above
3. Ensure `talk:` matches the value used in individual talks

The template page displays:

- Statistics (number of presentations, available videos, dates)
- Tabs for each language version with "Talk" and "Raw" views (for copy-pasting into CFPs)
- Chronological list of all conferences with visual cards

---

## About Page (`content/about/`)

The About page uses a custom layout that combines multiple Markdown files.

### Structure

```shell
content/about/
├── index.md              # Main page (minimal frontmatter)
├── 10-me.md              # "Who am I?" section
├── 20-details.md         # Additional details section
└── david_pilato.png      # Main avatar
```

### How It Works

The `layouts/about/single.html` layout:

1. First displays social links (from `data/socials.toml`)
2. Loads all `*.md` files from the folder, sorted by name (hence the 10-, 20- prefixes)
3. Displays each file as a section with its title (`title` from frontmatter)

### Section File Example

```yaml
---
title: Who am I?
---

Markdown content of the section...
```

---

## Posts (`content/posts/`)

Blog articles are in `content/posts/YYYY-MM-DD-title/`

### Post Structure

- `index.md`: Content with frontmatter
- Images and assets directly in the folder

### Post Frontmatter

```yaml
---
title: "Article Title"
description: "Short description"
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
cover: image.png              # Cover image (optional)
draft: false
---

Content before the "more"...

<!--more-->

Rest of the content...
```

### Creating a New Post

```sh
hugo new posts/YYYY-MM-DD-something-awesome/index.md
```

---

## Custom Shortcodes

### X (Twitter) Embed

```hugo
{{</* x user="dadoonet" id="1234567890" */>}}
```

### Speakerdeck Embed

```hugo
{{</* speakerdeck "slide_id" "wide" */>}}
```

The second parameter (`wide`) is optional and changes the aspect ratio.

### Figure (Hugo native)

```hugo
{{</* figure src="image.png" caption="Caption" */>}}
```

### YouTube (Hugo native)

```hugo
{{</* youtube VIDEO_ID */>}}
```

### Internal Reference

```hugo
{{</* ref "YYYY-MM-DD-post-name" */>}}
```

---

## Taxonomies

The site uses several taxonomies defined in `hugo.toml`:

- `categories`: Article categories
- `tags`: Tags/keywords
- `series`: Related article series
- `cities`: Cities (for talks)
- `languages`: Presentation languages

---

## Local Development

### Installing Dependencies

```sh
[[ -f package-lock.json || -f npm-shrinkwrap.json ]] && npm ci || true
```

### Running the Development Server

```sh
hugo server --buildFuture --buildDrafts -D
```

- `--buildFuture`: Includes content dated in the future
- `--buildDrafts` / `-D`: Includes drafts

### Production Build

```sh
hugo
```

### Updating the Theme

```sh
git submodule update --rebase --remote
```

---

## Custom Layouts

### Single Talk

In `layouts/talks/single.html`, main template for displaying an individual talk. Handles:

- Conference information display with country flag
- Speakers display (one or multiple with avatars)
- PDF embed with navigation
- YouTube video
- Links/resources
- X embeds
- "Played X times" sidebar (similar talks with link to template)
- "At this conference" sidebar (other talks at the same conference)
- Prev/next navigation

### Talk Templates

In `layouts/talks/template.html`, template for talk template pages. Displays:

- Talk statistics (number of presentations, videos, dates)
- Tabs for each language version
- "Talk" view (formatted abstract) and "Raw" view (for CFP)
- Chronological list of conferences with cards
- Navigation between templates

### About Page

In `layouts/about/single.html`, template for the About page. Combines social links with Markdown files from the `content/about/` folder.

### Author Partial

In `layouts/partials/author.html`, handles speaker display. Supports:

- Modern format: `authors` (list of authors with avatar and link)
- Legacy format: `author` + `avatar` (single author)

### PDF Partial

In `layouts/partials/pdf.html`, displays an interactive PDF viewer with slides. Uses pdf.js for rendering.

### Country Flag Partial

In `layouts/partials/countryFlag.html`, displays the country flag based on `country_code`.

### Lang Label Partial

In `layouts/partials/langLabel.html`, displays a badge indicating the talk language (`talk-lang: fr` or `en`).

### Slides Label Partial

In `layouts/partials/slidesLabel.html`, displays a badge if the talk has PDF slides available.

### Video Label Partial

In `layouts/partials/videoLabel.html`, displays a badge if the talk has a YouTube video available.

### X Embed Partial

In `layouts/partials/x-embed.html`, embeds X (Twitter) posts.

---

## Naming Conventions

- **Talks**: `YYYY-MM-DD-conference-name-optional-details`
  - Examples: `2024-04-18-devoxx-france-2024`, `2024-09-12-chti-jug-esql`
- **Posts**: `YYYY-MM-DD-title-in-kebab-case`
- **BBL (Brown Bag Lunch)**: Include `-bbl-` and `-private-event` if it's a private event
  - Example: `2024-05-23-bbl-talan-private-event`

---

## Configuration (`hugo.toml`)

Key configuration points:

- `baseURL`: `https://david.pilato.fr`
- `theme`: dream
- `params.talks.pdf_base_url`: Base URL for PDFs on GCS
- `params.showTableOfContents`: Table of contents enabled
- `params.imageZoomableInPost`: Click to zoom on images
- `params.showPrevNextPost`: Navigation between talks/posts

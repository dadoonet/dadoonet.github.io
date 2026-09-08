---
title: 'hugo-theme-devrel: the theme behind this site, now yours'
description: "I extracted the Hugo layouts that power david.pilato.fr into a reusable DevRel overlay — talks, templates, map, videos, and Pagefind search included."
author: David Pilato
avatar: /about/david_pilato.avif
tags:
  - hugo
  - theme
  - opensource
  - community
  - cursor
categories:
  - projects
date: '2026-09-07T19:30:00+02:00'
nolastmod: true
cover: cover.avif
draft: false
---

I spent the first half of 2026 turning [noti.st](https://noti.st/dadoonet) into this website. Then I spent the last few days doing the obvious next step: **extracting the speaker bits into a theme other Developer Advocates can actually use**.

It is called [`hugo-theme-devrel`](https://github.com/dadoonet/hugo-theme-devrel), it is MIT, and this page is running on it.

<!--more-->

If you already have a Hugo site, the entire install is one module import. If you do not, there is a fictional `exampleSite` at [devrel.hugo.pilato.fr](https://devrel.hugo.pilato.fr/) so you can see every layout without cloning my biography.

{{< figure src="cover.avif" caption="The talks page on david.pilato.fr — featured cards, then the archive." >}}

## Why a theme, not a gist of templates?

In [January]({{< ref "2026-01-10-13-years-migrating-to-hugo-with-cursor" >}}) I wrote about migrating hundreds of talks into Hugo. The layouts lived in *this* repository: talk pages with PDF.js, a “Played N times” sidebar, a Leaflet map, multilingual templates, YouTube galleries, social embeds.

That works until a friend asks “can I reuse this?” and the honest answer is “sure, after you delete my face, my GCS bucket, and forty hardcoded assumptions.”

So the generic parts moved to [`github.com/dadoonet/hugo-theme-devrel`](https://github.com/dadoonet/hugo-theme-devrel). This repo keeps identity: content, `data/socials.toml`, `params.author`, the PDF bucket URL. The theme keeps the machinery.

It is **not a fork of Dream**. It is an overlay. [Dream](https://github.com/g1eny0ung/hugo-theme-dream) stays upstream; `devrel` imports it as a Hugo module and replaces the layouts that matter for a speaker site. You import **one** module:

```toml
[module]
  [[module.imports]]
    path = "github.com/dadoonet/hugo-theme-devrel"
```

Do not set `theme = ["devrel", "dream"]`. Dream arrives as a dependency. Attribution stays in the footer and in `LICENSE-DREAM`.

Yes, Cursor helped. I already confessed that habit in [The Augmented Developer]({{< ref "2026-02-06-the-augmented-developer" >}}). The interesting part is not the AI, it is the split: **theme vs site**, so the next person does not have to replay my 200+ commits.

## What you get

A DevRel homepage is not only a blog. Mine has to answer: *where did you speak, with which slides, in which language, and is there a video?*

The overlay adds:

- **Talks** with conference city/country, optional coordinates, PDF slides, YouTube, co-speakers, and `social:` URLs (X, Bluesky, LinkedIn).
- **Talk templates** — one canonical abstract, EN/FR tabs, a “Raw” view for CFPs, and every occurrence of that talk.
- **A map** built from `conference.latitude` / `longitude`. No extra geo file.
- **A videos page** grouped by year.
- **An all-talks archive** grouped by year, with a map for each year.
- **About** assembled from numbered Markdown files (`10-me.md`, `20-details.md`, …).
- **Pagefind search** — the loupe in the nav, or Ctrl/Cmd+K.

{{< figure src="talk-single.avif" caption="A talk page: slides in the middle, “Played N times” and “Gave N talks at this conference” on the side." >}}

## The speaker archive is three indexes

`/talks` is the landing page (featured cards, then the rest). The pages I actually live in are the three satellites.

**`/talks/all`** is the full archive: jump links per year (with counts), then a card grid — cover, language, slides/video badges, conference, date. Scroll a year and you get a **map of that year only**, which is different from the global `/talks/map`.

{{< figure src="talks-all.avif" caption="`/talks/all` — year navigation and the 2026 card grid. Badges tell you if slides or a recording exist." >}}

{{< figure src="talks-all-year.avif" caption="Same page, a bit lower: the 2026 map. Eight talks, seven cities, two countries, one online." >}}

**`/talks/videos`** keeps only sessions with a `youtube:` id. Same year jump, red accents, 16:9 cards, click through to `#video` on the talk.

{{< figure src="talks-videos.avif" caption="`/talks/videos` — 100 recordings on this site, grouped by year." >}}

**`/talks/templates`** is the catalog of recurring topics, sorted by last played date. Open one template and you get stats, language tabs, **Talk** vs **Raw** (the CFP paste view), and every conference where that talk ran.

{{< figure src="talks-templates.avif" caption="`/talks/templates` — 23 topics. “Played 220 times” is not a flex, it is a sorting key." >}}

{{< figure src="talk-template.avif" caption="One template: first/last dates, EN/FR, Talk vs Raw. The conference list is further down the page." >}}

{{< figure src="talks-map.avif" caption="The global talks map at `/talks/map`. Pins come from front matter. The counts are computed at build time." >}}

## Search that does not need Elasticsearch (yes, I know)

I ship Elasticsearch for a living. This site is still a pile of static HTML on GitHub Pages. [Pagefind](https://pagefind.app) indexes the public folder after `hugo` and the theme wires the Component UI: a centered modal, covers in the results, section filters (posts, talks, templates, videos, about) once you type, type icons that survive dark mode.

Hit **Ctrl+K** or **Cmd+K**. Or click the loupe.

{{< figure src="search.avif" caption="Pagefind modal after typing “elasticsearch”. Filters appear on the same row as the query." >}}

The build is two steps:

```sh
# Generate static HTML pages so they can be indexed
hugo --minify
# Generate the Pagefind index
npx pagefind --site public
```

Empty queries (browse / filter only) sort by date. As soon as you type, relevance wins. That matches how I actually use a speaker archive: “what did I say about ES|QL last year?” vs “show me everything tagged talks.”

## The example site is no longer a stub

The first version of `exampleSite` had one post and two talks. That is enough to prove the module loads. It is not enough to see the map, the “Played N times” sidebar, co-speakers, or search covers.

It now follows a fictional advocate named **Alex Rivera**: blog posts, talks in several cities and online, bilingual templates, a co-speaker, recordings, and social embeds. Enough to walk `/talks`, `/talks/all`, `/talks/videos`, `/talks/templates`, and search without cloning my biography.

Alex does not exist. Copy the folders, not the bio. Source: [`exampleSite`](https://github.com/dadoonet/hugo-theme-devrel/tree/main/exampleSite). Live demo: [devrel.hugo.pilato.fr](https://devrel.hugo.pilato.fr/).

{{< figure src="home.avif" caption="The homepage is still a Dream post grid. The overlay is most visible once you leave `/` for `/talks`." >}}

## How to try it

### 1. Download Hugo

Install the **extended** edition from the [Hugo installation guide](https://gohugo.io/installation/). Dream compiles CSS at build time, so a non-extended binary will fail. Check with `hugo version`; the line should mention `extended`. GitHub Pages builds of this site use the extended Linux binary; locally, pick the extended package for your OS.

### 2. Turn the site into a Hugo module

Skip this if `go.mod` already exists.

```sh
hugo mod init github.com/you/your-site
```

### 3. Import the theme

In `hugo.toml` (or `hugo.yaml`), import **only** `devrel`. Dream arrives as a module dependency. Do not set `theme = ["devrel", "dream"]`.

```toml
[module]
  [[module.imports]]
    path = "github.com/dadoonet/hugo-theme-devrel"
```

Then:

```sh
hugo mod get github.com/dadoonet/hugo-theme-devrel
```

### 4. Set your identity

Still in `hugo.toml`:

```toml
[params]
  author = "Your Name"
  avatar = "/about/you.avif"
  headerTitle = "Your Name"
  motto = "Developer Advocate"
  email = "you@example.org"
  siteStartYear = 2024

[params.talks]
  # Prefix for talk pdf: paths. Empty = a PDF in the page bundle or a site-relative file.
  pdf_base_url = ""
```

Put the avatar file at `static/about/you.avif` (or whatever path you set). `params.author` / `params.avatar` are the defaults for archetypes and for talk bylines when you omit `avatar:` in front matter.

### 5. Add the talk index pages

The overlay expects a few `_index.md` files. Copy them from [`exampleSite/content/talks/`](https://github.com/dadoonet/hugo-theme-devrel/tree/main/exampleSite/content/talks) or create them:

| Path                                | Front matter          |
|-------------------------------------|-----------------------|
| `content/talks/_index.md`           | `title: "Talks"`      |
| `content/talks/all/_index.md`       | `layout: "all"`       |
| `content/talks/map/_index.md`       | `layout: "map"`       |
| `content/talks/videos/_index.md`    | `layout: "videos"`    |
| `content/talks/templates/_index.md` | `layout: "templates"` |

Example — `content/talks/all/_index.md`:

```yaml
---
title: "All talks"
layout: "all"
---
```

Search is shipped by the theme as `content/search/_index.md`. Override that file in your site if you need a custom title; disable with `params.search.enabled = false`.

### 6. Create a talk

```sh
hugo new talks/2026/2026-09-08-my-conference/index.md
```

Minimal front matter (a `cover.*` file in the same folder is picked up automatically; `avatar:` is inferred from the author name):

```yaml
---
title: "Talk Title"
conference:
  name: "Conference Name"
  city: "City"
  country: "Country"
  country_code: "fr"       # ISO code, or "online"
  url: "https://example.org/event"
  latitude: "48.856614"    # optional — used by the map
  longitude: "2.352222"
authors:
  - author: "Your Name"
date: 2026-09-08
talk-lang: en
talk: "Topic Name"         # groups occurrences + links to the template
youtube: "VIDEO_ID"        # optional
pdf: "2026/2026-09-08-my-conference.pdf"
---
```

Optional `social:` is a list of public X, Bluesky, or LinkedIn post URLs; the theme embeds them on the talk page.

For a recurring topic, add `content/talks/templates/<slug>/index.md` with `layout: "template"` and the same `talk:` value. The [README](https://github.com/dadoonet/hugo-theme-devrel#content-conventions) has the full YAML, including EN/FR `versions:`.

### 7. Build the HTML, then the search index

Pagefind reads the generated `public/` folder, so Hugo must run first:

```sh
# Generate static HTML pages so they can be indexed
hugo --minify
# Generate the Pagefind index
npx pagefind --site public
```

For local preview, `hugo server` is enough after you have indexed once. If you add a Pagefind mount, redeclare the default mounts as well (Hugo replaces them otherwise):

```toml
[[module.mounts]]
  source = "content"
  target = "content"
[[module.mounts]]
  source = "static"
  target = "static"
[[module.mounts]]
  source = "data"
  target = "data"
[[module.mounts]]
  source = "public/pagefind"
  target = "static/pagefind"
  disableWatch = true
```

Wire both commands into your CI or a `package.json` `build` script. That is what this site does on GitHub Pages.

### 8. Steal the example, not the biography

If you prefer a known-good tree to a blank `hugo new`, copy [`exampleSite`](https://github.com/dadoonet/hugo-theme-devrel/tree/main/exampleSite) and replace Alex Rivera. The live preview is [devrel.hugo.pilato.fr](https://devrel.hugo.pilato.fr/).

If you are a Developer Advocate who is tired of a speaker page that only exists in a slide appendix: clone it, delete Alex, put your talks in `content/talks/YYYY/`. And if you find a bug, [open an issue](https://github.com/dadoonet/hugo-theme-devrel/issues) — I will probably fix it with the same tool that helped me extract the theme in the first place. 😉

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

{{< figure src="cover.avif" caption="The talks page on david.pilato.fr — featured cards, then the archive. This is also `images/screenshot.png` in the theme repo." >}}

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

{{< figure src="search.avif" caption="Pagefind modal after typing “elasticsearch”. Filters appear on the same row as the query. This is the screenshot I wanted in the README." >}}

The build is two steps:

```sh
hugo --minify
npx pagefind --site public
```

Empty queries (browse / filter only) sort by date. As soon as you type, relevance wins. That matches how I actually use a speaker archive: “what did I say about ES|QL last year?” vs “show me everything tagged talks.”

## The example site is no longer a stub

The first version of `exampleSite` had one post and two talks. That is enough to prove the module loads. It is not enough to see the map, the “Played N times” sidebar, co-speakers, or search covers.

It now follows a fictional advocate named **Alex Rivera**:

- 4 blog posts with covers
- 7 talks in Lyon, Antwerp, Brussels, London, Málaga, Oslo, and online
- 3 templates with English and French abstracts
- a co-speaker on one session
- sample YouTube ids so `/talks/videos/` is not an empty room

Alex does not exist. Copy the folders, not the bio. Demo: [devrel.hugo.pilato.fr](https://devrel.hugo.pilato.fr/).

## Screenshots for the Hugo gallery

If I ever submit this to [themes.gohugo.io](https://themes.gohugo.io/), the rules are picky on purpose: an `images/` directory, **no browser chrome**, 3:2 ratio.

| File                    | Size                                |
|-------------------------|-------------------------------------|
| `images/screenshot.png` | 1500×1000 — talks page of this site |
| `images/tn.png`         | 900×600 — same crop, thumbnail      |

Extra shots (`talks-all.png`, `talks-videos.png`, `talks-templates.png`, `search.png`, …) live next to them and are linked from the [theme README](https://github.com/dadoonet/hugo-theme-devrel#screenshots). Absolute GitHub URLs, because the Hugo themes site does not resolve relative `images/` paths in a README.

{{< figure src="home.avif" caption="The homepage is still a Dream post grid. The overlay is most visible once you leave `/` for `/talks`." >}}

## How to try it

1. `hugo mod init github.com/you/your-site` if you are not a module yet.
2. Import `github.com/dadoonet/hugo-theme-devrel` as above.
3. Set `params.author`, `params.avatar`, `params.talks.pdf_base_url` if your slides live on a bucket.
4. Create `content/talks/all/_index.md`, `map`, `videos`, `templates` with the layouts documented in the README — or copy them from `exampleSite/`.
5. Run Pagefind after Hugo.

This website is the production reference. The example site is the toy. The README is the contract.

If you are a Developer Advocate who is tired of a speaker page that only exists in a slide appendix: clone it, delete Alex, put your talks in `content/talks/YYYY/`. And if you find a bug, [open an issue](https://github.com/dadoonet/hugo-theme-devrel/issues) — I will probably fix it with the same tool that helped me extract the theme in the first place. 😉

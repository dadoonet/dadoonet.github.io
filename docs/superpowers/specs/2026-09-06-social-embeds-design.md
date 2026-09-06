# Social embeds (X, Bluesky, LinkedIn)

Date: 2026-09-06

## Goal

Replace the talk-only `x:` frontmatter list with a single `social:` list that can mix X, Bluesky, and LinkedIn posts. Render them in list order in the existing « Buzz et feedback » block. Migrate every talk off `x:` in the same change. Do not keep compatibility with `x:`.

Blog shortcode `{{< x >}}` is out of scope and stays as-is.

## Authoring contract

Each talk that has social posts declares:

```yaml
social:
  - type: x          # required: x | bluesky | linkedin
    user: "handle"   # required
    id: "post-id"    # required
```

Order in the list is display order. Items from different networks may be interleaved.

| `type` | `user` | `id` | Post URL used internally |
| --- | --- | --- | --- |
| `x` | X handle without `@` | Numeric status id | `https://x.com/{user}/status/{id}` |
| `bluesky` | Handle, including `.bsky.social` when present | Post rkey | `https://bsky.app/profile/{user}/post/{id}` |
| `linkedin` | Vanity slug from the `/posts/{user}_…` URL | Numeric `activity-` id | Embed uses `urn:li:activity:{id}` only |

LinkedIn `user` is kept for symmetry with X and Bluesky. It is not used to build `linkedin.com/in/…` or `linkedin.com/company/…` (the slug can be either). The iframe uses only `id`.

Unknown `type`, or a missing `type` / `user` / `id`, is a build error.

## UI

On `layouts/talks/single.html`:

- Show the block when `.Params.social` is non-empty.
- Keep the current heading and intro: « Buzz et feedback » / « Here's what was said about this presentation on social media. »
- Range over `.Params.social` in order. Do not group by network.
- Wrapper class: `social-embeds` (replaces `x-embeds`).

Do not show the block for talks with no `social:` list.

## Components

### Dispatcher: `layouts/partials/social-embed.html`

Input: `type`, `user`, `id`, optional `ctx`.

Switch on `type` and call the matching embed partial. `errorf` on unknown type or missing fields.

### `layouts/partials/x-embed.html`

Keep the current oEmbed flow:

1. Honor `site.Config.Privacy.X` (`Disable` skips the embed).
2. `GET https://publish.x.com/oembed?url=…&dnt=…`
3. Output `.html` as `safeHTML`.
4. oEmbed failure: `warnidf`, build continues, no markup for that item.

### `layouts/partials/bluesky-embed.html`

Same pattern as X, without Hugo privacy config (none exists for Bluesky):

1. Post URL: `https://bsky.app/profile/{user}/post/{id}`
2. `GET https://embed.bsky.app/oembed?url={post URL}`
3. Unmarshal JSON, take `.html`.
4. Strip any `<script … src="https://embed.bsky.app/embed.js"…>` from that HTML so the script is not repeated per post.
5. Output the remaining HTML as `safeHTML`.
6. oEmbed failure: `warnidf`, build continues.

Load `https://embed.bsky.app/embed.js` once in the talk page `js` block if at least one item has `type: bluesky`.

### `layouts/partials/linkedin-embed.html`

No oEmbed. Always emit:

```html
<div class="linkedin-embed">
  <iframe
    src="https://www.linkedin.com/embed/feed/update/urn:li:activity:{id}"
    title="LinkedIn post"
    loading="lazy"
    allowfullscreen></iframe>
</div>
```

No extra fallback link in v1. The iframe `src` is the official embed. The permalink, if needed later, is `https://www.linkedin.com/feed/update/urn:li:activity:{id}`.

LinkedIn does not auto-resize. CSS:

- iframe `width: 100%`
- `max-width: 550px` on the wrapper (native embed is 504px)
- `min-height: 600px`
- `border: 0`
- Center the wrapper in the column

If the post is not public, LinkedIn’s iframe shows its own error. The build must not try to detect that.

No LinkedIn script tag.

### Page scripts (`layouts/talks/single.html` `js` block)

Replace `{{ with .Params.x }} … widgets.js` with scans of `.Params.social`:

- Any `type: x` → `https://platform.twitter.com/widgets.js` (same as today)
- Any `type: bluesky` → `https://embed.bsky.app/embed.js`
- LinkedIn → nothing

Honor `site.Config.Privacy.X.Disable` for the widgets.js include as well.

## Out of scope

- Backward compatibility with talk frontmatter `x:` or `bluesky:`
- New or changed blog shortcodes (`{{< x >}}` stays)
- Hugo privacy settings for Bluesky or LinkedIn
- Custom-styled cards, Open Graph scraping, or unofficial LinkedIn APIs
- `urn:li:share:` / `urn:li:ugcPost:` (this site uses activity ids from `/posts/…-activity-{id}-…` URLs)

## Migration

Same PR as the templates.

1. Every talk `index.md` that has a top-level `x:` list becomes `social:` with `type: x` on each item. Preserve `user` and `id` (quoting style may be normalized). Preserve item order inside the old list.
2. Drop top-level `bluesky:` wherever it exists. Those items move into the same `social:` list.
3. After migration, no talk file contains a top-level `x:` or `bluesky:` key.

### JUG Summer Camp 2026

File: `content/talks/2026/2026-09-04-jug-summer-camp/index.md`

Replace the current `x:` + `bluesky:` with:

```yaml
social:
  - type: x
    user: "dadoonet"
    id: "2095849248780616171"
  - type: bluesky
    user: "klf37.bsky.social"
    id: "3muol6taevk2h"
  - type: linkedin
    user: "jug-summer-camp"
    id: "7501648269345812481"
  - type: linkedin
    user: "jug-summer-camp"
    id: "7501560302577025025"
```

LinkedIn sources:

- `https://www.linkedin.com/posts/jug-summer-camp_jugsummercamp-larochelle-elastic-activity-7501648269345812481-LAY7`
- `https://www.linkedin.com/posts/jug-summer-camp_jugsummercamp-larochelle-activity-7501560302577025025-bUek`

## Documentation

Update in the same PR:

- `archetypes/talks.md`: commented `social:` example instead of `x:`
- `CURSOR.md`: talk frontmatter example and the X embed partial section (document the dispatcher + three embed partials)

## Error handling

| Situation | Behavior |
| --- | --- |
| Missing `type`, `user`, or `id` | `errorf` — fail the build |
| `type` not in `x`, `bluesky`, `linkedin` | `errorf` — fail the build |
| X oEmbed network/parse failure | `warnidf` — skip that item |
| Bluesky oEmbed network/parse failure | `warnidf` — skip that item |
| `privacy.x.disable` | Skip `type: x` items and do not load `widgets.js` |
| LinkedIn post not public / iframe empty | No build error; LinkedIn owns the iframe contents |

## Verification

- `hugo` (or the repo’s usual build) completes without `errorf`
- `rg -n '^x:' content/talks` is empty
- `rg -n '^bluesky:' content/talks` is empty
- JUG Summer Camp 2026 HTML contains, in order: one X embed, one Bluesky embed, two LinkedIn iframes with the two activity URNs
- A previously X-only talk (e.g. Touraine Tech 2026) still embeds its tweet via `social:`
- A talk with several X posts (e.g. Devoxx FR 2024) keeps all of them, same order
- Blog pages that use `{{< x >}}` still render
- Talk pages with no social list do not render « Buzz et feedback »

## Non-goals for follow-up

Shortcodes `{{< bluesky >}}` / `{{< linkedin >}}`, dark-mode restyling of third-party widgets, and `urn:li:share:` support can wait until a real need shows up.

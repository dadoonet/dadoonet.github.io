# Social Embeds Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Talk pages render a mixed `social:` list (X, Bluesky, LinkedIn) in declaration order, and every talk is migrated off `x:`.

**Architecture:** A dispatcher partial `social-embed.html` switches on `type` and calls `x-embed.html` (existing oEmbed), `bluesky-embed.html` (oEmbed + one `embed.js`), or `linkedin-embed.html` (iframe `urn:li:activity:{id}`). `layouts/talks/single.html` ranges `.Params.social` in one « Buzz et feedback » block.

**Tech Stack:** Hugo 0.161.1 extended, Go templates, YAML frontmatter, `static/css/custom.css`.

## Global Constraints

- Frontmatter key is `social:` only. No talk compatibility with `x:` or `bluesky:`.
- Each item is `{ type: x|bluesky|linkedin, user, id }`. Missing fields or unknown `type` → `errorf`.
- Display order is the list order. One « Buzz et feedback » block. Wrapper class `social-embeds`.
- Heading/intro copy unchanged: « Buzz et feedback » / « Here's what was said about this presentation on social media. »
- X: keep `publish.x.com/oembed` + `widgets.js`. Honor `site.Config.Privacy.X.Disable`.
- Bluesky: `embed.bsky.app/oembed` for `https://bsky.app/profile/{user}/post/{id}`. Strip per-item `embed.js`. Load `embed.js` once on the page if any `type: bluesky`.
- LinkedIn: iframe `https://www.linkedin.com/embed/feed/update/urn:li:activity:{id}` only. No oEmbed, no script, no fallback link. CSS: wrapper max-width 550px, centered; iframe width 100%, min-height 600px, border 0.
- Blog shortcode `{{< x >}}` is unchanged.
- JUG Summer Camp 2026 social list is exactly: X `dadoonet`/`2095849248780616171`, Bluesky `klf37.bsky.social`/`3muol6taevk2h`, LinkedIn `jug-summer-camp`/`7501648269345812481`, LinkedIn `jug-summer-camp`/`7501560302577025025`.
- Hugo CLI: 0.161.1 extended. Build with `--buildFuture` (same as CI).

---

### Task 1: Bluesky and LinkedIn embed partials + CSS

**Files:**
- Create: `layouts/partials/bluesky-embed.html`
- Create: `layouts/partials/linkedin-embed.html`
- Modify: `static/css/custom.css`

**Interfaces:**
- Consumes: dict `id`, `user`, optional `ctx` (same as `x-embed.html`)
- Produces: Bluesky oEmbed HTML without `embed.js`; LinkedIn iframe for `urn:li:activity:{id}`

- [ ] **Step 1: Add `layouts/partials/bluesky-embed.html`**

```go-html-template
{{- /*
  Partial pour afficher un embed Bluesky
  Paramètres attendus :
    - id: la rkey du post
    - user: le handle (ex: klf37.bsky.social)
    - ctx: (optionnel) le contexte pour les messages d'erreur
*/ -}}
{{- $id := .id -}}
{{- $user := .user -}}
{{- if and $id $user -}}
  {{- $url := printf "https://bsky.app/profile/%v/post/%v" $user $id -}}
  {{- $query := querify "url" $url -}}
  {{- $request := printf "https://embed.bsky.app/oembed?%s" $query -}}
  {{- with try (resources.GetRemote $request) -}}
    {{- with .Err -}}
      {{- if $.ctx -}}
        {{- warnidf "bluesky-embed-getremote" "The bluesky-embed partial was unable to retrieve the remote data: %s. See %s" . $.ctx.Position -}}
      {{- else -}}
        {{- warnidf "bluesky-embed-getremote" "The bluesky-embed partial was unable to retrieve the remote data: %s" . -}}
      {{- end -}}
    {{- else with .Value -}}
      {{- $html := (. | transform.Unmarshal).html -}}
      {{- $html = $html | replaceRE `<script[^>]*src="https://embed\.bsky\.app/embed\.js"[^>]*>\s*</script>` "" -}}
      {{- $html | safeHTML -}}
    {{- else -}}
      {{- if $.ctx -}}
        {{- warnidf "bluesky-embed-getremote" "The bluesky-embed partial was unable to retrieve the remote data for %s. See %s" $url $.ctx.Position -}}
      {{- else -}}
        {{- warnidf "bluesky-embed-getremote" "The bluesky-embed partial was unable to retrieve the remote data for %s" $url -}}
      {{- end -}}
    {{- end -}}
  {{- end -}}
{{- else -}}
  {{- errorf "The bluesky-embed partial requires two parameters: user and id. Got user=%v, id=%v" $user $id -}}
{{- end -}}
```

- [ ] **Step 2: Add `layouts/partials/linkedin-embed.html`**

```go-html-template
{{- /*
  Partial pour afficher un embed LinkedIn
  Paramètres attendus :
    - id: l'activity id
    - user: le slug vanity (requis par le contrat, non utilisé dans l'iframe)
*/ -}}
{{- $id := .id -}}
{{- $user := .user -}}
{{- if and $id $user -}}
<div class="linkedin-embed">
  <iframe
    src="https://www.linkedin.com/embed/feed/update/urn:li:activity:{{ $id }}"
    title="LinkedIn post"
    loading="lazy"
    allowfullscreen></iframe>
</div>
{{- else -}}
  {{- errorf "The linkedin-embed partial requires two parameters: user and id. Got user=%v, id=%v" $user $id -}}
{{- end -}}
```

- [ ] **Step 3: Append LinkedIn CSS to `static/css/custom.css`**

```css
.linkedin-embed {
  max-width: 550px;
  margin: 1rem auto;
}

.linkedin-embed iframe {
  width: 100%;
  min-height: 600px;
  border: 0;
}
```

- [ ] **Step 4: Commit**

```bash
git add layouts/partials/bluesky-embed.html layouts/partials/linkedin-embed.html static/css/custom.css
git commit -m "Add Bluesky oEmbed and LinkedIn iframe partials"
```

---

### Task 2: Dispatcher + talk page wiring

**Files:**
- Create: `layouts/partials/social-embed.html`
- Modify: `layouts/talks/single.html` (Buzz block ~166-174 and js widgets.js ~660-662)

**Interfaces:**
- Consumes: dict `type`, `user`, `id`, optional `ctx`
- Produces: calls `x-embed.html` / `bluesky-embed.html` / `linkedin-embed.html`; page loads `widgets.js` iff any `type: x` and privacy is not disabled; loads `embed.js` iff any `type: bluesky`

- [ ] **Step 1: Add `layouts/partials/social-embed.html`**

```go-html-template
{{- $type := .type -}}
{{- $user := .user -}}
{{- $id := .id -}}
{{- if not (and $type $user $id) -}}
  {{- errorf "The social-embed partial requires type, user, and id. Got type=%v, user=%v, id=%v" $type $user $id -}}
{{- else if eq $type "x" -}}
  {{- partial "x-embed.html" (dict "id" $id "user" $user "ctx" .ctx) -}}
{{- else if eq $type "bluesky" -}}
  {{- partial "bluesky-embed.html" (dict "id" $id "user" $user "ctx" .ctx) -}}
{{- else if eq $type "linkedin" -}}
  {{- partial "linkedin-embed.html" (dict "id" $id "user" $user "ctx" .ctx) -}}
{{- else -}}
  {{- errorf "The social-embed partial got unknown type %q. Expected x, bluesky, or linkedin." $type -}}
{{- end -}}
```

- [ ] **Step 2: Replace the Buzz block in `layouts/talks/single.html`**

Old:

```go-html-template
        {{- with .Params.x -}}
        <div class="x-embeds">
          <h2>Buzz et feedback</h2>
          <p>Here's what was said about this presentation on social media.</p>
          {{- range . -}}
            {{- partial "x-embed.html" (dict "id" .id "user" .user) -}}
          {{- end -}}
        </div>
        {{- end -}}
```

New:

```go-html-template
        {{- with .Params.social -}}
        <div class="social-embeds">
          <h2>Buzz et feedback</h2>
          <p>Here's what was said about this presentation on social media.</p>
          {{- range . -}}
            {{- partial "social-embed.html" (dict "type" .type "id" .id "user" .user) -}}
          {{- end -}}
        </div>
        {{- end -}}
```

- [ ] **Step 3: Replace the widgets.js include in the `js` block**

Old:

```go-html-template
{{ with .Params.x }}
<script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
{{ end }}
```

New:

```go-html-template
{{ with .Params.social }}
  {{ with where . "type" "x" }}
    {{ if not site.Config.Privacy.X.Disable }}
<script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
    {{ end }}
  {{ end }}
  {{ with where . "type" "bluesky" }}
<script async src="https://embed.bsky.app/embed.js" charset="utf-8"></script>
  {{ end }}
{{ end }}
```

- [ ] **Step 4: Commit**

```bash
git add layouts/partials/social-embed.html layouts/talks/single.html
git commit -m "Render mixed social embeds on talk pages"
```

---

### Task 3: Migrate all talk frontmatter

**Files:**
- Modify: every `content/talks/**/index.md` that has top-level `x:` or `bluesky:`
- Special: `content/talks/2026/2026-09-04-jug-summer-camp/index.md`

**Interfaces:**
- Consumes: existing `x:` / `bluesky:` lists of `{user, id}`
- Produces: `social:` lists of `{type, user, id}`; JUG Summer Camp 2026 also has the two LinkedIn items

- [ ] **Step 1: Run a one-off Python migration (do not add the script to the repo)**

Transform each talk frontmatter:

1. Take the top-level `x:` list, insert `type: x` on each item, rename the key to `social:`.
2. If `bluesky:` exists, insert `type: bluesky` on each item and append those items to `social:`, then delete `bluesky:`.
3. Preserve `user`/`id` values and item order. Quoting may be normalized.
4. Then set JUG Summer Camp 2026 to this exact list:

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

Surgical rewrite of only the `x:` / `bluesky:` blocks (do not dump the whole YAML document) so the rest of each file stays intact.

- [ ] **Step 2: Verify migration**

```bash
rg -n '^x:' content/talks
rg -n '^bluesky:' content/talks
```

Expected: no matches.

Confirm JUG Summer Camp 2026 frontmatter matches the four-item list above.

- [ ] **Step 3: Commit**

```bash
git add content/talks
git commit -m "Migrate talk frontmatter from x: to social:"
```

---

### Task 4: Docs

**Files:**
- Modify: `archetypes/talks.md`
- Modify: `CURSOR.md`

**Interfaces:**
- Consumes: the `social:` contract
- Produces: archetype example and CURSOR.md docs for the dispatcher + three embed partials

- [ ] **Step 1: Replace the commented `x:` example in `archetypes/talks.md`**

```yaml
#social:
#  - type: x
#    user: "USERNAME"
#    id: "TWEET_ID"
#  - type: bluesky
#    user: "HANDLE.bsky.social"
#    id: "POST_RKEY"
#  - type: linkedin
#    user: "VANITY-SLUG"
#    id: "ACTIVITY_ID"
```

- [ ] **Step 2: In `CURSOR.md`, replace the Optional X Tweets/Posts example with:**

```yaml
# Optional - Social posts (X, Bluesky, LinkedIn)
social:
  - type: x
    user: "dadoonet"
    id: "1234567890"
  - type: bluesky
    user: "klf37.bsky.social"
    id: "3muol6taevk2h"
  - type: linkedin
    user: "jug-summer-camp"
    id: "7501648269345812481"
```

Replace the « X Embed Partial » section with:

```markdown
### Social Embed Partials

`layouts/partials/social-embed.html` dispatches a talk `social:` item by `type`.

- `layouts/partials/x-embed.html` — X/Twitter oEmbed
- `layouts/partials/bluesky-embed.html` — Bluesky oEmbed
- `layouts/partials/linkedin-embed.html` — LinkedIn iframe (`urn:li:activity:{id}`)
```

- [ ] **Step 3: Commit**

```bash
git add archetypes/talks.md CURSOR.md
git commit -m "Document social: frontmatter and embed partials"
```

---

### Task 5: Hugo build verification

**Files:** none (read-only checks). Install Hugo extended 0.161.1 if missing.

- [ ] **Step 1: Build**

```bash
hugo --gc --minify --buildFuture
```

Expected: exit 0, no `errorf`. oEmbed warnings for deleted tweets are acceptable (`warnidf`).

- [ ] **Step 2: Assert output**

```bash
# no leftover keys
rg -n '^x:' content/talks; echo x_exit:$?
rg -n '^bluesky:' content/talks; echo bsky_exit:$?

# JUG Summer Camp 2026: X, Bluesky, two LinkedIn iframes in order
python3 - <<'PY'
from pathlib import Path
html = Path("public/talks/2026/2026-09-04-jug-summer-camp/index.html").read_text()
assert "Buzz et feedback" in html
assert "twitter-tweet" in html or "x.com/dadoonet/status/2095849248780616171" in html
assert "bluesky-embed" in html or "bsky.app/profile/klf37.bsky.social/post/3muol6taevk2h" in html
assert "urn:li:activity:7501648269345812481" in html
assert "urn:li:activity:7501560302577025025" in html
i1 = html.index("2095849248780616171")
i2 = html.index("3muol6taevk2h")
i3 = html.index("7501648269345812481")
i4 = html.index("7501560302577025025")
assert i1 < i2 < i3 < i4
print("jsc26 ok")
PY

# X-only talk still embeds
rg -n "2018274464362906110" public/talks/2026/2026-02-12-touraine-tech/index.html

# Multi X talk keeps all ids
rg -n "1767512736164917700|1780915696592978097|1780899191050342759|1780905823620714719" public/talks/2024/2024-04-18-devoxx-france-2024/index.html

# Blog shortcode still present
rg -n "275486949924548609" public/posts/2024/08/01/free-lunches-for-opensource-engineers/index.html

# Talk with no social list has no Buzz heading
python3 - <<'PY'
from pathlib import Path
p = Path("public/talks/2013/2013-01-09-bbl-sg-private-event/index.html")
html = p.read_text() if p.exists() else ""
assert "Buzz et feedback" not in html
print("no-social talk ok")
PY
```

- [ ] **Step 3: Fix any failures, then commit only if templates/content changed**

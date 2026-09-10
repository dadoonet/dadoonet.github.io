# david.pilato.fr

Built with [Hugo](https://gohugo.io) using the [devrel](https://github.com/dadoonet/hugo-theme-devrel) overlay on [Dream](https://github.com/g1eny0ung/hugo-theme-dream).

## Create a New Blog Post

From the base folder (otherwise it will fail):

```sh
hugo new posts/YYYY-MM-DD-something-awesome-to-share/index.md
```

## Create a New Talk

From the base folder (otherwise it will fail):

```sh
hugo new talks/YYYY/YYYY-MM-DD-conference-name/index.md
```

The talk will be created in the appropriate year folder with the date prefix. Make sure to fill in the front matter fields like `conference`, `youtube`, `cover`, etc.

Upload the PDF files to the Google Cloud Storage bucket:

```sh
gsutil cp YYYY-MM-DD-conference-name.pdf gs://dadoonet-talks/slides/YYYY/YYYY-MM-DD-conference-name.pdf
```

## Update the Theme

```sh
hugo mod get -u github.com/dadoonet/hugo-theme-devrel
hugo mod tidy
```

For local development against a clone of the theme:

```toml
# go.mod
replace github.com/dadoonet/hugo-theme-devrel => ../hugo-theme-devrel
```

## Run locally

On fresh new install, before running the build, you need to install the dependencies:

```sh
[[ -f package-lock.json || -f npm-shrinkwrap.json ]] && npm ci || true
hugo mod tidy
```

Then you can run hugo:

```sh
hugo server --buildFuture --buildDrafts -D
```

## Build

```sh
hugo
```

Production (GitHub Pages) does not use `--buildFuture`. Netlify PR previews do, so scheduled posts remain reviewable.

## Theme

Layouts live in [hugo-theme-devrel](https://github.com/dadoonet/hugo-theme-devrel) (Dream overlay). This repo keeps personal content, identity, and integrations (Utterances, GCS PDF base URL). Search uses [Pagefind](https://pagefind.app).

## Search (Pagefind)

```sh
npm ci
npm run build   # hugo + pagefind
# or during development:
hugo server --buildFuture --buildDrafts -D
# after a production build, reuse the index locally via the public/pagefind mount
```

### Social posts on a talk (X, Bluesky, LinkedIn)

Talk pages can embed public posts in the **Buzz and feedback** section. Paste the post URLs in a `social:` list. Items are rendered in that order and can mix networks. Query strings (`?ref_src=…`) are ignored.

```yaml
social:
  - "https://x.com/dadoonet/status/2095849248780616171"
  - "https://bsky.app/profile/klf37.bsky.social/post/3muol6taevk2h"
  - "https://www.linkedin.com/embed/feed/update/urn:li:activity:7501648269345812481"
```

Accepted URL shapes:

- **X:** `https://x.com/{user}/status/{id}` or `https://twitter.com/{user}/status/{id}`
- **Bluesky:** `https://bsky.app/profile/{handle-or-did}/post/{id}`
- **LinkedIn:** the official embed URL `https://www.linkedin.com/embed/feed/update/urn:li:activity:{id}`, a feed URL with the same URN, or a regular post URL that contains `-activity-{id}-`. The LinkedIn post must be public or the iframe will be empty.

Quote URLs that contain `&` or other YAML-special characters. Blog posts still use the `{{< x user="…" id="…" >}}` shortcode; they do not use `social:`.

## Convert an image to AVIF

AVIF is a modern image format with significantly better compression than PNG or JPEG. To convert an image using `ffmpeg`:

```sh
ffmpeg -i input.png -c:v libsvtav1 -crf 30 -b:v 0 output.avif
```

- `-c:v libsvtav1`: use the SVT-AV1 encoder
- `-crf 30`: quality factor (lower = better quality, higher = smaller file); range 0–63
- `-b:v 0`: disable bitrate target (required for CRF mode)

Example result: `cover.png` (658K) → `cover.avif` (71K), ~9× smaller.

> **Note:** `ffmpeg` must be compiled with `--enable-libsvtav1`. Install via Homebrew: `brew install ffmpeg`.

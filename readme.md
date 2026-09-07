# david.pilato.fr

Built with [Hugo](https://gohugo.io) based on the [eureka theme](https://github.com/wangchucheng/hugo-eureka).

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
git submodule update --rebase --remote
```

## Run locally

On fresh new install, before running the build, you need to install the dependencies:

```sh
[[ -f package-lock.json || -f npm-shrinkwrap.json ]] && npm ci || true
```

Then you can run hugo:

```sh
hugo server --buildFuture --buildDrafts -D
```

## Build

```sh
hugo
```

## Theme

The theme used for this blog is [Dream](https://g1en.site/hugo-theme-dream/).
Plus my own modifications (templates) for talks.

### Social posts on a talk (X, Bluesky, LinkedIn)

Talk pages can embed public posts in the **Buzz et feedback** section. Add a `social:` list in the talk front matter. Items are rendered in list order and can mix networks:

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
```

Every item needs `type`, `user`, and `id`. Copy those values from the public post URL:

**X** — URL shape `https://x.com/{user}/status/{id}` (or `https://twitter.com/…`).

- `user`: handle without `@`. In `https://x.com/dadoonet/status/2095849248780616171`, that is `dadoonet`.
- `id`: numeric status id after `/status/`. That is `2095849248780616171`.

**Bluesky** — URL shape `https://bsky.app/profile/{user}/post/{id}`.

- `user`: profile handle, including `.bsky.social` or a custom domain. In `https://bsky.app/profile/klf37.bsky.social/post/3muol6taevk2h`, that is `klf37.bsky.social`.
- `id`: post rkey after `/post/`. That is `3muol6taevk2h`.

**LinkedIn** — URL shape `https://www.linkedin.com/posts/{user}_{slug}-activity-{id}-{suffix}`.

Example: `https://www.linkedin.com/posts/jug-summer-camp_jugsummercamp-larochelle-elastic-activity-7501648269345812481-LAY7`

- `user`: vanity slug, the segment after `/posts/` and before the first `_`. That is `jug-summer-camp`. It can be a person or a company page. The embed iframe does not use this field; it is required so every `social:` item has the same `user` + `id` shape.
- `id`: activity id, the long number after `-activity-` and before the final `-XXXX` suffix. That is `7501648269345812481`.

You can also take `id` from LinkedIn’s **Embed this post** snippet (`urn:li:activity:{id}`) or from `https://www.linkedin.com/feed/update/urn:li:activity:{id}`. The post must be public or the iframe will be empty.

Blog posts still use the `{{< x user="…" id="…" >}}` shortcode; they do not use `social:`.

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

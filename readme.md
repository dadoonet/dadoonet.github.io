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

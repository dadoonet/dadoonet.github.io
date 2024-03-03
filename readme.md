# david.pilato.fr

Built with [Hugo](https://gohugo.io) based on the [eureka theme](https://github.com/wangchucheng/hugo-eureka).

## Create a New Blog Post

From the base folder (otherwise it will fail):

```sh
hugo new blog/YYYY-MM-DD-something-awesome-to-share/index.md
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
hugo server
```

Also serve future posts:

```sh
hugo server --buildFuture
```

## Build

```sh
hugo
```

---
title: 'Search your beans with Lucene — Highlighting'
description: "Let's find out where exactly in a text a query matched. That's called highlighting."
author: David Pilato
avatar: /about/david_pilato.avif
tags:
  - java
  - lucene
  - maven
  - search
categories:
  - tutorial
series:
  - Lucene Bean Search
date: '2026-09-17T07:00:00+02:00'
nolastmod: true
cover: cover.avif
draft: false
---

Let say we found some documents matching our query. But how could we know, where in the text,
it matched? Let's try to **bold** the tokens in the stored title, artist or genre.

<!--more-->

[Suggest]({{< ref "2026-09-15-lucene-bean-search-suggest" >}}) and highlighting look
similar in the UI — both wrap matched letters in `<b>` — but they are not the
same call.

`AnalyzingInfixSuggester.lookup(..., highlight=true)` returns a **display string**
(`highlightKey`) from a **second dictionary**. The chip value stays clean
(`key`); the bold markup is never stored.

`UnifiedHighlighter` runs on the **track index**, with the **same** `Query` that
just scored the hit. It reads stored field text and paints token offsets —
including the trailing `PrefixQuery` (`sincla` → `<b>Sinclar</b>`).

One is “help me write the query.” The other is “show me why this row matched.”

## Highlight my results

Highlighting lives in its own artefact:

```xml
<dependency>
  <groupId>org.apache.lucene</groupId>
  <artifactId>lucene-highlighter</artifactId>
  <version>10.5.1</version>
</dependency>
```

`WholeBreakIterator` keeps the **full** stored value as one fragment —
no sentence chopping for short metadata fields. Same builder as the playground:

```java
Query bob = new BooleanQuery.Builder()
  .add(new BoostQuery(new TermQuery(new Term("title", "bob")), 4.0f), BooleanClause.Occur.SHOULD)
  .add(new BoostQuery(new PrefixQuery(new Term("title", "bob")), 1.0f), BooleanClause.Occur.SHOULD)
  .add(new BoostQuery(new TermQuery(new Term("artist", "bob")), 3.0f), BooleanClause.Occur.SHOULD)
  .add(new BoostQuery(new PrefixQuery(new Term("artist", "bob")), 0.75f), BooleanClause.Occur.SHOULD)
  // … genre^2 / album^1.5 / label^1 / comment^0.5 (+ prefixes) …
  .setMinimumNumberShouldMatch(1)
  .build();

// Search and retrieve the 10 first hits
TopDocs hits = searcher.search(bob, 10);

UnifiedHighlighter highlighter = UnifiedHighlighter.builder(searcher, analyzer)
    .withMaxLength(10_000)
    .withBreakIterator(WholeBreakIterator::new)
    .build();
Map<String, String[]> hl = highlighter.highlightFields(
        new String[]{"title", "artist", "genre", "album", "label", "comment"},
        bob, hits);
```

Fields must be `Field.Store.YES` otherwise Lucene cannot extract the source data
we can highlight it.

Each field maps to a parallel array — one snippet per hit. Missing or blank
snippets mean that field did not contribute markup for that doc. Hand the map to
the template as display-only HTML; keep the clean bean for chips and URLs.

`q=Bob` wraps the token wherever it matched:

```html
Outro Lugar - <b>Bob</b> Sinclar Remix
Crazy (<b>Bob</b> Sinclar vs. Dimitri Vegas & Like Mike remix)
```

This also works for `PrefixQuery` even though the whole term is highlighted, not just the typed prefix:

```html
Outro Lugar - Bob <b>Sinclar</b> Remix
```

## How it works in Lucene

Search answers “which documents contain this term?” Highlighting answers “**where**
in the stored string?” Both read the same inverted index — they just dig one
level deeper.

You remember the posting list we generated in a previous post?

```text
artist:bob       →  1, 2, 3
artist:claude    →  4, 5
artist:francois  →  4, 5, 6
artist:marley    →  2
artist:sinclar   →  1, 3
artist:valery    →  6
```

Actually, it was not only generating posting lists for each term, it also kept track of the positions of those terms within each document.

### Positions for phrase queries

Each posting also stores **positions**: the ordinal of the term inside that
field’s token stream (0-based).

For example, consider the artist name “Claude François”, which is tokenized into two terms: `claude` and `francois`. The positions of these terms within the document are as follows:

| Position | Term      |
|----------|-----------|
| 0        | `claude`  |
| 1        | `francois`|

For the artist name François “Valéry” (tokenized as `francois` and `valery`), the positions are:

| Position | Term      |
|----------|-----------|
| 0        | `francois`|
| 1        | `valery`  |

For “Earth Wind and Fire”, the positions are:

| Position | Term      |
|----------|-----------|
| 0        | `earth`   |
| 1        | `wind`    |
| 2        | `and`     |
| 3        | `fire`    |

If you search for `francois valery`, you will get back the document "François Valéry" because one of the query terms matched the document. If you search for `valery francois`, it will give you the exact same two documents, because the order of terms in a simple conjunction query does not matter.

What if it matters? In that case, you would need to use a phrase query or a span query to enforce the order of terms. This is where **term positions** come into play.

### Offsets paint the characters

But **highlighting** needs one more step: map the position back onto characters of the **stored** surface
string (`Field.Store.YES`).

At analysis time, each token also carries character offsets into the original
string — start inclusive, end exclusive:

```text
"Earth Wind and Fire"
 earth         → [0, 5)
 wind          → [6, 10)
 and           → [11, 14)
 fire          → [15, 19)
```

The `UnifiedHighlighter` re-runs the **same** analyzer on the stored value,
keeps tokens that satisfy the query (`TermQuery` `wind`, or a `PrefixQuery`
`win*` that matches `wind`), and wraps those `[start, end)` slices with `<b></b>` html tags:

```html
Earth <b>Wind</b> and Fire
```

Now you just need to adapt the CSS to match the way you want it to look like.

{{< figure src="highlight-wind.avif" caption="`q=wind` — orange `<b>Wind</b>` on *Earth, Wind & Fire* and titles like *Ride Like the Wind*." >}}

---
title: 'Search your beans with Lucene — Highlighting'
description: "The query that scores a hit also marks the stored text. Bold tags follow token offsets — including the trailing PrefixQuery from Part 3."
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

[Part 3]({{< ref "2026-09-11-lucene-bean-search-query-sync" >}}) already built the
`BooleanQuery` that scores a track. Anyone used to a search UI expects the next
step: show *why* the row matched — bold the tokens in the stored title, artist,
or genre.

<!--more-->

## Suggest bold vs result bold

[Suggest]({{< ref "2026-09-14-lucene-bean-search-suggest" >}}) and highlighting look
similar in the UI — both wrap matched letters in `<b>` — but they are not the
same call.

`AnalyzingInfixSuggester.lookup(..., highlight=true)` returns a **display string**
(`highlightKey`) from a **second dictionary**. The chip value stays clean
(`key`); the bold markup is never stored.

`UnifiedHighlighter` runs on the **track index**, with the **same** `Query` that
just scored the hit. It reads stored field text and paints token offsets —
including the trailing `PrefixQuery` from Part 3 (`sincla` → `<b>Sinclar</b>`).
Empty query → match-all → stored text comes back unmarked.

One is “help me write the query.” The other is “show me why this row matched.”

## Add `lucene-highlighter`

Highlighting lives in its own artefact (same Lucene version as Part 1):

```xml
<dependency>
  <groupId>org.apache.lucene</groupId>
  <artifactId>lucene-highlighter</artifactId>
  <version>10.5.1</version>
</dependency>
```

## Build the highlighter

Reuse the Part 1 search analyzer so offsets line up with how title / artist were
tokenized. `WholeBreakIterator` keeps the **full** stored value as one fragment —
no sentence chopping for short metadata fields:

```java
UnifiedHighlighter highlighter = UnifiedHighlighter.builder(searcher, analyzer)
        .withMaxLength(10_000)
        .withBreakIterator(WholeBreakIterator::new)
        .build();
```

Fields must be `Field.Store.YES` (Part 1 already did that for text). Without
stored text, there is nothing to paint.

## Demo

Search first, then highlight the same `Query` and `TopDocs`:

```java
Query q = TrackLuceneQueryBuilder.buildStructured("Bob", Map.of(), Map.of());
TopDocs hits = searcher.search(q, 25);

Map<String, String[]> byField = highlighter.highlightFields(
        new String[]{"title", "artist", "genre", "album", "label", "comment"},
        q, hits);
```

Each field maps to a parallel array — one snippet per hit. Missing or blank
snippets mean that field did not contribute markup for that doc. Hand the map to
the template as display-only HTML; keep the clean bean for chips and URLs.

### Type “Bob”

{{< figure src="highlight-bob.avif" caption="`q=Bob` — matching fields show `<b>Bob</b>` in the stored title, artist, or album." >}}

`q=Bob` wraps the token wherever it matched:

```text
Outro Lugar - <b>Bob</b> Sinclar Remix
Crazy (<b>Bob</b> Sinclar vs. Dimitri Vegas & Like Mike remix)
```

Same query as Part 3 — the highlighter only adds tags where offsets hit.

### Type “nate”

ASCII folding from Part 1 still applies: typing `nate` marks **Naté** in the
artist field (`<b>Naté</b>`). The stored surface form stays accented; the match
ran on the folded token.

### Type “sincla”

The trailing `PrefixQuery` from Part 3 paints the **full** stored term, not just
the typed prefix:

```text
… (<b>Sinclar</b> Remix)
```

That is the same “last token is still being typed” behaviour as live search —
highlighting follows the query, not a separate prefix dictionary.

### Empty query

A blank `q` is match-all. Hits still return stored title / artist text, but
without `<b>` tags — there was no term to mark.

## How it works in Lucene

Search answers “which documents contain this term?” Highlighting answers “**where**
in the stored string?” Both read the same inverted index — they just dig one
level deeper.

### Posting lists find the hit

A `TextField` from Part 1 is tokenized at index time. For the title
`Free (Bob Sinclar Remix)`, the analyzer emits four terms. Lucene does **not**
keep a bag of words on the document. It keeps an **inverted** map: term → list of
documents (the posting list), with a frequency per doc:

```text
title:bob  →  doc#255465792 (freq=1), doc#…, …
title:free →  doc#255465792 (freq=1), …
```

`IndexSearcher` walks those lists, scores, and returns `TopDocs`. That is enough
to fill a result table with ids. It is **not** enough to draw `<b>` tags.

### Positions locate the token

Each posting also stores **positions**: the ordinal of the term inside that
field’s token stream (0-based). Same title, token order:

| Position | Term      |
|----------|-----------|
| 0        | `free`    |
| 1        | `bob`     |
| 2        | `sinclar` |
| 3        | `remix`   |

So `bob` on that document is not only “present” — it is **at position 1**. Phrase
queries and spans use that. Highlighting needs one more step: map the position
back onto characters of the **stored** surface string
(`Field.Store.YES` from Part 1).

### Offsets paint the characters

At analysis time, each token also carries character offsets into the original
string — start inclusive, end exclusive:

```text
"Free (Bob Sinclar Remix)"
 free          → [0, 4)
 Bob           → [6, 9)
 Sinclar       → [10, 17)
 Remix         → [18, 23)
```

`UnifiedHighlighter` re-runs the **same** Part 1 analyzer on the stored value,
keeps tokens that satisfy the query (`TermQuery` `bob`, or a `PrefixQuery`
`sincla*` that matches `sinclar`), and wraps those `[start, end)` slices:

```text
Free (<b>Bob</b> Sinclar Remix)
```

Folding still lines up: stored `Ultra Naté`, query `nate`, token `nate` with
offsets covering the four characters of `Naté` → `<b>Naté</b>`. A match-all
query has no term spans, so the stored text comes back unmarked.

Markup stays **display-only**. Do not write `<b>` back into the index, and do not
treat highlighted strings as chip values — the same split Suggest taught for
`highlightKey` vs `key`.

---
title: 'Search your beans with Lucene — Search'
description: "The tracks are indexed. Type Bob — should a title hit beat an album? Boosts, FILTER chips, MUST_NOT: build the query a real search engine runs."
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
date: '2026-09-11T07:00:00+02:00'
nolastmod: true
cover: cover.avif
draft: false
math: true
---

We already mapped beans to documents and indexed them.
Let's see what's happening when you type in the box, add a filter, exclude
two keys.

<!--more-->

Start with no criteria at all and enter the MatchAll query:

```java
// Open an index searcher using the same writer
IndexSearcher searcher = new IndexSearcher(DirectoryReader.open(writer));

// Search and retrieve the 10 first hits
TopDocs hits = searcher.search(MatchAllDocsQuery.INSTANCE, 10);

// Join stored ids back to beans:
for (var hit : hits.scoreDocs) {
    String id = searcher.storedFields().document(hit.doc).get("id");
    Track track = trackDatabase.get(id);
    if (track != null) {
        // Do something with the track, e.g., print it or add it to a list
    }
}
```

## Type “Bob”

{{< figure src="search-bob.avif" caption="`q=Bob` → 62 hits. Title boost beats artist; last token also gets a PrefixQuery." >}}

Analyze the query string and build the query from the tokens:

```java
TokenStream ts = analyzer.tokenStream("title", "Bob");
// → bob

// build query for bob
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
```

`buildQuery` is the fold the playground expands: each analyzed field is a
`SHOULD` `TermQuery` with a boost, plus a trailing `PrefixQuery` at a quarter of
that boost on the **last** typed token:

Lucene prints it as:

```text
((title:bob)^4.0 (title:bob*)^1.0 (artist:bob)^3.0 (artist:bob*)^0.75
 (genre:bob)^2.0 (genre:bob*)^0.5 (album:bob)^1.5 (album:bob*)^0.375
 (label:bob)^1.0 (label:bob*)^0.25 (comment:bob)^0.5 (comment:bob*)^0.125)~1
```

Several tokens are AND-ed (`MUST` each token’s builder). Only the **last** one
is a prefix; earlier words stay exact. `bob sincla` requires `bob` and a
`sincla…` prefix. `ouse` does not find `House` — not an infix.

You remember the posting list we generated in the previous post?

```text
artist:bob       →  1, 2, 3
artist:claude    →  4, 5
artist:francois  →  4, 5, 6
artist:marley    →  2
artist:sinclar   →  1, 3
artist:valery    →  6
```

You see the match with our search `(artist:bob)^3.0`?

## Add a filter (include Club)

{{< figure src="search-club.avif" caption="Same `q=Bob`, plus `FILTER genre=Club` — 62 tracks become 26." >}}

Wrap the free-text builder as `MUST` and add a `FILTER` — constrain, do not
score. Same leaf the playground emits:

```java
// Single filter on genre for club
Query genre = new TermQuery(new Term("genre.raw.normalized", "club"));

// Combine queries in a bool query
Query bool = new BooleanQuery.Builder()
  .add(bob, BooleanClause.Occur.MUST)
  // Filter in
  .add(genre, BooleanClause.Occur.FILTER)
  .build();
```

Lucene prints it as:

```text
+(((title:bob)^4.0 (title:bob*)^1.0 … )~1) #genre.raw.normalized:club
```

Index a normalized keyword twin (`genre.raw.normalized`) next to
`genre.raw`, so `Club` and `club` hit the same docs. Do not wildcard it.

## Exclude two keys (4A and 4B)

{{< figure src="search-keys.avif" caption="Club stays on. `MUST_NOT` 4A or 4B — 26 tracks become 23." >}}

Same `MUST` + `FILTER`, plus `MUST_NOT` for excluded keys. Several keys on the
same dimension are **OR** (`SHOULD`, `minShouldMatch = 1`):

```java
// Filter on keys 4a or 4b
Query keys = new BooleanQuery.Builder()
    .add(new TermQuery(new Term("key.code", "4a")), BooleanClause.Occur.SHOULD)
    .add(new TermQuery(new Term("key.code", "4b")), BooleanClause.Occur.SHOULD)
    .setMinimumNumberShouldMatch(1)
    .build();

Query bool = new BooleanQuery.Builder()
    .add(bob, BooleanClause.Occur.MUST)
    .add(genre, BooleanClause.Occur.FILTER)
    // Filter out
    .add(keys, BooleanClause.Occur.MUST_NOT)
    .build();
```

Lucene prints it as:

```text
+(((title:bob)^4.0 … )~1) #genre.raw.normalized:club -((key.code:4a key.code:4b)~1)
```

This means:

| UI                   | Playground preset   | Lucene clause                    |
|----------------------|---------------------|----------------------------------|
| Type “Bob”           | Bob → 62            | `MUST` match + last-token prefix |
| Include Club         | + Club → 26         | `FILTER` exact `club`            |
| Exclude 4A **or** 4B | − 4A,4B → 23        | `MUST_NOT` (`4a` `SHOULD` `4b`)  |

Scoring plays an important role in determining the relevance of search results.
Some clauses contribute to the score, while others act as filters or exclusions.

| Occur                           | Role                                | Scores? |
|---------------------------------|-------------------------------------|---------|
| `MUST`                          | analyzed match + last-token prefix  | yes     |
| `FILTER`                        | field constraint (genre, bpm, …)    | no      |
| `MUST_NOT`                      | exclusion                           | no      |
| `SHOULD` + `minShouldMatch = 1` | multi-select OR *inside* one clause | no      |

A `BooleanQuery` with only `MUST_NOT` matches nothing — add a `MUST`
`MatchAllDocsQuery` if the user excludes without typing. Blank everything is
`MatchAllDocsQuery`.

## Give me the "best" results first (sort by score)

If you want to understand how the score is computed, you can use the `explain` method on the `IndexSearcher` for a specific document and query:

```java
// Explain how the score is computed for the first hit
searcher.explain(query, hits.scoreDocs[0].doc);
```

This gives something like:

{{< figure src="search-explain.avif" caption="Score for doc 3473 on `q=Bob`: BM25 weights on `title:bob` and `album:bob` (boost × idf × tf)." >}}

That tree is Lucene’s **BM25** breakdown. For each matching term the score is:

\[
\begin{aligned}
\mathrm{idf} &= \log\!\left(1 + \frac{N - n + 0.5}{n + 0.5}\right) \\[0.6em]
\mathrm{tf} &= \frac{\mathrm{freq}}{\mathrm{freq} + k_1 \bigl(1 - b + b \cdot \tfrac{\mathrm{dl}}{\mathrm{avgdl}}\bigr)} \\[0.6em]
\mathrm{score} &= \mathrm{boost} \times \mathrm{idf} \times \mathrm{tf}
\end{aligned}
\]

`N` is documents that have the field, `n` those that contain the term, `freq`
occurrences in this document, `dl` / `avgdl` the field length vs the average.
`k1` and `b` are the usual BM25 knobs (defaults `1.2` and `0.75`).

Take `title:bob` on doc **3473** from the screenshot. Across the index,
**7** titles contain `bob` (`n = 7`) out of **4 322** docs that have a title
(`N = 4 322`). In this hit, `bob` appears once in the title (`freq = 1`), the
title is **5** tokens long (`dl = 5`), and the average title length is about
**4.24** (`avgdl`). The field boost is **4**:

\[
\begin{aligned}
\mathrm{idf}
  &= \log\!\left(1 + \frac{4322 - 7 + 0.5}{7 + 0.5}\right)
   \approx 6.357 \\[0.6em]
\mathrm{tf}
  &= \frac{1}{1 + 1.2\bigl(1 - 0.75 + 0.75 \cdot \tfrac{5}{4.242}\bigr)}
   \approx 0.424 \\[0.6em]
\mathrm{score}(\texttt{title:bob})
  &= 4 \times 6.357 \times 0.424
   \approx 10.77
\end{aligned}
\]

Same walk for `album:bob`: only **3** albums contain the term
(`n = 3`) out of **3 088** docs with an album (`N = 3 088`), still
`freq = 1`, `dl = 5`, `avgdl \approx 3.77`, boost **1.5**:

\[
\begin{aligned}
\mathrm{idf}
  &= \log\!\left(1 + \frac{3088 - 3 + 0.5}{3 + 0.5}\right)
   \approx 6.783 \\[0.6em]
\mathrm{tf}
  &= \frac{1}{1 + 1.2\bigl(1 - 0.75 + 0.75 \cdot \tfrac{5}{3.770}\bigr)}
   \approx 0.401 \\[0.6em]
\mathrm{score}(\texttt{album:bob})
  &= 1.5 \times 6.783 \times 0.401
   \approx 4.08
\end{aligned}
\]

Add the prefix leaves (`title:bob*` → `1`, `album:bob*` → `0.375`) and you get
the hit score: \(10.77 + 1 + 4.08 + 0.375 \approx 16.23\).

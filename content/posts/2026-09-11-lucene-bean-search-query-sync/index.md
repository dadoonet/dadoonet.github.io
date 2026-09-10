---
title: 'Integrating Apache Lucene for Bean Search — Part 3: Search'
description: "Build a BooleanQuery with MUST, FILTER, and MUST_NOT — then resolve Lucene hits back to your Java beans."
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
---

This post is part of a series:

* [Part 1: Indexing]({{< ref "2026-09-09-lucene-bean-search-indexing" >}})
* [Part 2: Index Lifecycle]({{< ref "2026-09-10-lucene-bean-search-lifecycle" >}})
* [Part 3: Search]({{< ref "2026-09-11-lucene-bean-search-query-sync" >}})
* Part 4: Suggest <!-- TODO: link when published -->
* Part 5: Facets <!-- TODO: link when published -->

[Part 1]({{< ref "2026-09-09-lucene-bean-search-indexing" >}}) mapped beans to documents.
[Part 2]({{< ref "2026-09-10-lucene-bean-search-lifecycle" >}}) owned the writer.
Lucene still returns **documents**, not your Java types — so this part is queries
and hit → bean resolution.

## From documents to beans

Run a Lucene query, collect hit ids (and scores when relevant), then join back to
your beans — either by filtering a caller-provided corpus or by loading from a
repository.

<!--more-->

## Keep free text and filters apart

Do **not** stuff facets into the search box (`genre:House bob`). That string is
painful to chip, autocomplete, and bookmark once a panel appears. Split the
request:

```
/tracks?q=bob sinclar&genre=club&bpm=110-120&key=1A,1B,2A
```

`q` is analyzed free text. Everything else is a structured filter. Keep both
bookmarkable; keep construction in one place (`TrackLuceneQueryBuilder`) so
parity tests can index known beans and assert hit ids.

## A standard `BooleanQuery`

This is the same boolean tree Elasticsearch users know as `bool` / `must` /
`filter` / `must_not`. Lucene’s Java API is that tree — no Query DSL, no parser
required:

```
MUST      freeText("bob sinclar")                 // analyzer tokenizes; score
FILTER    genre:club                              // 1 value → 1 clause
FILTER    bpm:[110 TO 119]
FILTER    (key:1A SHOULD key:1B SHOULD key:2A)    // multi-select = OR
MUST_NOT  freeText("bob")                         // unfielded -bob
MUST_NOT  genre:techno                            // excluded chip
```

| Occur                           | Role                                    | Scores?   |
|---------------------------------|-----------------------------------------|-----------|
| `MUST`                          | analyzed free text                      | yes       |
| `FILTER`                        | field constraint (genre, bpm, key, …)   | no        |
| `MUST_NOT`                      | exclusion                               | no        |
| `SHOULD` + `minShouldMatch = 1` | multi-select OR *inside* one `FILTER`   | no        |

`FILTER` is the important one. A `MUST` on `genre:club` would still constrain,
but it would also join the scoring. Facets should shrink the set **without**
changing whether title beats artist. Put them in `FILTER`.

Hand-assembled, that query is ordinary Lucene:

```java
BooleanQuery.Builder query = new BooleanQuery.Builder();

// MUST — free text, scored (title > artist > …)
query.add(freeText("bob sinclar"), BooleanClause.Occur.MUST);

// FILTER — constrain, do not score
query.add(new TermQuery(new Term(TrackIndexFields.GENRE_RAW, "club")),
        BooleanClause.Occur.FILTER);
query.add(DoublePoint.newRangeQuery(TrackIndexFields.BPM, 110.0, 119.0),
        BooleanClause.Occur.FILTER);

// key is another StringField — same recipe as genre.raw
BooleanQuery.Builder keys = new BooleanQuery.Builder();
keys.add(new TermQuery(new Term("key", "1a")), BooleanClause.Occur.SHOULD);
keys.add(new TermQuery(new Term("key", "1b")), BooleanClause.Occur.SHOULD);
keys.add(new TermQuery(new Term("key", "2a")), BooleanClause.Occur.SHOULD);
keys.setMinimumNumberShouldMatch(1);
query.add(keys.build(), BooleanClause.Occur.FILTER);

// MUST_NOT — drop matches
query.add(freeText("bob"), BooleanClause.Occur.MUST_NOT);
query.add(new TermQuery(new Term(TrackIndexFields.GENRE_RAW, "techno")),
        BooleanClause.Occur.MUST_NOT);

Query lucene = query.build();
TopDocs hits = searcher.search(lucene, 10);
```

A builder turns the structured request into that same tree:

```java
public static Query buildStructured(
        String freeText,
        Map<String, List<String>> filters,
        Map<String, List<String>> mustNots) {
    BooleanQuery.Builder query = new BooleanQuery.Builder();

    Query text = analyzedFreeText(freeText); // whitespace + lowercase, then boosts
    boolean hasText = !(text instanceof MatchAllDocsQuery);
    if (hasText) {
        query.add(text, BooleanClause.Occur.MUST);
    }

    int filterCount = 0;
    for (var entry : filters.entrySet()) {
        query.add(fieldFilter(entry.getKey(), entry.getValue()), BooleanClause.Occur.FILTER);
        filterCount++;
    }
    int notCount = 0;
    for (var entry : mustNots.entrySet()) {
        query.add(fieldFilter(entry.getKey(), entry.getValue()), BooleanClause.Occur.MUST_NOT);
        notCount++;
    }

    if (!hasText && filterCount == 0 && notCount == 0) {
        return new MatchAllDocsQuery();
    }
    // BooleanQuery with only MUST_NOT matches nothing — add a MUST match-all
    if (!hasText && filterCount == 0 && notCount > 0) {
        query.add(new MatchAllDocsQuery(), BooleanClause.Occur.MUST);
    }
    return query.build();
}

private static Query fieldFilter(String field, List<String> values) {
    if (values.size() == 1) {
        return leaf(field, values.getFirst()); // TermQuery, range, …
    }
    BooleanQuery.Builder sameField = new BooleanQuery.Builder();
    for (String value : values) {
        sameField.add(leaf(field, value), BooleanClause.Occur.SHOULD);
    }
    sameField.setMinimumNumberShouldMatch(1);
    return sameField.build();
}
```

Call it with maps, not a mixed leftover string:

```java
Map<String, List<String>> filters = Map.of(
        "genre", List.of("club"),
        "bpm", List.of("[110 TO 119]"),
        "key", List.of("1A", "1B", "2A"));
Map<String, List<String>> mustNots = Map.of("genre", List.of("techno"));

Query lucene = TrackLuceneQueryBuilder.buildStructured("bob sinclar", filters, mustNots);
```

| Intent            | Bookmarkable request      | Lucene clause                |
|-------------------|---------------------------|------------------------------|
| Free text         | `q=bob sinclar`           | `MUST` free-text             |
| Include Club      | `genre=club`              | `FILTER` term                |
| Exclude techno    | `minus-genre=techno`      | `MUST_NOT` term              |
| Keys 1A **or** 1B | `key=1A,1B`               | `FILTER` (`SHOULD` OR)       |
| Exclude a token   | unfielded `-bob`          | `MUST_NOT` free-text         |

Polarity is a **separate param**, not a dash on the value — otherwise you cannot
include an artist named `-M-`.

## Leaf queries

Inside each clause, the usual Lucene types:

| Constraint       | Lucene leaf                                      |
|------------------|--------------------------------------------------|
| `genre=Club`     | `TermQuery` on a `StringField`                   |
| `bpm=110-120`    | `DoublePoint.newRangeQuery`                      |
| `rating=5`       | `IntPoint` exact / range                         |
| `sinclar~`       | `FuzzyQuery` (opt-in)                            |
| blank everything | `MatchAllDocsQuery`                              |

Exact id, when you do not want a parser yet:

```java
// Exact id match on a StringField — not analyzed
Query q = new TermQuery(new Term(TrackIndexFields.ID, "42"));
TopDocs hits = searcher.search(q, 10);
```

Free-text across fields, with title beating artist — this inner `BooleanQuery` is
the `MUST` clause above:

```java
BooleanQuery.Builder fields = new BooleanQuery.Builder();
fields.add(new BoostQuery(containsQuery("title", term), 4.0f), BooleanClause.Occur.SHOULD);
fields.add(new BoostQuery(containsQuery("artist", term), 3.0f), BooleanClause.Occur.SHOULD);
fields.setMinimumNumberShouldMatch(1);
Query freeText = fields.build();
```

## Resolve hits to beans

1. Run the query against the full index.
2. Collect hit ids (score order when it matters).
3. Intersect against a caller-provided **corpus** (`List<Track>`), or load by id
   from a repository.

Playlist vs whole-library scoping stays **outside** Lucene: the handler picks the
base list, then `filter` drops ids that are not in it. Genre / bpm / key are
**inside** Lucene — they are `FILTER` clauses, not a second pass on the list.

```java
public List<Track> filter(
        List<Track> corpus,
        String freeText,
        Map<String, List<String>> filters,
        Map<String, List<String>> mustNots) {
    if (corpus.isEmpty()) {
        return List.of();
    }
    Query lucene = TrackLuceneQueryBuilder.buildStructured(freeText, filters, mustNots);
    if (lucene instanceof MatchAllDocsQuery) {
        return List.copyOf(corpus);
    }
    try {
        IndexSearcher searcher = index.searcher();
        try (IndexReader reader = searcher.getIndexReader()) {
            TopDocs hits = searcher.search(lucene, Math.max(1, reader.numDocs()));

            Map<String, Track> byId = new HashMap<>(corpus.size());
            for (Track track : corpus) {
                byId.put(track.id(), track);
            }

            List<Track> ordered = new ArrayList<>(hits.scoreDocs.length);
            for (var hit : hits.scoreDocs) {
                // Stored id (Field.Store.YES) — Lucene doc id ≠ Track.id
                String id = reader.storedFields().document(hit.doc).get(TrackIndexFields.ID);
                Track track = byId.get(id);
                if (track != null) {
                    ordered.add(track);
                }
            }
            return List.copyOf(ordered);
        }
    } catch (IOException e) {
        throw new UncheckedIOException("Unable to search track index", e);
    }
}
```

When free-text scoring matters, walk `hits.scoreDocs` in order — `FILTER` does
not disturb that ranking. When the query is pure filters, corpus order is often
enough.

## Next

You can score free text, constrain with `FILTER`, exclude with `MUST_NOT`, and
resolve hits. Part 4 will add autocomplete with `lucene-suggest` — prefix lookup
whose hits become `FILTER` chips, not leftover tokens in `q`. Part 5 will count
facet buckets under the same boolean query.

## Series

* [Part 1: Indexing]({{< ref "2026-09-09-lucene-bean-search-indexing" >}}) — Maven, fields, analyzer, document mapper
* [Part 2: Index Lifecycle]({{< ref "2026-09-10-lucene-bean-search-lifecycle" >}}) — writer, rebuild, upsert, keep warm
* [Part 3: Search]({{< ref "2026-09-11-lucene-bean-search-query-sync" >}}) — you are here
* Part 4: Suggest <!-- TODO: link when published --> — autocomplete
* Part 5: Facets <!-- TODO: link when published --> — counts and drill-down

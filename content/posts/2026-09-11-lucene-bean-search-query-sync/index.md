---
title: 'Integrating Apache Lucene for Bean Search — Part 3: Search'
description: "Build Lucene queries and resolve hits back to beans — the last mile from documents to your Java types."
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
* [Part 4: Suggest]({{< ref "2026-09-14-lucene-bean-search-suggest" >}})
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

## Build queries

Keep construction in one place (`TrackLuceneQueryBuilder`). That makes parity tests
easy: index known beans, assert hit ids.

A bookmarkable `q` string is enough for a local app:

| User query         | Lucene idea                        |
|--------------------|------------------------------------|
| `genre:Club`       | term on a keyword field            |
| `bpm:[120 TO 130]` | numeric range                      |
| `rating:5`         | exact numeric                      |
| `sinclar~`         | `FuzzyQuery` (opt-in)              |
| blank              | `MatchAllDocsQuery`                |

Hand-crafted queries look like this when you do not want a parser yet:

```java
// Exact id match on a StringField — not analyzed
Query q = new TermQuery(new Term(TrackIndexFields.ID, "42"));
TopDocs hits = searcher.search(q, 10);
```

Free-text across fields, with title beating artist:

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

Scoping (one playlist vs the whole library) stays **outside** Lucene: the handler
picks the base list, then `filter(base, q)` drops ids that are not in it.

```java
public List<Track> filter(List<Track> corpus, String q) {
    if (q == null || q.isBlank() || corpus.isEmpty()) {
        return List.copyOf(corpus);
    }
    try {
        IndexSearcher searcher = index.searcher();
        try (IndexReader reader = searcher.getIndexReader()) {
            TopDocs hits = searcher.search(
                    TrackLuceneQueryBuilder.build(q),
                    Math.max(1, reader.numDocs()));

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

When free-text scoring matters, walk `hits.scoreDocs` in order. When the query is
pure filters, corpus order is often enough.

## Next

You can filter and resolve hits. [Part 4]({{< ref "2026-09-14-lucene-bean-search-suggest" >}})
will add autocomplete with `lucene-suggest`. Part 5 will count facet buckets under the same `q`.

## Series

* [Part 1: Indexing]({{< ref "2026-09-09-lucene-bean-search-indexing" >}}) — Maven, fields, analyzer, document mapper
* [Part 2: Index Lifecycle]({{< ref "2026-09-10-lucene-bean-search-lifecycle" >}}) — writer, rebuild, upsert, keep warm
* [Part 3: Search]({{< ref "2026-09-11-lucene-bean-search-query-sync" >}}) — you are here
* [Part 4: Suggest]({{< ref "2026-09-14-lucene-bean-search-suggest" >}}) — autocomplete
* Part 5: Facets <!-- TODO: link when published --> — counts and drill-down

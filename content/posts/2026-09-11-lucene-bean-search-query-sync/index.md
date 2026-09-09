---
title: 'Integrating Apache Lucene for Bean Search — Part 3: Search'
description: "Build Lucene queries, resolve hits back to beans, and optionally add autocomplete with lucene-suggest."
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
date: '2026-09-11T10:00:00+02:00'
nolastmod: true
cover: cover.avif
draft: false
---

This post is part of a series of 3:

* [Part 1: Indexing]({{< ref "2026-09-09-lucene-bean-search-indexing" >}})
* [Part 2: Index Lifecycle]({{< ref "2026-09-10-lucene-bean-search-lifecycle" >}})
* [Part 3: Search]({{< ref "2026-09-11-lucene-bean-search-query-sync" >}})

[Part 1]({{< ref "2026-09-09-lucene-bean-search-indexing" >}}) mapped beans to documents.
[Part 2]({{< ref "2026-09-10-lucene-bean-search-lifecycle" >}}) owned the writer and kept
the index warm. Lucene still returns **documents**, not your Java types — so the last
mile is queries and hit → bean resolution.

## From documents to beans

Run a Lucene query, collect hit ids (and scores when relevant), then join back to your
beans — either by filtering a caller-provided corpus or by loading from a repository.

<!--more-->

## Build queries

You can hand-craft Lucene queries, or translate a user-facing string into a `Query`.

### Minimal example — term search

```java
// Exact id match on a StringField — not analyzed
Query q = new TermQuery(new Term(TrackIndexFields.ID, "42"));
TopDocs hits = searcher.search(q, 10); // at most 10 hits
```

### Free-text across boosted fields

Search several fields with relative boosts (title beats comment):

```java
BooleanQuery.Builder fields = new BooleanQuery.Builder();
// SHOULD = OR across fields; BoostQuery raises score when title matches
fields.add(new BoostQuery(containsQuery("title", term), 4.0f), BooleanClause.Occur.SHOULD);
fields.add(new BoostQuery(containsQuery("artist", term), 3.0f), BooleanClause.Occur.SHOULD);
fields.add(new BoostQuery(containsQuery("genre", term), 2.0f), BooleanClause.Occur.SHOULD);
fields.setMinimumNumberShouldMatch(1); // at least one field must match
Query freeText = fields.build();
```

### Fielded filters and ranges

Examples of what a small `TrackLuceneQueryBuilder` can produce from bookmarkable `q` strings:

| User query         | Lucene idea                                      |
|--------------------|--------------------------------------------------|
| `genre:Club`       | term / wildcard on a keyword field               |
| `bpm:[120 TO 130]` | `DoublePoint` / `DoubleField` range              |
| `rating:5`         | exact numeric                                    |
| `sinclar~`         | `FuzzyQuery` (opt-in typo tolerance)             |
| blank              | `MatchAllDocsQuery`                              |

Keep query construction in one place (`TrackLuceneQueryBuilder`). That makes parity tests
easy: index known beans, assert hit ids for representative queries.

## Resolve hits to beans

One approach that works well for playlist-style scoping:

1. Run the Lucene query against the full index.
2. Collect hit ids (and scores when relevant).
3. Intersect / order against a caller-provided **corpus** (`List<Track>`).

```java
/**
 * Narrow {@code corpus} to tracks that match {@code q}, preserving Lucene score order.
 * Scoping (playlist vs whole library) stays outside Lucene — pass the base list in.
 */
public List<Track> filter(List<Track> corpus, String q) {
    // Empty query → no filtering; return a defensive copy of the input
    if (q == null || q.isBlank() || corpus.isEmpty()) {
        return List.copyOf(corpus);
    }
    try {
        IndexSearcher searcher = index.searcher();
        // Close the reader when done — it holds a snapshot of the index
        try (IndexReader reader = searcher.getIndexReader()) {
            // Ask for up to every doc so we can intersect with corpus afterwards
            TopDocs hits = searcher.search(
                    TrackLuceneQueryBuilder.build(q),
                    Math.max(1, reader.numDocs()));

            // O(1) lookup: only keep hits that belong to this corpus (e.g. one playlist)
            Map<String, Track> byId = new HashMap<>(corpus.size());
            for (Track track : corpus) {
                byId.put(track.id(), track);
            }

            // Walk hits in score order; skip ids not in the corpus
            List<Track> ordered = new ArrayList<>(hits.scoreDocs.length);
            for (var hit : hits.scoreDocs) {
                // Stored id field (Field.Store.YES) — Lucene doc id ≠ Track.id
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

Why the corpus step? Keep **scoping outside Lucene**: the handler picks the base list
(all tracks or one playlist), then `filter(base, q)` drops ids that are not in that list.
For a generic bean store you can instead load beans by id from a repository after the search.

When free-text scoring matters, walk `hits.scoreDocs` in order. When the query is pure
filters, corpus order is often enough.

## Optional: autocomplete with `lucene-suggest`

If you declared `lucene-suggest`, wire an `AnalyzingInfixSuggester` on a second
directory. For small libraries it is fine to rebuild suggestions from the current bean
map after every mutation (incremental suggest delete is awkward):

```java
// Second Directory dedicated to suggestions (often also in-memory)
suggester = new AnalyzingInfixSuggester(suggestionDirectory, TrackAnalyzers.searchAnalyzer());
// Full rebuild after mutations — simpler than incremental suggest deletes
suggester.build(new YourInputIterator(beans));
// prefix → up to 10 suggestions; payloads can carry field name / metadata
List<Lookup.LookupResult> matches = suggester.lookup(prefix, Set.of(), 10, false, false);
```

Payloads can carry metadata (for example the field name: title / artist / genre). Skip
this entirely if you only need search and filters.

## Series

* [Part 1: Indexing]({{< ref "2026-09-09-lucene-bean-search-indexing" >}}) — Maven, fields, analyzer, document mapper
* [Part 2: Index Lifecycle]({{< ref "2026-09-10-lucene-bean-search-lifecycle" >}}) — writer, rebuild, upsert, keep warm
* [Part 3: Search]({{< ref "2026-09-11-lucene-bean-search-query-sync" >}}) — you are here

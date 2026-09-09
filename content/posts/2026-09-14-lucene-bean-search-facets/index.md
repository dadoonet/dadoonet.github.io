---
title: 'Integrating Apache Lucene for Bean Search — Part 5: Facets'
description: "Count and drill down on bean fields with Lucene facets — genre, rating, and friends — on the same in-process index as Parts 1–4."
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
date: '2026-09-14T10:00:00+02:00'
nolastmod: true
cover: cover.avif
draft: false
---

This post is part of a series:

* [Part 1: Indexing]({{< ref "2026-09-09-lucene-bean-search-indexing" >}})
* [Part 2: Index Lifecycle]({{< ref "2026-09-10-lucene-bean-search-lifecycle" >}})
* [Part 3: Search]({{< ref "2026-09-11-lucene-bean-search-query-sync" >}})
* [Part 4: Suggest]({{< ref "2026-09-12-lucene-bean-search-suggest" >}})
* [Part 5: Facets]({{< ref "2026-09-14-lucene-bean-search-facets" >}})

[Part 3]({{< ref "2026-09-11-lucene-bean-search-query-sync" >}}) can already **filter**
(`genre:Club`). A filter panel still needs something else: **how many** tracks sit
in Club vs Techno *under the current query*.

<!--more-->

You declared `lucene-facet` in [Part 1]({{< ref "2026-09-09-lucene-bean-search-indexing" >}}).
Counts live on the same in-process index as search. Lucene remains a **derived cache**:
rebuild or upsert after writes, then recount.

## Index the category

`genre.raw` is a `StringField` so `genre:Club` can be a term query. Counting is a
different access pattern: you want a **column** of labels, not a stored field on
each hit.

Add a `SortedSetDocValuesFacetField` next to the keyword (same idea for artist,
album, key). Do **not** facet on a `TextField` — tokens are not checkbox labels.
Numerics (`bpm`, `rating`, `year`) already carry DocValues from Part 1; range and
value counts read those, no extra field type.

```java
String genre = name(t.genre());
doc.add(new StringField(TrackIndexFields.GENRE_RAW, genre, Field.Store.YES));
// Category label for lucene-facet — not a replacement for the StringField above
doc.add(new SortedSetDocValuesFacetField("genre", genre));
```

`SortedSetDocValuesFacetField` is a helper. It does **not** write DocValues by
itself. Wrap every add / upsert with `FacetsConfig.build` or you silently count
nothing:

```java
private static final FacetsConfig FACETS = new FacetsConfig();

private static Document indexedDocument(Track track) throws IOException {
    return FACETS.build(TrackDocumentMapper.toDocument(track));
}
```

Use that same `FacetsConfig` instance at search time. After `commit`, open a new
NRT reader before counting.

## Count

Lucene 10.5 fills a collector, then `SortedSetDocValuesFacetCounts` turns it into
histograms. You do not walk `ScoreDoc`s.

```java
SortedSetDocValuesReaderState state =
        new DefaultSortedSetDocValuesReaderState(reader, FACETS);
FacetsCollector fc = FacetsCollectorManager.search(
                searcher, new MatchAllDocsQuery(), 1, new FacetsCollectorManager())
        .facetsCollector();
Facets facets = new SortedSetDocValuesFacetCounts(state, fc);
// facets.getAllChildren("genre") → Club=2, Techno=1
```

`n=1` is enough: we want the collector, not a hit list (`SearchService` already
resolved beans).

## Drill-down and sideways

Under `genre:Club`, the **key** histogram should shrink. The **genre** panel should
still show Techno — otherwise the user cannot change genre without clearing `q`.

Split the bookmarkable string: remainder (free text) is the base query; panel
tokens become `DrillDownQuery.add(dimension, query)`. Then `DrillSideways` runs
one collector for the filtered set and one per selected dimension *without* that
dimension’s own constraint:

```java
Query base = TrackLuceneQueryBuilder.build(remainder); // no genre: / bpm: tokens
DrillDownQuery drillDown = new DrillDownQuery(FACETS, base);
drillDown.add("genre", TrackLuceneQueryBuilder.build("genre:Club"));

Facets luceneFacets = new DrillSideways(searcher, FACETS, state)
        .search(drillDown, 1)
        .facets;
```

| Panel | Visible buckets (count > 0) |
|-------|-----------------------------|
| genre | Club **and** Techno         |
| bpm   | `80-90` **and** `120-130`   |

The **table** is still Club ∩ 120–129. Only the **counts** omit that panel’s own
filter — the usual e-commerce “narrow by brand without hiding the other brands”.

Keyword dims use `SortedSetDocValuesFacetCounts`. BPM bins use
`DoubleRangeFacetCounts` on the existing `bpm` field (half-open ranges, always
render every bucket including zeros). Rating / year use `LongValueFacetCounts`.
If you need both on the same collectors, override `DrillSideways.buildFacetsResult`
and wrap each collector with a `MultiFacets` — the default sideways class assumes
one implementation.

## Hand `(value, count)` to the UI

```java
public record FacetBucket(String value, int count) {}
```

Map `LabelAndValue` once in `TrackFacetService`. The template prints `Club (12)`.
Clicking a checkbox still toggles a token in `q`; the next request filters the
table (Part 3) and refreshes every panel here.

## What this model does not do

One JVM, one `Directory`, rebuilt at startup. No replica, no cluster. Restart
without a rebuild and search **and** facets are empty. If an upsert fails, fall
back to a full rebuild so the cache cannot drift.

When the corpus or the ops model outgrows a process-local Lucene cache, the next
step is a search server in front of the same beans — same `q`, same filter panel,
a different engine behind `TrackSearchIndex`. That is a switch, not a rewrite of
Parts 1–5.

## Series

* [Part 1: Indexing]({{< ref "2026-09-09-lucene-bean-search-indexing" >}}) — Maven, fields, analyzer, document mapper
* [Part 2: Index Lifecycle]({{< ref "2026-09-10-lucene-bean-search-lifecycle" >}}) — writer, rebuild, upsert, keep warm
* [Part 3: Search]({{< ref "2026-09-11-lucene-bean-search-query-sync" >}}) — queries, hits → beans
* [Part 4: Suggest]({{< ref "2026-09-12-lucene-bean-search-suggest" >}}) — autocomplete
* [Part 5: Facets]({{< ref "2026-09-14-lucene-bean-search-facets" >}}) — you are here

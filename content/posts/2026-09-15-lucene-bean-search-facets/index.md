---
title: 'Integrating Apache Lucene for Bean Search — Part 5: Facets'
description: "Count Club (26) and 120–130 (52) under the same BooleanQuery as Part 3 — lucene-facet histograms, not a second navigation model."
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
date: '2026-09-15T07:00:00+02:00'
nolastmod: true
cover: cover.avif
draft: false
---

{{< series-intro >}}

[Part 3]({{< ref "2026-09-11-lucene-bean-search-query-sync" >}}) already **navigates**:
`FILTER genre:Club`, `MUST_NOT` on keys, bookmarkable params. A filter panel still
needs something else: **how many** tracks sit in Club vs Dance *under that
boolean query*.

You declared `lucene-facet` in [Part 1]({{< ref "2026-09-09-lucene-bean-search-indexing" >}}).
Counts live on the same in-process index as search.

<!--more-->

{{< figure src="faceted-navigation.avif" caption="`q=Bob` with the filter panel open: BPM, genre, rating, and year buckets counted under the Part 3 query. Clicking a checkbox is still Part 3." >}}

`q=Bob` is the free-text `MUST` from Part 3. The numbers on the right
(`Club (26)`, `120 – 130 (52)`, `★★★★★ (13)`, `2020s (15)`) are facet counts
on that same query. Clicking **Club** still writes `genre=Club` — the Java from
Part 3. This post only adds the histograms.

## Index the category

`genre.raw` is a `StringField` so Part 3 can filter. Counting is a different
access pattern: you want a **column** of labels, not a stored field on each hit.

Add a `SortedSetDocValuesFacetField` next to the keyword. Do **not** facet on a
`TextField` — tokens are not checkbox labels. Numerics (`bpm`, `rating`, `year`)
already carry DocValues from Part 1; range and value counts read those, no extra
field type.

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

## Count under `q=Bob`

Lucene 10.5 fills a collector, then `SortedSetDocValuesFacetCounts` turns it into
histograms. You do not walk `ScoreDoc`s. Reuse the Part 3 query:

```java
Query lucene = freeText("Bob"); // the MUST query from Part 3

SortedSetDocValuesReaderState state =
        new DefaultSortedSetDocValuesReaderState(reader, FACETS);
FacetsCollector fc = FacetsCollectorManager.search(
                searcher, lucene, 1, new FacetsCollectorManager())
        .facetsCollector();
Facets facets = new SortedSetDocValuesFacetCounts(state, fc);
// facets.getAllChildren("genre") → Club=26, Dance=2, …
```

`n=1` is enough: we want the collector, not a hit list. Part 3 already resolved
the table.

BPM bins and star ratings on the screenshot are the same collector, different
readers:

```java
// 10-BPM buckets, including zeros so empty ranges stay visible
Facets bpm = new DoubleRangeFacetCounts("bpm", fc, ranges);
// exact stars 0–5
Facets rating = new LongValueFacetCounts("rating", fc);
// year / decade from the same IntField DocValues
Facets year = new LongValueFacetCounts("year", fc);
```

Hand `(value, count)` to the template once:

```java
public record FacetBucket(String value, int count) {}
// Club (26), 120 – 130 (52), ★★★★★ (13)
```

## When a Part 3 FILTER is on

Under `genre=Club`, the **BPM** histogram should shrink. The **genre** panel
should still show Dance — otherwise the user cannot change genre without
clearing the param. That is counting, not a new navigation model: the table
still uses the full Part 3 `BooleanQuery`.

If `FILTER genre:Club` were already in the base query, Lucene could not drop it
for the genre collector. Split the request:

* **Base** — `MUST` free text, `MUST_NOT` exclusions, `FILTER` for *other*
  dimensions (bpm, key, …).
* **Drill-down** — each selected panel dim via `DrillDownQuery.add`.

Then `DrillSideways` runs one collector for the filtered set and one per selected
dimension *without* that dimension’s own constraint:

```java
Query base = TrackLuceneQueryBuilder.buildStructured(
        "Bob",          // MUST
        otherFilters,   // FILTER — bpm, key, … (not genre)
        mustNots);      // MUST_NOT

DrillDownQuery drillDown = new DrillDownQuery(FACETS, base);
drillDown.add("genre", new TermQuery(new Term(TrackIndexFields.GENRE_RAW, "Club")));

Facets luceneFacets = new DrillSideways(searcher, FACETS, state)
        .search(drillDown, 1)
        .facets;
```

The usual e-commerce trick: narrow the table by brand without hiding the other
brands. If you need keywords and numeric ranges on the same collectors, override
`DrillSideways.buildFacetsResult` and wrap each collector with a `MultiFacets` —
the default sideways class assumes one implementation.

When a playlist is selected, `FILTER` a `TermInSetQuery` on `id` into the **base**
so histograms match the table. Corpus intersection after search (Part 3) cannot
fix counts.

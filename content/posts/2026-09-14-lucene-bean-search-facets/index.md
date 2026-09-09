---
title: 'Integrating Apache Lucene for Bean Search — Part 4: Facets'
description: "Count and drill down on bean fields with Lucene facets — genre, rating, and friends — on the same in-process index as Parts 1–3."
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

This post is part of a series of 4:

* [Part 1: Indexing]({{< ref "2026-09-09-lucene-bean-search-indexing" >}})
* [Part 2: Index Lifecycle]({{< ref "2026-09-10-lucene-bean-search-lifecycle" >}})
* [Part 3: Search]({{< ref "2026-09-11-lucene-bean-search-query-sync" >}})
* [Part 4: Facets]({{< ref "2026-09-14-lucene-bean-search-facets" >}})

[Part 1]({{< ref "2026-09-09-lucene-bean-search-indexing" >}}) mapped `Track` beans to documents.
[Part 2]({{< ref "2026-09-10-lucene-bean-search-lifecycle" >}}) owned the writer.
[Part 3]({{< ref "2026-09-11-lucene-bean-search-query-sync" >}}) turned a `q` string into hits
and joined those hits back to beans. You can already **filter** (`genre:Club`). A filter
panel still needs something else: **how many** tracks sit in Club vs Techno vs House
*under the current query*.

<!--more-->

Lucene remains a **derived cache**. Counts come from the same in-process index as search;
the primary store stays the source of truth. Rebuild or upsert after successful writes,
then recount — never treat a facet bucket as authoritative on its own.

Walking every hit and tallying stored fields works for a few thousand documents. It is
not faceting. Apache Lucene ships `lucene-facet` for this: DocValues ordinals, range
counts, `DrillDownQuery`, and `DrillSideways` so a selected checkbox does not hide its
neighbours. That is the recipe below.

## Add `lucene-facet`

Same version as Parts 1–3 (**10.5.1**). Pin it next to `lucene-core` in the parent
`dependencyManagement`, then declare it (without a version) in the module that owns
the index.

```xml
<dependency>
  <groupId>org.apache.lucene</groupId>
  <artifactId>lucene-facet</artifactId>
  <version>10.5.1</version>
</dependency>
```

Look up the **latest stable** Lucene release at implementation time; keep
`lucene-core`, `lucene-analysis-common`, `lucene-suggest`, and `lucene-facet` on the
**same** version.

No taxonomy index. Our dimensions are flat labels (`Club`, `8A`, `present`), not
`Electronics/Phones/Pixel` trees. Sorted-set DocValues are enough — one extra field
on the same `Directory`, no second writer.

## Index twice: filter vs count

Part 1 already stored `genre.raw` as a `StringField` so `genre:Club` can be a term
query. Counting is a different access pattern. Stored fields are row-oriented: you
recover a value *after* you have a hit. Facet counts need **column-stride** data —
every genre in the matching set, without loading title, artist, or id.

So each keyword you want on a checkbox list is indexed **twice on purpose**:

```java
String genre = name(t.genre());
// Filter / bookmarkable q — term query, stored if you still read it on hits
doc.add(new StringField(TrackIndexFields.GENRE_RAW, genre, Field.Store.YES));
// Count — SortedSet DocValues ordinals. lucene-facet reads this column, not the StringField
doc.add(new SortedSetDocValuesFacetField("genre",
        genre.isBlank() ? TrackFacets.MISSING_VALUE : genre));
```

Do the same for `artist`, `album`, `key`, `artwork`. Keep the analyzed `TextField`s
from Part 1 for free-text search — you cannot facet on a token stream (`Ultra` / `naté`
is not an Artist checkbox). The SSDV copy is the **category label**, not a replacement
for the analyzer.

Numerics are already in good shape. `DoubleField` / `IntField` / `LongField` write
DocValues; `DoubleRangeFacetCounts` and `LongValueFacetCounts` read those. You do
**not** add a second field type for BPM, rating, or year.

| Role                         | Field                                            | Why                                                                 |
|------------------------------|--------------------------------------------------|---------------------------------------------------------------------|
| Filter (`genre:Club`)        | `StringField` `genre.raw`                        | Exact term / wildcard in `TrackLuceneQueryBuilder`                  |
| Count (genre histogram)      | `SortedSetDocValuesFacetField("genre", …)`       | Column of ordinals; no stored-field visit per hit                   |
| Filter (`bpm:[120 TO 129]`)  | `DoubleField` `bpm`                              | Points + DocValues from Part 1                                      |
| Count (BPM ranges)           | same `bpm` DocValues                             | `DoubleRangeFacetCounts` bins the existing numeric column           |
| Free-text                    | `TextField` `artist` / `title`                   | Search only — never a facet source                                  |

### Empty labels cannot be facet values

Lucene’s `FacetLabel` **rejects** an empty path component. The bookmarkable token for
“no genre” can still be `genre:""`; the **indexed** SSDV value cannot be `""`. Use a
sentinel (`$missing`) at index time, strip it from the histogram you render, and read
it back when the panel needs a “No genre” count.

```java
/** Indexed SSDV label when a keyword is blank. Not a user-facing token. */
public static final String MISSING_VALUE = "$missing";
```

## `FacetsConfig.build` is not optional

`SortedSetDocValuesFacetField` is an indexing **helper**. It does not write DocValues
by itself. `FacetsConfig.build(doc)` copies each dim/path into the `$facets` sorted-set
column that `SortedSetDocValuesFacetCounts` reads, and into the drill-down terms
`DrillDownQuery` expects. Index the raw helper and search later: you silently count
**nothing**.

Share **one** `FacetsConfig` between index and search — the config is not stored in
the index. Keyword dims here are single-valued (one genre per track), so you do not
call `setMultiValued`.

```java
public final class TrackFacets {

    public static final String GENRE = "genre";
    public static final String ARTIST = "artist";
    public static final String ALBUM = "album";
    public static final String KEY = "key";
    public static final String ARTWORK = "artwork";
    public static final String MISSING_VALUE = "$missing";

    // Same instance at index time and search time
    private static final FacetsConfig CONFIG = new FacetsConfig();

    public static FacetsConfig config() {
        return CONFIG;
    }
}
```

Wrap every add and upsert in Part 2’s writer:

```java
private static Document indexedDocument(Track track) throws IOException {
    // build() materializes $facets; skip it and SortedSetDocValuesFacetCounts sees an empty column
    return TrackFacets.config().build(TrackDocumentMapper.toDocument(track));
}

public void rebuild(List<Track> tracks) throws IOException {
    synchronized (writeLock) {
        writer.deleteAll();
        for (Track track : tracks) {
            writer.addDocument(indexedDocument(track));
        }
        writer.commit();
    }
}
```

`updateDocument` must use the same helper. After commit, open a **new** NRT reader
before counting: `DefaultSortedSetDocValuesReaderState` is tied to that reader. Cache
the state across upserts and the ordinals go stale.

A tiny fixture is enough to prove `build()` ran — two Club, one Techno, then
`getAllChildren("genre")` must return those labels. If the list is empty, `build()`
never wrapped the document.

## Count without visiting hits

Lucene 10.5 gathers matching docs with `FacetsCollectorManager` (not a hand-rolled
loop over `ScoreDoc`). Then `SortedSetDocValuesFacetCounts` turns the collector into
per-dimension histograms.

```java
IndexSearcher searcher = index.searcher();
try (IndexReader reader = searcher.getIndexReader()) {
    FacetsConfig config = TrackFacets.config();
    // State is per-reader: rebuild it after every commit / upsert (NRT ordinals change)
    SortedSetDocValuesReaderState state =
            new DefaultSortedSetDocValuesReaderState(reader, config);

    // n=1: we want the collector, not a hit list (SearchService already resolved beans)
    FacetsCollector fc = FacetsCollectorManager.search(
                    searcher, new MatchAllDocsQuery(), 1, new FacetsCollectorManager())
            .facetsCollector();

    Facets facets = new SortedSetDocValuesFacetCounts(state, fc);
    org.apache.lucene.facet.FacetResult genre = facets.getAllChildren("genre");
    // genre.labelValues → Club=2, Techno=1  (LabelAndValue, still Lucene types)
}
```

That is global counts. A filter panel also needs **drill-down** (counts under
`genre:Club`) and **sideways** counts (the genre panel itself still shows Techno).

## Drill-down is a different query type

If panel tokens stay inside the same `q` string that `TrackLuceneQueryBuilder` parses
for search, `DrillSideways` cannot drop one dimension for the sideways collector —
it never saw which clause was “the genre checkbox”.

Split the bookmarkable string:

1. **Remainder** (free text, `artist:` as a search field, …) → base `Query`.
2. **Panel tokens** (`genre:Club`, `bpm:[120 TO 129]`, `rating:5`) →
   `DrillDownQuery.add(dimension, query)`.

`QueryFacets.parse` / `toQuery` from a small helper next to the query builder already
round-trip those tokens. Reuse it:

```java
QueryFacets parsed = QueryFacets.parse(q);
// Remainder only — if genre:Club stayed here, DrillSideways could not omit it sideways
Query base = TrackLuceneQueryBuilder.build(parsed.remainder());
DrillDownQuery drillDown = new DrillDownQuery(TrackFacets.config(), base);

// Dimension name is how sideways collection is keyed; the Query is what actually filters
if (!parsed.genres().isEmpty() || parsed.missingGenre()) {
    drillDown.add("genre", TrackLuceneQueryBuilder.build(genreOnly(parsed).toQuery()));
}
if (!parsed.bpmBuckets().isEmpty() || parsed.missingBpm()) {
    // Ranges are not SSDV labels — pass the same numeric Query search already uses
    drillDown.add("bpm", TrackLuceneQueryBuilder.build(bpmOnly(parsed).toQuery()));
}
```

`SearchService` keeps calling `TrackLuceneQueryBuilder.build(q)` on the **full**
string. The table and the panel share one bookmarkable `q`; only counting needs the
split. Dual indexing (keyword `StringField` + SSDV) is what makes that split cheap.

Optional playlist scope stays a `MUST` `TermInSetQuery` on `id`, on the **base** query,
exactly as in Part 3. Empty scope → `MatchNoDocsQuery`.

## Self-excluding: `DrillSideways`

Selecting `genre:Club` must shrink the **table** and the **key** histogram, but the
genre panel must still show Techno. Otherwise the user cannot add a second genre
without clearing `q` by hand.

A second `search` after stripping `genre:` from `q` would re-parse, re-score, and
drift from the drill-down Lucene already built. `DrillSideways` runs one drill-down
collector plus one sideways collector **per selected dimension**:

```java
SortedSetDocValuesReaderState state =
        new DefaultSortedSetDocValuesReaderState(reader, config);
DrillSideways sideways = new TrackDrillSideways(searcher, config, state);
// n=1 again: facets, not hits
Facets luceneFacets = sideways.search(drillDown, 1).facets;
```

On a tiny fixture (Club@82, Club@128, Techno@128) with
`q = "genre:Club bpm:[120 TO 129]"`:

| Panel | Visible buckets (count > 0) |
|-------|-----------------------------|
| genre | Club **and** Techno         |
| bpm   | `80-90` **and** `120-130`   |

The **result list** is still Club ∩ 120–129. Only the **counts** on each panel omit
that panel’s own drill-down. That is the usual e-commerce “narrow by brand without
hiding the other brands” behaviour.

## Mix keyword and numeric facets

`DrillSideways` defaults to one facet implementation. We need three on the **same**
collectors:

| Dimension                          | Lucene counter                  | Why                                                   |
|------------------------------------|---------------------------------|-------------------------------------------------------|
| genre, artist, album, key, artwork | `SortedSetDocValuesFacetCounts` | Discrete labels already in `$facets`                  |
| bpm                                | `DoubleRangeFacetCounts`        | Fixed UI ranges, not one bucket per 128.0 / 128.5     |
| rating, year                       | `LongValueFacetCounts`          | Distinct ints already on the numeric DocValues column |

Subclass `DrillSideways` and override `buildFacetsResult` so each collector (drill-down
**and** each sideways array slot) is wrapped the same way:

```java
private static final class TrackDrillSideways extends DrillSideways {

    TrackDrillSideways(
            IndexSearcher searcher, FacetsConfig config, SortedSetDocValuesReaderState state) {
        super(searcher, config, state);
    }

    @Override
    protected Facets buildFacetsResult(
            FacetsCollector drillDowns,
            FacetsCollector[] drillSideways,
            String[] drillSidewaysDims) throws IOException {
        Facets drillDownFacets = mix(drillDowns);
        if (drillSideways == null || drillSideways.length == 0) {
            return drillDownFacets;
        }
        // One sideways collector per selected dim — MultiFacets picks by dimension name
        Map<String, Facets> sideways = new HashMap<>();
        for (int i = 0; i < drillSideways.length; i++) {
            sideways.put(drillSidewaysDims[i], mix(drillSideways[i]));
        }
        return new MultiFacets(sideways, drillDownFacets);
    }

    private Facets mix(FacetsCollector hits) throws IOException {
        FacetsCollector collector = hits != null ? hits : new FacetsCollector();
        Map<String, Facets> byDim = new LinkedHashMap<>();
        Facets ssdv = new SortedSetDocValuesFacetCounts(state, collector);
        byDim.put("genre", ssdv);
        byDim.put("artist", ssdv);
        byDim.put("album", ssdv);
        byDim.put("key", ssdv);
        byDim.put("artwork", ssdv);
        byDim.put("bpm", new DoubleRangeFacetCounts("bpm", collector, BPM_RANGES));
        byDim.put("rating", new LongValueFacetCounts("rating", collector));
        byDim.put("year", new LongValueFacetCounts("year", collector));
        return new MultiFacets(byDim);
    }
}
```

The same `SortedSetDocValuesFacetCounts` instance serves every keyword dim — it
already knows all SSDV dimensions from the reader state.

### BPM — declare the bins once

Do not emit one bucket per stored BPM. Map the DocValues double onto closed UI
ranges, and **always** return every range (count may be 0) so the checkbox list
does not jump:

| Bucket id | Query token        | `DoubleRange` (min, max)   |
|-----------|--------------------|----------------------------|
| `lt80`    | `bpm:[0 TO 79]`    | `(0, 80)` — 0 is “missing” |
| `80-90`   | `bpm:[80 TO 89]`   | `[80, 90)`                 |
| `90-100`  | `bpm:[90 TO 99]`   | `[90, 100)`                |
| `100-110` | `bpm:[100 TO 109]` | `[100, 110)`               |
| `110-120` | `bpm:[110 TO 119]` | `[110, 120)`               |
| `120-130` | `bpm:[120 TO 129]` | `[120, 130)`               |
| `130-140` | `bpm:[130 TO 139]` | `[130, 140)`               |
| `140-150` | `bpm:[140 TO 149]` | `[140, 150)`               |
| `150+`    | `bpm:[150 TO 999]` | `[150, 1000)`              |

The label can say `120 – 130` while the range is `[120, 130)`. Put `bpm <= 0` in a
separate `$missing` range `(-∞, 0]`, not in `lt80`.

```java
// Half-open [min, max+1) so 129.9 lands in 120-130 and 130.0 in the next bucket
ranges.add(new DoubleRange(bucket.id(), min, true, max + 1.0, false));
```

### Rating and year — distinct values, then group in Java if needed

`LongValueFacetCounts` already returns one bucket per distinct int. Always render
stars `5` down to `0` (fill zeros). For the year **panel**, group those ints into
decades (`2010s`, `2020s`) in Java; when the current query leaves only one decade
in scope, show the individual years instead. The query tokens stay
`year:[2010 TO 2019]` / `year:2022` — Part 3 already knows how to build them.

## Return `(value, count)`, not Lucene docs

The UI wants `Club (12)`, not `LabelAndValue`. Map once at the edge of
`TrackFacetService`:

```java
public record FacetBucket(String value, int count) {}

private static List<FacetBucket> keywordBuckets(String dimension, Facets facets)
        throws IOException {
    Map<String, Integer> counts = new HashMap<>();
    org.apache.lucene.facet.FacetResult raw = facets.getAllChildren(dimension);
    if (raw != null) {
        for (LabelAndValue lv : raw.labelValues) {
            counts.merge(lv.label, lv.value.intValue(), Integer::sum);
        }
    }
    counts.remove(TrackFacets.MISSING_VALUE); // sentinel is not a checkbox label
    return counts.entrySet().stream()
            .map(e -> new FacetBucket(e.getKey(), e.getValue()))
            .sorted(Comparator.comparing(FacetBucket::value, String.CASE_INSENSITIVE_ORDER))
            .toList();
}
```

Hide zero-count **dynamic** values (a genre that never appears). Keep zero-count
**fixed** buckets (BPM ranges, star ratings). Clicking a checkbox still toggles a
token in `q`; the next request filters the table via `SearchService` and refreshes
every panel via `TrackFacetService`.

## What this model does not do

This is still one JVM, one `ByteBuffersDirectory` (or one `FSDirectory`), rebuilt at
startup and upserted after writes:

* Facet ordinals live next to the search index. Restart without a rebuild and both
  are empty.
* `DefaultSortedSetDocValuesReaderState` must follow the NRT reader. After `upsert`,
  open a new searcher before counting.
* There is no replica, no REST API, no cluster.
* The primary store remains authoritative. If an upsert fails, fall back to a full
  rebuild so search **and** facets cannot drift silently.

When the corpus, the ops model, or the query language outgrows a process-local Lucene
cache, the next step is a search server in front of the same beans — same `q`, same
filter panel, a different engine behind `TrackSearchIndex`. That is a switch, not a
rewrite of Parts 1–4.

## Series

* [Part 1: Indexing]({{< ref "2026-09-09-lucene-bean-search-indexing" >}}) — Maven, fields, analyzer, document mapper
* [Part 2: Index Lifecycle]({{< ref "2026-09-10-lucene-bean-search-lifecycle" >}}) — writer, rebuild, upsert, keep warm
* [Part 3: Search]({{< ref "2026-09-11-lucene-bean-search-query-sync" >}}) — queries, hits → beans, optional suggest
* [Part 4: Facets]({{< ref "2026-09-14-lucene-bean-search-facets" >}}) — you are here

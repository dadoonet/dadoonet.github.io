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

## Same artefacts as Parts 1–3

Apache Lucene ships a `lucene-facet` module (taxonomy index, `FacetsConfig`,
`SortedSetDocValuesFacetCounts`, `DrillDownQuery`). You do **not** need it here.

Parts 1–3 already store the keyword and numeric values a filter panel will count
(`genre.raw`, `rating`, `bpm`, `year`) with `Field.Store.YES`. For a few thousand beans,
run the **same** query `SearchService` uses, walk the hits, and tally stored fields.
No extra Maven artefact, no second directory, no `FacetsConfig`. Stay on Lucene
**10.5.1** — `lucene-core`, `lucene-analysis-common`, and optional `lucene-suggest` —
exactly as in Part 1.

`lucene-facet` starts to pay off when the corpus is large enough that visiting every
matching document is the slow path. Until then, stored-field counting keeps the recipe
on one `IndexSearcher`.

## Store the values you will count

Part 1 already indexed filter fields. Facet counting reads those **stored** values, so
the mapper delta is small: add any extra dimension you want on the panel, and keep
`Store.YES`.

Analyzed `TextField`s (`title`, `artist`) are a bad facet source — tokens are split and
lowercased. Count a sibling keyword (`genre.raw`), not the full-text field.

```java
// Already in Part 1 — Store.YES is what counting will read back
doc.add(new StringField(TrackIndexFields.GENRE_RAW, name(t.genre()), Field.Store.YES));
doc.add(new DoubleField(TrackIndexFields.BPM, t.bpm(), Field.Store.YES));
doc.add(new IntField(TrackIndexFields.RATING, t.ratingStars(), Field.Store.YES));

// Extra dimensions the filter panel will count (same Store.YES rule)
doc.add(new StringField(TrackIndexFields.KEY_RAW, name(t.key()), Field.Store.YES));
doc.add(new IntField(TrackIndexFields.YEAR, t.year(), Field.Store.YES));
```

| Dimension | Indexed as                  | Facet value              |
|-----------|-----------------------------|--------------------------|
| genre     | `genre.raw` (`StringField`) | exact name (`Club`)      |
| key       | `key.raw` (`StringField`)   | key name (`8A`)          |
| rating    | `rating` (`IntField`)       | `0`–`5`                  |
| bpm       | `bpm` (`DoubleField`)       | range bucket (`120-130`) |
| year      | `year` (`IntField`)         | decade (`2020s`) or year |

`artist` stays a `TextField` for search. If you ever need an Artist checkbox list, add
an `artist.raw` `StringField` the same way as `genre.raw` — do not facet on the analyzed
field.

## Return `(value, count)`, not Lucene docs

The UI wants labels like `Club (12)`, not `ScoreDoc`s. Two small types are enough:

```java
/** One value in one dimension, plus how many matching tracks carry it. */
public record FacetBucket(String value, int count) {}

/** Immutable buckets keyed by dimension name (`genre`, `rating`, …). */
public final class FacetResult {

    private final Map<String, List<FacetBucket>> bucketsByDimension;

    public FacetResult(Map<String, List<FacetBucket>> bucketsByDimension) {
        this.bucketsByDimension = bucketsByDimension.entrySet().stream()
                .collect(Collectors.toUnmodifiableMap(
                        Map.Entry::getKey,
                        e -> List.copyOf(e.getValue())));
    }

    public List<FacetBucket> buckets(String dimension) {
        return bucketsByDimension.getOrDefault(dimension, List.of());
    }
}
```

## Count stored fields under the current query

`TrackFacetService` shares `TrackSearchIndex` with `SearchService`. Blank `q` means the
whole index (`MatchAllDocsQuery` inside `TrackLuceneQueryBuilder`). Otherwise it is the
same bookmarkable string as search: `genre:Club`, `bpm:[120 TO 129]`, free text, …

```java
public final class TrackFacetService {

    private static final Set<String> DIMENSIONS =
            Set.of("genre", "key", "rating", "bpm", "year");

    private final TrackSearchIndex index;

    public TrackFacetService(TrackSearchIndex index) {
        this.index = index;
    }

    /** Aggregations under {@code q}; blank q means the whole index. */
    public FacetResult facets(String q, Set<String> dimensions) {
        return facets(q, dimensions, Set.of());
    }

    /**
     * {@code excludeDimensions} are stripped from {@code q} before counting
     * (self-excluding navigation — see below).
     */
    public FacetResult facets(String q, Set<String> dimensions, Set<String> excludeDimensions) {
        Set<String> requested = dimensions == null ? Set.of() : new HashSet<>(dimensions);
        requested.retainAll(DIMENSIONS);
        if (requested.isEmpty()) {
            return new FacetResult(Map.of());
        }

        try {
            IndexSearcher searcher = index.searcher();
            try (IndexReader reader = searcher.getIndexReader()) {
                Query query = queryExcluding(q, excludeDimensions);
                // Same ceiling as SearchService: every doc, then we tally stored fields
                TopDocs hits = searcher.search(query, Math.max(1, reader.numDocs()));

                Map<String, Map<String, Integer>> counts = new LinkedHashMap<>();
                requested.stream().sorted()
                        .forEach(dim -> counts.put(dim, new HashMap<>()));
                Set<String> wanted = storedFieldsFor(counts.keySet());
                StoredFields storedFields = searcher.storedFields();

                for (var hit : hits.scoreDocs) {
                    // Load only the facet fields — not title / artist / id
                    var document = storedFields.document(hit.doc, wanted);
                    for (String dimension : counts.keySet()) {
                        accumulate(counts.get(dimension), dimension, document);
                    }
                }

                Map<String, List<FacetBucket>> result = new LinkedHashMap<>();
                for (var entry : counts.entrySet()) {
                    result.put(entry.getKey(), toBuckets(entry.getKey(), entry.getValue()));
                }
                return new FacetResult(result);
            }
        } catch (IOException e) {
            throw new UncheckedIOException("Unable to compute track facets", e);
        }
    }
}
```

`storedFields.document(docId, wanted)` is the cheap path: ask Lucene for `genre.raw` and
`rating`, not the whole stored document.

Numeric fields need `numericValue()`, not `document.get(field)`:

```java
private static String numericIntValue(Document document, String field) {
    IndexableField value = document.getField(field);
    return value != null && value.numericValue() != null
            ? String.valueOf(value.numericValue().intValue())
            : null;
}

private static void accumulate(
        Map<String, Integer> counts, String dimension, Document document) {
    switch (dimension) {
        case "rating" -> {
            String raw = numericIntValue(document, TrackIndexFields.RATING);
            if (raw != null) counts.merge(raw, 1, Integer::sum);
        }
        case "bpm" -> {
            String raw = numericDoubleValue(document, TrackIndexFields.BPM);
            if (raw == null) return;
            bpmBucketForValue(Double.parseDouble(raw))
                    .ifPresent(bucket -> counts.merge(bucket.id(), 1, Integer::sum));
        }
        case "year" -> {
            String raw = numericIntValue(document, TrackIndexFields.YEAR);
            if (raw != null) {
                int year = Integer.parseInt(raw);
                counts.merge(decadeLabel(decadeStart(year)), 1, Integer::sum);
            }
        }
        default -> { // genre, key — stored keyword as-is
            String value = switch (dimension) {
                case "genre" -> document.get(TrackIndexFields.GENRE_RAW);
                case "key" -> document.get(TrackIndexFields.KEY_RAW);
                default -> null;
            };
            if (value != null && !value.isBlank()) {
                counts.merge(value, 1, Integer::sum);
            }
        }
    }
}
```

## Drill-down: filter and recount

Pass the **current** `q` into `facets`. Other dimensions shrink to the filtered set:

```java
try (TrackSearchIndex index = new TrackSearchIndex()) {
    index.rebuild(tracks);
    TrackFacetService facets = new TrackFacetService(index);

    FacetResult all = facets.facets("", Set.of("key"));
    FacetResult club = facets.facets("genre:Club", Set.of("key"));

    // all.buckets("key") covers the whole library
    // club.buckets("key") only keys that appear on Club tracks
}
```

On a tiny fixture (two Club tracks, one Techno), `genre:Club` drops the key histogram
from 3 documents to 2 — the same query `SearchService.filter(corpus, "genre:Club")` would
use. There is no separate “facet query” type: drill-down **is** the search `q`.

## Self-excluding navigation

If you count `genre` while `q` already contains `genre:Club`, the genre panel collapses
to a single bucket. Checkboxes for Techno disappear, so the user cannot add a second
genre (or switch) without clearing the query by hand.

The fix is to **strip that dimension** from `q` before counting it. Genre counts then
ignore the selected genre, but still honour BPM, rating, and free text. BPM counts ignore
the selected BPM bucket, but still honour genre. Each panel stays navigable.

```java
private static Query queryExcluding(String q, Set<String> excludeDimensions) {
    QueryFacets parsed = QueryFacets.parse(q);
    if (excludeDimensions != null && !excludeDimensions.isEmpty()) {
        parsed = parsed.withoutDimensions(excludeDimensions);
    }
    // Rebuild the bookmarkable string, then the same Lucene query as search
    return TrackLuceneQueryBuilder.build(parsed.toQuery());
}
```

`QueryFacets` is a structured view of the panel-owned tokens inside `q` (`genre`, `key`,
`bpm`, `rating`, `year`). `parse` / `toQuery` round-trip so the search bar stays the
single source of truth (bookmarkable URLs). `withoutDimensions` clears one field and
leaves the remainder (free text, `artist:`, …) untouched.

```java
QueryFacets parsed = QueryFacets.parse("genre:Club bpm:[120 TO 129]");
QueryFacets withoutGenre = parsed.withoutDimensions(Set.of("genre"));
// withoutGenre.toQuery() → "bpm:[120 TO 129]"  (genre stripped, BPM kept)
```

Call it per panel:

```java
// Genre checkboxes: honour BPM / text, ignore the selected genre
facets.facets(q, Set.of("genre"), Set.of("genre"));

// BPM checkboxes: honour genre / text, ignore the selected BPM range
facets.facets(q, Set.of("bpm"), Set.of("bpm"));
```

With three tracks (Club@82, Club@128, Techno@128) and
`q = "genre:Club bpm:[120 TO 129]"`:

| Panel counted with self-exclusion | Visible buckets (count > 0) |
|-----------------------------------|-----------------------------|
| `genre` (genre stripped)          | Club **and** Techno         |
| `bpm` (bpm stripped)              | `80-90` **and** `120-130`   |

The **result list** is still Club ∩ 120–129. Only the **counts** on each panel pretend
that panel’s own filter is off. That is the usual e-commerce “narrow by brand without
hiding the other brands” behaviour.

## Numeric buckets

Keyword dimensions (`genre`, `key`) emit one bucket per distinct stored value, sorted
case-insensitively. Numerics need a stable list so a checkbox does not vanish when its
count is zero. `bpmBucketForValue` and `decadeStart` in `accumulate` are the helpers
behind the tables below.

### Rating — six fixed stars

Always render `5` down to `0`, even when a star has no tracks:

```java
List<FacetBucket> buckets = new ArrayList<>();
for (int stars = 5; stars >= 0; stars--) {
    buckets.add(new FacetBucket(
            String.valueOf(stars),
            counts.getOrDefault(String.valueOf(stars), 0)));
}
```

### BPM — fixed ranges

Do not emit one bucket per BPM value (`128.0`, `128.5`, …). Map the stored double onto
a closed range, and always return every range:

| Bucket id | Query token           | Inclusive range |
|-----------|-----------------------|-----------------|
| `lt80`    | `bpm:[0 TO 79]`       | 0–79            |
| `80-90`   | `bpm:[80 TO 89]`      | 80–89           |
| `90-100`  | `bpm:[90 TO 99]`      | 90–99           |
| `100-110` | `bpm:[100 TO 109]`    | 100–109         |
| `110-120` | `bpm:[110 TO 119]`    | 110–119         |
| `120-130` | `bpm:[120 TO 129]`    | 120–129         |
| `130-140` | `bpm:[130 TO 139]`    | 130–139         |
| `140-150` | `bpm:[140 TO 149]`    | 140–149         |
| `150+`    | `bpm:[150 TO 999]`    | 150–999         |

The label can say `120 – 130` while the token is `[120 TO 129]` — the next bucket starts
at 130, so the upper bound is exclusive of that start. Skip BPM `<= 0` (missing) rather
than stuffing it into `lt80`.

### Year — decades, then years

Count decades (`2010s`, `2020s`) from `year / 10 * 10`. When the current query leaves
only **one** decade in scope, switch the panel to individual years in that decade
(`2018`, `2019`). The query tokens stay ranges (`year:[2010 TO 2019]`) or exact years
(`year:2022`) — the same syntax Part 3 already built.

## Optional: scope to a subset of ids

Search in Part 3 scoped **after** Lucene, by intersecting hit ids with a caller-provided
corpus (one playlist). Facet counts need the restriction **inside** the query, or the
panel would show library-wide numbers next to a playlist-sized table.

AND a `TermInSetQuery` on the stored `id` field:

```java
if (scopeIds != null) {
    if (scopeIds.isEmpty()) {
        return new MatchNoDocsQuery("empty facet scope");
    }
    List<BytesRef> ids = scopeIds.stream().map(BytesRef::new).toList();
    return new BooleanQuery.Builder()
            .add(searchQuery, BooleanClause.Occur.MUST)
            .add(new TermInSetQuery(TrackIndexFields.ID, ids), BooleanClause.Occur.MUST)
            .build();
}
```

Pass `scopeIds = null` for the whole library. The index does not store playlist
membership — the handler still owns that list, same as Part 3.

## Wire counts into the UI

The handler asks for buckets, the template prints `value (count)`:

```java
List<FacetBucket> genres = facetService
        .facets(q, Set.of("genre"), Set.of("genre"))
        .buckets("genre");
// → Club (12), House (4), Techno (7)
```

Hide zero-count **dynamic** values (a genre that never appears). Keep zero-count **fixed**
buckets (BPM ranges, star ratings) so the layout does not jump. Clicking a checkbox
toggles a token in `q` (`genre:Club`, `rating:5`, `bpm:[120 TO 129]`) and the next
request both filters the table and refreshes every panel.

Missing-value rows are ordinary tokens: `genre:""`, `bpm:0`, `year:0`. Count them with
the same self-excluding rule — “No genre” stays visible while a genre is selected.

## What this model does not do

This is still one JVM, one `ByteBuffersDirectory` (or one `FSDirectory`), rebuilt at
startup and upserted after writes:

* Counts visit every matching document. Fine at ~4k tracks; not an aggregation engine.
* There is no replica, no REST API, no cluster. Restart without a rebuild and the cache
  is empty.
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

---
title: 'Search your beans with Lucene — Elasticsearch'
description: "Same Track beans, same Bob → Club → facets journey — this time declared on Elasticsearch instead of wired by hand in Lucene."
author: David Pilato
avatar: /about/david_pilato.avif
tags:
  - java
  - lucene
  - elasticsearch
  - maven
  - search
categories:
  - tutorial
series:
  - Lucene Bean Search
date: '2026-09-24T07:00:00+02:00'
nolastmod: true
cover: cover.avif
draft: true
---

We mapped beans, owned a writer, typed `Bob`, filtered Club, counted facets,
suggested prefixes, and painted hits. That was **Lucene** next to the JVM.

Same `Track` beans. Same acceptance targets. What changes when the inverted
index lives behind a cluster URL instead of an `IndexWriter`?

<!--more-->

## Add Elasticsearch to Maven

Lucene grew one artefact at a time (`lucene-core`, then `analysis-common`, then
`suggest`, `facet`, `highlighter`). Elasticsearch is **one** Java client
coordinate. Look up the current stable release when you implement; this series
uses **9.5.4**:

```xml
<dependency>
  <groupId>co.elastic.clients</groupId>
  <artifactId>elasticsearch-java</artifactId>
  <version>9.5.4</version>
</dependency>
```

No `Directory`. No `IndexWriter`. No hand-built `Analyzer` graph in Java.

## Talk to a cluster

Point the client at a URL and authenticate — API key in production:

```java
ElasticsearchClient client = ElasticsearchClient.of(b -> b
        .host(System.getenv("ES_URL"))          // e.g. https://es.example.com:9200
        .apiKey(System.getenv("ES_API_KEY")));  // the API Key
```

Then wrap it behind the same `TrackSearch` contract as Lucene:

```java
TrackSearch search = new TrackSearchElasticsearchImpl(client);
```

The interesting path is a **session**: prepare once, execute once, read hits and 
facets from the same round-trip:

```java
TrackSearchSession session = search.prepareRequest(
        "Bob", filters, mustNots, 25);
session.execute();      // one POST /tracks/_search
session.totalHits();    // 62 even when size is 25
session.getHits();
session.getFacets();
```

## Declare the mapping once

In Lucene you built a `Document` field by field: `TextField` for search,
`StringField` for the original label, another `StringField` for the
case-folded filter, plus a facet field that keeps the original casing.
On Elasticsearch you declare that shape **once** as an index template —
analyzer, normalizer, properties — then recreate the index:

```java
client.indices().putIndexTemplate(t -> t
        // The index template name
        .name("tracks")
        // The index patterns this template applies
        .indexPatterns("tracks*")
        .template(te -> te
                .settings(s -> s.analysis(a -> a
                        // The custom "track" analyzer
                        .analyzer("track", an -> an.custom(c -> c
                                .tokenizer("standard")
                                .filter("lowercase", "asciifolding")))
                        // The custom "keyword_ci" normalizer
                        .normalizer("keyword_ci", n -> n.custom(c -> c
                                .filter("lowercase", "asciifolding")))))
                .mappings(m -> m
                        .properties("title", textWithRaw())
                        .properties("artist", textWithRaw())
                        .properties("genre", textWithRaw())
                        // album, label, comment…
                        .properties("key", p -> p.keyword(k -> k
                                .normalizer("keyword_ci")
                                .fields("raw", f -> f.keyword(kw -> kw))))
                        .properties("bpm", p -> p.double_(d -> d))
                        .properties("rating", p -> p.integer(i -> i))
                        .properties("year", p -> p.integer(i -> i)))));

if (client.indices().exists(e -> e.index("tracks")).value()) {
    // This is only if you need to start from scratch at every run.
    client.indices().delete(d -> d.index("tracks"));
}
// This can be omitted actually as the first sent document 
// will create the index automatically.
client.indices().create(c -> c.index("tracks"));
```

`textWithRaw()` is the Mapping post in one helper — **three** roles:

```java
private static Property textWithRaw() {
    return Property.of(p -> p.text(t -> t
            .analyzer("track")
            .fields("raw", f -> f.keyword(k -> k))
            .fields("normalized", f -> f.keyword(k -> k.normalizer("keyword_ci")))));
}
```

| Role             | Lucene (you wrote)                      | Elasticsearch (you declare)             |
|------------------|-----------------------------------------|-----------------------------------------|
| Free-text search | `TextField("genre", …)`                 | `genre` text, analyzer `track`          |
| Facet / UI label | `SortedSetDocValuesFacetField("genre")` | `genre.raw` keyword (**no** normalizer) |
| Filter / chip    | `StringField("genre.raw.normalized")`   | `genre.normalized` + `keyword_ci`       |

Same Lucene split as the Facets post: **display** and **filter** are two
fields. A `terms` aggregation returns the **indexed** term — so facet labels
need the original casing on `.raw` (`Club`). Filters go through `.normalized`
with `keyword_ci`, so `Club`, `club`, and `CLUB` hit the same docs.

`key` follows the same idea for Camelot codes: filter on the normalized
parent (`4a`), show `10A` from `key.raw` on the wheel. Recreate the index
after a mapping change — a normalizer lives in the mapping, not in the query.

Note that this Java code could actually be replaced by a pure JSON curl request:

```bash
curl -X PUT "http://localhost:9200/_index_template/tracks" \
  -H "Content-Type: application/json" \
  -d '<JSON MAPPING HERE>'
```

And the following JSON shows the complete mapping for the `tracks` index (`<JSON MAPPING HERE>`).

```json
{
  "index_patterns": [ "tracks*" ],
  "template": {
    "settings": {
      "analysis": {
        "analyzer": {
          "track": {
            "type": "custom",
            "tokenizer": "standard",
            "filter": [ "lowercase", "asciifolding" ]
          }
        },
        "normalizer": {
          "keyword_ci": {
            "type": "custom",
            "filter": [ "lowercase", "asciifolding" ]
          }
        }
      }
    },
    "mappings": {
      "properties": {
        "title": {
          "type": "text",
          "analyzer": "track",
          "fields": {
            "raw": {
              "type": "keyword"
            },
            "normalized": {
              "type": "keyword",
              "normalizer": "keyword_ci"
            }
          }
        },
        "artist": {
          "type": "text",
          "analyzer": "track",
          "fields": {
            "raw": {
              "type": "keyword"
            },
            "normalized": {
              "type": "keyword",
              "normalizer": "keyword_ci"
            }
          }
        },
        "genre": {
          "type": "text",
          "analyzer": "track",
          "fields": {
            "raw": {
              "type": "keyword"
            },
            "normalized": {
              "type": "keyword",
              "normalizer": "keyword_ci"
            }
          }
        },
        "key": {
          "type": "keyword",
          "normalizer": "keyword_ci",
          "fields": {
            "raw": {
              "type": "keyword"
            }
          }
        },
        "bpm": {
          "type": "double"
        },
        "rating": {
          "type": "integer"
        },
        "year": {
          "type": "integer"
        }
      }
    }
  }
}
```

Let say you have an Elasticsearch admin team (like a DBA), you could hand them
the JSON and let them manage the index template. Which means that those "Java"
calls are useless.

## Bulk the beans as-is

No `TrackDocumentMapper.toDocument`. The bean **is** the document:

```java
try (BulkIngester<Void> ingester = BulkIngester.of(b -> b
        .client(client)
        .maxOperations(500)
        .globalSettings(s -> s.index("tracks")))) {
    for (Track track : tracks) {
        ingester.add(op -> op.index(idx -> idx.id(track.id()).document(track)));
    }
}
client.indices().refresh(r -> r.index("tracks"));
```

We flush the bulk every 500 operations and rely on the `try-with-resources` block to
automatically flush any remaining operations and close the ingester. `refresh` makes
the bulk visible to search — the same moment Lucene needed a `commit` before a new
`DirectoryReader`.

Small tip: using `.globalSettings(s -> s.index("tracks"))` saves you from repeating the
index name for every operation within the bulk ingester. It saves your network bandwidth.

## Type “Bob”

In Lucene you assembled a `BooleanQuery`: per-field `BoostQuery` + trailing
`PrefixQuery` on the last token. Elasticsearch expresses that shape as one
`multi_match` of type `bool_prefix`, with `operator: and`:

```java
Query bob = Query.of(qb -> qb.bool(b -> b
        .must(m -> m.multiMatch(mm -> mm
                .query("Bob")
                .type(TextQueryType.BoolPrefix)
                .operator(Operator.And)
                .fields("title^4", "artist^3", "genre^2",
                        "album^1.5", "label^1", "comment^0.5")))));

SearchResponse<Track> response = client.search(s -> s
                .index("tracks")
                .query(bob),
        Track.class);
```

Same boost ladder as before. Same rules: several tokens are AND-ed; only the
last one is a prefix. Hits deserialize straight back to `Track` — no stored-id
join step for the demo.

| Query         | Lucene behaviour                 | Elasticsearch                  |
|---------------|----------------------------------|--------------------------------|
| `Bob`         | 62 hits                          | 62 hits                        |
| `bob sincla`  | `bob` + `sincla…` prefix         | `bool_prefix` + `and`          |
| `bo sinclar`  | empty (`bo` alone is too weak)   | empty                          |
| `ouse`        | does not find `House`            | same — not an infix            |

## Add a filter (include Club)

Wrap the free-text clause as `must` and add a `filter` on the
**normalized** twin — constrain, do not score:

```java
Query bool = Query.of(qb -> qb.bool(b -> b
        .must(m -> m.multiMatch(mm -> mm
                .query("Bob")
                .type(TextQueryType.BoolPrefix)
                .operator(Operator.And)
                .fields("title^4", "artist^3", "genre^2",
                        "album^1.5", "label^1", "comment^0.5")))
        .filter(f -> f.term(t -> t
                .field("genre.normalized")
                .value("club")))));
```

`Club` and `club` hit the same docs because `keyword_ci` lowercases (and
folds) at index time on `.normalized`. Do not wildcard it. Do not filter
on `.raw` unless you want a case-sensitive exact label.

When you also want **facet** histograms that keep sibling genres visible,
that genre chip will move to `post_filter` instead of `query` — next
section.

## Exclude two keys (4A and 4B)

Same `must` + `filter`, plus `must_not`. Several keys on one dimension are
**OR** (`should`, `minimum_should_match = 1`). Excludes always stay in the
query (they shrink every panel):

```java
Query bool = Query.of(qb -> qb.bool(b -> b
        .must(m -> m.multiMatch(mm -> mm
                .query("Bob")
                .type(TextQueryType.BoolPrefix)
                .operator(Operator.And)
                .fields("title^4", "artist^3", "genre^2",
                        "album^1.5", "label^1", "comment^0.5")))
        .filter(f -> f.term(t -> t.field("genre.normalized").value("club")))
        .mustNot(mn -> mn.bool(k -> k
                .should(s -> s.term(t -> t.field("key").value("4a")))
                .should(s -> s.term(t -> t.field("key").value("4b")))
                .minimumShouldMatch("1")))));
```

| UI                   | Result  | Elasticsearch clause               |
|----------------------|---------|------------------------------------|
| Type “Bob”           | 62 hits | `must` `multi_match` `bool_prefix` |
| Include Club         | 26 hits | `filter` / `post_filter` on genre  |
| Exclude 4A **or** 4B | 23 hits | `must_not` (`4a` `should` `4b`)    |

## Facets: one `_search`, Lucene’s DrillSideways in Query DSL

Lucene needed `FacetsCollector`, range readers, and a `DrillSideways`
subclass so **genre** and **key** stay visible while BPM / rating / year
shrink under a selected chip.

Elasticsearch keeps the hit table and the histograms in **one**
`_search`:

* **query** — free text, non-sideways includes (bpm, rating, year), and
  **all** excludes;
* **post_filter** — genre and key *includes* only (narrows **hits**, not
  the aggregations’ base set);
* **filter aggregations** — recreate sideways maps: genre filtered by key
  (not by genre), key filtered by genre (not by key), bpm/rating/year
  filtered by both.

Genre buckets read **`genre.raw`**. Key buckets read **`key.raw`**. Chips
that narrow hits use the normalized fields:

```java
client.search(s -> {
            s.index("tracks")
                    .size(25)
                    .query(query)   // Bob + excludes; no genre/key includes
                    .aggregations("genre", a -> a
                            .filter(keyChip)      // omit genre
                            .aggregations("genre", m -> m.terms(t -> t
                                    .field("genre.raw").size(50))))
                    .aggregations("key", a -> a
                            .filter(genreChip)    // omit key
                            .aggregations("key", m -> m.terms(t -> t
                                    .field("key.raw").size(50))))
                    .aggregations("drill", a -> a
                            .filter(genreAndKey)
                            .aggregations("bpm", /* ranges */)
                            .aggregations("rating", /* terms */)
                            .aggregations("year", /* decade histogram */));
            s.postFilter(genreAndKey);   // hits only
            return s;
        },
        Track.class);
```

Under `q=Bob`: **Club** 26 (not `club`), BPM 120–130 = **52**, rating 5 =
**13**, decades as expected — same numbers **and** the same labels as
Lucene. Click Club: BPM shrinks; Dance stays on the genre panel. Click a
Camelot slice: the key wheel keeps its siblings for the same reason.

| Role                       | Lucene                                     | Elasticsearch                      |
|----------------------------|--------------------------------------------|------------------------------------|
| Checkbox label + count     | `SortedSetDocValuesFacetField` → `$facets` | `terms` on `genre.raw` / `key.raw` |
| Chip (sideways include)    | `DrillDownQuery.add`                       | `post_filter` + filter aggs        |
| Chip (non-sideways / out)  | base `BooleanQuery` FILTER / MUST_NOT      | `query` filter / `must_not`        |
| Numeric histogram          | `*RangeFacetCounts`                        | `range` / `histogram` aggs         |

`size = 0` is aggregations-only (no hit page, no highlight). The session
still reports `totalHits`.

## Suggest: search + highlight, no second Directory

Lucene ran `AnalyzingInfixSuggester` on its **own** `Directory`. Here
autocomplete reuses the track index: `multi_match` `bool_prefix` on title /
artist / genre, request highlights, dedupe into suggestions. An empty
scope still yields nothing. (Unlike Lucene, a non-empty scope is not used
to restrict the ES query — the Demo still pins chips from the suggestion
payload.)

```java
SearchResponse<Track> response = client.search(s -> s
                .index("tracks")
                .size(200)
                .query(q -> q.multiMatch(mm -> mm
                        .query("club")
                        .type(TextQueryType.BoolPrefix)
                        .operator(Operator.And)
                        .fields("title", "artist", "genre")))
                .highlight(h -> h.fields(
                        NamedValue.of("title", HighlightField.of(f -> f.numberOfFragments(0))),
                        NamedValue.of("artist", HighlightField.of(f -> f.numberOfFragments(0))),
                        NamedValue.of("genre", HighlightField.of(f -> f.numberOfFragments(0))))),
        Track.class);
```

Type `club` → a genre hit comes back with markup you can show as
**Club** House. Selecting it still means: put a FILTER chip on `genre`
and run search — same UI contract, without rebuilding a second
dictionary after every mutation.

## By the numbers

Same `TrackSearch` contract, same tests, two implementation classes. Both
sides grew past the first draft (session, full facet maps, highlights on
hits). The contrast is still **what you own**: Lucene inlines analyzer,
`Document`, collectors, `DrillSideways`, and a second suggest
`Directory`; Elasticsearch declares a template and a Query DSL body, then
shapes buckets and highlights.

**Performance** is a different story — and more nuanced than
“cluster = slower.” On the same **4 322** tracks, measured locally:

| Step                         | Lucene (RAM) | Elasticsearch (`localhost:9200`) |
|------------------------------|--------------|----------------------------------|
| Index / rebuild all tracks   | **523 ms**   | **639 ms**                       |
| `MatchAll` search            | ~**5 ms**    | ~**16 ms**                       |
| `q=Bob` search               | ~**15–30 ms**| ~**15–30 ms**                    |

The indexing overhead is **small** — a bit over 100 ms for the full
library, with the network hop and bulk path included. Search is where
Lucene-in-RAM still wins on a `MatchAll` (~5 ms vs ~16 ms): no
serialization, no HTTP. Once the query has real work (`q=Bob`), both land
in the same **15–30 ms** band on this dataset.

So Elasticsearch does **not** buy you a faster micro-benchmark here. What
you **do** gain is operational:

* the index survives process restarts (no rebuild-on-boot unless you
  choose to);
* **replicas** keep serving if a node dies;
* scaling search and indexing capacity is a cluster concern, not another
  `Directory` in your app;
* several app instances share one search tier instead of each holding a
  cache that can drift.

**Relevance is not identical either.** Same acceptance counts (`Bob` → 62,
Club → 26, …) do not mean the same top-N order. Type `joe`: both engines
return the **same 11 titles**, but Lucene ranks *Joe Smooth* /
*Joe Killington* higher, while Elasticsearch prefers
*Miss You (Joe Liggins)* or *Joey Negro*. That is not a filter bug — it
is the query shape.

The Lucene implementation prints `q=joe` as term **plus** prefix on every
field (`SHOULD` clauses add up; the term leaf is **BM25**):

```text
((title:joe)^4.0 (title:joe*)^1.0 (artist:joe)^3.0 (artist:joe*)^0.75
 (genre:joe)^2.0 (genre:joe*)^0.5 (album:joe)^1.5 (album:joe*)^0.375
 (label:joe)^1.0 (label:joe*)^0.25 (comment:joe)^0.5 (comment:joe*)^0.125)~1
```

Elasticsearch `multi_match` `bool_prefix` on a **single** token is not
that query. `_validate/query?rewrite=true` rewrites it to **prefix-only**
— still shown here in Lucene’s query syntax:

```text
(title:joe*)^4.0 (artist:joe*)^3.0 (genre:joe*)^2.0
(album:joe*)^1.5 label:joe* (comment:joe*)^0.5
```

`_explain` then shows a **constant score = field boost**, not BM25 — so
`Joey` / `JOEL` on `title^4` can beat an exact `artist:joe` that Lucene
would have scored with tf/idf.

You could assemble the Lucene-shaped bool on Elasticsearch (`term` on
every token + `prefix` only on the last, same boosts, clauses that sum).
It would never be bit-identical, but the order would get much closer. For
this series we **keep Elasticsearch’s default** `bool_prefix` behaviour —
honest about the ranking delta.

## Try it in the Demo

The playground Demo tab switches the same `TrackSearch` contract between
Lucene-in-RAM and Elasticsearch. Set the cluster URL (default
`http://localhost:9200/`) and API key, then **Save and index**. The LCD
shows `printQuery()` as a copy-paste `curl` (and the JSON response after
execute). After a mapping change, re-index so `.raw` / `.normalized`
actually exist on `tracks`.

Stay in-process with Lucene when the library fits in memory and “embedded
cache next to the JVM” is the product. Reach for Elasticsearch when the
same bean contract should outlive one process — and when replicas, shared
state, and “URL + API key” matter more than keeping the inverted index
inside your heap.

Same beans. Same Bob → Club → facets journey. Less plumbing between you
and the inverted index — not a bit-identical score.

The full demo lives on GitHub: [lucene-search-tracks](https://github.com/dadoonet/lucene-search-tracks).

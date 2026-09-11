---
title: 'Integrating Apache Lucene for Bean Search — Part 3: Search'
description: "Type Bob, add a FILTER chip, then two MUST_NOT keys — the BooleanQuery Lucene actually runs, then resolve hits back to beans."
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
* [Part 5: Facets]({{< ref "2026-09-15-lucene-bean-search-facets" >}})

[Part 1]({{< ref "2026-09-09-lucene-bean-search-indexing" >}}) mapped beans to documents.
[Part 2]({{< ref "2026-09-10-lucene-bean-search-lifecycle" >}}) owned the writer.
This part is the query you actually run: type in the box, add a filter, exclude
two keys — and watch the `BooleanQuery` grow.

The screenshots are from the same Rekordbox-style library as Parts 1 and 2.
The Java is the Lucene tree behind those three URLs. Same recipe for any bean
index.

<!--more-->

Keep free text and filters **apart**. Do not stuff facets into the search box
(`genre:Club bob`). That string is painful to chip, autocomplete, and bookmark
once a panel appears:

```
/tracks?q=Bob
/tracks?q=Bob&genre=Club
/tracks?q=Bob&genre=Club&minus-key=4A,4B
```

`q` is analyzed free text. Everything else is a structured filter. Polarity is a
**separate param** (`minus-key=`), not a dash on the value — otherwise you cannot
include an artist named `-M-`.

This is the same boolean tree Elasticsearch users know as `bool` / `must` /
`filter` / `must_not`. Lucene’s Java API *is* that tree — no Query DSL, no parser
required. Lucene’s `Query.toString()` prints `+` for `MUST`, `#` for `FILTER`
(no score), `-` for `MUST_NOT`, `(a b)~1` for `SHOULD` with `minShouldMatch = 1`,
and `^4.0` for a boost.

## Type “Bob”

{{< figure src="search.avif" caption="`q=Bob` — 62 tracks. Title, artist, or another analyzed field matches the token *bob*, or starts with it." >}}

The analyzer from Part 1 (standard tokenizer + lowercase + ASCII folding) turns
`Bob` into the token `bob`. Free text is an analyzed **match** across those
fields — `TermQuery`, not a leading/trailing wildcard — with title beating
artist. The last typed token also gets a trailing `PrefixQuery` at a quarter of
the field boost, so typing still works:

```java
BooleanQuery.Builder fields = new BooleanQuery.Builder();
addField(fields, "title", "bob", 4.0f, true);
addField(fields, "artist", "bob", 3.0f, true);
addField(fields, "genre", "bob", 2.0f, true);
addField(fields, "album", "bob", 1.5f, true);
addField(fields, "label", "bob", 1.0f, true);
addField(fields, "comment", "bob", 0.5f, true);
fields.setMinimumNumberShouldMatch(1);
Query lucene = fields.build();
```

```java
private static void addField(
        BooleanQuery.Builder fields, String field, String token, float boost, boolean prefix) {
    fields.add(new BoostQuery(new TermQuery(new Term(field, token)), boost),
            BooleanClause.Occur.SHOULD);
    if (prefix) {
        fields.add(new BoostQuery(new PrefixQuery(new Term(field, token)), boost * 0.25f),
                BooleanClause.Occur.SHOULD);
    }
}
```

That is the whole query — no outer `BooleanQuery` yet. Lucene prints it as:

```
((title:bob)^4.0 (title:bob*)^1.0 (artist:bob)^3.0 (artist:bob*)^0.75
 (genre:bob)^2.0 (genre:bob*)^0.5 (album:bob)^1.5 (album:bob*)^0.375
 (label:bob)^1.0 (label:bob*)^0.25 (comment:bob)^0.5 (comment:bob*)^0.125)~1
```

`Crazy (Bob Sinclar vs. Dimitri Vegas & Like Mike remix)` matches on **title**
(`bob` is its own token — `StandardTokenizer` splits on punctuation).
`Bob Sinclar` as artist matches on **artist**. `Bobo au coeur` is still a hit:
`bob*` prefixes `bobo`. Ranking follows the boosts, so a title hit sorts above a
comment hit.

Several tokens are AND-ed. Only the **last** one is a prefix; earlier words stay
exact. `bob sincla` requires a `bob` token and a `sincla…` prefix (`sincla*`
finds `Sinclar`). `bo sinclar` misses. This is not an infix: `ouse` does not
find `House`. One character is enough (`bob sinclar c` finds `Cerrone`). That is
why Part 1 did not index edge n-grams — grams 2–5 would miss `sincla` and still
need this query-time prefix for the rest.

Run it, then join stored ids back to beans (playlist scoping stays **outside**
Lucene — the handler picks the corpus, search drops ids that are not in it):

```java
IndexSearcher searcher = index.searcher();
try (IndexReader reader = searcher.getIndexReader()) {
    // The full list of Track beans is already in RAM (the corpus).
    // Build a Map so we can look a bean up by id after search.
    Map<String, Track> byId = new HashMap<>();
    for (Track track : corpus) {
        byId.put(track.id(), track);
    }

    // We will create our resultset here
    List<Track> ordered = new ArrayList<>();

    // lucene is the Query we built above (free text, then FILTER / MUST_NOT)
    TopDocs hits = searcher.search(lucene, Math.max(1, reader.numDocs()));
    for (var hit : hits.scoreDocs) {
        // Get the id from the Lucene result
        String id = reader.storedFields().document(hit.doc).get(TrackIndexFields.ID);

        // Looking up the track from the Map knowing its id and add it to the resultset
        Track track = byId.get(id);
        if (track != null) {
            ordered.add(track);
        }
    }
    return List.copyOf(ordered);
}
```

Lucene document ids are not `Track.id`. Store the bean id (`Field.Store.YES` in
Part 1) and read it back. Walk `hits.scoreDocs` in order while free text scores;
pure filters can keep corpus order.

## Add a filter (include Club)

{{< figure src="search-filter-on.avif" caption="Same `q=Bob`, plus a green **genre: Club** chip. 62 tracks become 27." >}}

The chip writes `genre=Club` next to `q`. It does **not** rewrite the box to
`genre:Club Bob`. Wrap the previous free-text query as `MUST` and add a
`FILTER` — constrain, do not score:

```java
BooleanQuery.Builder query = new BooleanQuery.Builder();
query.add(freeText, BooleanClause.Occur.MUST);   // the query from the previous section
query.add(new TermQuery(new Term("genre.raw.normalized", "club")),
        BooleanClause.Occur.FILTER);
Query lucene = query.build();
```

```
+(((title:bob)^4.0 (title:bob*)^1.0 (artist:bob)^3.0 … )~1) #genre.raw.normalized:club
```

`FILTER` is the important one. A `MUST` on `genre:club` would still constrain,
but it would also join the scoring. The chip should shrink the set **without**
changing whether title beats artist.

The leaf is an exact `TermQuery` — the same as typing `genre:Club` in a
power-user string. A checkbox is not a different query type. Index a
normalized keyword twin (`genre.raw.normalized`) next to Part 1’s `genre.raw`
`StringField`, so `Club` and `club` hit the same docs. Do not wildcard it:
`club` must not match a genre named `Club House`.

*Ultra Naté — Free (Bob Sinclar Remix)* stays: title has the token `bob`, genre
is Club. *TRIANGLE DES BERMUDES* (Reggaeton) drops. *Give Me Love* (Dance) drops.

## Exclude two keys (4A and 4B)

{{< figure src="search-filter-on-off.avif" caption="Club stays on (green). **4A** and **4B** are off. 27 tracks become 24." >}}

Exclusions are `minus-key=4A,4B`, not a dash on the chip value. Same `MUST` +
`FILTER`, plus one `MUST_NOT`. Several keys on the same dimension are **OR**
(`SHOULD`, `minShouldMatch = 1`): “not (4A or 4B)”.

```java
BooleanQuery.Builder query = new BooleanQuery.Builder();
query.add(freeText, BooleanClause.Occur.MUST);
query.add(new TermQuery(new Term("genre.raw.normalized", "club")),
        BooleanClause.Occur.FILTER);

BooleanQuery.Builder keys = new BooleanQuery.Builder();
keys.add(new TermQuery(new Term("key.code", "4a")), BooleanClause.Occur.SHOULD);
keys.add(new TermQuery(new Term("key.code", "4b")), BooleanClause.Occur.SHOULD);
keys.setMinimumNumberShouldMatch(1);
query.add(keys.build(), BooleanClause.Occur.MUST_NOT);

Query lucene = query.build();
```

```
+(((title:bob)^4.0 (title:bob*)^1.0 … )~1) #genre.raw.normalized:club -((key.code:4a key.code:4b)~1)
```

Keys use a `TermQuery` on the extracted Camelot code (`key.code`), not a
wildcard. `4A` must not match `12A`. Index that code as a `StringField` next to
the display name.

*Crazy (Bob Sinclar vs. …)* was 4A Club — gone. *Free (Bob Sinclar Remix)* was
4B Club — gone. *I Feel For You* (2A Club) stays. The free-text ranking is
untouched: `FILTER` and `MUST_NOT` do not score.

In production, one builder turns the structured request into that tree so tests
can index known beans and assert hit ids:

```java
Query lucene = TrackLuceneQueryBuilder.buildStructured(
        "Bob",
        Map.of("genre", List.of("Club")),
        Map.of("key", List.of("4A", "4B")));
```

The web layer parses the URL first (`QueryFacets.fromRequest(q, params)`),
then calls that builder. The three screenshots are:

| UI                         | Bookmarkable request                 | Lucene clause                          |
|----------------------------|--------------------------------------|----------------------------------------|
| Type “Bob”                 | `q=Bob`                              | `MUST` match + last-token prefix       |
| Include Club               | `genre=Club`                         | `FILTER` exact `club`                  |
| Exclude 4A **or** 4B       | `minus-key=4A,4B`                    | `MUST_NOT` (`4a` `SHOULD` `4b`)        |

| Occur                           | Role                                   | Scores? |
|---------------------------------|----------------------------------------|---------|
| `MUST`                          | analyzed match + last-token prefix     | yes     |
| `FILTER`                        | field constraint (genre, bpm, key, …)  | no      |
| `MUST_NOT`                      | exclusion                              | no      |
| `SHOULD` + `minShouldMatch = 1` | multi-select OR *inside* one clause    | no      |

A `BooleanQuery` with only `MUST_NOT` matches nothing — add a `MUST`
`MatchAllDocsQuery` if the user excludes without typing or including. Blank
everything is `MatchAllDocsQuery`.

## Next

You can score free text, constrain with `FILTER`, exclude with `MUST_NOT`, and
resolve hits. [Part 4]({{< ref "2026-09-14-lucene-bean-search-suggest" >}}) adds
autocomplete with `lucene-suggest` — prefix lookup whose hits become `FILTER`
chips, not leftover tokens in `q`. [Part 5]({{< ref "2026-09-15-lucene-bean-search-facets" >}})
counts facet buckets under the same boolean query.

## Series

* [Part 1: Indexing]({{< ref "2026-09-09-lucene-bean-search-indexing" >}}) — Maven, fields, analyzer, document mapper
* [Part 2: Index Lifecycle]({{< ref "2026-09-10-lucene-bean-search-lifecycle" >}}) — writer, rebuild, upsert, keep warm
* [Part 3: Search]({{< ref "2026-09-11-lucene-bean-search-query-sync" >}}) — you are here
* [Part 4: Suggest]({{< ref "2026-09-14-lucene-bean-search-suggest" >}}) — autocomplete
* [Part 5: Facets]({{< ref "2026-09-15-lucene-bean-search-facets" >}}) — counts and drill-down

---
title: 'Integrating Apache Lucene for Bean Search — Part 4: Suggest'
description: "Type a few letters and pick the artist, the title, or the genre before you hit Enter. Autocomplete is the index helping you write the query."
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
date: '2026-09-14T07:00:00+02:00'
nolastmod: true
cover: cover.avif
draft: false
---

In [Part 1]({{< ref "2026-09-09-lucene-bean-search-indexing" >}}) we added
`lucene-suggest` to Maven and never used it. Time has come.

The [previous post]({{< ref "2026-09-11-lucene-bean-search-query-sync" >}}) showed
how to run a search query on whatever field you mapped. Anyone used to a search
engine already knows the next step: autocomplete, so the index can help you find
the right query.

Skip this post if you only need search and filters — Parts 1–3 do not depend on it.

<!--more-->

## A second Directory

`AnalyzingInfixSuggester` is not an `IndexSearcher` on the track index. It is a
**dictionary** with its own `Directory`. Use the **same** analyzer as Part 1
so prefixes match how titles were tokenized:

```java
// Dedicated Directory — do not share it with the track IndexWriter
Directory suggestionDirectory = new ByteBuffersDirectory();
AnalyzingInfixSuggester suggester =
        new AnalyzingInfixSuggester(suggestionDirectory, TrackAnalyzers.searchAnalyzer());
```

Keep it next to `TrackSearchIndex`, behind the same write lock as rebuild / upsert.
The writer is thread-safe; the suggester rebuild is not something you want racing
a lookup.

## Rebuild after writes

Incremental delete on an infix suggester is awkward. For a few thousand beans,
rebuild the dictionary after every mutation — the same budget as the ~400 ms
track-index rebuild in Part 2. Feed **title**, **artist**, and **genre**. Deduplicate.
`payload()` is the field name so the UI can iconify the row:

```java
suggester.build(new TrackSuggestionIterator(tracks));
```

`text` (the `BytesRef` from `next()`) is what you later put in the URL. Do **not**
store the highlighted string — that is display-only.

## Type “club”

{{< figure src="suggest-genre.avif" caption="Typing `club` — Lucene highlights the infix. A tag is genre, a note is title. Live search still runs underneath." >}}

The last flag is `highlight`. `allTermsRequired` stays `false`:

```java
List<Lookup.LookupResult> matches =
        suggester.lookup("club", Set.of(), 10, false, true);
// last two flags: allTermsRequired, highlight

for (Lookup.LookupResult match : matches) {
    // payload is the field we indexed: title / artist / genre
    String field = match.payload.utf8ToString();
    // chip value — no markup
    String text = match.key.toString();
    // e.g. <b>Club</b> House — display only
    String highlight = match.highlightKey.toString();
}
```

A tag row is `field = "genre"` (`Club House`). A note row is `field = "title"`
(`In Da Club`). Live search on `q=club` is the Part 3 query — a **second** call.
Keep typeahead and search apart: the prefix is not a filter param.

## Type “Madonna”

{{< figure src="suggest-artist.avif" caption="Typing `Madonna` — artist rows (user icon) sit next to title hits. The matched letters are the `highlight` payload, not the chip value." >}}

Same Java, different prefix:

```java
List<Lookup.LookupResult> matches =
        suggester.lookup("Madonna", Set.of(), 10, false, true);
```

User-icon rows are `field = "artist"` (`Madonna`, `Madonna vs Chaka Khan`).
Note rows are titles that contain the infix (`Let the Music (Reprise Madonna)`).
Map each hit once:

```java
public record TrackSuggestion(String text, String field, String highlight) {}

TrackSuggestion hit = new TrackSuggestion(text, field, highlight);
```

## Apply a hit as a FILTER chip

Selecting *Club House* (`field = "genre"`) writes the same structured param as
Part 3, and **clears** `q`:

```text
/tracks?genre=Club House
```

Selecting *Madonna* (`field = "artist"`):

```text
/tracks?artist=Madonna
```

That is a Part 3 `FILTER` — not a `MUST` free-text clause. If you stuffed the
suggestion into `q` instead, the typed prefix would AND with the chip
(`q=club` plus `genre=Club House`) and hide rows that no longer contain `club`
in other fields.

## Scope to the current FILTER set

The dictionary does not run Part 3’s `BooleanQuery`. A Club playlist would still
offer artists that only appear on Techno tracks. Post-filter lookup against the
**current result set** — the same `FILTER` / `MUST_NOT` maps, **without** the
typed prefix:

```java
// prefix is only the lookup string — do not AND it into the corpus
List<Track> scoped = search.filter(corpus, "", filters, mustNots);
List<TrackSuggestion> hits = index.suggest(prefix, scoped);
```

Inside `suggest`, keep values that appear on those tracks (title, artist, or
genre). When the scope is a small subset of the dictionary, ask the suggester
for **more than 10** hits, then cap after filtering — otherwise the first ten
library-wide matches can starve the in-scope ones.

An empty scope yields no suggestions. `scope == null` searches the whole
dictionary.

## Close

Close the suggester and its `Directory` in the same `close()` as Part 2,
typically **before** the track `IndexWriter`. A process restart rebuilds both
from the source of truth anyway.

## Next

Autocomplete sits beside search, not instead of it. Part 5 will count
facet buckets under the same boolean query so a filter panel can show
`Club (26)` instead of a blind checkbox list.

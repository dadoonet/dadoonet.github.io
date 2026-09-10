---
title: 'Integrating Apache Lucene for Bean Search — Part 4: Suggest'
description: "Add autocomplete with lucene-suggest — prefix lookup, Lucene highlight, and FILTER chips scoped to the current result set."
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

This post is part of a series:

* [Part 1: Indexing]({{< ref "2026-09-09-lucene-bean-search-indexing" >}})
* [Part 2: Index Lifecycle]({{< ref "2026-09-10-lucene-bean-search-lifecycle" >}})
* [Part 3: Search]({{< ref "2026-09-11-lucene-bean-search-query-sync" >}})
* [Part 4: Suggest]({{< ref "2026-09-14-lucene-bean-search-suggest" >}})
* Part 5: Facets <!-- TODO: link when published -->

[Part 3]({{< ref "2026-09-11-lucene-bean-search-query-sync" >}}) scored free text
(`MUST`) and constrained with `FILTER`. The search box still feels incomplete
until typing `sin` offers *Sinclar* before the user hits Enter.

<!--more-->

You already declared `lucene-suggest` in [Part 1]({{< ref "2026-09-09-lucene-bean-search-indexing" >}}).
Skip this post entirely if you only need search and filters — the index in Parts 1–3
does not depend on it.

## A second Directory

`AnalyzingInfixSuggester` is not an `IndexSearcher` on the track index. It is a
**dictionary** with its own `Directory` (in-memory is fine for a local library).
Use the **same** analyzer as `TextField` so prefixes match how titles were tokenized.

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
rebuild the dictionary from the current map after every mutation — the same
budget as the ~400 ms track-index rebuild in Part 2.

```java
// InputIterator: text to suggest + payload (field name: title / artist / genre)
suggester.build(new TrackSuggestionIterator(tracks));
```

Feed title, artist, and genre (whatever you show in the dropdown). Deduplicate
if the same string appears on several tracks. `payload()` returns the field so
the UI can iconify the row; the chip later uses the **unhighlighted** text.

## Lookup

Ask Lucene to wrap the matched prefix. The last flag is `highlight`:

```java
public record TrackSuggestion(String text, String field, String highlight) {}

List<Lookup.LookupResult> matches =
        suggester.lookup(prefix, Set.of(), 10, false, true);
// last two flags: allTermsRequired, highlight

for (Lookup.LookupResult match : matches) {
    String field = match.payload.utf8ToString();       // title / artist / genre
    String text = match.key.toString();                // chip value — no markup
    String highlight = match.highlightKey.toString();  // e.g. <b>Sin</b>clar
    // …
}
```

`text` is what you put in the URL. `highlight` is display-only (`<b>` around the
infix). Do not write the highlighted string into `artist=` — you would persist
HTML in a bookmark.

The lookup string is a **prefix** on the search box, not a filter param
(`genre=`, `bpm=`). Keep “typeahead” and “run search” as two calls.

## Scope to the current FILTER set

The dictionary does not run Part 3’s `BooleanQuery`. A Club playlist (or
`genre=club`) would still offer artists that only appear on Techno tracks.
Post-filter the lookup against the **current result set** — playlist corpus plus
the same `FILTER` / `MUST_NOT` maps, **without** the typed prefix:

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
dictionary (tests, unfiltered library).

## Apply a hit as a FILTER chip

Selecting *Sinclar* (field `artist`) writes the same structured param as a cell
filter in Part 3, and **clears** `q`:

```
/tracks?artist=Sinclar
```

That is a `FILTER` `TermQuery` (or contains query) on `artist` — not a `MUST`
free-text clause. If you stuffed the suggestion into `q` instead, the typed
prefix would AND with the chip (`q=sin` plus `artist=Sinclar`) and hide rows
that no longer contain `sin` in other fields.

On the web side, debounce the input, `GET` a small JSON endpoint
(`text`, `field`, `highlight`), and render the highlight. Arrow keys move,
Enter or click applies the chip, Escape closes the list. Live search on the
typed remainder can still run if no suggestion is chosen.

## Close

Close the suggester and its `Directory` in the same `close()` as Part 2,
typically **before** the track `IndexWriter`. A process restart rebuilds both
from the source of truth anyway.

## Next

Autocomplete sits beside search, not instead of it. Part 5 will count facet
buckets under the same boolean query so a filter panel can show `Club (12)`
instead of a blind checkbox list.

## Series

* [Part 1: Indexing]({{< ref "2026-09-09-lucene-bean-search-indexing" >}}) — Maven, fields, analyzer, document mapper
* [Part 2: Index Lifecycle]({{< ref "2026-09-10-lucene-bean-search-lifecycle" >}}) — writer, rebuild, upsert, keep warm
* [Part 3: Search]({{< ref "2026-09-11-lucene-bean-search-query-sync" >}}) — MUST / FILTER / MUST_NOT, hits → beans
* [Part 4: Suggest]({{< ref "2026-09-14-lucene-bean-search-suggest" >}}) — you are here
* Part 5: Facets <!-- TODO: link when published --> — counts and drill-down

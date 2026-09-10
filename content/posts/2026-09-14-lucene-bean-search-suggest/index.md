---
title: 'Integrating Apache Lucene for Bean Search — Part 4: Suggest'
description: "Add autocomplete on top of the in-process Lucene index with lucene-suggest — prefix lookup, a second Directory, rebuild after writes."
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
* [Part 5: Facets]({{< ref "2026-09-15-lucene-bean-search-facets" >}})

[Part 3]({{< ref "2026-09-11-lucene-bean-search-query-sync" >}}) turned a `q` string into
a list of beans. The search box still feels incomplete until typing `sin` offers
*Sinclar* before the user hits Enter.

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
// InputIterator: text to suggest + optional payload (field name, id, …)
suggester.build(new TrackSuggestionIterator(tracks));
```

Feed title, artist, and genre (whatever you show in the dropdown). Deduplicate
if the same string appears on several tracks.

## Lookup

```java
// prefix → up to 10 suggestions; last two flags: allTermsRequired, highlight
List<Lookup.LookupResult> matches =
        suggester.lookup(prefix, Set.of(), 10, false, false);
```

Payloads can carry metadata — for example which field matched (`title` / `artist` /
`genre`) so the UI can group or iconify rows. The lookup string is a prefix, not
the full `q` grammar from Part 3: keep “typeahead” and “run search” as two calls.

On the web side, debounce the input and hit a small endpoint that returns those
rows. Selecting a suggestion either fills the box or navigates straight to
`filter(corpus, suggestedText)`.

## Close

Close the suggester when you close the index (Part 2), after the `IndexWriter`.
A process restart rebuilds both from the source of truth anyway.

## Next

Autocomplete sits beside search, not instead of it. [Part 5]({{< ref "2026-09-15-lucene-bean-search-facets" >}})
will count facet buckets under the same `q` so a filter panel can show `Club (12)` instead of a
blind checkbox list.

## Series

* [Part 1: Indexing]({{< ref "2026-09-09-lucene-bean-search-indexing" >}}) — Maven, fields, analyzer, document mapper
* [Part 2: Index Lifecycle]({{< ref "2026-09-10-lucene-bean-search-lifecycle" >}}) — writer, rebuild, upsert, keep warm
* [Part 3: Search]({{< ref "2026-09-11-lucene-bean-search-query-sync" >}}) — queries, hits → beans
* [Part 4: Suggest]({{< ref "2026-09-14-lucene-bean-search-suggest" >}}) — you are here
* [Part 5: Facets]({{< ref "2026-09-15-lucene-bean-search-facets" >}}) — counts and drill-down

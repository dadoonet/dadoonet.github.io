---
title: 'Search your beans with Lucene — Suggest'
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
date: '2026-09-15T07:00:00+02:00'
nolastmod: true
cover: cover.avif
draft: false
aliases:
  - /posts/2026-09-12-lucene-bean-search-suggest/
  - /posts/2026-09-14-lucene-bean-search-suggest/
---

We have seen so far how to run a search query on whatever field you mapped.
Anyone used to a search engine already knows the next step: autocomplete,
so the index can help you find the right query.

<!--more-->

Autocomplete lives in its own artefact:

```xml
<dependency>
  <groupId>org.apache.lucene</groupId>
  <artifactId>lucene-suggest</artifactId>
  <version>10.5.1</version>
</dependency>
```

## A second Directory

`AnalyzingInfixSuggester` is not an `IndexSearcher` on the track index. It is a
**dictionary** with its own `Directory`. Use the **same** analyzer as before so
prefixes match how titles were tokenized:

```java
Directory suggestionDirectory = new ByteBuffersDirectory();
AnalyzingInfixSuggester suggester = new AnalyzingInfixSuggester(
        suggestionDirectory, analyzer);
suggester.build(new TrackSuggestionInputIterator(tracks.values()));
```

Keep it next to the track writer, behind the same write lock as rebuild /
upsert. Incremental delete on an infix suggester is awkward; for a few thousand
beans, rebuild the dictionary after every mutation.

## Type “club”

{{< figure src="suggest-club.avif" caption="Prefix `club`. Hover a row to see `lookup()` → `highlightKey`, field, FILTER chip." >}}

```java
List<Lookup.LookupResult> matches =
        suggester.lookup("club", Set.of(), 10, true, true);
Lookup.LookupResult match = matches.get(0);
String text = match.key.toString();              
// "Club House"
String field = match.payload.utf8ToString();     
// "genre"
String highlight = match.highlightKey.toString(); 
// "<b>Club</b> House"
```

This means that the first suggestion is `Club House` coming from the `genre` field and could be presented to the user as:

> **Club** House.

## Filter with the suggestion

Selecting `Club House` (`field = "genre"`) could then call your backend search
API: `/tracks?genre=Club House` and update the UI to reflect the selected filter
chip.

If you want suggestions to respect the current filter set, change the call:

```java
List<Track> scoped = search.filter(corpus, "", filters, mustNots);
List<TrackSuggestion> hits = index.suggest(prefix, scoped);
```

`filter(..., "", filters, mustNots)` applies the chips already on, with an empty
query string. `suggest(prefix, scoped)` then looks up only inside that subset —
so `club` cannot propose a genre that those chips already excluded.

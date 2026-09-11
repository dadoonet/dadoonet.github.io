---
title: 'Integrating Apache Lucene for Bean Search — Part 1: Mapping'
description: "You have the tracks. What you lack is search. Add Lucene in-process and map your Java beans to documents the engine can actually find."
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
date: '2026-09-09T07:00:00+02:00'
nolastmod: true
cover: cover.avif
draft: false
---

This tutorial embeds **Apache Lucene** as an in-process search index over domain
beans — here, `Track` records from a Rekordbox-style library. The same pattern
applies to any Java bean: map it to a Lucene `Document`, index it, search, then
join hits back to your objects.

## What you get

```
Your beans (source of truth)
        │
        ▼
Document mapper  ──►  Lucene Document(s)
        │
        ▼
IndexWriter (in-memory Directory)
        │
        ▼
IndexSearcher + Query  ──►  hit IDs  ──►  filter / order your bean list
                              ↘ Facets → (value, count)
```

<!--more-->

Lucene is a **derived cache**, never the source of truth. Keep your database as
the system of record, and rebuild or upsert Lucene documents after successful writes.

## Add Lucene to Maven

One project, four artefacts, **same** version. Look up the latest stable Lucene
release on Maven Central when you implement; this series uses **10.5.1**.

```xml
<dependency>
  <groupId>org.apache.lucene</groupId>
  <artifactId>lucene-core</artifactId>
  <version>10.5.1</version>
</dependency>
<dependency>
  <groupId>org.apache.lucene</groupId>
  <artifactId>lucene-analysis-common</artifactId>
  <version>10.5.1</version>
</dependency>
<dependency>
  <groupId>org.apache.lucene</groupId>
  <artifactId>lucene-facet</artifactId>
  <version>10.5.1</version>
</dependency>
<dependency>
  <groupId>org.apache.lucene</groupId>
  <artifactId>lucene-suggest</artifactId>
  <version>10.5.1</version>
</dependency>
```

| Artefact                 | Role                                           |
|--------------------------|------------------------------------------------|
| `lucene-core`            | Index, search, documents, queries              |
| `lucene-analysis-common` | Tokenizers / filters                           |
| `lucene-facet`           | Counts / drill-down (Part 5)                   |
| `lucene-suggest`         | Autocomplete (Part 4) — omit if you skip that  |

Lucene is pure Java: it shades into a fat-jar with no native libraries.

## Start from your existing bean

{{< figure src="track.avif" caption="A `Track` in the UI: title, artist, genre, BPM, key, rating, year — plus album, comment, and the rest of the bean." >}}

```java
public record Track(
        String id,
        String title,
        Artist artist,
        Genre genre,
        MusicalKey key,
        double bpm,
        int ratingStars,
        int year
        // … album, comment, paths, …
) {}
```

Index what you need to **find** documents; keep the full bean elsewhere and join
by id after search.

1. **Stable id** — `Track.id`, used to upsert and delete.
2. **Full-text** — strings users type (title, artist).
3. **Filters / facets** — exact keywords or numerics (genre, rating, bpm, year).

## Name your Lucene fields

One constants class so mapper and queries stay in sync:

```java
public final class TrackIndexFields {
    public static final String ID = "id";
    public static final String TITLE = "title";
    public static final String ARTIST = "artist";
    public static final String GENRE = "genre";
    public static final String GENRE_RAW = "genre.raw";
    public static final String BPM = "bpm";
    public static final String RATING = "rating";

    private TrackIndexFields() {}
}
```

| Pattern       | Example           | Lucene type                         |
|---------------|-------------------|-------------------------------------|
| Analyzed text | `title`, `artist` | `TextField`                         |
| Exact keyword | `id`, `genre.raw` | `StringField`                       |
| Numeric       | `bpm`, `rating`   | `DoubleField` / `IntField`          |

`TextField` is tokenized (search). `StringField` is not (ids, filters, later facets).
Store the id (`Field.Store.YES`) so hits can return it; everything else can be
`Store.NO` if you always reload the bean from your primary store.

## Choose an analyzer

The analyzer runs at **index time** for `TextField` and should match query-time
tokens. Standard tokenization + lowercase + ASCII folding works well for music
metadata: no stemming (artist names stay intact), no stop words (`Around The
World` stays searchable), and `nate` finds `Naté`. NFC can still happen in the
mapper for stored values.

```java
public final class TrackAnalyzers {

    /** Same analyzer for indexing TextFields and for query-time analysis. */
    public static Analyzer searchAnalyzer() {
        return new Analyzer() {
            @Override
            protected TokenStreamComponents createComponents(String fieldName) {
                Tokenizer source = new StandardTokenizer();
                TokenStream filter = new LowerCaseFilter(source);
                filter = new ASCIIFoldingFilter(filter);
                return new TokenStreamComponents(source, filter);
            }
        };
    }
}
```

Use that **same** analyzer on the way in and on the way out. Do **not** add
edge-ngram twin fields (`title.ngram`, …) for type-as-you-go prefixes. Grams
2–5 leave a dead zone (`sincl` hits, `sincla` misses, `sinclar` hits again),
need a per-field index analyzer, and double every text field. Prefix matching
is a **query-time** `PrefixQuery` on the last typed token — [Part 3]({{< ref "2026-09-11-lucene-bean-search-query-sync" >}})
builds it. On a local in-memory index a trailing prefix is cheap, and there is
no gap.

## Map the bean to a Lucene `Document`

One static method. This is the heart of the integration:

```java
public final class TrackDocumentMapper {

    public static Document toDocument(Track t) {
        Document doc = new Document();

        // Identity — not analyzed; stored so search hits can return it
        doc.add(new StringField(TrackIndexFields.ID, t.id(), Field.Store.YES));

        // Full-text — tokenized by TrackAnalyzers
        doc.add(new TextField(TrackIndexFields.TITLE, nfc(t.title()), Field.Store.YES));
        doc.add(new TextField(TrackIndexFields.ARTIST, name(t.artist()), Field.Store.YES));

        // Exact keyword + numerics for filters / ranges (genre:Club, bpm:[120 TO 130])
        doc.add(new StringField(TrackIndexFields.GENRE_RAW, name(t.genre()), Field.Store.YES));
        doc.add(new DoubleField(TrackIndexFields.BPM, t.bpm(), Field.Store.YES));
        doc.add(new IntField(TrackIndexFields.RATING, t.ratingStars(), Field.Store.YES));

        return doc;
    }
}
```

Part 5 will add a facet field next to `genre.raw`. You do not need it to search.

## Next

You have the artefacts, field names, an analyzer, and a bean → `Document` mapper.
[Part 2]({{< ref "2026-09-10-lucene-bean-search-lifecycle" >}}) will wrap Lucene’s 
`IndexWriter` and `Directory`: rebuild, upsert, delete, and open a searcher.

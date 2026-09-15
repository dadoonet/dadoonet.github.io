---
title: 'Search your beans with Lucene — Mapping'
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
applies to any Java bean.

Lucene sits **next to** your objects as a **derived cache**, never as the source
of truth. Keep the database as the system of record: map a bean to a `Document`,
search, join **hit ids** back to the original list, and rebuild or upsert Lucene
after successful writes. This post is only the mapping.

<!--more-->

## Add Lucene to Maven

One project, two artefacts, **same** version. Look up the latest stable Lucene
release on Maven Central when you implement; this series uses **10.5.1**.
Later parts add one artefact each when you need autocomplete or facet counts.

```xml
<!-- Index, search, documents, queries -->
<dependency>
  <groupId>org.apache.lucene</groupId>
  <artifactId>lucene-core</artifactId>
  <version>10.5.1</version>
</dependency>
<!-- Tokenizers / filters -->
<dependency>
  <groupId>org.apache.lucene</groupId>
  <artifactId>lucene-analysis-common</artifactId>
  <version>10.5.1</version>
</dependency>
```

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

* **Stable id** — `Track.id`, used to upsert and delete.
* **Full-text** — strings users type (title, artist).
* **Filters / facets** — exact keywords or numerics (genre, rating, bpm, year).

## Choose an analyzer

The analyzer runs at **index time** for `TextField` and should match query-time
tokens. Standard tokenization + lowercase + ASCII folding works well for music
metadata: no stemming (artist names stay intact), no stop words
(`Around The World` stays searchable), and `nate` finds `Naté`. NFC can still
happen in the mapper for stored values.

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

Let's map our fields to the Lucene fields:

| Pattern       | Example                   | Lucene type                         |
|---------------|---------------------------|-------------------------------------|
| Analyzed text | `title`, `artist`         | `TextField`                         |
| Exact keyword | `id`, `genre.raw`         | `StringField`                       |
| Numeric       | `bpm`, `rating`, `year`   | `DoubleField` / `IntField`          |

`TextField` is tokenized (search). `StringField` is not (ids, filters, later facets).
This mapper stores every field (`Field.Store.YES`) so a hit can return id, title,
or genre without a join. Keep the id stored; switch the rest to `Store.NO` if you
always reload the bean from your primary store.

One static method. This is the heart of the integration:

```java
public final class TrackDocumentMapper {
    public static final String ID = "id";
    public static final String TITLE = "title";
    public static final String ARTIST = "artist";
    public static final String GENRE = "genre";
    public static final String GENRE_RAW = "genre.raw";
    public static final String BPM = "bpm";
    public static final String RATING = "rating";
    public static final String YEAR = "year";

    public static Document toDocument(Track t) {
        Document doc = new Document();

        // Identity — not analyzed; stored so search hits can return it
        doc.add(new StringField(ID, t.id(), Field.Store.YES));

        // Full-text — tokenized by TrackAnalyzers
        doc.add(new TextField(TITLE, t.title(), Field.Store.YES));
        doc.add(new TextField(ARTIST, t.artist().name(), Field.Store.YES));

        // Exact keyword + numerics for filters / ranges (genre:Club, bpm:[120 TO 130])
        doc.add(new StringField(GENRE_RAW, t.genre().name(), Field.Store.YES));
        doc.add(new DoubleField(BPM, t.bpm(), Field.Store.YES));
        doc.add(new IntField(RATING, t.ratingStars(), Field.Store.YES));
        doc.add(new IntField(YEAR, t.year(), Field.Store.YES));

        return doc;
    }
}
```

## Next

You have the artefacts, field names, an analyzer, and a bean → `Document` mapper.
The next page will wrap Lucene’s `IndexWriter` and `Directory`: rebuild, upsert,
delete, and open a searcher.

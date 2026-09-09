---
title: 'Integrating Apache Lucene for Bean Search — Part 1: Indexing'
description: "Embed Apache Lucene as an in-process index over Java beans — Maven deps, field design, analyzer, and Document mapping, using Track records from a Rekordbox-style library."
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
date: '2026-09-09T10:00:00+02:00'
nolastmod: true
cover: cover.avif
draft: false
---

This post is part of a series of 4:

* [Part 1: Indexing]({{< ref "2026-09-09-lucene-bean-search-indexing" >}})
* Part 2: Index Lifecycle <!-- TODO: link when published -->
* Part 3: Search <!-- TODO: link when published -->
* Part 4: Facets <!-- TODO: link when published -->

This tutorial explains how to embed **Apache Lucene** as an in-process search index
over domain beans — specifically `Track` records loaded from a Rekordbox-style library.
The same pattern applies to **any Java bean** (a product, a customer, a document, …):
map the bean to a Lucene `Document`, index it, then search and map hits back to your objects.

Audience: Java / Maven developers who want a concrete, copyable recipe rather than an
abstract Lucene overview.

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
```

<!--more-->

Lucene is a **derived cache**, never the source of truth. Keep your database (or whatever
authoritative store you use) as the system of record, and rebuild or upsert Lucene
documents after successful writes.

## Add Lucene to Maven

Pin versions in the **parent** `dependencyManagement`, then declare artefacts
(without versions) in the module that owns the index.

### Parent POM (`dependencyManagement`)

```xml
<!-- Apache Lucene (embedded search index) -->
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
  <artifactId>lucene-suggest</artifactId>
  <version>10.5.1</version>
</dependency>
```

| Artefact                 | Role                                                                      |
|--------------------------|---------------------------------------------------------------------------|
| `lucene-core`            | Index, search, documents, queries                                         |
| `lucene-analysis-common` | Tokenizers / filters (`WhitespaceTokenizer`, `LowerCaseFilter`, …)        |
| `lucene-suggest`         | Autocomplete (`AnalyzingInfixSuggester`) — optional if you only need search |

Look up the **latest stable** Lucene release on Maven Central at implementation time; keep
all three artefacts on the **same** version.

### Module POM (consumer)

In the module that builds the index:

```xml
<dependency>
  <groupId>org.apache.lucene</groupId>
  <artifactId>lucene-core</artifactId>
</dependency>
<dependency>
  <groupId>org.apache.lucene</groupId>
  <artifactId>lucene-analysis-common</artifactId>
</dependency>
<dependency>
  <groupId>org.apache.lucene</groupId>
  <artifactId>lucene-suggest</artifactId>
</dependency>
```

No version here if the parent manages it. Lucene is pure Java — it shades cleanly into a
fat-jar with no native libraries.

## Start from your existing bean

You already have a domain type. Here is an immutable record for a music track:

```java
public record Track(
        String id,
        String uuid,
        String title,
        Path filePath,
        Path artworkPath,
        Artist artist,
        Genre genre,
        MusicalKey key,
        double bpm,
        int ratingStars,
        Duration length,
        // …
        String comment,
        LocalDate dateAdded,
        Album album,
        int year,
        Label label
) {}
```

For **your** bean, decide:

1. **Stable document id** — a string that uniquely identifies the bean (`Track.id`).
   You will upsert and delete by this id.
2. **Full-text fields** — strings users type into a search box (title, artist, …).
3. **Filter / facet fields** — exact keywords or numerics (genre, rating, bpm, year).
4. **What stays out of the index** — heavy or rarely queried data (file paths you do
   not search, binary blobs, nested graphs you will resolve after the hit).

Rule of thumb: index what you need to **find** documents; keep the full bean elsewhere
and join by id after search.

## Name your Lucene fields

Centralize field names in one constants class so mapper and queries stay in sync:

```java
public final class TrackIndexFields {
    public static final String ID = "id";
    public static final String TITLE = "title";
    public static final String ARTIST = "artist";
    public static final String GENRE = "genre";
    public static final String BPM = "bpm";
    public static final String RATING = "rating";
    // … plus "raw" / "present" helpers as needed

    private TrackIndexFields() {} // constants only
}
```

Common conventions you can reuse for any bean:

| Pattern        | Example                   | Purpose                                                    |
|----------------|---------------------------|------------------------------------------------------------|
| Analyzed text  | `title`, `artist`         | Free-text / contains search (`TextField`)                  |
| Exact keyword  | `id`, `genre.raw`         | Term queries, facets (`StringField`)                       |
| Numeric        | `bpm`, `rating`, `year`   | Ranges (`DoubleField` / `IntField` / `LongField`)          |
| Presence flag  | `artist.present = "true"` | “missing artist” style filters without storing empty strings |

## Choose an analyzer

The analyzer runs at **index time** (for `TextField`) and should match how you normalize
query tokens at **search time**.

A small custom analyzer works well for music metadata: whitespace tokens + lowercase.
Accent / NFC normalization can happen in the document mapper so indexed values stay
consistent with older Java-side filters:

```java
public final class TrackAnalyzers {

    /** Same analyzer for indexing TextFields and for query-time analysis. */
    public static Analyzer searchAnalyzer() {
        return new Analyzer() {
            @Override
            protected TokenStreamComponents createComponents(String fieldName) {
                // Split on whitespace only — titles like "Mr. Brightside" stay one token each
                Tokenizer source = new WhitespaceTokenizer();
                // Case-insensitive matching without stemming (good for artist / title names)
                TokenStream filter = new LowerCaseFilter(source);
                return new TokenStreamComponents(source, filter);
            }
        };
    }
}
```

For another domain you might prefer `StandardAnalyzer`, language-specific analyzers, or
`KeywordAnalyzer` for codes. Whatever you pick, use the **same** analyzer (or an
explicitly paired query-time strategy) for indexing and searching those fields.

## Map the bean to a Lucene `Document`

This is the heart of the integration. One static method turns a bean into fields:

```java
public final class TrackDocumentMapper {

    /** One Lucene Document per Track — only fields you need to find or filter. */
    public static Document toDocument(Track t) {
        Document doc = new Document();

        // Identity — not analyzed; Store.YES so hits can return the id
        doc.add(new StringField(TrackIndexFields.ID, t.id(), Field.Store.YES));

        // Full-text — tokenized by TrackAnalyzers (nfc/name normalize before indexing)
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

### Field type cheat sheet

| Lucene type                           | When to use                                                                      |
|---------------------------------------|----------------------------------------------------------------------------------|
| `StringField`                         | Exact match, ids, facets — **not** tokenized                                     |
| `TextField`                           | Full-text search — tokenized by the analyzer                                     |
| `IntField` / `LongField` / `DoubleField` | Numbers + range queries (also store if you need the value on the hit)         |

`Field.Store.YES` keeps the value available on search hits (e.g. to read `id`).
`Field.Store.NO` is fine when you only need the field for matching and will load the
full bean from your primary store.

You can also index helper fields (`*.present`, normalized raw keywords). That is optional
sugar for “empty / missing” queries — start with id + text + a few filters, then grow.

## Next

You now have Maven deps, field names, an analyzer, and a bean → `Document` mapper.
<!-- TODO: link Part 2 when published -->
Part 2 will wrap Lucene’s `IndexWriter` and `Directory`: rebuild, upsert, delete, and
open a searcher.

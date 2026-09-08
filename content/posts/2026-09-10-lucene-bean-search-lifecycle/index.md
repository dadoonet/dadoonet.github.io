---
title: 'Integrating Apache Lucene for Bean Search — Part 2: Index Lifecycle'
description: "Own Lucene’s IndexWriter for your beans: in-memory Directory, rebuild, upsert, delete by id, and keep the index warm after writes."
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
date: '2026-09-10T10:00:00+02:00'
nolastmod: true
cover: cover.avif
draft: false
---

This post is part of a series of 3:

* [Part 1: Indexing]({{< ref "2026-09-09-lucene-bean-search-indexing" >}})
* [Part 2: Index Lifecycle]({{< ref "2026-09-10-lucene-bean-search-lifecycle" >}})
* Part 3: Search <!-- TODO: link when published -->

In [Part 1]({{< ref "2026-09-09-lucene-bean-search-indexing" >}}) we added Lucene to Maven,
named fields, chose an analyzer, and mapped a `Track` bean to a Lucene `Document`.
That is only half the story: you still need a small class that **owns** the index.

## Own the index lifecycle

Wrap Lucene’s low-level types in a class dedicated to **your** bean.
`TrackSearchIndex` is the template: create the directory and writer, rebuild or mutate,
open a searcher, and close everything when the process shuts down.

<!--more-->

### Create (in-memory)

```java
public final class TrackSearchIndex implements AutoCloseable {

    private final Directory directory;
    private final IndexWriter writer;
    // One lock for mutations (+ suggest rebuild if you add one later)
    private final Object writeLock = new Object();

    public TrackSearchIndex() throws IOException {
        // Whole index in heap — swap for FSDirectory.open(path) to persist on disk
        directory = new ByteBuffersDirectory();
        // Analyzer must match the one used when building TextField queries
        IndexWriterConfig config = new IndexWriterConfig(TrackAnalyzers.searchAnalyzer());
        writer = new IndexWriter(directory, config);
    }
}
```

`ByteBuffersDirectory` keeps the whole index in heap — ideal for a local library that
fits in memory and is rebuilt at process start. Swap in `FSDirectory.open(path)` if you
need persistence across restarts.

### Rebuild (full replace)

```java
public void rebuild(List<Track> tracks) throws IOException {
    synchronized (writeLock) {
        writer.deleteAll(); // wipe previous docs — full replace, not incremental
        for (Track track : tracks) {
            writer.addDocument(TrackDocumentMapper.toDocument(track));
        }
        writer.commit(); // make changes visible to new DirectoryReaders
    }
}
```

### Real numbers (~4k tracks)

On a local music library of **4 322** tracks (in-memory `ByteBuffersDirectory` + suggest
dictionary), a full rebuild looks like this:

| Metric                    | Value       |
|---------------------------|-------------|
| Documents                 | 4 322       |
| Wall time                 | **369 ms**  |
| Heap delta (rough JVM)    | ~**15 MB**  |
| `ramBytesUsed` (total)    | ~**1.7 MB** |
| `ramBytesUsed` (index)    | ~1.1 MB     |
| `ramBytesUsed` (suggest)  | ~0.6 MB     |

So for a few thousand beans, a full rebuild is cheap enough to run at startup — and even
as a fallback when incremental sync fails. The Lucene footprint is about **1.7 MB**; the
~15 MB heap delta is a rough JVM measurement (allocations during the rebuild), not the
steady-state index size.

Worth instrumenting `rebuild` / `upsert` in your own `TrackSearchIndex` if you want
numbers for *your* corpus before choosing RAM vs disk.

### Upsert / delete by id

```java
public void upsert(Track track) throws IOException {
    synchronized (writeLock) {
        // Deletes any existing doc with this id, then adds the new one
        writer.updateDocument(
                new Term(TrackIndexFields.ID, track.id()),
                TrackDocumentMapper.toDocument(track));
        writer.commit();
    }
}

public void deleteById(String trackId) throws IOException {
    synchronized (writeLock) {
        // Term must match how id was indexed (StringField → exact term)
        writer.deleteDocuments(new Term(TrackIndexFields.ID, trackId));
        writer.commit();
    }
}
```

`updateDocument(Term, Document)` deletes any existing docs matching the term, then adds
the new one — the usual “upsert by primary key” pattern.

### Open a searcher

```java
public IndexSearcher searcher() throws IOException {
    // Opens a near-real-time reader on the writer — caller must close the reader
    return new IndexSearcher(DirectoryReader.open(writer));
}
```

Callers must close the `IndexReader` obtained from `searcher.getIndexReader()`
(typically in a try-with-resources around the search call).

### Close

```java
@Override
public void close() throws IOException {
    synchronized (writeLock) {
        writer.close();    // flushes and releases the IndexWriter
        directory.close(); // then the Directory (order matters)
    }
}
```

Serialize mutations with a lock if the index is shared across request threads.
Lucene’s `IndexWriter` is thread-safe for many operations, but if you also keep a
side structure (for example a suggest dictionary rebuilt after writes), one lock keeps
both consistent.

## Keep the index warm and consistent

### At startup

Rebuild once from the source of truth:

```java
TrackSearchIndex index = new TrackSearchIndex();
index.rebuild(library.tracks()); // full replace from the authoritative store
SearchService search = new SearchService(index);
```

Swap the live reference and close the previous index when you rebuild on a running server.

### After writes

Prefer **upsert / delete by id** for single-row edits; **full rebuild** for bulk
operations or when sync fails:

```java
// after a successful DB commit
trackIndexSync.upsert(changedIds);   // load bean → index.upsert
// or
trackIndexSync.rebuild();            // index.rebuild(library.tracks())
```

Never treat Lucene as authoritative. If an upsert fails mid-batch, fall back to a
full rebuild so the cache cannot drift silently.

## Next

The index stays in sync with your store.
<!-- TODO: link Part 3 when published -->
Part 3 will build queries, resolve hits back to beans, and optionally add autocomplete.

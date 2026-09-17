---
title: 'Search your beans with Lucene — Index'
description: "The beans are mapped. Now own the index: rebuild at startup, upsert when a track changes, and never let Lucene drift from the source of truth."
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
date: '2026-09-10T07:00:00+02:00'
nolastmod: true
cover: cover.avif
draft: false
---

In [the previous post]({{< ref "2026-09-09-lucene-bean-search-indexing" >}}) we
added Lucene to Maven, chose an analyzer, and mapped a `Track` bean to a
**search-ready** Lucene `Document`. That is only half the story: you still need
a small class that **owns** the index — and you should see what “inverted” means
for a token like `bob`.

<!--more-->

## Own the index lifecycle

Wrap Lucene’s low-level types in a class dedicated to **your** bean. Create the
directory and writer, rebuild or mutate, and close everything when the process
shuts down. The playground does the same with an in-memory
`ByteBuffersDirectory` — plain `addDocument(doc)`, no facet rewrite yet:

```java
// We will use an in-memory index
Directory dir = new ByteBuffersDirectory();

// Create the index writer with the analyzer
IndexWriter writer = new IndexWriter(dir, new IndexWriterConfig(analyzer));

// Create Lucene doc for track #255465792: Ultra Naté - Free (Bob Sinclar Remix)
Document doc255465792 = mapper.toDocument(Tracks.trackFrom(255465792));
writer.addDocument(doc255465792);

// Index track #172523747: Daft Punk - Around The World
Document doc172523747 = mapper.toDocument(Tracks.trackFrom(172523747));
writer.addDocument(doc172523747);

// Index track #106352474: Claude François - Cette année-là
Document doc106352474 = mapper.toDocument(Tracks.trackFrom(106352474));
writer.addDocument(doc106352474);

// Commit all the documents that have been indexed so far
writer.commit();
```

For a full library, wipe and reload under one write lock:

```java
public void rebuild(List<Track> tracks) throws IOException {
    synchronized (writeLock) {
        writer.deleteAll();
        for (Track track : tracks) {
            writer.addDocument(TrackDocumentMapper.toDocument(track));
        }
        writer.commit();
    }
}
```

`ByteBuffersDirectory` keeps the whole index in heap — ideal for a local library
rebuilt at process start. Swap in `FSDirectory.open(path)` if you need
persistence across restarts.

### Upsert / delete by id

```java
public void upsert(Track track) throws IOException {
    synchronized (writeLock) {
        writer.updateDocument(
                new Term(TrackDocumentMapper.ID, track.id()),
                TrackDocumentMapper.toDocument(track));
        writer.commit();
    }
}

public void deleteById(String trackId) throws IOException {
    synchronized (writeLock) {
        writer.deleteDocuments(new Term(TrackDocumentMapper.ID, trackId));
        writer.commit();
    }
}
```

### Close

```java
writer.close();
directory.close(); // order matters — writer first
```

Serialize mutations with a lock if the index is shared across request threads.

### Keep the index warm and consistent

Rebuild once from the source of truth at startup. Prefer **upsert / delete by
id** for single-row edits; **full rebuild** for bulk operations or when sync
fails. Never treat Lucene as authoritative.

### Real numbers (~4k tracks)

On a local music library of **4 322** tracks (in-memory `ByteBuffersDirectory`),
a full rebuild looks like this:

| Metric      | Value       |
|-------------|-------------|
| Documents   | 4 322       |
| Wall time   | **~400 ms** |
| Memory used | ~**1.1 MB** |

So for a few thousand beans, a full rebuild is cheap enough to run at startup —
and even as a fallback when incremental sync fails. (A suggest dictionary, if
you add one later, sits in its own `Directory` and adds a little more RAM.)

## The inverted index

{{< figure src="index-bob.avif" caption="Term `bob` on field `title`: posting list of docs that contain that token." >}}

After commit, Lucene does **not** keep a bag of words on each document. It keeps
an **inverted** map: term → documents (the posting list). Type `bob` on `title`
and you read every track whose title tokenized to `bob` — including
*Free (Bob Sinclar Remix)*.

Same idea on `artist`. Six tracks, four distinct names after analysis:

| Docs | Artist (stored) |
|------|-----------------|
| 1, 3 | Bob Sinclar     |
| 2    | Bob Marley      |
| 4, 5 | Claude François |
| 6    | François Valery |

Lucene does not store that table. It stores the **sorted** inverted map —
lowercased, ASCII-folded (`François` → `francois`):

```text
artist:bob       →  1, 2, 3
artist:claude    →  4, 5
artist:francois  →  4, 5, 6
artist:marley    →  2
artist:sinclar   →  1, 3
artist:valery    →  6
```

That posting list is what you use when searching. We will talk about this in
the next article.

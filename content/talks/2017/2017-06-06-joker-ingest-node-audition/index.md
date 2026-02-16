---
title: 'Ingest node: (re)index and enrich documents in Elasticsearch'
conference: 
  name: 'Joker<?>'
  url: "https://www.jokerconf.com/"
  country: "Online"
  country_code: "online" # online, fr, us, etc.
authors:
  - author: David Pilato
    avatar: /about/david_pilato.avif
date: '2017-06-06'
talk-lang: en # fr or en
nolastmod: true
draft: false
#cover: "cover.avif"

talk: Ingest Node

# Speaker specific fields
youtube: "8TD_c25a4Zk"
links:
  - title: "Repository used for the demo"
    url: "https://github.com/dadoonet/bano-elastic/"

  - title: "Blog post part 1"
    url: "https://www.elastic.co/blog/enriching-your-postal-addresses-with-the-elastic-stack-part-1"
  - title: "Blog post part 2"
    url: "https://www.elastic.co/blog/enriching-your-postal-addresses-with-the-elastic-stack-part-2"
  - title: "Blog post part 3"
    url: "https://www.elastic.co/blog/enriching-your-postal-addresses-with-the-elastic-stack-part-3"

attendees: 5
---

When you ingest data into Elasticsearch, you may need to perform fairly simple transformation operations. Until now, these operations had to be done outside of Elasticsearch, before the actual indexing.

Welcome Ingest node! A new type of node that allows you to do just that.

This talk explains the concept of Ingest Node, how to integrate it with the rest of the Elastic software suite, and how to develop your own Ingest plugin in practice by showing how I developed the ingest-bano plugin to enrich French postal addresses and/or geographic coordinates (for now).

This talk will also cover the reindex API which can also benefit from the ingest pipeline to modify your data on the fly during reindexing.

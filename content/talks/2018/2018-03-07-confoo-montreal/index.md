---
title: "Ingest node: enriching documents within Elasticsearch"
conference: 
  name: "ConFoo Montreal"
  city: "Montreal"
  country: "Canada"
  country_code: "ca"
  latitude: "45.501689"
  longitude: "-73.567256"
author: David Pilato
avatar: /about/david_pilato.png
# talk: conferences
date: 2018-03-07
lang: en
nolastmod: true
draft: false
pdf: "2018/2018-03-07-confoo-montreal.pdf"


# Speaker specific fields
#youtube: ""
attendees: 50
notist: "dadoonet/EpnH6d"
aliases:
  - /EpnH6d
---
Wanna transform your documents on the fly before indexing them into elasticsearch? Node ingest is built for you.

The talk will also cover the reindex api, which can be used in combination with ingest pipelines to modify data while reindexing.

Last but not least, I’ll tell you how to write your own Ingest processor in Java as a plugin! Our own processor will convert postal addresses from/to geo points.

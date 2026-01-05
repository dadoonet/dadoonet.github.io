---
title: "Indexing your office documents with Elastic stack and FSCrawler"
conference: 
  name: "Elastic London Revival"
  city: "London"
  country: "UK"
  country_code: "gb"
  latitude: "51.507351"
  longitude: "-0.127758"
  url: "https://www.meetup.com/London-Elastic-Fantastics/events/285591510/"
author: David Pilato
avatar: /about/david_pilato.png
tags:
  - elasticsearch
  - conference
  - java
  - cloud
categories:
  - speaker
series:
  - conferences
date: 2022-05-17
nolastmod: true
draft: false
pdf: "2022/2022-05-17-elastic-london-revival.pdf"


# Speaker specific fields
#youtube: ""
notist: "dadoonet/k195XM"

x:
  - user: "elastic_london"
    id: "1524018650080022529"
  - user: "elastic_london"
    id: "1526555816295268353"
  - user: "dadoonet"
    id: "1526507302949363718"

links:
  - title: "Demo: FSCrawler"
    url: "https://github.com/dadoonet/demo-fscrawler"
    description: "This repository contains the code for the FSCrawler demo."
  - title: "Documentation: FSCrawler"
    url: "https://fscrawler.readthedocs.io/"
    description: "The official FSCrawler documentation"

aliases:
  - /k195XM
---
You have plenty of Open Office, Microsoft Office, PDF, images… documents and you may want to be able to search for their metadata and content. How can you do that?

In this talk, David will explain how Apache Tika can be used for that and how to combine this fantastic library with Elastic Stack:

*
Elasticsearch [ingest-attachment plugin](https://www.elastic.co/guide/en/elasticsearch/plugins/current/ingest-attachment.html)

*
[FSCrawler](https://github.com/dadoonet/fscrawler)

*
[Workplace Search](https://www.elastic.co/workplace-search) connector for FSCrawler to have a ready to use and powerful user interface for your documents.

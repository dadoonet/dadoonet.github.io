---
title: "Indexer ses documents bureautique avec la suite Elastic et FSCrawler"
conference: 
  name: "Capitole du Libre"
  city: "Toulouse"
  country: "France"
  country_code: "fr"
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
date: 2022-11-19
nolastmod: true
draft: false
cover: cover.jpg

# Speaker specific fields
#youtube: ""
notist: "dadoonet/hmRw07"

links:
  - title: "Event page"
    url: "https://cfp.capitoledulibre.org/cdl-2022/talk/SAGLQM/"
  - title: "FSCrawler"
    url: "https://fscrawler.readthedocs.io/"

aliases:
  - /hmRw07
---
Vous avez sous la main des tonnes de documents Open Office, Microsoft Office, PDF voire des images… Et vous aimeriez être capable de chercher dans leurs meta-données et dans le contenu lui-même.

Comment faire ? Surtout depuis l’annonce de la fin de Google Search Appliance.

Dans cette session, David expliquera comment Apache Tika peut fournir ce service et comment combiner cette fantastique librairie avec elasticsearch :

* Elasticsearch [ingest-attachment plugin](https://www.elastic.co/guide/en/elasticsearch/plugins/current/ingest-attachment.html)
* [FSCrawler](https://github.com/dadoonet/fscrawler)
* Connecteur [Workplace Search](https://www.elastic.co/workplace-search) pour FSCrawler afin de disposer sur étagère d’une interface utilisateur puissante pour vos documents

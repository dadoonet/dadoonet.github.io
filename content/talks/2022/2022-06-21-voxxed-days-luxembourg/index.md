---
title: "Indexer ses documents bureautique avec la suite Elastic et FSCrawler"
conference: 
  name: "Voxxed Days Luxembourg"
  city: "Luxembourg"
  country: "Luxembourg"
  country_code: "lu"
  latitude: "49.815273"
  longitude: "6.129583"
  url: "https://luxembourg.voxxeddays.com/"
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
date: 2022-06-21
nolastmod: true
draft: false
pdf: "2022/2022-06-21-voxxed-days-luxembourg.pdf"


# Speaker specific fields
youtube: "ozMF8ddY75g"
notist: "dadoonet/MKrtPl"

x:
  - user: "voxxed_lu"
    id: "1538172189047934977"
  - user: "dadoonet"
    id: "1539211376526254081"
  - user: "dadoonet"
    id: "1539210577121255425"

links:
  - title: "Documentation: FSCrawler"
    url: "https://fscrawler.readthedocs.io/"
    description: "This is the official FSCrawler documentation."

aliases:
  - /MKrtPl
---
Vous avez sous la main des tonnes de documents Open Office, Microsoft Office, PDF voire des images… Et vous aimeriez être capable de chercher dans leurs meta-données et dans le contenu lui-même.

Comment faire ? Surtout depuis l’annonce de la fin de Google Search Appliance.

Dans cette session, David expliquera comment Apache Tika peut fournir ce service et comment combiner cette fantastique librairie avec elasticsearch :

* Elasticsearch [ingest-attachment plugin](https://www.elastic.co/guide/en/elasticsearch/plugins/current/ingest-attachment.html)

*
[FSCrawler](https://github.com/dadoonet/fscrawler)

* Connecteur [Workplace Search](https://www.elastic.co/workplace-search) pour FSCrawler afin de disposer sur étagère d’une interface utilisateur puissante pour vos documents

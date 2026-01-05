---
title: "Indexer ses documents bureautique avec la suite Elastic et FSCrawler"
conference: 
  name: "Snowcamp 2023"
  city: "Grenoble"
  country: "France"
  country_code: "fr"
  latitude: "45.188529"
  longitude: "5.724524"
  url: "https://snowcamp.io/fr/"
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
date: 2023-01-25
nolastmod: true
draft: false
pdf: "2023/2023-01-25-snowcamp-2023.pdf"


# Speaker specific fields
#youtube: ""
notist: "dadoonet/UGtHAu"

x:
  - user: "ponceto91"
    id: "1618546896926314496"
  - user: "mupsigraphy"
    id: "1618547196655464450"
  - user: "dadideo"
    id: "1618550368245551107"
  - user: "dadoonet"
    id: "1618529295173050368"
  - user: "dadoonet"
    id: "1614989473837629442"
  - user: "dadoonet"
    id: "1611365091995275266"
  - user: "dadoonet"
    id: "1618564206521110529"

links:
  - title: "Demo: FSCrawler"
    url: "https://github.com/dadoonet/demo-fscrawler"
    description: "This demo shows how you can use FSCrawler to index your documents"
  - title: "Documentation: FSCrawler"
    url: "https://fscrawler.readthedocs.io/"
    description: "This is the official FSCrawler documentation."

aliases:
  - /UGtHAu
---
Vous avez sous la main des tonnes de documents Open Office, Microsoft Office, PDF voire des images… Et vous aimeriez être capable de chercher dans leurs meta-données et dans le contenu lui-même.

Comment faire ? Surtout depuis l’annonce de la fin de Google Search Appliance.

Dans cette session, David expliquera comment Apache Tika peut fournir ce service et comment combiner cette fantastique librairie avec elasticsearch :

* Elasticsearch [ingest-attachment plugin](https://www.elastic.co/guide/en/elasticsearch/plugins/current/ingest-attachment.html)

*
[FSCrawler](https://github.com/dadoonet/fscrawler)

* Connecteur [Workplace Search](https://www.elastic.co/workplace-search) pour FSCrawler afin de disposer sur étagère d’une interface utilisateur puissante pour vos documents

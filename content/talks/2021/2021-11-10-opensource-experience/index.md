---
title: "Indexer ses documents bureautique avec la suite Elastic et FSCrawler"
conference: 
  name: "Opensource Experience"
  city: "Paris"
  country: "France"
  country_code: "fr"
  latitude: "48.856614"
  longitude: "2.352222"
author: David Pilato
avatar: /about/david_pilato.png
talk: FSCrawler
date: 2021-11-10
talk-lang: fr
nolastmod: true
draft: false
pdf: "2021/2021-11-10-opensource-experience.pdf"


# Speaker specific fields
youtube: "J03D9OeXC2Q"
notist: "dadoonet/57G2Nv"

x:
  - user: "dadoonet"
    id: "1452966886472364037"
  - user: "dadoonet"
    id: "1458424405139279879"

links:
  - title: "Documentation: FSCrawler"
    url: "https://fscrawler.readthedocs.io/"
    description: "This is the official FSCrawler documentation."

aliases:
  - /57G2Nv
---
Vous avez sous la main des tonnes de documents Open Office, Microsoft Office, PDF voire des images… Et vous aimeriez être capable de chercher dans leurs meta-données et dans le contenu lui-même.

Comment faire ? Surtout depuis l’annonce de la fin de Google Search Appliance.

Dans cette session, David expliquera comment Apache Tika peut fournir ce service et comment combiner cette fantastique librairie avec elasticsearch :

* Elasticsearch [ingest-attachment plugin](https://www.elastic.co/guide/en/elasticsearch/plugins/current/ingest-attachment.html)
* [FSCrawler](https://github.com/dadoonet/fscrawler)
* Connecteur [Workplace Search](https://www.elastic.co/workplace-search) pour FSCrawler afin de disposer sur étagère d’une interface utilisateur puissante pour vos documents

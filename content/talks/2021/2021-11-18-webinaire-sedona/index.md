---
title: Indexer ses documents bureautique avec la suite Elastic et FSCrawler
conference:
  name: Webinaire Sedona
  url: ''
  country: "Online"
  country_code: "Online"
author: David Pilato
avatar: /about/david_pilato.png
# talk: conferences
date: 2021-11-18
lang: fr
nolastmod: true
draft: false
pdf: "2021/2021-11-18-webinaire-sedona.pdf"

notist: dadoonet/dTVWXj
links:
  - title: "Event page"
    url: "https://app.livestorm.co/sedona-1/decouvrez-comment-ameliorer-la-pertinence-de-vos-resultats-avec-elasticsearch"

  - title: "FSCrawler"
    url: "https://fscrawler.readthedocs.io/"


aliases:
- /dTVWXj
x:
- user: SedonaFR
  id: '1460621101701246977'
- user: SedonaFR
  id: '1460621168088596480'
- user: SedonaFR
  id: '1461653975237808131'
- user: dadoonet
  id: '1466057432719835137'
- user: dadoonet
  id: '1466333417830858754'
---
Vous avez sous la main des tonnes de documents Open Office, Microsoft Office, PDF voire des images… Et vous aimeriez être capable de chercher dans leurs meta-données et dans le contenu lui-même.

Comment faire ? Surtout depuis l’annonce de la fin de Google Search Appliance.

Dans cette session, David expliquera comment Apache Tika peut fournir ce service et comment combiner cette fantastique librairie avec elasticsearch :

* Elasticsearch [ingest-attachment plugin](https://www.elastic.co/guide/en/elasticsearch/plugins/current/ingest-attachment.html)
* [FSCrawler](https://github.com/dadoonet/fscrawler)
* Connecteur [Workplace Search](https://www.elastic.co/workplace-search) pour FSCrawler afin de disposer sur étagère d’une interface utilisateur puissante pour vos documents

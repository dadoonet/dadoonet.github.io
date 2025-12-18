---
title: "Un moteur de recherche de documents d’entreprise"
conference: 
  name: "JDLL"
  city: "Lyon"
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
date: 2023-04-02
nolastmod: true
draft: false
cover: cover.jpg

# Speaker specific fields
#youtube: ""
notist: "dadoonet/D5Qumy"

x:
  - user: "dadoonet"
    id: "1638567651847929861"

links:
  - title: "Conference Page"
    url: "https://jdll.org/programme"
  - title: "Workshop instructions"
    url: "https://github.com/dadoonet/JDLL"
  - title: "Ingest Attachment Processor"
    url: "https://www.elastic.co/guide/en/elasticsearch/reference/current/attachment.html"
  - title: "FSCrawler"
    url: "https://fscrawler.readthedocs.io/"

aliases:
  - /D5Qumy
---
Lors de cet atelier, nous allons expliquer comment mettre en place un moteur de recherche pour les données de notre entreprise.

Afin d’éviter le côté trop “magique” parfois des solutions sur étagère, nous verrons d’abord :

* les bases du moteur de recherche Elasticsearch
* l’indexation de contenu JSON
* l’extraction de texte et de meta-données depuis un document binaire avec le [processor `attachment`](https://www.elastic.co/guide/en/elasticsearch/plugins/current/ingest-attachment.html)
* l’utilisation du projet [FSCrawler](https://github.com/dadoonet/fscrawler) open-source pour réaliser plus simplement ces étapes

Nous verrons ensuite comment chercher dans les données ainsi indexées.

Enfin, nous mettrons en place une interface de recherche sur étagère, portée par la solution gratuite [Workplace Search](https://www.elastic.co/workplace-search) qui nous permettra de chercher dans différentes sources documentaires avec assez peu d’efforts.

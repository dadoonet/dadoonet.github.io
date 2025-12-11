---
title: "Un moteur de recherche de documents d’entreprise"
description: ""
conference: 
  name: "Devoxx France 2023"
  url: ""
  city: "Paris"
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
date: 2023-04-12
nolastmod: true
draft: false
cover: cover.jpg

# Speaker specific fields
#youtube: ""
notist: "dadoonet/dnEdLV"
---

Lors de cet atelier, nous allons expliquer comment mettre en place un moteur de recherche pour les données de notre entreprise.
Afin d’éviter le côté trop “magique” parfois des solutions sur étagère, nous verrons d’abord :

les bases du moteur de recherche Elasticsearch
l’indexation de contenu JSON
la transformation à la volée du contenu JSON via les pipelines ingest
l’extraction de texte et de meta-données depuis un document binaire avec le processor attachment

l’utilisation du tout nouveau processeur d’inférence pour déterminer des entités nommées de nos documents ainsi qu’une analyse de sentiments
l’utilisation du projet FSCrawler open-source pour réaliser plus simplement ces étapes

Nous verrons ensuite comment chercher dans les données ainsi indexées.
Enfin, nous mettrons en place une interface de recherche sur étagère, portée par la solution gratuite Workplace Search qui nous permettra de chercher dans différentes sources documentaires avec assez peu d’efforts.

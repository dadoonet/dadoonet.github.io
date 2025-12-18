---
title: "Un moteur de recherche de documents d’entreprise"
description: ""
conference: 
  name: "JDLL"
  url: ""
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
  - title: "dadoonet/JDLL"
    url: "https://github.com/dadoonet/JDLL"
  - title: "elastic/enterprise-search-network-drives-connector"
    url: "https://github.com/elastic/enterprise-search-network-drives-connector"
  - title: "dadoonet/fscrawler"
    url: "https://github.com/dadoonet/fscrawler"

aliases:
  - /D5Qumy
---
Lors de cet atelier, nous allons expliquer comment mettre en place un moteur de recherche pour les données de notre entreprise.
Afin d’éviter le côté trop “magique” parfois des solutions sur étagère, nous verrons d’abord :

les bases du moteur de recherche Elasticsearch
l’indexation de contenu JSON
l’extraction de texte et de meta-données depuis un document binaire avec le processor attachment

l’utilisation du projet FSCrawler open-source pour réaliser plus simplement ces étapes

Nous verrons ensuite comment chercher dans les données ainsi indexées.
Enfin, nous mettrons en place une interface de recherche sur étagère, portée par la solution gratuite Workplace Search qui nous permettra de chercher dans différentes sources documentaires avec assez peu d’efforts.

---
title: "Déployer et monitorer la suite Elastic sur Google Cloud Platform"
conference: 
  name: "GDG Lille"
  city: "Lille"
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
date: 2017-12-14
nolastmod: true
draft: false
cover: cover.jpg

# Speaker specific fields
#youtube: ""
notist: "dadoonet/tlQJC5"

x:
  - user: "_abarbare"
    id: "941364493396914176"
  - user: "LudovicBorie"
    id: "940857659351359488"
  - user: "dadoonet"
    id: "941416788730023938"
  - user: "dadoonet"
    id: "941416363456974849"
  - user: "dadoonet"
    id: "941374288535392256"
  - user: "gui_gillon"
    id: "941377671740710912"

links:
  - title: "GDG Lille"
    url: "https://www.meetup.com/fr-FR/GDG-Lille/events/245130596/"

aliases:
  - /tlQJC5
---
Pour déployer elasticsearch sur Google Compute Platform, plusieurs options s’offrent à vous :

Démarrer des instances GCE, installer et configurer elasticsearch pour le discovery
Idem mais installer le plugin discovery-gce qui vous simplifiera la découverte des noeuds
Puis installer X-Pack basic pour monitorer les ressources.
Utiliser Elastic Cloud Entreprise et le déployer sur des instances GCE
Laisser elastic la société, déployer et manager vos instances sur GCP via cloud.elastic.co

Ce talk vous décrira ces différentes options disponibles ainsi que quelques trucs et astuces pour optimiser au mieux votre usage d’elasticsearch quelque soit le mode de déploiement.

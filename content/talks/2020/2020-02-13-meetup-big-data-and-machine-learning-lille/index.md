---
title: "Identifier les menaces avec Elastic SIEM"
conference: 
  name: "Meetup Big Data and Machine Learning Lille"
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
date: 2020-02-13
nolastmod: true
draft: false
cover: cover.png

# Speaker specific fields
youtube: "_NXhiQM3Cl8"
notist: "dadoonet/LvVK63"

x:
  - user: "dadoonet"
    id: "1228349290403303424"
  - user: "MeetupDataLille"
    id: "1227620844211441664"
  - user: "EmmanuelDemey"
    id: "1220645207928078337"

links:
  - title: "AuditD Rules"
    url: "https://github.com/linux-audit/audit-userspace/tree/master/rules"
    description: "Templates for common auditD rules"
  - title: "Demo repository"
    url: "https://github.com/xeraa/auditbeat-in-action"

aliases:
  - /LvVK63
---
Savoir ce qui se passe dans votre environnement est une part importante pour être informé de problèmes de sécurité. Mais comment capturer et visualiser les informations pertinentes ? Un outil open source est mondialement utilisé pour cela : la suite Elastic. Ce talk vous fera découvrir par la pratique comment ingérer les données utiles provenant de votre couche réseau, de vos machines, de vos logs ainsi que le moyen de facilement les visualiser afin d’identifier des patterns et comportements suspicieux. Nous utiliserons notamment pour cela le tout dernier outil SIEM de la suite Elastic.
Nous utiliserons pour cela des données type “piège à miel” :

La première étape est de lire, extraire et enrichir la donnée afin d’identifier les attaques, leur source et plus encore.
Puis stocker et explorer la donnée collectée pour trouver des indicateurs pertinents.
Ce qui nous amènera à créer des visualisations spécifiques à notre besoin - par exemple la localisation de l’attaquant ou des patterns type d’attaque.
Puis nous combinerons ces visualisations dans un tableau de bord consolidant l’information.
Au final, nous utiliserons l’application SIEM pour voir comment toute cette recherche et analyse est dorénavant grandement simplifiée.

Tout cela en live.

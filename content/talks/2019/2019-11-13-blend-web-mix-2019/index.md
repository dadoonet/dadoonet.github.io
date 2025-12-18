---
title: "Identifier les menaces avec Elastic SIEM"
conference: 
  name: "Blend Web Mix 2019"
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
date: 2019-11-13
nolastmod: true
draft: false
cover: cover.png

# Speaker specific fields
youtube: "_NXhiQM3Cl8"
notist: "dadoonet/AhSY43"

x:
  - user: "unees15"
    id: "1194615963284627456"
  - user: "k33g_org"
    id: "1194615797429211142"
  - user: "blendwebmix"
    id: "1194615246285148160"
  - user: "blendwebmix"
    id: "1194603461310107648"
  - user: "k33g_org"
    id: "1194602451934076928"
  - user: "blendwebmix"
    id: "1194602333273018368"
  - user: "SiegfriedEhret"
    id: "1194602187218997248"
  - user: "SiegfriedEhret"
    id: "1194599210265534464"
  - user: "dadoonet"
    id: "1194578283242885121"
  - user: "dadoonet"
    id: "1194675827037917184"
  - user: "dadoonet"
    id: "1194681222494113797"
  - user: "k33g_org"
    id: "1194893501957378048"

links:
  - title: "AuditD Rules"
    url: "https://github.com/linux-audit/audit-userspace/tree/master/rules"
    description: "Templates for common auditD rules"
  - title: "Demo repository"
    url: "https://github.com/xeraa/auditbeat-in-action"

aliases:
  - /AhSY43
---
Savoir ce qui se passe dans votre environnement est une part importante pour être informé de problèmes de sécurité. Mais comment capturer et visualiser les informations pertinentes ? Un outil open source est mondialement utilisé pour cela : la suite Elastic. Ce talk vous fera découvrir par la pratique comment ingérer les données utiles provenant de votre couche réseau, de vos machines, de vos logs ainsi que le moyen de facilement les visualiser afin d’identifier des patterns et comportements suspicieux. Nous utiliserons notamment pour cela le tout dernier outil SIEM de la suite Elastic.

Nous utiliserons pour cela des données type “piège à miel” :

* La première étape est de lire, extraire et enrichir la donnée afin d’identifier les attaques, leur source et plus encore.
* Puis stocker et explorer la donnée collectée pour trouver des indicateurs pertinents.
* Ce qui nous amènera à créer des visualisations spécifiques à notre besoin - par exemple la localisation de l’attaquant ou des patterns type d’attaque.
* Puis nous combinerons ces visualisations dans un tableau de bord consolidant l’information.
* Au final, nous utiliserons l’application SIEM pour voir comment toute cette recherche et analyse est dorénavant grandement simplifiée.

Tout cela en live.

---
title: "Testcontainers pour de vrais tests d’intégration d’Elasticsearch"
description: ""
conference: 
  name: "Devfest Lille"
  url: ""
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
date: 2019-06-14
nolastmod: true
draft: false
cover: cover.jpg

# Speaker specific fields
youtube: "ex2jS3GTUfk"
notist: "dadoonet/L5rDwO"

x:
  - user: "dadoonet"
    id: "1139509930002735106"
  - user: "fdelbrayelle"
    id: "1139544412952940544"
  - user: "mattmasztalir"
    id: "1139544445039370246"
---

Les tests d’intégration peuvent devenir un cauchemar lorsqu’ils sont lancés depuis la même JVM que votre code:

Conflit de JARs (JAR Hell)
Security Manager
Effets de bord

De plus, tester avec un produit qui est lancé de façon différente de la façon dont il est lancé en production, ne garantira jamais que les tests d’intégration sont sincères.
Aussi, après avoir découvert le projet Testcontainers qui lance des conteneurs Docker, j’ai décidé d’écrire une implémentation pour Elasticsearch: testcontainers-java-module-elasticsearch.
Je vous propose de découvrir tout cela pendant cette session.

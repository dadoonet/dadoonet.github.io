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

# Speaker specific fields
#youtube: ""
notist: "dadoonet/L5rDwO"
---

Les tests d’intégration peuvent devenir un cauchemar lorsqu’ils sont lancés depuis la même JVM que votre code:

Conflit de JARs (JAR Hell)
Security Manager
Effets de bord

De plus, tester avec un produit qui est lancé de façon différente de la façon dont il est lancé en production, ne garantira jamais que les tests d’intégration sont sincères.
Aussi, après avoir découvert le projet Testcontainers qui lance des conteneurs Docker, j’ai décidé d’écrire une implémentation pour Elasticsearch: testcontainers-java-module-elasticsearch.
Je vous propose de découvrir tout cela pendant cette session.

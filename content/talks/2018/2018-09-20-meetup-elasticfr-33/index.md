---
title: "ElasticFR #33: Testcontainers pour de vrais tests d'intégration d'Elasticsearch"
conference:
  name: "Meetup ElasticFR"
  url: "https://www.meetup.com/elasticfr/events/253542268"
  city: "Paris"
  country: "France"
  country_code: "fr"
  latitude: "48.856614"
  longitude: "2.352222"
author: David Pilato
avatar: /about/david_pilato.avif
talk: Testcontainers
date: 2018-09-20
talk-lang: fr
nolastmod: true
draft: false
#pdf: "2023/2023-11-15-meetup-elasticfr-88.pdf"

# Speaker specific fields
youtube: "0e6uZj2pQro"

links:
  - title: "Demo: Elasticsearch Integration Tests"
    url: "https://github.com/dadoonet/elasticsearch-integration-tests"
    description: "This demo shows how you can test your Elasticsearch integration with Testcontainers."
  - title: "Repository: Elasticsearch Module for TestContainers"
    url: "https://github.com/testcontainers/testcontainers-java/tree/main/modules/elasticsearch"
    description: "This repository contains the code for the Elasticsearch Module for TestContainers."
  - title: "Documentation: Elasticsearch TestContainers module"
    url: "https://java.testcontainers.org/modules/elasticsearch/"
    description: "This documentation contains the information about the Elasticsearch TestContainers module."

---

Les tests d'intégration peuvent devenir un cauchemar lorsqu'ils sont lancés depuis la même JVM que votre code:

* Conflit de JARs (JAR Hell)
* Security Manager
* Effets de bord

De plus, tester avec un produit qui est lancé de façon différente de la façon dont il est lancé en production, ne garantira jamais que les tests d'intégration sont sincères.

Aussi, après avoir découvert le projet [Testcontainers](https://www.testcontainers.org/) qui lance des conteneurs Docker, j'ai décidé d'écrire une implémentation pour Elasticsearch: [testcontainers-java-module-elasticsearch](https://www.testcontainers.org/modules/elasticsearch/).
Je vous propose de découvrir tout cela pendant cette session.

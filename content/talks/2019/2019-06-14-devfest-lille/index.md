---
title: "Testcontainers pour de vrais tests d’intégration d’Elasticsearch"
conference: 
  name: "Devfest Lille"
  city: "Lille"
  country: "France"
  country_code: "fr"
  latitude: "50.629250"
  longitude: "3.057256"
author: David Pilato
avatar: /about/david_pilato.png
# talk: conferences
date: 2019-06-14
talk-lang: fr
nolastmod: true
draft: false


# Speaker specific fields
youtube: "hlfy1EDAP4U"
notist: "dadoonet/L5rDwO"

x:
  - user: "dadoonet"
    id: "1139509930002735106"
  - user: "fdelbrayelle"
    id: "1139544412952940544"
  - user: "mattmasztalir"
    id: "1139544445039370246"

links:
  - title: "Demo: elasticsearch-integration-tests repository"
    url: "https://github.com/dadoonet/elasticsearch-integration-tests"
    description: "This repository contains the code for the elasticsearch-integration-tests demo."
  - title: "Repository: Elasticsearch Module for TestContainers"
    url: "https://github.com/testcontainers/testcontainers-java/tree/master/modules/elasticsearch"
    description: "This repository contains the code for the Elasticsearch Module for TestContainers."
  - title: "Documentation: Elasticsearch TestContainers module"
    url: "https://www.testcontainers.org/modules/elasticsearch/"
    description: "This documentation contains the information about the Elasticsearch TestContainers module."

aliases:
  - /L5rDwO
---
Les tests d’intégration peuvent devenir un cauchemar lorsqu’ils sont lancés depuis la même JVM que votre code:

* Conflit de JARs (JAR Hell)
* Security Manager
* Effets de bord

De plus, tester avec un produit qui est lancé de façon différente de la façon dont il est lancé en production, ne garantira jamais que les tests d’intégration sont sincères.

Aussi, après avoir découvert le projet [Testcontainers](https://www.testcontainers.org/) qui lance des conteneurs Docker, j’ai décidé d’écrire une implémentation pour Elasticsearch: [testcontainers-java-module-elasticsearch](https://www.testcontainers.org/modules/elasticsearch/).
Je vous propose de découvrir tout cela pendant cette session.

---
title: "Testcontainers pour de vrais tests d’intégration d’Elasticsearch"
conference: 
  name: "Devoxx FR"
  city: "Paris"
  country: "France"
  country_code: "fr"
  latitude: "48.856614"
  longitude: "2.352222"
  url: "https://devoxx.fr/"
author: David Pilato
avatar: /about/david_pilato.png
# talk: conferences
date: 2018-04-20
nolastmod: true
draft: false
pdf: "2018/2018-04-20-devvoxx-france.pdf"


# Speaker specific fields
youtube: "ex2jS3GTUfk"
attendees: 100

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
---
Les tests d’intégration peuvent devenir un cauchemar lorsqu’ils sont lancés depuis la même JVM que votre code:

* Conflit de JARs (JAR Hell)
* Security Manager
* Effets de bord

De plus, tester avec un produit qui est lancé de façon différente de la façon dont il est lancé en production, ne garantira jamais que les tests d’intégration sont sincères.

Aussi, après avoir découvert le projet [Testcontainers](https://www.testcontainers.org/) qui lance des conteneurs Docker, j’ai décidé d’écrire une implémentation pour Elasticsearch: [testcontainers-java-module-elasticsearch](https://www.testcontainers.org/modules/elasticsearch/).
Je vous propose de découvrir tout cela pendant cette session.

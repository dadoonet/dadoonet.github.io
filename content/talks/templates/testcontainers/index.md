---
title: "Testcontainers for real integration tests with Elasticsearch"
layout: "template"
talk: Testcontainers
nolastmod: true
draft: false

versions:
  - label: "EN"
    flag: "gb"
    title: "Testcontainers for real integration tests with Elasticsearch"
    abstract: |
      How are you testing with your database?

      * Mocking is not an option since you want to test the actual system.
      * In-memory databases, like H2 or HSQLDB, have subtle differences and not all datastores have in-memory cousins.
      * Managing and running tests in parallel against the actual datastore is a pain.

      So what is the solution? There are some very neat solutions based on containers, namely the Docker-Maven-Plugin and Testcontainers. From your tests you can start a lightweight, throwaway instance of your datastore and this talk will walk you through how to do that.

      And we will introduce the module we built for Elasticsearch: https://www.testcontainers.org/modules/elasticsearch/.
  - label: "FR"
    flag: "fr"
    title: "Testcontainers pour de vrais tests d'intégration d'Elasticsearch"
    abstract: |
      Les tests d'intégration peuvent devenir un cauchemar lorsqu'ils sont lancés depuis la même JVM que votre code:

      * Conflit de JARs (JAR Hell)
      * Security Manager
      * Effets de bord

      De plus, tester avec un produit qui est lancé de façon différente de la façon dont il est lancé en production, ne garantira jamais que les tests d'intégration sont sincères.

      Aussi, après avoir découvert le projet [Testcontainers](https://www.testcontainers.org/) qui lance des conteneurs Docker, j'ai décidé d'écrire une implémentation pour Elasticsearch: [testcontainers-java-module-elasticsearch](https://www.testcontainers.org/modules/elasticsearch/).
      Je vous propose de découvrir tout cela pendant cette session.

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

---
title: "Elasticsearch Query Language: ES|QL"
layout: "template"
talk: ES|QL
date: 2024-09-17
nolastmod: true
draft: false

versions:
  - label: "EN"
    flag: "gb"
    title: "Elasticsearch Query Language: ES|QL"
    abstract: |
      Elasticsearch and Kibana added a brand new query language: ES|QL — coming with a new endpoint (`_query`) and a simplified syntax. It lets you refine your results one step at a time and adds new features like data enrichment and processing right in your query. And you can use it across the Elastic Stack — from the Elasticsearch API to Discover and Alerting in Kibana. But the biggest change is behind the scenes: Using a new compute engine that was built with performance in mind.
      
      Join us for an overview and a look at syntax and internals.
  - label: "EN - Slideless"
    flag: "gb"
    title: "Elasticsearch Query Language: ES|QL"
    abstract: |
      In this no-slides session, we'll discover through hands-on practice what the new `ES|QL` language brings to dig into our data indexed in Elasticsearch, interactively and visually.
      
      `ES|QL` and especially the new engine behind the `_query` API bring both a simplified syntax allowing you to refine your results step by step and add new features like data enrichment and on-the-fly transformation directly in your query, as well as unparalleled performance.
  - label: "FR"
    flag: "fr"
    title: "Elasticsearch Query Language: ES|QL"
    abstract: |
      Elasticsearch et Kibana apportent un tout nouveau langage, ES|QL, avec une nouvelle API (`_query`) et une syntaxe simplifiée. Cela vous permet d'affiner vos résultats, étape par étape et ajouter de nouvelles fonctionnalités comme par exemple l'enrichissement de données et la transformation à la volée, directement dans votre requête. Et vous pouvez l'utiliser sur toute la plateforme Elastic — depuis les API Elasticsearch jusqu'aux fonctions de "Discover" et d'"Alerting" de Kibana. Mais le changement principal n'est pas celui que vous verrez : les ingénieurs ont développé un tout nouveau moteur de calcul, construit avec la performance comme guide. 
      
      Venez découvrir un aperçu de ce nouveau moteur avec découverte de la syntaxe et du fonctionnement interne.

  - label: "FR - Slideless"
    flag: "fr"
    title: "Elasticsearch Query Language: ES|QL"
    abstract: |
      Dans cette session sans slides, nous découvrirons par la pratique ce qu'apporte le nouveau language `ES|QL` pour aller fouiller dans nos données indexées dans Elasticsearch et ce, de façon interactive et visuelle.
      
      `ES|QL` et surtout le nouveau moteur derrière l'API `_query` apportent à la fois une syntaxe simplifiée permettant d'affiner vos résultats, étape par étape et ajouter de nouvelles fonctionnalités comme par exemple l'enrichissement de données et la transformation à la volée, directement dans votre requête, mais également des performances inégalées.

links:
  - title: "Demo code"
    url: "https://github.com/dadoonet/esql-demo"
    description: "The code played during the demo"
  - title: "Playground page"
    url: "https://esql.demo.elastic.co"
    description: "If you want to try ES|QL, there's an open instance with some data."
  - title: "ES|QL Guide"
    url: "https://www.elastic.co/guide/en/elasticsearch/reference/current/esql.html"
    description: "The official guide"
  - title: "Java Demo code"
    url: "https://github.com/dadoonet/elasticsearch-java-client-demo"
    description: "The Java demo for ES|QL"
---

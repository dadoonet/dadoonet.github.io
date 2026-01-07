---
title: "Elasticsearch Query Language: ES|QL"
conference: 
  name: "BreizhCamp"
  city: "Rennes"
  country: "France"
  country_code: "fr"
  latitude: "48.117266"
  longitude: "-1.677793"
  url: "https://2024.breizhcamp.org/"
author: David Pilato
avatar: /about/david_pilato.png
talk: ES|QL
date: 2024-06-28
nolastmod: true
draft: false
pdf: "2024/2024-06-28-breizhcamp.pdf"


# Speaker specific fields
youtube: "jcIDh5LR8_Y"
notist: "dadoonet/pSNxdE"

x:
  - user: "dadoonet"
    id: "1805508048858849526"
  - user: "dadoonet"
    id: "1806589600355549534"
  - user: "dadoonet"
    id: "1806688935277404408"

links:
  - title: "Demo: ES|QL"
    url: "https://github.com/dadoonet/esql-demo"
    description: "This repository contains the code for the ES|QL demo."
  - title: "Demo: Playground page"
    url: "https://esql.demo.elastic.co"
    description: "This is an open instance with some data where you can try ES|QL."
  - title: "Documentation: ES|QL"
    url: "https://www.elastic.co/guide/en/elasticsearch/reference/current/esql.html"
    description: "This is the official ES|QL guide."
  - title: "Demo: Elasticsearch Java client with ES|QL"
    url: "https://github.com/dadoonet/elasticsearch-java-client-demo"
    description: "This demo shows how you can use the Elasticsearch Java client to interact with ES|QL"

aliases:
  - /pSNxdE
---
Elasticsearch et Kibana apportent un tout nouveau langage, ES|QL, avec une nouvelle API (`_query`) et une syntaxe simplifiée. Cela vous permet d’affiner vos résultats, étape par étape et ajouter de nouvelles fonctionnalités comme par exemple l’enrichissement de données et la transformation à la volée, directement dans votre requête. Et vous pouvez l’utiliser sur toute la plateforme Elastic — depuis les API Elasticsearch jusqu’aux fonctions de “Discover” et d‘“Alerting” de Kibana. Mais le changement principal n’est pas celui que vous verrez : les ingénieurs ont développé un tout nouveau moteur de calcul, construit avec la performance comme guide.
Venez découvrir un aperçu de ce nouveau moteur avec découverte de la syntaxe et du fonctionnement interne.

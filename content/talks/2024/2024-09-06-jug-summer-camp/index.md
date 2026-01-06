---
title: "Elasticsearch Query Language: ES|QL"
conference: 
  name: "JUG Summer Camp"
  city: "La Rochelle"
  country: "France"
  country_code: "fr"
  latitude: "46.160329"
  longitude: "-1.151139"
  url: "https://www.jugsummercamp.org/edition/15/presentations/GxmHLbTOhV23O4y88B1Z"
author: David Pilato
avatar: /about/david_pilato.png
talk: conferences
date: 2024-09-06
nolastmod: true
draft: false
pdf: "2024/2024-09-06-jug-summer-camp.pdf"


# Speaker specific fields
youtube: "Fa6ICBs1KM0"
notist: "dadoonet/CzXjMr"

x:
  - user: "dadoonet"
    id: "1827998166865637459"
  - user: "dadoonet"
    id: "1830635264806621289"
  - user: "jugsummercamp"
    id: "1829150830089646215"

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
  - /CzXjMr
---
Elasticsearch et Kibana apportent un tout nouveau langage, ES|QL, avec une nouvelle API (`_query`) et une syntaxe simplifiée. Cela vous permet d’affiner vos résultats, étape par étape et ajouter de nouvelles fonctionnalités comme par exemple l’enrichissement de données et la transformation à la volée, directement dans votre requête. Et vous pouvez l’utiliser sur toute la plateforme Elastic — depuis les API Elasticsearch jusqu’aux fonctions de “Discover” et d‘“Alerting” de Kibana. Mais le changement principal n’est pas celui que vous verrez : les ingénieurs ont développé un tout nouveau moteur de calcul, construit avec la performance comme guide.
Venez découvrir un aperçu de ce nouveau moteur avec découverte de la syntaxe et du fonctionnement interne.

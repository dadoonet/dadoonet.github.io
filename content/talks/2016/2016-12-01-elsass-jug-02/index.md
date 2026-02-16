---
title: 'Ingest node : (ré)indexer et enrichir des documents dans Elasticsearch'
conference:
  url: "https://www.meetup.com/elsassjug/events/235671400/"
  name: "Elsass JUG"
  city: "Strasbourg"
  country: "France"
  country_code: "fr"
  latitude: "48.5835421"
  longitude: "7.7478388"
author: David Pilato
avatar: /about/david_pilato.webp
talk: Ingest Node
date: 2016-12-01T20:15:00+01:00
talk-lang: fr
nolastmod: true
draft: false
pdf: "2016/2016-12-01-elsass-jug-02.pdf"

attendees: 25
---

Lorsque vous injectez des données dans elasticsearch, vous pouvez avoir besoin de réaliser des opérations de transformation assez simples. Jusqu'à présent, ces opérations devaient s'effectuer en dehors d'elasticsearch, avant l'indexation proprement dite.

Souhaitez la bienvenue à Ingest node ! Un nouveau type de noeud qui vous permet justement de faire cela.

Ce talk explique le concept de Ingest Node, comment l'intégrer avec le reste de la suite logicielle Elastic et comment développer son propre plugin Ingest par la pratique en montrant comment j'ai développé le plugin ingest-bano pour enrichir des adresses postales et/ou des coordonnées géographiques françaises (pour l'instant).

Ce talk parlera également de l'API de réindexation qui peut également bénéficier du pipeline d'ingestion pour modifier vos données à la volée lors de la réindexation.

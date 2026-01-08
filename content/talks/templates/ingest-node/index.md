---
title: "Ingest node: (re)index and enrich documents in Elasticsearch"
layout: "template"
talk: Ingest Node
date: 2016-12-01
nolastmod: true
draft: false

versions:
  - label: "EN"
    flag: "gb"
    title: "Ingest node: (re)index and enrich documents in Elasticsearch"
    abstract: |
      When you ingest data into Elasticsearch, you may need to perform fairly simple transformation operations. Until now, these operations had to be done outside of Elasticsearch, before the actual indexing.
      
      Welcome Ingest node! A new type of node that allows you to do just that.
      
      This talk explains the concept of Ingest Node, how to integrate it with the rest of the Elastic software suite, and how to develop your own Ingest plugin in practice by showing how I developed the ingest-bano plugin to enrich French postal addresses and/or geographic coordinates (for now).
      
      This talk will also cover the reindex API which can also benefit from the ingest pipeline to modify your data on the fly during reindexing.
  - label: "FR"
    flag: "fr"
    title: "Ingest node : (ré)indexer et enrichir des documents dans Elasticsearch"
    abstract: |
      Lorsque vous injectez des données dans elasticsearch, vous pouvez avoir besoin de réaliser des opérations de transformation assez simples. Jusqu'à présent, ces opérations devaient s'effectuer en dehors d'elasticsearch, avant l'indexation proprement dite.
      
      Souhaitez la bienvenue à Ingest node ! Un nouveau type de noeud qui vous permet justement de faire cela.
      
      Ce talk explique le concept de Ingest Node, comment l'intégrer avec le reste de la suite logicielle Elastic et comment développer son propre plugin Ingest par la pratique en montrant comment j'ai développé le plugin ingest-bano pour enrichir des adresses postales et/ou des coordonnées géographiques françaises (pour l'instant).
      
      Ce talk parlera également de l'API de réindexation qui peut également bénéficier du pipeline d'ingestion pour modifier vos données à la volée lors de la réindexation.
---

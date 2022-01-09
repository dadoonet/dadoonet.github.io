---
title: "ScrutMyDocs : un moteur de recherche pour documents"
#description: 
toc: true
authors:
  - David Pilato
tags:
  - elasticsearch
  - java
  - spring
  - enterprise search
categories:
  - projects
date: 2012-07-20 23:38:00 +0200
featuredImage: blog/2012-07-20-scrutmydocs-un-moteur-de-recherche-pour-documents/scrutmydocs.png
draft: false
aliases:
  - /blog/2012/07/20/scrutmydocs-un-moteur-de-recherche-pour-documents/
---

Avec Malloum, nous venons de publier notre premier projet open-source commun: Scrut My Docs !

{{< figure src="technical1.jpg" caption="Technical overview" >}}

<!-- more -->

## Nos objectifs

* Fournir une application web clé en main permettant d’indexer des documents de vos disques locaux.
* Fournir à la communauté Elasticsearch un modèle de base pour développer votre propre webapp pour une utilisation simple de recherche (« à la google »).
* Aider les débutants Elasticsearch Java avec des exemples concrets en Java

## Les technologies employées

* Elasticsearch ! et son écosystème (rivers, plugins)
* Spring
* JSF
* Primefaces

## Comment démarrer ?

Télécharger la webapp <https://github.com/downloads/scrutmydocs/scrutmydocs/scrutmydocs-0.1.0.war> et la déployer dans votre conteneur favori (testé sur Tomcat et Jetty).

La documentation est sur la repository [GitHub](https://github.com/scrutmydocs/scrutmydocs).

Plus de détails et une démo sur le site web : <http://www.scrutmydocs.org>

Les commentaires sur le projet, les demandes d’évolution, les rapports de bug et les pull requests sont évidemment les bienvenus !

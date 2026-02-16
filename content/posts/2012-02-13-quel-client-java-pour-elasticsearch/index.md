---
title: Quel client Java pour elasticsearch ?
description: "Il existe deux modes d'accès à elasticsearch en Java : inscrire un noeud client dans le cluster elasticsearch ou utiliser un client simple."
author: David Pilato
avatar: /about/david_pilato.webp
tags:
  - elasticsearch
  - java
  - maven
categories:
  - tutorial
date: 2012-02-13 21:37:12 +00:00
nolastmod: true
draft: false
aliases:
  - /blog/2012/02/13/quel-client-java-pour-elasticsearch/
  - /blog-2012-02-13-quel-client-java-pour-elasticsearch/
---

Il existe deux modes d'accès à elasticsearch en Java :

* Inscrire un noeud client dans le cluster elasticsearch
* Utiliser un client "simple"

<!--more-->

## Noeud client dans un cluster elasticsearch

L'idée de cette méthode est de fabriquer un noeud elasticsearch (node) qui démarre avec les mêmes caractéristiques qu'un noeud d'indexation et de recherche sauf qu'on lui précise qu'il n'hébergera pas de données.

Pour cela, on utilise la propriété suivante :

```yaml
node.data=false
```

Elle indique que le noeud que nous démarrons n'hébergera pas de données. En gros, c'est un noeud qui sert juste à fabriquer des clients...

L'avantage est qu'il n'est pas nécessaire de configurer quoi que ce soit car la particularité des noeuds elasticsearch est de s'auto-découvrir les uns les autres grâce aux fonctions de multicast.

Démarrer un noeud autonome est également intéressant pour réaliser des tests unitaires. En effet, dans ce cas, vous avez une instance autonome complète d'elasticsearch.

Démarrer un noeud et obtenir un client, ce n'est pas bien difficile :

```java
// Build a node
Node node = NodeBuilder.nodeBuilder().node();

// Get a client from the node
Client client = node.client();
```

Avec la première ligne, vous devriez voir apparaître dans les logs de vos noeuds Elasticsearch, le fait qu'un nouveau noeud a rejoint le cluster.

## Client "simple" ou TransportClient

Un Transport Client est un client Elasticsearch autonome plus léger qui n'appartient pas réellement au cluster de noeuds Elasticsearch. Ainsi, lorsqu'un client démarre, aucune trace n’apparaît dans les logs des noeuds du cluster puisque ce client ne fait pas proprement parti du cluster.

Pour qu'un tel client sache comment trouver des noeuds Elasticsearch du cluster que vous souhaitez rejoindre, il faut lui indiquer au moins une adresse. Vous pouvez préciser plusieurs adresses pour mieux gérer les pannes et la répartition de charge.

Pour démarrer un tel client, on écrit donc :

```java
TransportClient client = new TransportClient()
  .addTransportAddress(new InetSocketTransportAddress("localhost", 9300))
  .addTransportAddress(new InetSocketTransportAddress("localhost", 9301));
```

## Quel client choisir ?

Passer par un noeud pour obtenir un client peut perturber votre cluster, même si en théorie, ça devrait être neutre. Car le noeud fait partie du cluster. Donc, quand il meurt, les autres noeuds doivent être prévenus pour prendre des décisions. En l’occurrence, aucune décision à prendre car le noeud n'héberge pas de données. Mais cela nécessite un traitement même minime de la part des noeuds.

De la même façon quand un noeud arrive dans le cluster, il se déclare, occupe deux ports de communication (9200-9299 et 9300-9399) car en tant que noeud il peut être amené à recevoir des requêtes.

De plus, un noeud Elasticsearch démarre plus de Threads et notamment un qui pose problème en ce moment en raison d'un souci avec la librairie Guava. En mode debug sous Eclipse par exemple, cela va vous empêcher de redémarrer proprement votre webapp sans avoir à redémarrer le serveur d'application.

En production, c'est pareil. Si vous embarquez dans votre webapp un noeud client Elasticsearch, vous devrez obligatoirement redémarrer le serveur d'application sous peine d'erreur de mémoire (OOM).

Donc, mon expérience m'indique qu'il vaut mieux passer par des clients plus légers et neutres pour le cluster. J'ai donc choisi dans mes projets la deuxième option lorsque j'ai besoin d'un client dans une webapp.

Lorsque je veux faire des tests unitaires (ou d'intégration) de mon application, j'utilise plutôt la première méthode.

## Et il y a un moyen de choisir quand je veux ce que je veux ?

Dans un prochain article, je vous décrirai la factory Spring que j'ai développée et publiée sur [github](https://github.com/dadoonet/spring-elasticsearch).

La version n'est pas encore finalisée, notamment en raison d'un [petit bug](https://github.com/elasticsearch/elasticsearch/issues/1691) avec la version 0.19.0.RC2 d'Elasticsearch, mais la version SNAPSHOT est en cours de tests dans un de mes projets.

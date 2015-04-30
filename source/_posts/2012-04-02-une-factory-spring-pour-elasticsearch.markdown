---
author: dadoonet
comments: true
date: 2012-04-02 20:02:09+00:00
layout: post
slug: une-factory-spring-pour-elasticsearch
title: Une factory Spring pour Elasticsearch
wordpress_id: 224
categories:
- Elasticsearch
- Java
- Maven
- Spring
tags:
- elasticsearch
- featured
- Spring
---

# Le besoin


Il existe dans Hibernate une fonctionnalité que j'aime beaucoup : la mise à jour automatique du schéma de la base en fonction des entités manipulées.

Mon besoin est de faire quasiment la même chose avec Elasticsearch. C'est à dire que je souhaite pouvoir appliquer un mapping pour un type donné à chaque fois que je démarre mon projet (en l’occurrence une webapp).

En me basant sur le projet développé par [Erez Mazor](http://techo-ecco.com/blog/elasticsearch-with-spring/), j'ai donc développé une[ factory Spring](https://github.com/dadoonet/spring-elasticsearch) visant à démarrer des clients (voire des noeuds) Elasticsearch.


# La solution


Donc, on se place dans un environnement de développement Java, Maven et Spring.

Pour importer la factory, il suffit d'ajouter ces quelques lignes à votre pom.xml.

[sourcecode language="xml"]

fr.pilato.spring
spring-elasticsearch
0.0.1-SNAPSHOT

[/sourcecode]

Il suffit ensuite de définir son bean client Elasticsearch ainsi :

[sourcecode language="xml"]






[/sourcecode]

Par défaut, on obtient ainsi un [TransportClient](http://dev.david.pilato.fr/?p=185) qui se connecte automatiquement au noeud Elasticsearch tournant à l'adresse http://localhost:9200/.

L'intérêt de cette factory est donc de pouvoir prédéfinir ses index et ses types au moment où elle démarre. Ainsi, si vous avez un index nommé twitter et un type nommé tweet, vous pouvez en définir les propriétés respectives en plaçant simplement dans votre classpath un fichier **es/twitter/_settings.json** et un fichier **es/twitter/tweet.json**. Le premier sera appliqué au moment de la création de l'index. Le deuxième sera appliqué au moment de la création du type.

Pour cela, il faut, comme pour Hibernate, définir les types gérés :

[sourcecode language="xml"]




twitter/tweet




[/sourcecode]

La factory permet également de gérer la création automatique d'alias sur des index. Pour cela, on utilise la syntaxe suivante.

[sourcecode language="xml"]




twitter:twitter2012
twitter:twitter2013
twitter:twitter2014




[/sourcecode]

Ainsi, au démarrage, les index twitter2012, twitter2013 et twitter2014 auront un alias twitter.

D'autres fonctionnalités sont possibles. Voir le [README](https://github.com/dadoonet/spring-elasticsearch/blob/master/README.textile) disponible sur github.

J'utilise déjà ces premières fonctionnalités en production sur un de mes projets au boulot.

Dernière petite fonction mais à manier avec précaution car elle est plutôt destinée à faire de l'intégration continue. Il s'agit du paramètre **forceReinit** qui reconstruit à chaque démarrage les types gérés. Aussi, toutes les données de ces types sont perdues à chaque lancement de la factory.

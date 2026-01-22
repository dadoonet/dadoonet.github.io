---
title: Une factory Spring pour Elasticsearch
description: "Il existe dans Hibernate une fonctionnalité que j'aime beaucoup : la mise à jour automatique du schéma de la base en fonction des entités manipulées.
Mon besoin est de faire quasiment la même chose avec Elasticsearch. C'est à dire que je souhaite pouvoir appliquer un mapping pour un type donné à chaque fois que je démarre mon projet (en l’occurrence une webapp)."
author: David Pilato
avatar: /about/david_pilato.png
tags:
  - elasticsearch
  - java
  - maven
  - spring
categories:
  - projects
series:
  - elasticsearch spring factories
date: 2012-04-02 20:02:09 +00:00
nolastmod: true
draft: false
aliases:
  - /blog/2012/04/02/une-factory-spring-pour-elasticsearch/
  - /blog/2012-04-02-une-factory-spring-pour-elasticsearch/
---

## Le besoin

Il existe dans Hibernate une fonctionnalité que j'aime beaucoup : la mise à jour automatique du schéma de la base en fonction des entités manipulées.

Mon besoin est de faire quasiment la même chose avec Elasticsearch. C'est à dire que je souhaite pouvoir appliquer un mapping pour un type donné à chaque fois que je démarre mon projet (en l’occurrence une webapp).

<!--more-->

En me basant sur le projet développé par Erez Mazor, j'ai donc développé une[factory Spring](https://github.com/dadoonet/spring-elasticsearch) visant à démarrer des clients (voire des noeuds) Elasticsearch.

## La solution

Donc, on se place dans un environnement de développement Java, Maven et Spring.

Pour importer la factory, il suffit d'ajouter ces quelques lignes à votre `pom.xml`:

```xml
<dependency>
 <groupId>fr.pilato.spring</groupId>
 <artifactId>spring-elasticsearch</artifactId>
 <version>0.0.1-SNAPSHOT</version>
</dependency>
```

Il suffit ensuite de définir son bean client Elasticsearch ainsi :

```xml
<?xml version="1.0" encoding="UTF-8"?>
<beans xmlns="http://www.springframework.org/schema/beans"
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
 xmlns:context="http://www.springframework.org/schema/context"
 xmlns:util="http://www.springframework.org/schema/util"
 xmlns:elasticsearch="http://www.pilato.fr/schema/elasticsearch"
 xsi:schemaLocation="http://www.springframework.org/schema/beans http://www.springframework.org/schema/beans/spring-beans-3.0.xsd
 http://www.springframework.org/schema/util http://www.springframework.org/schema/util/spring-util-3.0.xsd
 http://www.springframework.org/schema/context http://www.springframework.org/schema/context/spring-context-3.0.xsd
 http://www.pilato.fr/schema/elasticsearch http://www.pilato.fr/schema/elasticsearch/elasticsearch-0.1.xsd">

 <elasticsearch:client id="esClient" />

</beans>
```

Par défaut, on obtient ainsi un [TransportClient]({{< ref "2012-02-13-quel-client-java-pour-elasticsearch" >}}) qui se connecte automatiquement au noeud Elasticsearch tournant à l'adresse <http://localhost:9200/>.

L'intérêt de cette factory est donc de pouvoir prédéfinir ses index et ses types au moment où elle démarre. Ainsi, si vous avez un index nommé twitter et un type nommé tweet, vous pouvez en définir les propriétés respectives en plaçant simplement dans votre classpath un fichier `es/twitter/_settings.json` et un fichier `es/twitter/tweet.json`. Le premier sera appliqué au moment de la création de l'index. Le deuxième sera appliqué au moment de la création du type.

Pour cela, il faut, comme pour Hibernate, définir les types gérés :

```xml
<bean id="esClient" class="fr.pilato.spring.elasticsearch.ElasticsearchClientFactoryBean" >
 <property name="mappings">
 <list>
  <value>twitter/tweet</value>
 </list>
 </property>
</bean>
```

La factory permet également de gérer la création automatique d'alias sur des index. Pour cela, on utilise la syntaxe suivante.

```xml
<bean id="esClient" class="fr.pilato.spring.elasticsearch.ElasticsearchClientFactoryBean" >
 <property name="aliases">
  <list>
   <value>twitter:twitter2012</value>
   <value>twitter:twitter2013</value>
   <value>twitter:twitter2014</value>
  </list>
 </property>
</bean>
```

Ainsi, au démarrage, les index `twitter2012`, `twitter2013` et `twitter2014` auront un alias `twitter`.

D'autres fonctionnalités sont possibles. Voir le [README](https://github.com/dadoonet/spring-elasticsearch/blob/master/README.md) disponible sur github.

J'utilise déjà ces premières fonctionnalités en production sur un de mes projets au boulot.

Dernière petite fonction mais à manier avec précaution car elle est plutôt destinée à faire de l'intégration continue. Il s'agit du paramètre `forceReinit` qui reconstruit à chaque démarrage les types gérés. Aussi, toutes les données de ces types sont perdues à chaque lancement de la factory.

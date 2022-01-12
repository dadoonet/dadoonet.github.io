---
title: "Mon premier plugin elasticsearch : RSS River"
#description: 
toc: true
authors:
  - David Pilato
tags:
  - elasticsearch
  - java
  - maven
  - plugin
categories:
  - projects
date: 2011-09-14 21:30:07 +00:00
lastmod: 2011-09-14 21:30:07 +00:00
# featuredImage: blog/2012-07-20-scrutmydocs-un-moteur-de-recherche-pour-documents/scrutmydocs.png
draft: false
aliases:
  - /blog/2011/09/14/mon-premier-plugin-elasticsearch-rss-river/
---

Il existe dans [elasticsearch](http://www.elasticsearch.org/) la notion de [river](http://www.elasticsearch.org/guide/reference/river/) (rivière) qui comme son nom le laisse supposer permet de voir s'écouler des données depuis une source jusqu'à elasticsearch.

Au fur et à mesure que les données arrivent, la rivière les transporte et les envoie à l'indexation dans elasticsearch.

<!-- more -->

En standard, il existe 4 rivières :

* CouchDB qui permet d'indexer toutes les nouveautés d'une base CouchDB. Voir aussi [cet article à ce propos]({{< ref "2011-05-13-couchdb" >}}).
* RabbitMQ qui permet de récupérer des documents dans une queue de traitement asynchrone (genre JMS)
* Twitter qui permet d'indexer votre flux de messages twitter par exemple
* Wikipedia qui permet d'indexer toutes les nouveautés de l'encyclopédie au fur et à mesure de leurs publications

## Premiers pas

J'ai commencé par bidouiller un peu la rivière CouchDB pour y apporter quelques fonctionnalités dont mes collègues avaient besoin :

* désactivation du champ _attachement. Voir [Pull Request 1283](https://github.com/elasticsearch/elasticsearch/pull/1283).
* récupération du contenu d'une vue plutôt que le document original lui même. Voir [Pull Request 1258](https://github.com/elasticsearch/elasticsearch/pull/1258).

Finalement, le principe se révèle assez simple. Il faut une classe qui implémente [River](https://github.com/elasticsearch/elasticsearch/blob/master/modules/elasticsearch/src/main/java/org/elasticsearch/river/River.java) et qui hérite de [AbstractRiverComponent](https://github.com/elasticsearch/elasticsearch/blob/master/modules/elasticsearch/src/main/java/org/elasticsearch/river/AbstractRiverComponent.java).

Là, il ne reste plus qu'à implémenter :

* Le constructeur
* La méthode `start()` qui se lance quand la rivière démarre
* La méthode `close()` qui se lance lorsque la rivière stoppe

## Et mon flux RSS alors ?

Oui... J'y viens...

Au fait, tout le monde sait ce qu'est un flux RSS ? La spécification officielle est [ici](http://www.rssboard.org/rss-specification).

Je reprends donc le plugin [CouchDB River](https://github.com/elasticsearch/elasticsearch/tree/master/plugins/river/couchdb), je le mavenise (ouais, je ne suis pas encore super fan de Gradle), et je l'adapte à mes besoins.

Pour faire simple, je vais suivre la mécanique suivante :

* Toutes les x minutes, je télécharge le flux RSS demandé que je transforme en POJO en me basant sur le travail fait par [Lars Vogel](http://www.vogella.de/articles/RSSFeed/article.html)
* Je compare la date du flux (balise pubDate) avec la dernière date de flux (que j'avais stockée dans elasticsearch)
* Si le flux est plus récent, je parcours tous les éléments du flux (item)
* Je fabrique un identifiant de l'item basé sur un encodage du champ description. Pour cela, je me sers de ce qui est [déjà présent dans ES](https://github.com/elasticsearch/elasticsearch/blob/master/modules/elasticsearch/src/main/java/org/elasticsearch/common/UUID.java).
* Si cet identifiant a déjà été envoyé à elasticsearch, alors on ignore cet item.
* Sinon, on le pousse vers elasticsearch dans un document de type "page"

Les champs récupérés pour le moment dans le flux RSS sont :

* title
* description
* author
* link

## Ca marche ?

Mes profs en école d'ingé me disaient : "non ! ça fonctionne..."

Bon, une fois le plugin publié sous github, il est simple de l'utiliser.

Tout d'abord, on l'installe :

```sh
bin/plugin -install dadoonet/rssriver/0.0.1
```

Puis, on démarre elasticsearch et on créé notre index pour stocker le flux RSS :

```sh
curl -XPUT 'http://localhost:9200/lemonde/' -d '{}'
```

Puis on ajoute la rivière :

```sh
curl -XPUT 'http://localhost:9200/_river/lemonde/_meta' -d '{
  "type": "rss",
  "rss": {
    "url": "http://www.lemonde.fr/rss/une.xml"
  }
}'
```

**Et voilà...**

A partir de ce moment, on peut faire des recherches dans le flux... Par exemple :

```sh
curl –XGET 'http://localhost:9200/lemonde/_search?q=taxe'
```

On peut jouer sur les paramètres de la rivière en modifiant les paramètres `url` pour l'adresse du flux et `update_rate` pour la fréquence de mise à jour du flux (en millisecondes).

Egalement, il peut être souhaitable (conseillé) de modifier le mapping par défaut du type "page" :

```sh
curl -XPUT 'http://localhost:9200/lefigaro/' -d '{}'
curl -XPUT 'http://localhost:9200/lefigaro/page/_mapping' -d '{
  "page" : {
    "properties" : {
      "title" : {"type" : "string", "analyzer" : "french"},
      "description" : {"type" : "string", "analyzer" : "french"},
      "author" : {"type" : "string"},
      "link" : {"type" : "string"}
    }
  }
}'
curl -XPUT 'localhost:9200/_river/lefigaro/_meta' -d '{
  "type": "rss",
  "rss": {
    "url": "http://rss.lefigaro.fr/lefigaro/laune",
    "update_rate": 900000
  }
}'
```

## Et maintenant ?

> Que vais-je faire de tout ce temps ? Que sera ma vie ?

{{< youtube hmSBAJdie7E >}}

J'envisage de faire une nouvelle évolution du plugin CouchDB car pour le moment, il ne traite pas la récupération des pièces jointes (format binaire).

Et bien évidemment, poursuivre sur le plugin RSS River qui doit traiter d'autres balises et être testé avec d'autres flux...

D'ailleurs, si vous l'utilisez et que vous rencontrez des problèmes, n'hésitez pas à contribuer en créant [des bugs](https://github.com/dadoonet/rssriver/issues) ou en forkant et améliorant le projet.

Les sources sont ici : <https://github.com/dadoonet/rssriver>

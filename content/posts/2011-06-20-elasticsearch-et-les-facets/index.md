---
title: Elasticsearch et les "facets"
description: "Les facettes (facets) avec Elasticsearch"
author: David Pilato
avatar: /about/david_pilato.webp
tags:
  - elasticsearch
  - java
categories:
  - tutorial
series:
  - Découverte Elasticsearch
date: 2011-06-20 20:34:49 +00:00
nolastmod: true
draft: false
aliases:
  - /blog/2011/06/20/elasticsearch-et-les-facets/
  - /blog/2011-06-20-elasticsearch-et-les-facets/
---

Les aventures avec Elasticsearch [se poursuivent]({{< ref "2011-03-09-la-recherche-elastique" >}}).

Combien de fois ai-je dit récemment que ce projet est absolument génial et qu'il va constituer à mon sens un des projets majeurs des prochaines années...

Qui n'a pas besoin de moteur de recherche ? Qui s'est déjà "emmerdé" à fabriquer ça lui-même ou à utiliser des briques pouvant aider au prix d'une complexité plus ou moins grande de mise en oeuvre ?

Je crois que nous sommes tous passés par là !!!

Et là, ce projet permet en quelques heures (minutes) de faire tourner un moteur de recherche complet...

<!--more-->

## Les facettes (facets)

Bref, là n'est pas mon propos d'aujourd'hui. Le thème du jour est la notion de facets. Je l'ai testé en quelques minutes sur une base de 1,5 millions de documents indexés à mon boulot. Résultat bluffant !

Une facette permet d'ajouter des informations à un résultat de recherche. Imaginez un site marchand. Vous cherchez un ou plusieurs mots, par exemple : rasoir.

Le site vous fournit une liste des éléments correspondants et en général ajoute des informations pour vous aider à affiner votre recherche.

Par exemple, le nom des fabricants de ces produits avec le nombre d'objets trouvés pour les 10 principaux fabricants. Dans notre cas, on pourrait avoir par exemple :

* Tous (134)
* Philips (35)
* Braun (21)
* Calor (12)

Ce résultat qui décore notre résultat de recherche se nomme une facette (facet in english).

Il existe différents types de facettes. Celle dont nous venons de parler est une facette de type TERMS, c'est à dire qu'Elastic Search va renvoyer la distribution des 10 principaux termes trouvés pour une propriété donnée des documents par rapport à une requête.

```js
{
  "query" : {
    "match_all" : { }
  },
  "facets" : {
    "tag" : {
      "terms" : {
        "field" : "tag",
        "size" : 10
      }
    }
  }
}
```

En passant une requête de ce type, on obtiendra la consolidation et le comptage associé de tous les principaux termes du champ tag de toute notre base de documents.

Il existe d'autres types de facettes très intéressantes :

* les facettes [RANGE](https://www.elastic.co/guide/en/elasticsearch/reference/0.90/search-facets-range-facet.html) : pour donner une distribution sur un intervale de valeurs. Par exemple, pour reprendre notre exemple de site marchand, vous pouvez utiliser la facette RANGE pour donner la distribution des prix pour les intervales de 0 à 10 €, de 10 à 20 €, de 20 à 50 € et au delà de 50 €.

* les facettes [DATE HISTOGRAM](https://www.elastic.co/guide/en/elasticsearch/reference/0.90/search-facets-date-histogram-facet.html) : pour donner un comptage avec un axe X des temps (période à décider : jour, mois, année, ...). Par exemple, le nombre de vente par mois pour un produit donné.

La liste complète est disponible sur le site [d'elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/0.90/search-facets.html).

## Et les résultats ?

Là où cela devient très fort, c'est que cette recherche s'exécute en temps réel, même sur des données "neuves" qui arrivent en permanence et avec un temps de réponse assez incroyable.

A titre d'exemple, sur la base de 1,5 millions de documents que je citais plus haut en début de document, j'ai pu ainsi faire un outil d'analyse rapidement (à peine 4 heures de boulot - et encore, c'est juste parce que je ne suis pas assez bon en Javascript !) sur des déclarations en douane. Ce qui est surprenant, c'est que sans avoir fait le moindre effort d'optimisation, nous avons pu regarder l'effet des saisons sur l'importation de tomates au fur et à mesure des années et sur les TOP 10 des pays d'importation !

Pour réaliser cela, je n'ai fait que suivre l'excellent article sur le blog d'[elasticsearch](https://www.elastic.co/blog/data-visualization-with-elasticsearch-and-protovis/). Je ne peux pas malheureusement pas vous montrer le résultat :-( Mais sachez que cela réagit en quelques secondes sur un poste bureautique avec peu de mémoire. Alors, imaginez si vous mettez cela en production avec 16 ou 32 Go de RAM distribué sur plusieurs noeuds !!!

Vous pouvez également utiliser le résultat des facettes comme point d'entrée ergonomique pour filtrer ensuite le résultat de vos recherches : un clic sur le nom du fabriquant du produit fera par exemple la même recherche dans Elastic Search avec en plus un filtre posé sur le nom du fabriquant.

## Quelle(s) conclusion(s) en tirer ?

Bon, j'ai un peu bluffé dans mon premier exemple... La possibilité d'avoir la somme totale de tous les résultats ( Tous (134) ) n'existe pas encore. Shay Banon, l'auteur du projet, a accepté ma [demande d'évolution #1029](https://github.com/elastic/elasticsearch/issues/1029) à ce sujet. Pour le moment, il faut faire un calcul à la main (enfin, en javascript je veux dire) !

Dans la même requête, vous pouvez associer plusieurs facettes d'un seul coup. Dans mon cas de démo au boulot, j'ai mis 5 facettes. Un appel = les 10 premiers résultats de ma recherche plus 5 facettes d'analyse des données...

Sinon, oubliez les requêtes SQL que vous faites tourner pendant quelques minutes pour vous fabriquer vos statistiques. Oubliez les moteurs de recherche en SQL (si ! si ! ça existe encore !). Je me demande du coup quel sera le devenir de projets comme Hibernate Search ? Même si avec la sortie d'Hibernate OGM, on sent une tentative astucieuse de garder la communauté des développeurs Hibernate.

Pour ma part, j'avais commencé à écrire un plugin Hibernate pour elasticsearch mais finalement je l'ai supprimé de mon projet car il n'apporte quasiment que des contraintes pour le peu d'intérêt qu'il apporte. Une vraie novation pourrait être d'ajouter à Hibernate Search un stockage des données dans elasticsearch, mais Shay Banon a un point de vue divergent sur les annotations utilisées. Du coup, un projet (OSEM) soutenu par Shay a vu le jour grâce à l'excellent travail d'[Aloïs Cochard](https://github.com/aloiscochard/elasticsearch-osem). Une fois stabilisé, ce projet rejoindra le projet elasticsearch afin de proposer des annotations standards pour vos objets Java à rendre cherchables (Searchable).

De mon côté, je réfléchis au développement d'un simple plugin maven pour générer automatiquement les fichiers de mapping pour elasticsearch basés sur les entités annotées [Searchable](https://github.com/aloiscochard/elasticsearch-osem/blob/master/src/main/java/org/elasticsearch/osem/annotations/Searchable.java). A suivre donc !

Installez chez vous elasticsearch et testez juste en ligne de commande (avec des curl) ces fonctionnalités et dites vous que le petit résultat que vous observez sur quelques documents tient autant la route sur une forte volumétrie... C'est la puissance de Lucene associée à l'ingéniosité de l'auteur d'elasticsearch qui met ainsi à notre disposition un outil simple, basé sur des technos simples mais au combien efficace !!!

Je vous ai dit que j'adore ce projet ???? 😉

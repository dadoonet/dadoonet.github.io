---
title: 'Il était une fois : un conte de fées élastique !'
description: "Il y a 2 ans, je cherchais un moyen pour distribuer Hibernate search sur plusieurs noeuds. Ma première idée était de stocker les index dans une base de données partagée par les différents noeuds. Oui ! Il s'agit d'une idée stupide en terme de performances, mais j'avais envie
d'essayer et de construire ce modèle.

Après avoir cherché du code source, je suis finalement tombé sur la classe JdbcDirectory du projet Compass. Et sur la page d'accueil du projet, j'aperçois quelque chose qui parle du future de Compass et d'Elasticsearch."
author: David Pilato
avatar: /about/david_pilato.avif
tags:
  - career
  - culture
  - travels
categories:
  - culture
series:
  - career at elastic
date: 2013-01-15 19:00:13 +02:00
nolastmod: true
cover: es1.avif
draft: false
aliases:
  - /blog/2013/01/15/il-etait-une-fois-un-conte-de-fees-elastique/
  - /blog/2013-01-15-il-etait-une-fois-un-conte-de-fees-elastique/
---

> Il était une fois...

En fait, il y a 2 ans, je cherchais un moyen pour distribuer Hibernate search sur plusieurs noeuds. Ma première idée était de stocker les index dans une base de données partagée par les différents noeuds. Oui ! Il s'agit d'une idée stupide en terme de performances, mais j'avais envie d'essayer et de construire ce modèle.

Après avoir cherché du code source, je suis finalement tombé sur la classe `JdbcDirectory` du projet Compass. Et sur la page d'accueil du projet, j'aperçois quelque chose qui parle du future de Compass et d'Elasticsearch.

{{< figure src="es1.avif" caption="Le futur de Compass et Elasticsearch" >}}

<!--more-->

Deux clics plus tard, je découvre Elasticsearch. Je le télécharge, le démarre et me dis : "Bordel ! Mais comment est-ce possible ?". Ce projet venait non seulement de résoudre tous mes problèmes en ajoutant des fonctionnalités dont je n'avais même pas conscience, le tout en moins de 30 secondes ! Je n'ai pas dormi pendant une semaine entière, vraiment ! C'était trop magique pour être vrai ! Après quelques heures de travail, Elasticsearch était intégré dans mon projet et fournissait déjà les premières recherches full text. J'ai dit à mes collègues que ce projet est si magnifique que je veux en faire parti si un jour une société est créée.

A partir de ce moment, j'ai cherché comment contribuer en retour sur le projet. Mais, je n'étais ni un expert Elasticsearch, ni même un expert Lucene. J'ai alors cherché du contenu français parlant du projet et je n'ai trouvé qu'un ou deux articles. J'ai commencé alors à écrire du contenu sur [mon blog personnel]({{< ref "2011-03-09-la-recherche-elastique" >}}). J'ai également commencé à écrire quelques plugins. La [rivière RSS](https://david.pilato.fr/rssriver/) fut la première. Elle fut d'ailleurs mon premier projet open-source.

J'ai rencontré Shay Banon la première fois en Juin 2011 pour une conférence donnée à Paris. Il donnait un talk sans slides comme il sait les faire. Très impressionnant ! It just works ! Je lui ai alors dit que comme je ne pouvais pas directement contribuer au coeur du projet, je pouvais essayer de promouvoir le projet en France. Il a immédiatement accepté. La communauté française était née !

{{< figure src="es2.avif" caption="Communauté française Elasticsearch" >}}

Une année plus tard, [mon talk pour Devoxx France](https://www.devoxx.com/display/FR12/ElasticSearch+++moteur+de+recherche+NoSQL+REST+JSON+taille+pour+le+cloud) était accepté et tout allait vraiment démarrer à partir de là. Le groupe français n'a pas cessé de grossir depuis, de jour en jour.

Quelques mois plus tard, la société Elasticsearch BV était créée. Il était vraiment clair dans mon esprit que je devais les rejoindre. Quand vous tombez amoureux, vous devez vous marier ! J'ai rencontré à nouveau Shay à Devoxx 2012 et nous en avons parlé, notamment de ce que je pourrais apporter à Elasticsearch. Et maintenant, deux ans après ma première rencontre avec Elasticsearch, mon rêve devient réalité, comme dans les contes de fées !

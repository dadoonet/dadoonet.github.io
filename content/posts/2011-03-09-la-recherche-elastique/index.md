---
title: La recherche élastique...
description: "Elasticsearch, un projet mature en quelques mois... A suivre de très près !"
author: David Pilato
avatar: /about/david_pilato.avif
tags:
  - elasticsearch
  - hibernate
  - java
categories:
  - tutorial
series:
  - Découverte Elasticsearch
date: 2011-03-09 21:30:32 +00:00
nolastmod: true
draft: false
aliases:
  - /blog/2011/03/09/la-recherche-elastique/
  - /blog/2011-03-09-la-recherche-elastique/
---

Elasticsearch, un projet mature en quelques mois... A suivre de très près !

<!--more-->

En cherchant un bout de code pour rendre la couche [Hibernate Search](https://docs.hibernate.org/search/3.4/reference/en-US/html/search-configuration.html#jms-backend) facilement distribuable sur un cluster de machines JBoss, je suis tombé sur le projet [Elasticsearch](https://www.elastic.co).

Au début, un peu interloqué... Puis, je me lance...

Je télécharge le projet. Je dézippe.

Je lance...

Miracle. En quelques secondes, je dispose d'un outil dans un Cloud, simple, me permettant d'indexer n'importe quel type de document, de le récupérer et de faire une recherche (au sens google du terme) sur n'importe quel champ... Et cela, quelque soit la technologie employée (Java, C#, .Net, Php, à la main, ...).

La simplicité repose sur l'intégration de quelques technologies simples et éprouvées : JSon, REST, Lucene.

Là, où cela devient très fort, c'est lorsque vous démarrez sur une seconde machine dans le même réseau, une autre instance d'Elasticsearch... Et là : réplication automatique. Votre nouvelle instance fait parti du Cloud...

Sans rien faire... Presque magique.

Lorsque vous montez encore 2 autres instances (ça peut être sur la même machine - les ports d'écoute s'adaptent automatiquement), alors Elasticsearch réparti l'indexation sur plusieurs machines...

La Team est très active. Il suffit de regarder [la fréquence des commits](https://github.com/elasticsearch/elasticsearch) sur github. Elle fournit un composant Java simple à utiliser.

En deux lignes, on se connecte au cloud (sans trop savoir à quelle machine exactement, le principal étant de trouver un service), et on envoie nos demandes d'indexation ou de recherche...

Je vous recommande fortement de regarder de très près ce projet qui va rapidement s'imposer comme une référence.

Pour ma part, je travaille en ce moment à développer une méthode très simple pour interfacer automatiquement et de façon transparente l'indexation des entités gérées par Hibernate. L'idée est de pousser les entités Hibernate à chaque fois qu'elles sont insérées, mises à jour ou effacées vers Elasticsearch plutôt que vers Hibernate Search. Le tout avec très peu d'annotations.

Plus d'informations dans quelques jours je pense...

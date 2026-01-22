---
title: CouchDB
description: "Après avoir testé Elasticsearch, me voici parti pour regarder ce monde étrange qu'on appelle le NoSQL... Découvrons aujourd'hui CouchDB."
author: David Pilato
avatar: /about/david_pilato.png
tags:
  - couchdb
  - elasticsearch
categories:
  - tutorial
series:
  - Découverte Elasticsearch
date: 2011-05-13 21:08:22 +00:00
nolastmod: true
cover: featured.svg
draft: false
aliases:
  - /blog/2011/05/13/couchdb/
  - /blog/2011-05-13-couchdb/
---

Après avoir testé [Elasticsearch]({{< ref "2011-03-09-la-recherche-elastique" >}}), me voici parti pour regarder ce monde étrange qu'on appelle le [NoSQL](https://fr.wikipedia.org/wiki/Nosql)...

<!--more-->

A dire vrai, j'ai entendu ce mot il y a quelques années, sans jamais vraiment m'y interesser... Après tout, une base de données non SQL, ça n'est tout simplement pas possible !!!

Puis, à force de cotoyer le monde d'Elasticsearch et les technos JSon et REST, je me lance.

Pour des raisons très pratiques, je choisis [CouchDB](https://couchdb.apache.org/) de Apache. D'une part, il est directement intégrable avec Elasticsearch, et à la lecture rapide de sa [documentation](https://guide.couchdb.org/editions/1/fr/index.html), il semble répondre à un des besoins auquel une équipe de mon pôle de développement est confrontée.

## Notre besoin (résumé)

* Archiver des données de notre SI afin notamment de décharger les bases live (Front Office).
* Historiser ces données
* Y associer des pièces jointes (vues PDF et XML)
* Etre en mesure d'y accéder facilement
* Prévenir des consommateurs de ces documents qu'il y a des nouveautés à récupérer et à traiter (Décisionnel)
* Etre en mesure de rechercher ces document
* ...

Au début, les équipes ont pensé mettre en place des copies via des fichiers XML dans des répertoires partagés depuis les applications Front Office (live), puis des scripts shell pour recopie dans des espaces propres à chaque consommateur de données qui traitera ensuite les flux à son rythme. Sans entrer dans les détails, c'est un peu genre "je fais tout moi-même à la main, comme je l'aurais fait en 1995"...

Depuis le monde a un peu changé, non ?

## Alors, que peut faire CouchDB pour nous?

* Stocker des documents (format JSON)
* Y associer des pièces jointes (PDF et XML)
* Le tout avec un mode de transport simple : HTTP / REST
* Gestion d'un flux type RSS pour informer n'importe qui de toutes les modifications apportées à la base
* Gestion des révisions de chaque document
* Non adhérence à un format particulier (contrairement aux SGBD-R)
* Capacité de stockage et de montée en charge
* Réplication ultra simple
* Partitionnement
* ...

Bon, ça c'est sur le papier... Rien ne vaut un bon test...

On se lance donc avec un ami pour mettre en place une plate-forme de test.

Nous partons d'une base de données disposant de plusieurs millions d'enregistrements divers (sous Oracle). Notre objectif :

* Les lire avec un DAO classique dans Oracle
* JSONiser chaque entité
* La transformer aussi en une vue XML (module déjà existant)
* La transformer aussi en une vue PDF (nous avons déjà développé tout cela avant)
* Envoyer le tout à CouchDB.

Il faut 5 minutes pour installer CouchDB (grand max !), 20 minutes pour comprendre que le firewall de Microsoft n'est pas notre ami et que nous avons intérêt à ouvrir le port CouchDB si nous voulons pouvoir communiquer avec CouchDB depuis une autre machine !

On lance le batch sur une machine et on envoie vers un CouchDB... Là, tranquille, au rythme de 15-20 documents par seconde, notre base se remplit petit à petit !

On consulte un document JSON ainsi : <http://couchdb/index/ref000000001/>

Si on veut prendre la version PDF, c'est beaucoup plus compliqué : <http://couchdb/index/ref000000001/ref000000001.pdf>

Je passe la version XML... C'est aussi compliqué !

Au bout de 50 000 documents, nous nous lançons un nouveau défi : répliquer sur une autre instance CouchDB.

Installation de CouchDB sur une autre machine. Cette fois, on ne perd pas de temps pour le firewall : on sait directement où enlever le blocage...

Puis on se connecte sur l['interface de gestion de CouchDB](http://127.0.0.1:5984/_utils/) et on demande une réplication de la première machine vers la deuxième... Il faut 10 secondes pour configurer cela. C'est vraiment trop simple pour fonctionner directement ! Mais, si ! Ca fonctionne !

La réplication commence... 20 à 50 documents répliqués par seconde... Le tout sur un PC assez lent. On est loin des conditions de PROD !

En même temps, notre BATCH continue à alimenter la première instance.

Arrivés à 100 000 documents, nous n'en n'avons pas assez !!!

Nous décidons de nous lancer un nouveau défi. Il nous reste 10 minutes avant une réunion de présentation de ces concepts à notre management. Nous avons largement le temps !

Alors, nous décidons de lancer un noeud Elasticsearch sur une machine et d'y ajouter le [plugin river CouchDB](https://github.com/elastic/elasticsearch-river-couchdb/). Puis nous activons ce plugin pour ouvrir une rivière (river) vers la première instance de CouchDB... Et là, encore un miracle... Nos documents se déversent sans aucun effort dans Elasticsearch.

Nous avons donc au final, au bout d'une demi journée d'efforts surhumains (fallait quand même développer le batch initial), atteint nos objectifs.

Reste à regarder cette histoire de flux RSS (sorte d'inscription aux nouveautés de la base). Cela est nativement porté par la fonction [_changes](https://guide.couchdb.org/editions/1/fr/notifications.html) de CouchDB. C'est absolument génial. Comme si vous aviez un trigger permanent et automatique sur chaque modification apportée dans la base. Avec la possibilité de faire un appel à _changes en précisant là où nous en étions la dernière fois que nous y avons fait appel ([gestion différentielle](https://guide.couchdb.org/editions/1/fr/notifications.html#polling)), ou encore mieux, [de façon continue](https://guide.couchdb.org/editions/1/fr/notifications.html#continuous), de laisser en permanence un flux HTTP ouvert dans lequel se déverse au fil de l'eau chaque changement apporté...

C'est vraiment bluffant et simplissime à l'usage.

C'en est tellement facile que cela paraît suspect...

Les prochains tests sont maintenant de faire monter la volumétrie à quelques millions de données pour voir comment cela se passe...

La suite au prochain numéro !

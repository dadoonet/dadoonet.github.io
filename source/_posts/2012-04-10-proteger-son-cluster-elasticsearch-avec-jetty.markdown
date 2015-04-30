---
author: dadoonet
comments: true
date: 2012-04-10 20:29:29+00:00
layout: post
slug: proteger-son-cluster-elasticsearch-avec-jetty
title: Protéger son cluster Elasticsearch avec Jetty
wordpress_id: 241
categories:
- Elasticsearch
tags:
- elasticsearch
- Jetty
---

Nativement, Elasticsearch expose l'ensemble de ses services sans aucune authentification et donc une commande du type curl -XDELETE http://localhost:9200/myindex peut faire de nombreux dégâts non désirés.

De plus, si vous développez une application JQuery avec un accès direct depuis le poste client à votre cluster Elasticsearch, le risque qu'un utilisateur joue un peu avec votre cluster est grand !

Alors, pas de panique... La société Sonian Inc. a open sourcé son [plugin Jetty pour Elasticsearch](https://github.com/sonian/elasticsearch-jetty) pour notre plus grand bonheur ;-)


# Principe


Le principe consiste à rajouter une surcouche Jetty à Elasticsearch, sous forme de plugin.

Il ne reste plus qu'à restreindre certaines URL et certaines méthodes (DELETE par exemple) à certains utilisateurs.


# Guide d'installation


Pour installer le plugin, connectez vous à votre serveur hébergeant Elasticsearch et allez dans le répertoire d'installation :

[gist id="0aca4f40e8c8d2178964" file="script1.sh"]

Installez le plugin (vérifiez la compatibilité entre la version du plugin et celle de votre noeud) :

[gist id="0aca4f40e8c8d2178964" file="script2.sh"]


Récupérez le fichier de configuration de jetty proposé par Sonian en exemple :




[gist id="0aca4f40e8c8d2178964" file="script3.sh"]







Idem pour le fichier avec les logins / password :


[gist id="0aca4f40e8c8d2178964" file="script4.sh"]

Il faut ensuite modifier la configuration Elasticsearch et ajouter la ligne suivante dans config/elasticsearch.yml :

[gist id="0aca4f40e8c8d2178964" file="elasticsearch.yml"]

[gist id="0aca4f40e8c8d2178964" file="script5.sh"]

Les petits gars de Sonian ayant très bien fait leur boulot, les protections nécessaires sont déjà en place avec le fichier config/jetty.xml très complet.

Modifiez les valeurs par défaut de login/password dans config/realm.properties :

[gist id="0aca4f40e8c8d2178964" file="realm.properties"]

Redémarrez Elasticsearch. Si vous l'avez installé en tant que service :

[gist id="0aca4f40e8c8d2178964" file="script6.sh"]

Et voilà ! Impossible de faire des commandes du type :

[gist id="0aca4f40e8c8d2178964" file="script7.sh"]

Mais avec authentification, ça passe :

[gist id="0aca4f40e8c8d2178964" file="script8.sh"]

---
title: Protéger son cluster Elasticsearch avec Jetty
description: "Nativement, Elasticsearch expose l'ensemble de ses services
  sans aucune authentification et donc une commande du type curl -XDELETE
  http://localhost:9200/myindex peut faire de nombreux dégâts non désirés."
author: David Pilato
avatar: /about/david_pilato.png
tags:
  - elasticsearch
  - jetty
categories:
  - tutorial
date: 2012-04-10 20:29:29 +00:00
nolastmod: true
draft: false
aliases:
  - /blog/2012/04/10/proteger-son-cluster-elasticsearch-avec-jetty/
  - /blog/2012-04-10-proteger-son-cluster-elasticsearch-avec-jetty/
---

Nativement, Elasticsearch expose l'ensemble de ses services sans aucune authentification et donc une commande du type `curl -XDELETE http://localhost:9200/myindex` peut faire de nombreux dégâts non désirés.

De plus, si vous développez une application JQuery avec un accès direct depuis le poste client à votre cluster Elasticsearch, le risque qu'un utilisateur joue un peu avec votre cluster est grand !

Alors, pas de panique... La société Sonian Inc. a open sourcé son [plugin Jetty pour Elasticsearch](https://github.com/sonian/elasticsearch-jetty) pour notre plus grand bonheur 😉

<!--more-->

## Principe

Le principe consiste à rajouter une surcouche Jetty à Elasticsearch, sous forme de plugin.

Il ne reste plus qu'à restreindre certaines URL et certaines méthodes (`DELETE` par exemple) à certains utilisateurs.

## Guide d'installation

Pour installer le plugin, connectez vous à votre serveur hébergeant Elasticsearch et allez dans le répertoire d'installation :

```sh
cd /usr/local/elasticsearch/elasticsearch-0.19.2/
```

Installez le plugin (vérifiez la compatibilité entre la version du plugin et celle de votre noeud) :

```sh
sudo bin/plugin -install sonian/elasticsearch-jetty/0.19.2
```

```txt
- Installing sonian/elasticsearch-jetty/0.19.2...
Trying https://github.com/downloads/sonian/elasticsearch-jetty/elasticsearch-jetty-0.19.2.zip...
Downloading .......................................................................................................................................................................DONE
Installed jetty
```

Récupérez le fichier de configuration de jetty proposé par Sonian en exemple :

```sh
sudo curl https://raw.github.com/sonian/elasticsearch-jetty/master/config/jetty.xml -o config/jetty.xml
```

Idem pour le fichier avec les logins / password :

```sh
sudo curl https://raw.github.com/sonian/elasticsearch-jetty/master/config/realm.properties -o config/realm.properties
```

Il faut ensuite modifier la configuration Elasticsearch et ajouter la ligne suivante dans `config/elasticsearch.yml` :

```sh
sudo vi config/elasticsearch.yml
```

```yaml
# Jetty Plugin
http.type: com.sonian.elasticsearch.http.jetty.JettyHttpServerTransportModule
```

Les petits gars de Sonian ayant très bien fait leur boulot, les protections nécessaires sont déjà en place avec le fichier `config/jetty.xml` très complet.

Modifiez les valeurs par défaut de login/password dans `config/realm.properties` :

```properties
superuser: YOURSUPERUSERPASSWORD,admin,readwrite
user: USERPASSWORD,readwrite
```

Redémarrez Elasticsearch. Si vous l'avez installé en tant que service :

```sh
sudo service elasticsearch restart
```

Et voilà ! Impossible de faire des commandes du type :

```sh
curl http://localhost:9200/_refresh
# 401 Unauthorized
```

Mais avec authentification, ça passe :

```sh
curl -u user:USERPASSWORD http://localhost:9200/_refresh
# {"ok":true,"_shards":{"total":23,"successful":23,"failed":0}}
```

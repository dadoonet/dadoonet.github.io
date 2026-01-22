---
title: La mise en place d'une forge
description: "Description de la mise en place de la forge GForge pour les besoins de mon centre informatique."
author: David Pilato
avatar: /about/david_pilato.png
tags:
  - fusionforge
  - gforge
categories:
  - tutorial
series:
  - FusionForge
date: 2010-01-26 22:13:47 +00:00
nolastmod: true
draft: false
aliases:
  - /blog/2010/01/26/la-mise-en-place-dune-forge/
  - /blog/2010-01-26-la-mise-en-place-dune-forge/
---

Description de la mise en place de la forge GForge pour les besoins de mon centre informatique.

<!--more-->

Pour les besoins internes de la douane, j'ai proposé la mise en place d'une forge afin de consolider nos moyens de développement et de gestion de projets.

Histoire d'être cohérent avec d'autres choix faits par l'administration, [projet Adullact](https://adullact.net/), j'ai retenu la forge [GFORGE](https://gforge.com/).

Je vais décrire ici le processus d'installation que je vais suivre afin de partager cette information avec d'autres personnes qui pourraient être intéressés par cette démarche.

## Installation de la Forge sur Ubuntu 9.10

Tout d'abord, il faut télécharger les [sources de la forge](https://gforge.com/downloads/). Je me suis basé sur la dernière version connue à ce moment : [5.7b2 Community Edition](https://gforge.com/legacy-downloads/).

### Correction du problème avec Postgresql

La version de postgres téléchargée par Ubuntu ne correspond pas à la version attendue dans le script d'installation **install-gforge-2-db.php**.

Pour corriger ce problème, j'ai remplacé partout (sauf à la fin) la version 8.3 par 8.4.

Par exemple la ligne

```sh
'/etc/init.d/postgresql-8.3',
```

est devenue

```sh
'/etc/init.d/postgresql-8.4',
```

### Correction du problème avec la distribution Apache pour Ubuntu (Rewrite)

La gestion de la configuration Apache n'est pas "standard" sur Ubuntu. J'ai donc suivi les recommandations du [blog de Josh Street](https://josh.st/2005/03/06/ubuntu-apache-and-making-mod_rewrite-happy/) pour corriger le problème.

```sh
cd /etc/apache2/mods-enabled
sudo ln -s ../mods-available/rewrite.load rewrite.load
sudo service apache2 start
```

Finalement, Adullact a annoncé vouloir passer sous [FusionForge](http://fusionforge.org/) qui est un fork de GForge afin de conserver la forge dans le monde open-source. La team FusionForge travaille en ce moment sur la version 5.0 mais elle n'est pas encore stabilisée. Nous allons donc installer la [version 4.8.3](http://fusionforge.org/frs/?group_id=6).

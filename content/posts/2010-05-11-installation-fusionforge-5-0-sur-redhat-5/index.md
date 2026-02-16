---
title: Installation FusionForge 5.0 sur Redhat 5
description: "Voici la suite de l'article sur l'installation d'une forge. Finalement, le temps d'obtenir une machine sous Redhat 5 a laissé le temps à la team FusionForge de sortir une release finale de la version 5.0."
author: David Pilato
avatar: /about/david_pilato.webp
tags:
  - fusionforge
categories:
  - tutorial
series:
  - FusionForge
date: 2010-05-11 22:23:27 +00:00
nolastmod: true
draft: false
cover: maforge.webp
aliases:
  - /blog/2010/05/11/installation-fusionforge-5-0-sur-redhat-5/
  - /blog/2010-05-11-installation-fusionforge-5-0-sur-redhat-5/
---

Voici la suite de l'article sur l'[installation d'une forge]({{< ref "2010-01-26-la-mise-en-place-dune-forge" >}}).

Finalement, le temps d'obtenir une machine sous Redhat 5 a laissé le temps à la team FusionForge de sortir une release finale de la version 5.0.

Nous voilà donc lancés dans cette installation que je me propose de décrire ici.

<!--more-->

> [!NOTE]
> Pour le moment la forge n'est pas totalement opérationnelle. Des évolutions dans la configuration devront être menées et j'espère pouvoir tenir à jour cet article pour les décrire.

## Préinstallation

### Création du sous-domaine

Il faut choisir un nom « agréable » pour la machine et le déclarer dans le DNS. Dans le reste du document, on considère qu'on installe la forme sous le nom `maforge.mondomaine`.

### Espace disque

Il est recommandé également de prévoir un espace disque suffisant pour la forge en montant par exemple un disque sur une baie SAN. Dans le reste du document, on considère que le répertoire disponible est `/maforge`.

### Configuration YUM pour internet

Les scripts d'installation nécessitent d'avoir un accès à internet pour télécharger à l'aide de yum les modules nécessaires pouvant manquer dans l'installation par défaut de la machine. Pour cela, si il est nécessaire de passer par un proxy, le déclarer dans yum.conf sous la forme d'une ligne :

```conf
proxy=http://adresseipproxy:port/
```

### Téléchargement de la distribution fusionforge

Les packages à télécharger pour installer la forge sont disponibles à l'adresse : <https://fr.wikipedia.org/wiki/FusionForge>.

> [!NOTE]
> Le document présent est basé sur la version 5.0 de la forge. Il est conseillé de prendre la version notée « allinone ».
>
> Dans la suite, on considère qu'on a téléchargé le fichier : `fusionforge-5.0-allinone.tar.bz2`

## Processus  d'installation

Une fois le fichier d'installation téléchargé, le déposer dans un répertoire temporaire de la machine, par exemple : `/tmp`

Puis en tant qu'utilisateur root :

```sh
cd /tmp
bunzip2 fusionforge-5.0-allinone.tar.bz2
tar xf fusionforge-5.0-allinone.tar
```

On doit se retrouver avec un répertoire /tmp/fusionforge-5.0

```sh
cd /tmp/fusionforge-5.0
install.sh maforge.modomaine
```

Ce script exécute l'installation de la forge :

* Téléchargement des dépendances (via le script `fusionforge-install-1-deps.php`)
* Installation des scripts de la forge, des répertoires, ... (via le script `fusionforge-install-2.php`)
* Création de la base de données (`fusionforge-install-3-db.php`)

Lors de l'installation, le script demande d'entrer le nom de l'utilisateur administrateur de la forge et son mot de passe.

> [!NOTE]
> Lors de l'installation, le script semble ne pas avoir complètement fonctionné correctement. Des analyses sont en cours.
>
> De ce fait, un démarrage manuel de la base postgres a dû être effectué à l'aide la commande suivante :
>
> ```sh
> /etc/rc.d/init.d/postgresql start
> ```

Une fois ces opérations menées, il doit être possible d'ouvrir un navigateur web à l'adresse : <http://maforge.mondomaine/>

{{< figure src="maforge.webp" caption="Page d'accueil de la forge" >}}

## Processus post-installation

### Déplacement des fichiers sur la baie SAN

La forge s'installe dans ses répertoires par défaut. En attendant que la communauté de développeur de la forge rende paramétrable les répertoires, un certain nombre d'action sont nécessaires pour déplacer les répertoires d'installation vers un disque adéquat (sur la baie SAN par exemple).

Pour faire ces déplacements, il est nécessaire de stopper la base de données :

```sh
/etc/rc.d/init.d/postgresql stop
```

Le tableau ci-dessous donne les répertoires par défaut d'installation de la forge et les répertoires cibles vers lesquels on souhaite se déplacer.

|Répertoire origine |Répertoire destination      |Commentaire                             |
|-------------------|----------------------------|----------------------------------------|
|`/opt/gforge`      |`/maforge/fforge50`         |Contient les sources, les scripts php, bref, tout le "programme" forge |
|`/var/lib/gforge`  |`/maforge/files`            |Contient les répertoires de travail (`svn`, `uploads`, ...) |
|`/var/lib/pgsql`   |`/maforge/pgsql`            |Contient la base de données             |
|`/etc/gforge`      |`/maforge/conf`             |Contient la configuration (forge, apache, plugins) |
|`/opt/groups`      |`/maforge/groups`           |???                                     |

Pour déplacer les fichiers, faire :

```sh
mkdir /maforge/conf
mv /etc/gforge/* /maforge/conf/
rmdir /etc/gforge
ln -s /maforge/conf/ /etc/gforge

mkdir /maforge/pgsql
mv /var/lib/pgsql/* /maforge/pgsql/
mv /var/lib/pgsql/.bash_profile /maforge/pgsql/
rmdir /var/lib/pgsql
ln -s /maforge/pgsql/ /var/lib/pgsql

mkdir /maforge/files
mv /var/lib/gforge/* /maforge/files/
rmdir /var/lib/gforge
ln -s /maforge/files/ /var/lib/gforge

mkdir /maforge/fforge50
mv /opt/gforge/* /maforge/fforge50/
rmdir /opt/gforge
ln -s /maforge/fforge50/ /opt/gforge

mkdir /maforge/groups
mv /opt/groups/* /maforge/groups/
rmdir /opt/groups
ln -s /maforge/groups/ /opt/groups
```

Puis redémarrer postgres :

```sh
/etc/rc.d/init.d/postgresql start
```

### Patch sur les répertoires SVN et CVS

L'installation de la forge semble poser des problèmes sur Redhat 5 et CentOS 5 car des répertoires attendus par la forge ne sont pas créés. Il faut donc, créer des liens symboliques pour corriger ce problème :

```sh
ln -s /maforge/files/svnroot /maforge/files/svn
ln -s /maforge/files/cvsroot /maforge/files/cvs
ln -s /maforge/files /scmrepos
ln -s /maforge/files/svnroot /svnroot
ln -s /maforge/files/cvsroot /cvsroot
```

### Installation BIND et configuration DNS (PROVISOIRE/EN COURS)

La forge doit gérer elle-même ses DNS afin de pouvoir déclarer chaque nouveau projet dans son espace propre (par exemple `nomprojet.maforge.mondomaine`).

Pour cela, une délégation de DNS doit être réalisée par le DNS principal du domaine `mondomaine` pour laisser le service BIND de la forge gérer le sous-domaine `maforge.mondomaine`.

Il faut donc également installer le service BIND sur la forge et le configurer.

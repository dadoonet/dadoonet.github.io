---
comments: true
date: 2010-05-11 22:23:27+00:00
layout: post
title: Installation FusionForge 5.0 sur Redhat 5
categories:
- forge
- FusionForge
---

Voici la suite de l'article sur l'[installation d'une forge](/?p=23).

Finalement, le temps d'obtenir une machine sous Redhat 5 a laissé le temps à la team FusionForge de sortir une release finale de la version 5.0.

Nous voilà donc lancés dans cette installation que je me propose de décrire ici.

A noter que pour le moment la forge n'est pas totalement opérationnelle. Des évolutions dans la configuration devront être menées et j'espère pouvoir tenir à jour cet article pour les décrire.


# Processus d'installation

## Préinstallation

### Création du sous-domaine

Il faut choisir un nom « agréable » pour la machine et le déclarer dans le DNS. Dans le reste du document, on considère qu'on installe la forme sous le nom **maforge.mondomaine**.

### Espace disque

Il est recommandé également de prévoir un espace disque suffisant pour la forge en montant par exemple un disque sur une baie SAN. Dans le reste du document, on considère que le répertoire disponible est **/maforge**.

### Configuration YUM pour internet

Les scripts d'installation nécessitent d'avoir un accès à internet pour télécharger à l'aide de yum les modules nécessaires pouvant manquer dans l'installation par défaut de la machine. Pour cela, si il est nécessaire de passer par un proxy, le déclarer dans yum.conf sous la forme d'une ligne :

```
proxy=http://adresseipproxy:port/
```

### Téléchargement de la distribution fusionforge

Les packages à télécharger pour installer la forge sont disponibles à l'adresse : http://fusionforge.org/frs/?group_id=6.

A noter que le document présent est basé sur la version 5.0 de la forge. Il est conseillé de prendre la version notée « allinone ».

Dans la suite, on considère qu'on a téléchargé le fichier : `fusionforge-5.0-allinone.tar.bz2`

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

**Note :**

Lors de l'installation, le script semble ne pas avoir complètement fonctionné correctement. Des analyses sont en cours.

De ce fait, un démarrage manuel de la base postgres a dû être effectué à l'aide la commande suivante.

```sh
/etc/rc.d/init.d/postgresql start
```

Une fois ces opérations menées, il doit être possible d'ouvrir un navigateur web à l'adresse : http://maforge.mondomaine/

[caption id="attachment_111" align="aligncenter" width="300" caption="Page d'accueil de la forge"][![](http://dev.david.pilato.fr/wp-content/uploads/2010/05/maforge-300x144.png)](http://dev.david.pilato.fr/wp-content/uploads/2010/05/maforge.png)[/caption]


## Processus post-installation

### Déplacement des fichiers sur la baie SAN

La forge s'installe dans ses répertoires par défaut. En attendant que la communauté de développeur de la forge rende paramétrable les répertoires, un certain nombre d'action sont nécessaires pour déplacer les répertoires d'installation vers un disque adéquat (sur la baie SAN par exemple).

Pour faire ces déplacements, il est nécessaire de stopper la base de données :

```sh
/etc/rc.d/init.d/postgresql stop
```

Le tableau ci-dessous donne les répertoires par défaut d'installation de la forge et les répertoires cibles vers lesquels on souhaite se déplacer.

<table >
<tbody >
<tr >
Répertoire origine
Répertoire destination
Commentaire
</tr>
<tr >

<td width="26%" >/opt/gforge
</td>

<td width="28%" >/maforge/fforge50
</td>

<td width="47%" >Contient les sources, les scripts php, bref, toute le « programme » forge
</td>
</tr>
<tr >

<td width="26%" >/var/lib/gforge
</td>

<td width="28%" >/maforge/files
</td>

<td width="47%" >Contient les répertoires de travail (svn, uploads, ...)
</td>
</tr>
<tr >

<td width="26%" >/var/lib/pgsql
</td>

<td width="28%" >/maforge/pgsql
</td>

<td width="47%" >Contient la base de données
</td>
</tr>
<tr >

<td width="26%" >/etc/gforge
</td>

<td width="28%" >/maforge/conf
</td>

<td width="47%" >Contient la configuration (forge, apache, plugins)
</td>
</tr>
<tr >

<td width="26%" >/opt/groups
</td>

<td width="28%" >/maforge/groups
</td>

<td width="47%" >???
</td>
</tr>
</tbody>
</table>

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


La forge doit gérer elle-même ses DNS afin de pouvoir déclarer chaque nouveau projet dans son espace propre (par exemple nomprojet.maforge.mondomaine).

Pour cela, une délégation de DNS doit être réalisée par le DNS principal du domaine mondomaine pour laisser le service BIND de la forge gérer le sous-domaine maforge.mondomaine.

Il faut donc également installer le service BIND sur la forge et le configurer.

**Note :** A compléter

Voir aussi : [https://fusionforge.org/docman/view.php/6/1/gforge_manual.plain.html#id2623367](https://fusionforge.org/docman/view.php/6/1/gforge_manual.plain.html#id2623367)

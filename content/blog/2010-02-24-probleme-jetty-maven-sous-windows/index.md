---
title: Problème Jetty / Maven sous Windows
#description: 
toc: true
authors:
  - David Pilato
tags:
  - java
  - jetty
  - maven
categories:
  - tips
date: 2010-02-24 20:14:51 +00:00
lastmod: 2010-02-24 20:14:51 +00:00
# featuredImage: blog/2010-05-11-installation-fusionforge-5-0-sur-redhat-5/maforge.png
draft: false
aliases:
  - /blog/2010/02/24/probleme-jetty-maven-sous-windows/
---

Lorsqu'on souhaite lancer une WebApp avec le plugin [Jetty](http://docs.codehaus.org/display/JETTY/Maven+Jetty+Plugin) sous Maven 2 depuis un PC sous windows on obtient une erreur référencée sous JIRA [#JETTY-1063](http://jira.codehaus.org/browse/JETTY-1063) :

```txt
java.net.URISyntaxException: Illegal character in path at index 18: file:/C:/Documents and Settings/USER/.m2/repository/org/mortbay/jetty/jetty-maven-plugin/7.0.0.1beta2/jetty-maven-plugin-7.0.0.1beta2.jar
```

<!-- more -->

Ce problème n’est résolu que sous [Maven 3](http://maven.apache.org/release-notes-3.0.x.html).

Pour ceux qui souhaitent rester sous Maven 2 (Maven 3 est encore en version alpha), il faut modifier l'emplacement de la repository pour éviter le souci du caractère ESPACE présent dans le chemin `C:\Documents and settings\USER\.m2\repository` (chemin par défaut).

Il est fortement recommandé de déplacer le répertoire repository dans `c:\maven2\repository`par exemple et modifier ensuite le fichier settings.xml qui se trouve normalement dans `C:\Documents and settings\USER\.m2` ou (moins bien) dans votre répertoire d’installation de maven sous `/conf`.

```xml
<localRepository>/c:/maven2/repository</localRepository>
```

Ainsi, Maven ira chercher les libs dans un répertoire sans espaces…

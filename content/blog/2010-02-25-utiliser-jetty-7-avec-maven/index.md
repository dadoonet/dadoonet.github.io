---
title: Utiliser Jetty 7 avec Maven
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
date: 2010-02-25 23:52:07 +00:00
# featuredImage: blog/2010-05-11-installation-fusionforge-5-0-sur-redhat-5/maforge.png
draft: false
aliases:
  - /blog/2010/02/25/utiliser-jetty-7-avec-maven/
---

Jetty peut être très utile aux projets Maven, notamment dans la phase de tests d'intégration.

Il faut souvent déployer l'application sur un serveur type JBoss puis lancer les tests. Avec Jetty, on dispose alors d'un conteneur léger qui permet de disposer des fonctionnalités essentielles d'un conteneur (webapp, datasource, ...).

<!-- more -->

Problème : avec la version 7 de Jetty, il faut gérer l'authentification. Sinon, on obtient une erreur du type :

```txt
java.lang.IllegalStateException: No LoginService for org.eclipse.jetty.security.authentication.BasicAuthenticator@4095c5ec in ConstraintSecurityHandler@28f52a14@
```

J'ai trouvé la solution à ce problème sur le blog de [Max Berger](http://blog.max.berger.name/2010/02/jetty-7-maven-plugin-authentication.html).

A SUIVRE

---
title: Publication de documentation fonctionnelle avec Maven
description: "Voici une astuce permettant de laisser les analystes ou concepteurs utiliser leurs logiciels habituels de documentation (oOo ou Word), tout en permettant de publier automatiquement avec la génération du site un document PDF lisible par tous."
author: David Pilato
avatar: /about/david_pilato.png
tags:
  - maven
  - documentation
categories:
  - tutorial
date: 2010-02-23 12:40:26 +00:00
nolastmod: true
draft: false
aliases:
  - /blog/2010/02/23/publication-de-documentation-fonctionnelle-avec-maven/
  - /blog/2010-02-23-publication-de-documentation-fonctionnelle-avec-maven/
---

Voici une astuce permettant de laisser les analystes ou concepteurs utiliser leurs logiciels habituels de documentation (oOo ou Word), tout en permettant de publier automatiquement avec la génération du site un document PDF lisible par tous.

<!--more-->

Lorsqu'on utilise Maven, se pose souvent la question de génération de documents à intégrer dans le site web généré par Maven.

Au début, j'ai regardé le [format APT](http://maven.apache.org/doxia/references/apt-format.html) qui a l'avantage certain de générer du contenu directement consultable sous forme de page Web. Il existe de plus un plugin qui permet de fabriquer un PDF en regroupant les fichiers APT souhaités.

Mais, cela reste un nouveau langage à apprendre pour des équipes fonctionnelles et le format APT est trop limité pour permettre un travail efficace par les équipes de conception ou d'analyse.

Après avoir tourné et viré, testé quelques solutions, j'en suis arrivé à la conclusion que le plus pratique est de laisser les concepteurs utiliser leurs outils office ([Microsoft](http://www.microsoft.com/france/office/) ou [oOo](http://fr.openoffice.org/)) et de transformer ces documents en PDF lors de la fabrication du site.

Pour cela, un petit plugin miracle (`jodconverter-maven-plugin`) couplé à oOo permet de faire le travail.

Tout d'abord, il faut lancer oOo en mode serveur. Sous Linux, ça se fait comme ça :

```sh
/opt/openoffice.org3/program/soffice -headless -accept="socket,host=localhost,port=8100;urp;" -nofirststartwizard
```

Sous Windows :

```sh
"C:\Program Files\OpenOffice.org 3\program\soffice.exe" -accept="socket,host=localhost,port=8100;urp;"
```

Puis ajouter dans le `pom.xml` :

```xml
<build>
   <plugins>
      <plugin>
         <groupId>com.artofsolving</groupId>
         <artifactId>jodconverter-maven-plugin</artifactId>
         <version>2.2.3</version>
         <inherited>false</inherited>
         <configuration>
            <sourceDirectory>${basedir}/src/site/docs</sourceDirectory>
            <outputDirectory>${project.reporting.outputDirectory}/docs</outputDirectory>
            <include>**/*.odt,**/*.odp</include>
            <outputFormat>pdf</outputFormat>
            <port>8100</port>
         </configuration>
         <executions>
            <execution>
               <id>convert</id>
               <phase>pre-site</phase>
               <goals>
                  <goal>convert</goal>
               </goals>
            </execution>
         </executions>
      </plugin>
   </plugins>
</build>
```

Ainsi, lors de la génération du site, tous les documents odt ou odp présents dans le répertoire `/src/site/docs` et sous-répertoires seront transformés en documents PDF dans le répertoire de sortie du site sous `/docs`. Les sous-répertoires sont également recréés.

Il ne reste plus qu'à faire des liens vers ces documents générés que ce soit dans site.xml ou dans un fichier APT.

Dans l'exemple suivant, le fichier source `MonDoc.odt` se trouve dans `/src/site/docs/1`.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!-- Extrait du site.xml -->
<body>
   <menu name="Fonctionnel">
      <item name="Mon document" href="./docs/1/MonDoc.pdf" />
   </menu>
</body>
```

Dans le cadre des projets que je gère, j'ai mis en place [Hudson](http://hudson-ci.org/) qui me reconstruit toutes les nuits une vision documentaire de mes projets. Ainsi, lorsqu'un concepteur valide dans CVS ou SVN pendant la journée un document, il est automatiquement publié la nuit sur le site Maven correspondant.

Autre intérêt : à chaque livraison ([release](http://maven.apache.org/plugins/maven-release-plugin/)), une photographie complète de l'état de la documentation au moment de la fabrication des livrables est générée. Il est ainsi possible de retrouver facilement le contexte fonctionnel d'une version particulière...

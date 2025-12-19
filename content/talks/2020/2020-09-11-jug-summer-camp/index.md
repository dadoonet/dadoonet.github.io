---

title: "Identifier les menaces avec Elastic SIEM"
conference: 
  name: "JUG Summer Camp"
  city: "La Rochelle"
  country: "France"
  country_code: "fr"
  latitude: "46.160329"
  longitude: "-1.151139"
  url: "https://www.jugsummercamp.org/edition/11/presentations/si4HEEvfcNOR3P36Npy0"
author: David Pilato
avatar: /about/david_pilato.png
tags:
  - elasticsearch
  - conference
  - java
  - cloud
categories:
  - speaker
series:
  - conferences
date: 2020-09-11
nolastmod: true
draft: false
cover: cover.png

# Speaker specific fields
youtube: "nvCERPGuUFo"
notist: "dadoonet/FIdoIN"

links:
  - title: "AuditD Rules"
    url: "https://github.com/linux-audit/audit-userspace/tree/master/rules"
    description: "Templates for common auditD rules"
  - title: "Demo: Auditbeat in Action"
    url: "https://github.com/xeraa/auditbeat-in-action"
    description: "This demo shows how you can use Auditbeat to ingest data from your environment and visualize it in Kibana."

aliases:
  - /FIdoIN

---

Savoir ce qui se passe dans votre environnement est une part importante pour être informé de problèmes de sécurité. Mais comment capturer et visualiser les informations pertinentes ? Un outil open source est mondialement utilisé pour cela : la suite Elastic. Ce talk vous fera découvrir par la pratique comment ingérer les données utiles provenant de votre couche réseau, de vos machines, de vos logs ainsi que le moyen de facilement les visualiser afin d’identifier des patterns et comportements suspicieux. Nous utiliserons notamment pour cela le tout dernier outil SIEM de la suite Elastic.

Nous utiliserons pour cela des données type “piège à miel” :

* La première étape est de lire, extraire et enrichir la donnée afin d’identifier les attaques, leur source et plus encore.
* Puis stocker et explorer la donnée collectée pour trouver des indicateurs pertinents.
* Ce qui nous amènera à créer des visualisations spécifiques à notre besoin - par exemple la localisation de l’attaquant ou des patterns type d’attaque.
* Puis nous combinerons ces visualisations dans un tableau de bord consolidant l’information.
* Au final, nous utiliserons l’application SIEM pour voir comment toute cette recherche et analyse est dorénavant grandement simplifiée.

Tout cela en live.

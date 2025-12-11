---
title: "do MORE with stateLESS Elasticsearch"
description: ""
conference: 
  name: "JUG Summer Camp"
  url: "https://www.jugsummercamp.org/"
  city: "La Rochelle"
  country: "France"
  country_code: "fr"
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
date: 2025-09-05
nolastmod: true
draft: false
cover: cover.jpg

# Speaker specific fields
#youtube: ""
notist: "dadoonet/WA1Ort"
---

Comment feriez-vous pour créer Elasticsearch si vous commenciez ce projet en 2025 ?

Découpler le calcul (compute) du stockage (storage)
Externaliser la gestion de la persistence et la réplication à un blob store comme S3, Google Cloud Storage ou encore Azure Blob Storage
Dynamiquement ajouter ou supprimer des instances
Avoir les bonnes valeurs par défaut
Et un chemin hyper clair et fluide pour les développeurs

C’est exactement ce que nous avons fait avec Elastic Serverless.
Lors de cette session, vous allez découvrir comment nous avons re-conçu Elasticsearch pour lui permettre d’en faire davantage avec une architecture Stateless qui peut exécuter des requêtes sur un espace de stockage froid (cold storage).

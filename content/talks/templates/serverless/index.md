---
title: "do MORE with stateLESS Elasticsearch"
layout: "template"
talk: Serverless
date: 2025-09-05
nolastmod: true
draft: false

links:
  - title: "Documentation: Elastic Serverless"
    url: "https://www.elastic.co/docs/deploy-manage/deploy/elastic-cloud/serverless"
    description: "This is the official Elastic Serverless documentation."
  - title: "Documentation: Elasticsearch Serverless API"
    url: "https://www.elastic.co/docs/api/doc/elasticsearch-serverless/"
    description: "This is the official Elasticsearch Serverless API documentation."
---
Comment feriez-vous pour créer Elasticsearch si vous commenciez ce projet en 2025 ?

* Découpler le calcul (compute) du stockage (storage)
* Externaliser la gestion de la persistence et la réplication à un blob store comme S3, Google Cloud Storage ou encore Azure Blob Storage
* Dynamiquement ajouter ou supprimer des instances
* Avoir les bonnes valeurs par défaut
* Et un chemin hyper clair et fluide pour les développeurs

C'est exactement ce que nous avons fait avec Elastic Serverless.

Lors de cette session, vous allez découvrir comment nous avons re-conçu Elasticsearch pour lui permettre d'en faire davantage avec une architecture Stateless qui peut exécuter des requêtes sur un espace de stockage froid (cold storage).


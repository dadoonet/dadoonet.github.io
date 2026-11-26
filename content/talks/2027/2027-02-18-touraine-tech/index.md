---
title: "Chercher une frame dans un pot de rillettes"
subtitle: "L’IA multimodale au secours de vos vidéos"
conference:
  name: "Touraine Tech"
  city: "Tours"
  country: "France"
  country_code: "fr"
  url: "https://touraine.tech/talk/cmvkwcxtr007e01t771v9w65d/"
  date: "2027-02-18"
  latitude: "47.3646161"
  longitude: "0.6838372"
authors:
  - author: "David Pilato"
talk: "Video Search"
date: "2026-11-12"
talk-lang: "fr"
nolastmod: true
draft: false
---

Retrouver un moment précis dans des téraoctets d'archives vidéo, c'est littéralement chercher un morceau de viande précis dans un pot de rillettes. Vous savez pertinemment que ce moment où Jean-Michel fait tomber son sandwich dans les douves du château de Chambord a été filmé... mais allez-vous vraiment visionner 12 heures de visites touristiques en x4 pour le débusquer ?

Oubliez le taggage manuel laborieux et les recherches par noms de fichiers obscurs. Il est temps d'appeler les artisans de la donnée ! Dans cette session, nous allons construire un véritable moteur de recherche vidéo "Omnisearch". L'objectif ? Retrouver la seconde exacte de votre action à partir d'une simple requête en langage naturel (ex : "sandwich qui tombe à l'eau près d'un château").

Au programme de notre recette technique :

* **Effilocher la donnée (Video Chunking) :** Les bonnes rillettes s'effilochent avec soin. Avant d'indexer, on découpe les vidéos ! Chronomètre vs changements de plans : découvrons comment échantillonner intelligemment pour conserver la texture et la sémantique de l'action.
* **La magie du Clos Lucé (Jina Embeddings) :** Telle une invention de Léonard de Vinci, découvrez comment un modèle multimodal de dernière génération (*jina-embeddings-v5-omni-small*) transforme l'art visuel de vos images et de vos textes en de pures mathématiques (vecteurs denses).
* **La vie de château avec Elasticsearch :** Oubliez les recherches qui tournent en rond dans l'escalier à double révolution de Chambord, foncez ! Avec la recherche des plus proches voisins (kNN), sans aucun malentendu ça va *matcher*. Nous verrons comment naviguer entre les résultats et filtrer les doublons au moment de conclure.

Pas besoin d'être le nouveau Léonard de Vinci pour assister à cette session, un niveau de développement basique suffit. Vous repartirez avec les concepts clés pour implémenter votre propre moteur, de l'idée jusqu'à l'œuvre finale.

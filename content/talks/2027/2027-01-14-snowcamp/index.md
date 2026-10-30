---
title: "Les Bronzés cherchent une Vidéo"
subtitle: "L'IA multimodale au secours de vos souvenirs"
conference: 
  date: 2027-01-14
  name: "Snowcamp"
  city: "Grenoble"
  country: "France"
  country_code: "fr"
  latitude: "45.1546344"
  longitude: "5.7326528"
  url: "https://snowcamp.io/"
authors: 
  - author: David Pilato
  - author: Benjamin Dauvissat
    link: "https://www.linkedin.com/in/%F0%9F%94%8E%F0%9F%8F%8Dbenjamin-dauvissat-07037310/"
avatar: /about/david_pilato.avif
talk: Video Search
date: 2026-10-30
talk-lang: fr
nolastmod: true
draft: false
#pdf: "2027/2027-01-14-snowcamp.pdf"

# Speaker specific fields
#youtube: ""

links:
  - title: "Demo: Video search"
    url: "https://github.com/dadoonet/video-search"
    description: "This demo shows how you can search for specific video moments using natural language queries."

---

Retrouver un moment précis dans des téraoctets d'archives vidéo, c'est littéralement chercher un flocon dans une botte de neige. Vous savez pertinemment que ce fameux "soleil" de Jean-Michel dans la poudreuse a été filmé... mais allez-vous vraiment visionner 12 heures de rushs GoPro en x4 pour le débusquer ?

Oubliez le taggage manuel laborieux et les recherches par noms de fichiers obscurs. Il est temps d'appeler les pisteurs-secouristes de la donnée ! Dans cette session, nous allons sortir des sentiers battus pour construire un véritable moteur de recherche vidéo "Omnisearch". L'objectif ? Retrouver la seconde exacte de votre action à partir d'une simple requête en langage naturel (ex : "chute mémorable dans la neige au coucher du soleil").

Au programme de notre expédition technique :

* **Passer la dameuse sur vos rushs (Video Chunking) :** Avant de skier, on lisse la neige. Avant d'indexer, on découpe les vidéos ! Chronomètre vs changements de plans : découvrons comment échantillonner intelligemment pour conserver la sémantique de l'action.
* **La poudreuse vectorielle (Jina Embeddings) :** Comment un modèle multimodal de dernière génération (*jina-embeddings-v5-omni-small*) compresse la sémantique de vos images et de vos textes en vecteurs denses.
* **Tout schuss vers la bonne frame avec Elasticsearch :** Oublie que t'as aucune chance de la retrouver manuellement, fonce ! Avec la recherche des plus proches voisins (kNN), sans aucun malentendu ça va *matcher*. Nous verrons comment slalomer entre les résultats et filtrer les doublons au moment de conclure.

Un niveau "piste bleue" en développement suffit pour suivre, pas besoin de maîtriser le planter de bâton ! Vous repartirez avec les concepts clés pour implémenter votre propre moteur de recherche vidéo... et ensuite, nous irons prendre un bon verre de vin chaud ! 🍷

---
title: "Finding a frame in a haystack"
layout: "template"
talk: Video Search
nolastmod: true
draft: false

versions:
  - label: "EN"
    flag: "gb"
    title: "Finding a frame in a haystack: Multimodal AI to the rescue of your videos"
    abstract: |
      Finding a specific moment in terabytes of video archives is literally like looking for a needle in a haystack. Are you really going to watch 12 hours of footage at 4x speed just to find that one specific 3-second clip?

      Forget tedious manual tagging and searching by obscure filenames. In this session, we will build a true "Omnisearch" video search engine. The goal? Find the exact second of your action using a simple natural language query (e.g., "sunset over a mountain").

      On the agenda for our technical deep dive:
      * **Video Chunking:** Fixed time vs. scene changes. Let's discover how to sample our frames intelligently so the AI doesn't lose the flow of the action.
      * **Multimodal Embeddings:** How a next-generation multimodal model (*jina-embeddings-v5-omni-small*) compresses the semantics of your images and texts into dense vectors.
      * **Elasticsearch & kNN:** Vector ingestion, k-Nearest Neighbors (kNN) search using cosine distance, and tips to filter out duplicate clips at query time so we don't overwhelm the user.

      You'll leave this session with the key concepts to implement your own video search engine from scratch!
  - label: "FR"
    flag: "fr"
    title: "Chercher une frame dans une botte de foin : L'IA multimodale au secours de vos vidéos"
    abstract: |
      Retrouver un moment précis dans des téraoctets d'archives vidéo, c'est littéralement chercher une aiguille dans une botte de foin. Allez-vous vraiment visionner 12 heures de rushs en x4 pour débusquer ces 3 petites secondes de clip ? 

      Oubliez le taggage manuel laborieux et les recherches par noms de fichiers obscurs. Dans cette session, nous allons construire un véritable moteur de recherche vidéo "Omnisearch". L'objectif ? Retrouver la seconde exacte de votre action à partir d'une simple requête en langage naturel (ex : "coucher de soleil sur la montagne").

      Au programme :
      * **Video Chunking :** Chronomètre vs changements de plans : découvrons comment échantillonner intelligemment nos frames pour conserver la sémantique de l'action.
      * **Embeddings multimodaux :** Comment un modèle multimodal de dernière génération (*jina-embeddings-v5-omni-small*) compresse la sémantique de vos images et de vos textes en vecteurs denses.
      * **Elasticsearch & kNN :** Ingestion, recherche des plus proches voisins (kNN) via la distance cosinus, et astuces de filtrage pour ne pas noyer l'utilisateur sous des clips en double.

      Vous repartirez avec les concepts clés pour implémenter votre propre moteur de recherche vidéo !
links:
  - title: "Demo: Video search"
    url: "https://github.com/dadoonet/video-search"
    description: "This demo shows how you can search for specific video moments using natural language queries."

---

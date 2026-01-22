---
title: "Search: a new era"
conference: 
  name: "jPrime 2024"
  city: "Sofia"
  country: "Bulgaria"
  country_code: "bg"
  latitude: "42.697708"
  longitude: "23.321868"
  url: "https://jprime.io/"
author: David Pilato
avatar: /about/david_pilato.png
talk: AI Search
date: 2024-05-29
talk-lang: en
nolastmod: true
draft: false
pdf: "2024/2024-05-29-jprime-2024.pdf"


# Speaker specific fields
#youtube: ""
notist: "dadoonet/NizzH6"

x:
  - user: "dadoonet"
    id: "1795423218313912325"
  - user: "piotrprz"
    id: "1795743726465355921"
  - user: "jPrimeConf"
    id: "1759498858676056236"

links:
  - title: "Demo: Music search"
    url: "https://github.com/dadoonet/music-search"
    description: "This demo shows how you can use the principles of vector search to find pieces of music that are (maybe) similar to others."

aliases:
  - /NizzH6
---
Search is not just traditional TF/IDF any more but the current trend of machine learning and models has opened another dimension for search.

This talk gives an overview of:

* “Classic” search and its limitations
* What is a model and how can you use it
* How to use vector search or hybrid search in Elasticsearch
* Where OpenAI’s ChatGPT or similar LLMs come into play to with Elastic

This talk covers the state of the art in terms of search nowadays: BM25, Vector search, Embeddings, Hybrid Search, Reciprocal Rank Fusion, and OpenAI integration. The main demo covers how to generate embeddings from a piece of music and then use the techniques we learned to propose the most probable version of it when we hum a song.

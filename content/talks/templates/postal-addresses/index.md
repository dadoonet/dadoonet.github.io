---
title: "Enriching postal addresses with Elastic stack"
layout: "template"
talk: Postal Addresses
date: 2019-04-12
nolastmod: true
draft: false

versions:
  - label: "EN"
    flag: "gb"
    title: "Enriching postal addresses with Elastic stack"
    abstract: |
      > Come and learn how you can enrich your existing data with normalized postal addresses with geo location points thanks to open data and [BANO project](https://bano.openstreetmap.fr/data/).
      
      Most of the time postal addresses from our customers or users are not very well formatted or defined in our information systems. And it can become a nightmare if you are a call center employee for example and want to find a customer by its address.
      Imagine as well how a sales service could easily put on a map where are located the customers and where they can open a new shop…
      
      Let's take a simple example:
      
      ```json
      {
        "name": "Joe Smith",
        "address": {
          "number": "23",
          "street_name": "r verdiere",
          "city": "rochelle",
          "country": "France"
        }
      }
      ```
      
      Or the opposite. I do have the coordinates but I can't tell what is the postal address corresponding to it:
      
      ```json
      {
        "name": "Joe Smith",
        "location": {
          "lat": 46.15735,
          "lon": -1.1551
        }
      }
      ```
      
      In this live coding session, I will show you how to solve all those questions using the Elastic stack.
  - label: "FR"
    flag: "fr"
    title: "Enrichir les adresses postales avec la suite Elastic"
    abstract: |
      > Venez apprendre comment enrichir vos données existantes avec des adresses postales normalisées et des points de géolocalisation grâce à l'open data et au [projet BANO](https://bano.openstreetmap.fr/data/).
      
      La plupart du temps, les adresses postales de nos clients ou utilisateurs ne sont pas très bien formatées ou définies dans nos systèmes d'information. Et cela peut devenir un cauchemar si vous êtes un employé de centre d'appel par exemple et que vous voulez trouver un client par son adresse.
      Imaginez également comment un service commercial pourrait facilement mettre sur une carte où sont situés les clients et où ils peuvent ouvrir un nouveau magasin…
      
      Prenons un exemple simple :
      
      ```json
      {
        "name": "Joe Smith",
        "address": {
          "number": "23",
          "street_name": "r verdiere",
          "city": "rochelle",
          "country": "France"
        }
      }
      ```
      
      Ou l'inverse. J'ai les coordonnées mais je ne peux pas dire quelle est l'adresse postale correspondante :
      
      ```json
      {
        "name": "Joe Smith",
        "location": {
          "lat": 46.15735,
          "lon": -1.1551
        }
      }
      ```
      
      Dans cette session de live coding, je vous montrerai comment résoudre toutes ces questions en utilisant la suite Elastic.

links:
  - title: "Blog: Enriching Your Postal Addresses With the Elastic Stack - Part 1"
    url: "https://www.elastic.co/blog/enriching-your-postal-addresses-with-the-elastic-stack-part-1"
  - title: "Blog: Enriching Your Postal Addresses With the Elastic Stack - Part 2"
    url: "https://www.elastic.co/blog/enriching-your-postal-addresses-with-the-elastic-stack-part-1"
  - title: "Blog: Enriching Your Postal Addresses With the Elastic Stack - Part 3"
    url: "https://www.elastic.co/blog/enriching-your-postal-addresses-with-the-elastic-stack-part-3"
  - title: "Code: bano-elastic"
    url: "https://github.com/dadoonet/bano-elastic/"
---

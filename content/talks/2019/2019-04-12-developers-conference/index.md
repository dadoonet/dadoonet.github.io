---
title: "Enrichir ses adresses postales avec la suite Elastic"
description: ""
conference: 
  name: "Developers Conference"
  url: ""
  city: "Moka"
  country: "Mauritius"
  country_code: "mu"
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
date: 2019-04-12
nolastmod: true
draft: false
cover: cover.png

# Speaker specific fields
#youtube: ""
notist: "dadoonet/tibZw7"

x:
  - user: "MSCraftsman"
    id: "1116654694561193985"
  - user: "dadoonet"
    id: "1116959232115580928"
  - user: "dadoonet"
    id: "1116986432223088642"
  - user: "dadoonet"
    id: "1116341860606328833"
  - user: "nashcsshtml"
    id: "1116658341982425089"
  - user: "kevanmoothien"
    id: "1116638121897148416"
  - user: "VanessaChellen"
    id: "1116661036529143808"
  - user: "rishiabee"
    id: "1116681930060312577"
  - user: "dadoonet"
    id: "1116676391184080896"
---

Souvent, les adresses postales de nos clients ou utilisateurs sont très mal formatées dans nos systèmes d’information. De fait, si on est un service client, un call center et que l’on souhaite retrouver un client par son adresse, cela devient assez compliqué. De même, comment répondre au service commercial qui souhaiterait présenter sur une carte où sont physiquement localisés les clients, où peut-on ouvrir une nouvelle boutique, …
Prenons un cas simple :
{
  "name": "Joe Smith",
  "address": {
    "number": "23",
    "street_name": "r verdiere",
    "city": "rochelle",
    "country": "France"
  }
}

Ou l’inverse. J’ai des coordonnées, mais je ne peux pas dire à quelle adresse cela correspond :
{
  "name": "Joe Smith",
  "location": {
    "lat": 46.15735,
    "lon": -1.1551
  }
}

Cette session, sans slides, vous fera découvrir comment résoudre ces problèmes en utilisant la suite Elastic et en particulier, Logstash et Elasticsearch.

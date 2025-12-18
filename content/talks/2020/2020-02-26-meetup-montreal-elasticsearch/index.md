---
title: "Enrichir ses adresses postales avec la suite Elastic"
conference: 
  name: "Meetup Montreal Elasticsearch"
  city: "Montreal"
  country: "Canada"
  country_code: "ca"
  latitude: "45.501689"
  longitude: "-73.567256"
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
date: 2020-02-26
nolastmod: true
draft: false
cover: cover.png

# Speaker specific fields
#youtube: ""
notist: "dadoonet/W6DrOR"

x:
  - user: "dadoonet"
    id: "1230526309102706689"
  - user: "dadoonet"
    id: "1230829244646903808"

links:
  - title: "Meetup Elasticsearch-Montreal"
    url: "https://www.meetup.com/fr-FR/Elasticsearch-Montreal/events/268675767/"
  - title: "Blog post part 1"
    url: "https://www.elastic.co/blog/enriching-your-postal-addresses-with-the-elastic-stack-part-1"
  - title: "Blog post part 2"
    url: "https://www.elastic.co/blog/enriching-your-postal-addresses-with-the-elastic-stack-part-1"
  - title: "Blog post part 3"
    url: "https://www.elastic.co/blog/enriching-your-postal-addresses-with-the-elastic-stack-part-3"
  - title: "Repository used for the demo"
    url: "https://github.com/dadoonet/bano-elastic/"

aliases:
  - /W6DrOR
---
Souvent, les adresses postales de nos clients ou utilisateurs sont très mal formatées dans nos systèmes d’information. De fait, si on est un service client, un call center et que l’on souhaite retrouver un client par son adresse, cela devient assez compliqué. De même, comment répondre au service commercial qui souhaiterait présenter sur une carte où sont physiquement localisés les clients, où peut-on ouvrir une nouvelle boutique, …

Prenons un cas simple :

```
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
Ou l’inverse. J’ai des coordonnées, mais je ne peux pas dire à quelle adresse cela correspond :

```
{
  "name": "Joe Smith",
  "location": {
    "lat": 46.15735,
    "lon": -1.1551
  }
}
```
Cette session, sans slides, vous fera découvrir comment résoudre ces problèmes en utilisant la suite Elastic et en particulier, Logstash et Elasticsearch.

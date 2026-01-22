---
title: Enrichir ses adresses postales avec la suite Elastic
conference:
  name: BBL Neo9 (Private Event)
  url: "https://neo9.fr/"
  country: "Online"
  country_code: "Online"
author: David Pilato
avatar: /about/david_pilato.png
talk: Postal Addresses
date: 2022-02-17
talk-lang: fr
nolastmod: true
draft: false

notist: dadoonet/RxDtjn
links:
  - title: "Repository used for the demo"
    url: "https://github.com/dadoonet/bano-elastic/"

  - title: "Blog post part 1"
    url: "https://www.elastic.co/blog/enriching-your-postal-addresses-with-the-elastic-stack-part-1"

  - title: "Blog post part 2"
    url: "https://www.elastic.co/blog/enriching-your-postal-addresses-with-the-elastic-stack-part-1"

  - title: "Blog post part 3"
    url: "https://www.elastic.co/blog/enriching-your-postal-addresses-with-the-elastic-stack-part-3"


aliases:
- /RxDtjn
x:
- user: dadoonet
  id: '1493867495081619457'
---
Souvent, les adresses postales de nos clients ou utilisateurs sont très mal formatées dans nos systèmes d’information. De fait, si on est un service client, un call center et que l’on souhaite retrouver un client par son adresse, cela devient assez compliqué. De même, comment répondre au service commercial qui souhaiterait présenter sur une carte où sont physiquement localisés les clients, où peut-on ouvrir une nouvelle boutique, …

Prenons un cas simple :

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

Ou l’inverse. J’ai des coordonnées, mais je ne peux pas dire à quelle adresse cela correspond :

```json
{
  "name": "Joe Smith",
  "location": {
    "lat": 46.15735,
    "lon": -1.1551
  }
}
```

Cette session, sans slides, vous fera découvrir comment résoudre ces problèmes en utilisant la suite Elastic et en particulier, Logstash et Elasticsearch.

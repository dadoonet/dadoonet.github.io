---
title: "Enrichir ses adresses postales avec la suite Elastic"
conference: 
  name: "Developers Conference"
  city: "Moka"
  country: "Mauritius"
  country_code: "mu"
  latitude: "-20.219524"
  longitude: "57.502332"
  url: "https://conference.mscc.mu/"
author: David Pilato
avatar: /about/david_pilato.avif
talk: Postal Addresses
date: 2019-04-12
talk-lang: fr
nolastmod: true
draft: false

# Speaker specific fields
#youtube: ""
notist: "dadoonet/tibZw7"

social:
  - "https://x.com/MSCraftsman/status/1116654694561193985"
  - "https://x.com/dadoonet/status/1116959232115580928"
  - "https://x.com/dadoonet/status/1116986432223088642"
  - "https://x.com/dadoonet/status/1116341860606328833"
  - "https://x.com/nashcsshtml/status/1116658341982425089"
  - "https://x.com/kevanmoothien/status/1116638121897148416"
  - "https://x.com/VanessaChellen/status/1116661036529143808"
  - "https://x.com/rishiabee/status/1116681930060312577"
  - "https://x.com/dadoonet/status/1116676391184080896"
links:
  - title: "Blog: Enrichir ses adresses postales avec la suite Elastic - Part 1"
    url: "https://www.elastic.co/blog/enriching-your-postal-addresses-with-the-elastic-stack-part-1"
  - title: "Blog: Enrichir ses adresses postales avec la suite Elastic - Part 2"
    url: "https://www.elastic.co/blog/enriching-your-postal-addresses-with-the-elastic-stack-part-1"
  - title: "Blog: Enrichir ses adresses postales avec la suite Elastic - Part 3"
    url: "https://www.elastic.co/blog/enriching-your-postal-addresses-with-the-elastic-stack-part-3"
  - title: "Code: bano-elastic"
    url: "https://github.com/dadoonet/bano-elastic/"

aliases:
  - /tibZw7
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

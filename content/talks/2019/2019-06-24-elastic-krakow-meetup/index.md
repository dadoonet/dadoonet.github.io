---
title: "Enriching postal addresses with Elastic stack"
conference: 
  name: "Elastic Krakow Meetup"
  city: "Kraków"
  country: "Poland"
  country_code: "pl"
  latitude: "50.064651"
  longitude: "19.944981"
  url: "https://www.meetup.com/fr-FR/Elastic-Krakow/events/262282793/"
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
date: 2019-06-24
nolastmod: true
draft: false
cover: cover.png

# Speaker specific fields
#youtube: ""
notist: "dadoonet/im8Q3z"

x:
  - user: "dadoonet"
    id: "1139124121546235904"

links:
  - title: "Blog post part 1"
    url: "https://www.elastic.co/blog/enriching-your-postal-addresses-with-the-elastic-stack-part-1"
  - title: "Blog post part 2"
    url: "https://www.elastic.co/blog/enriching-your-postal-addresses-with-the-elastic-stack-part-1"
  - title: "Blog post part 3"
    url: "https://www.elastic.co/blog/enriching-your-postal-addresses-with-the-elastic-stack-part-3"
  - title: "Repository used for the demo"
    url: "https://github.com/dadoonet/bano-elastic/"

aliases:
  - /im8Q3z
---
> Come and learn how you can enrich your existing data with normalized postal addresses with geo location points thanks to open data and [BANO project](http://bano.openstreetmap.fr/data/).

Most of the time postal addresses from our customers or users are not very well formatted or defined in our information systems. And it can become a nightmare if you are a call center employee for example and want to find a customer by its address.
Imagine as well how a sales service could easily put on a map where are located the customers and where they can open a new shop…

Let’s take a simple example:

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
Or the opposite. I do have the coordinates but I can’t tell what is the postal address corresponding to it:

```json
{
  "name": "Joe Smith",
  "location": {
    "lat": 46.15735,
    "lon": -1.1551
  }
}
```
In this live coding session, I will show you how to solve all those questions using the Elastic stack with a lot of focus on Logstash and Elasticsearch.

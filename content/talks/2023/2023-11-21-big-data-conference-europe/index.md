---

title: "Enriching postal addresses with Elastic stack"
conference: 
  name: "Big Data Conference Europe"
  url: "https://events.pinetool.ai/3079/#sessions/101080"
  city: "Vilnius"
  country: "Lithuania"
  country_code: "lt"
  latitude: "54.687156"
  longitude: "25.279651"
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
date: 2023-11-21
nolastmod: true
draft: false
cover: cover.png

# Speaker specific fields
youtube: "zJjVnp1davo"
notist: "dadoonet/TN5yX9"

x:
  - user: "dadoonet"
    id: "1724109443783082295"
  - user: "dadoonet"
    id: "1727277492808085806"

links:
  - title: "Blog: Enriching Your Postal Addresses With the Elastic Stack - Part 1"
    url: "https://www.elastic.co/blog/enriching-your-postal-addresses-with-the-elastic-stack-part-1"
  - title: "Blog: Enriching Your Postal Addresses With the Elastic Stack - Part 2"
    url: "https://www.elastic.co/blog/enriching-your-postal-addresses-with-the-elastic-stack-part-1"
  - title: "Blog: Enriching Your Postal Addresses With the Elastic Stack - Part 3"
    url: "https://www.elastic.co/blog/enriching-your-postal-addresses-with-the-elastic-stack-part-3"
  - title: "Code: bano-elastic"
    url: "https://github.com/dadoonet/bano-elastic/"

aliases:
  - /TN5yX9

---

> Come and learn how you can enrich your existing data with normalized postal addresses with geo location points thanks to open data and [BANO project](http://bano.openstreetmap.fr/data/).

Most of the time postal addresses from our customers or users are not very well formatted or defined in our information systems. And it can become a nightmare if you are a call center employee for example and want to find a customer by its address.
Imagine as well how a sales service could easily put on a map where are located the customers and where they can open a new shop…

Let’s take a simple example:

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

Or the opposite. I do have the coordinates but I can’t tell what is the postal address corresponding to it:

```
{
  "name": "Joe Smith",
  "location": {
    "lat": 46.15735,
    "lon": -1.1551
  }
}
```

In this live coding session, I will show you how to solve all those questions using the Elastic stack.

---
title: "Elasticsearch"
conference: 
  name: "BBL Accenture (Private Event)"
  city: "Amsterdam"
  country: "Netherlands"
  country_code: "nl"
  latitude: "52.370216"
  longitude: "4.895168"
  url: "https://www.accenture.com/nl-en"
author: David Pilato
avatar: /about/david_pilato.png
talk: Elasticsearch
date: 2022-03-18
nolastmod: true
draft: false
pdf: "2022/2022-03-18-bbl-accenture-private-event.pdf"


# Speaker specific fields
#youtube: ""
notist: "dadoonet/OjlDev"

x:
  - user: "dadoonet"
    id: "1504474921715466259"
  - user: "dadoonet"
    id: "1504770694818963458"
  - user: "dadoonet"
    id: "1504799847735562241"

links:
  - title: "Demo: Kibana script for BBL"
    url: "https://gist.github.com/dadoonet/f911291c4dd19b0802031db3064c648f"
    description: "This is the Kibana script I’m starting from when doing the talk"

aliases:
  - /OjlDev
---
Do you still use SQL queries to search? Your users blame you for not being able to search any and all data? Your average response time is greater than half a second with only a few million documents? Do you need 3 days to produce statistics on your data? Do you dream of offering a “google search” on your IS data?

Enter Elasticsearch: A simple-to-setup and simple-to-use search service. You simply feed it the information you want to be searchable using its index APIs and use its simple-yet-powerful search APIs to let users search for this information in milliseconds.

Elasticsearch is an open source horizontally-scalable, distributed search and analytics engine based on Apache Lucene. Elasticsearch is one of the most popular projects on Github with 1100+ contributors, 12,000+ forks and 43,000+ commits. Organizations around the world, from startups to governments to large corporations, are using Elasticsearch for numerous use cases to gain real-time insights from large volumes of data.

This talk will introduce you to Elasticsearch in a conceptual and hands-on, practical way. We will talk about documents, indices, search, aggregations and language analysis. But we will also see each of these concepts in action via live demos. We will feed actual information into the Elasticsearch service and later retrieve it by searching for it! At the end of this talk you will be comfortable spinning up your very own Elasticsearch service for your very own application!

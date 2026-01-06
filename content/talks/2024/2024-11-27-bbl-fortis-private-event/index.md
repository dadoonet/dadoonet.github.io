---
title: "Elasticsearch Query Language: ES|QL"
conference: 
  name: "BBL Fortis (private event)"
  url: "https://www.bnpparibasfortis.be/"
  city: "Brussels"
  country: "Belgium"
  country_code: "be"
  latitude: "50.850340"
  longitude: "4.351710"
author: David Pilato
avatar: /about/david_pilato.png
talk: conferences
date: 2024-11-27
nolastmod: true
draft: false
pdf: "2024/2024-11-27-bbl-fortis-private-event.pdf"


# Speaker specific fields
#youtube: ""
notist: "dadoonet/PhbmgJ"
links:
  - title: "Fortis"
    url: "https://www.bnpparibasfortis.be/"

  - title: "Demo code"
    url: "https://github.com/dadoonet/esql-demo"
    description: "The code played during the demo"

  - title: "Playground page"
    url: "https://esql.demo.elastic.co"
    description: "If you want to try ES|QL, there’s an open instance with some data."

  - title: "ES|QL Guide"
    url: "https://www.elastic.co/guide/en/elasticsearch/reference/current/esql.html"
    description: "The official guide"

  - title: "Java Demo code"
    url: "https://github.com/dadoonet/elasticsearch-java-client-demo"
    description: "The Java demo for ES|QL"



aliases:
  - /PhbmgJ
---
Elasticsearch and Kibana added a brand new query language: ES|QL — coming with a new endpoint (`_query`) and a simplified syntax. It lets you refine your results one step at a time and adds new features like data enrichment and processing right in your query. And you can use it across the Elastic Stack — from the Elasticsearch API to Discover and Alerting in Kibana. But the biggest change is behind the scenes: Using a new compute engine that was built with performance in mind.

Join us for an overview and a look at syntax and internals.

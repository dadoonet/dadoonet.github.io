---
title: "Deploying and Monitoring Elastic Stack on GCP"
conference: 
  name: "Google Cloud Next ’19 UK"
  city: "London"
  country: "UK"
  country_code: "gb"
  latitude: "51.507351"
  longitude: "-0.127758"
  url: "https://cloud.withgoogle.com/next/uk/speakers?session=DZ105"
author: David Pilato
avatar: /about/david_pilato.png
talk: conferences
date: 2019-11-20
nolastmod: true
draft: false
pdf: "2019/2019-11-20-google-cloud-next-19-uk.pdf"


# Speaker specific fields
#youtube: ""
notist: "dadoonet/jYxmxg"

x:
  - user: "glaforge"
    id: "1197143672556597249"
  - user: "Julien_iZiWEB"
    id: "1197141827071217670"
  - user: "VenziaIT"
    id: "1197087109607305217"
  - user: "dadoonet"
    id: "1197159764800802818"

links:
  - title: "Documentation: Elastic Cloud on Kubernetes (ECK)"
    url: "https://www.elastic.co/guide/en/cloud-on-k8s/current/index.html"
    description: "This is the official Elastic Cloud on Kubernetes (ECK) documentation."
  - title: "Documentation: Kibana"
    url: "https://www.elastic.co/guide/en/kibana/current/introduction.html"
    description: "This is the official Kibana documentation."
  - title: "Documentation: Elasticsearch"
    url: "https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html"
    description: "This is the official Elasticsearch documentation."

aliases:
  - /jYxmxg
---
To deploy elastic stack on Google Compute Platform (GCP), you have several options:

* Start GCE instances, install and configure elasticsearch nodes discovery, SSL and security
* Do the same but install `discovery-gce` plugin to simplify nodes discovery
* Use Elastic Cloud Enterprise and deploy it on GCE instances
* Use Elastic Cloud Kubernetes operator on GKE

Or, you can let Elastic, the company behind elastic stack, deploy and manage it for you with cloud.elastic.co

---
title: "Les Vendredis noirs : même pas peur !"
conference: 
  name: "Devopsdays Geneva 2019"
  city: "Geneva"
  country: "Switzerland"
  country_code: "ch"
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
date: 2019-02-22
nolastmod: true
draft: false
cover: cover.jpg

# Speaker specific fields
#youtube: ""
notist: "dadoonet/lYu3b1"

x:
  - user: "DevopsdaysGe"
    id: "1098905223337250817"
  - user: "dadoonet"
    id: "1098926966814715904"
  - user: "mathieu_b"
    id: "1098902999773138945"
  - user: "SgGuibert"
    id: "1099028173050781696"

links:
  - title: "Quantitative Cluster Sizing"
    url: "https://www.elastic.co/fr/elasticon/conf/2016/sf/quantitative-cluster-sizing"
    description: "How many shards should I have? How many nodes should I have? What about replicas? Do these questions sound familiar? The answer is often ‘it depends’. This talk will outline the factors that affect sizing and walk you through a quantitative approach to estimating the configuration and size of your cluster."
  - title: "Rollover API"
    url: "https://www.elastic.co/guide/en/elasticsearch/reference/6.6/indices-rollover-index.html"
    description: "The rollover index API rolls an alias over to a new index when the existing index is considered to be too large or too old."
  - title: "Shrink Index API"
    url: "https://www.elastic.co/guide/en/elasticsearch/reference/6.6/indices-shrink-index.html"
    description: "The shrink index API allows you to shrink an existing index into a new index with fewer primary shards."
  - title: "Split Index API"
    url: "https://www.elastic.co/guide/en/elasticsearch/reference/6.6/indices-split-index.html"
    description: "The split index API allows you to split an existing index into a new index, where each original primary shard is split into two or more primary shards in the new index."
  - title: "Talk video from a past session"
    url: "https://www.youtube.com/watch?v=h7R79ypXJsI"
    description: "Talk give at DevopsDDay Marseille, November 2018."
  - title: "Official photos from DevopsDays Geneva"
    url: "https://photos.app.goo.gl/Y4yUQbPbCrdG9DpNA"

aliases:
  - /lYu3b1
---
Surveiller une application complexe n’est pas une tâche aisée, mais avec les bons outils, ce n’est pas si sorcier. Néanmoins, des périodes fortes telles que les opérations de type “Black Friday” (Vendredi noir) ou période de Noël peuvent pousser votre application aux limites de ce qu’elle peut supporter, ou pire, la faire crasher. Parce que le système est fortement sollicité, il génère encore davantage de logs qui peuvent également mettre à mal votre système de supervision.
Dans cette session, j’aborderai les bonnes pratiques d’utilisation de la suite Elastic pour centraliser et monitorer vos logs. Je partagerai également avec vous quelques trucs et astuces pour vous aider à passer sans souci vos Vendredis noirs !

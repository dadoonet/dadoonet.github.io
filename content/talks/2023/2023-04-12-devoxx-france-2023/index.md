---
title: "Un moteur de recherche de documents d’entreprise"
conference: 
  name: "Devoxx France 2023"
  city: "Paris"
  country: "France"
  country_code: "fr"
  latitude: "48.856614"
  longitude: "2.352222"
  url: "https://cfp.devoxx.fr/2023/talk/SPD-7040/Un_moteur_de_recherche_de_documents_d'entreprise"
author: David Pilato
avatar: /about/david_pilato.png
# talk: conferences
date: 2023-04-12
nolastmod: true
draft: false
pdf: "2023/2023-04-12-devoxx-france-2023.pdf"


# Speaker specific fields
#youtube: ""
notist: "dadoonet/dnEdLV"

x:
  - user: "dadoonet"
    id: "1626194106346094592"
  - user: "dadoonet"
    id: "1621486584032907265"

links:
  - title: "Workshop instructions"
    url: "https://github.com/dadoonet/DevoxxFR-2023"
  - title: "Documentation: Ingest Attachment Processor"
    url: "https://www.elastic.co/guide/en/elasticsearch/reference/current/attachment.html"
    description: "This is the official Ingest Attachment Processor documentation."
  - title: "Documentation: FSCrawler"
    url: "https://fscrawler.readthedocs.io/"
    description: "This is the official FSCrawler documentation."

aliases:
  - /dnEdLV
---
Lors de cet atelier, nous allons expliquer comment mettre en place un moteur de recherche pour les données de notre entreprise.

Afin d’éviter le côté trop “magique” parfois des solutions sur étagère, nous verrons d’abord :

* les bases du moteur de recherche Elasticsearch
* l’indexation de contenu JSON
* la transformation à la volée du contenu JSON via les pipelines ingest
* l’extraction de texte et de meta-données depuis un document binaire avec le [processor `attachment`](https://www.elastic.co/guide/en/elasticsearch/plugins/current/ingest-attachment.html)
* l’utilisation du tout nouveau processeur d’inférence pour déterminer des entités nommées de nos documents ainsi qu’une analyse de sentiments
* l’utilisation du projet [FSCrawler](https://github.com/dadoonet/fscrawler) open-source pour réaliser plus simplement ces étapes

Nous verrons ensuite comment chercher dans les données ainsi indexées.

Enfin, nous mettrons en place une interface de recherche sur étagère, portée par la solution gratuite [Workplace Search](https://www.elastic.co/workplace-search) qui nous permettra de chercher dans différentes sources documentaires avec assez peu d’efforts.

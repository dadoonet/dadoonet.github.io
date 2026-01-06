---
title: "Indexing your office documents with Elastic stack and FSCrawler"
conference: 
  name: "Java2Days"
  url: "https://2022.java2days.com/"
  country: "Online"
  country_code: "Online"
author: David Pilato
avatar: /about/david_pilato.png
series:
  - conferences
date: 2022-03-09
nolastmod: true
draft: false
pdf: "2022/2022-03-09-java2days.pdf"


# Speaker specific fields
#youtube: ""
notist: "dadoonet/A6Jbu7"

x:
- user: Java2Days
  id: '1500060100437979142'
- user: dadoonet
  id: '1501447005914214403'

links:
  - title: "Documentation: FSCrawler"
    url: "https://fscrawler.readthedocs.io/"

aliases:
  - /A6Jbu7
---
You have plenty of Open Office, Microsoft Office, PDF, images… documents and you may want to be able to search for their metadata and content. How can you do that? In this talk, David will explain how Apache Tika can be used for that and how to combine this fantastic library with Elastic Stack:

* Elasticsearch [ingest-attachment plugin](https://www.elastic.co/guide/en/elasticsearch/plugins/current/ingest-attachment.html)
* [FSCrawler](https://github.com/dadoonet/fscrawler)
* [Workplace Search](https://www.elastic.co/workplace-search) connector for FSCrawler to have a ready to use and powerful user interface for your documents.

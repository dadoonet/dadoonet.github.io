---
title: Indexing your office documents with Elastic stack and FSCrawler
conference:
  name: JCon 2022
  url: ''
  country: "Online"
  country_code: "Online"
author: David Pilato
avatar: /about/david_pilato.png
talk: conferences
date: 2022-11-24
nolastmod: true
draft: false
pdf: "2022/2022-11-24-jcon-2022.pdf"

notist: dadoonet/K6AjsW
links:
  - title: "Event page"
    url: "https://www.techweek.ro/software-architecture-summit"

  - title: "FSCrawler"
    url: "https://fscrawler.readthedocs.io/"


aliases:
- /K6AjsW
x:
- user: dadoonet
  id: '1592127445821685763'
---
You have plenty of Open Office, Microsoft Office, PDF, images… documents and you may want to be able to search for their metadata and content. How can you do that?

In this talk, David will explain how Apache Tika can be used for that and how to combine this fantastic library with Elastic Stack:

*
Elasticsearch [ingest-attachment plugin](https://www.elastic.co/guide/en/elasticsearch/plugins/current/ingest-attachment.html)

*
[FSCrawler](https://github.com/dadoonet/fscrawler)

*
[Workplace Search](https://www.elastic.co/workplace-search) connector for FSCrawler to have a ready to use and powerful user interface for your documents.

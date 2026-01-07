---
title: "Indexing your office documents with Elastic stack and FSCrawler"
conference: 
  name: "Software Architecture Summit"
  city: "Bucharest"
  country: "Romania"
  country_code: "ro"
  latitude: "44.426767"
  longitude: "26.102538"
  url: "https://www.techweek.ro/software-architecture-summit"
author: David Pilato
avatar: /about/david_pilato.png
# talk: conferences
date: 2022-06-17
nolastmod: true
draft: false
pdf: "2022/2022-06-17-software-architecture-summit.pdf"


# Speaker specific fields
youtube: "D6dpQ-avd0g"
notist: "dadoonet/64HZzX"

x:
  - user: "dadoonet"
    id: "1533828626499747841"
  - user: "iemejia"
    id: "1537719880652398592"
  - user: "dadoonet"
    id: "1537787842109313025"
  - user: "dadoonet"
    id: "1537791722989707264"
  - user: "dadoonet"
    id: "1543972927116296194"

links:
  - title: "Documentation: FSCrawler"
    url: "https://fscrawler.readthedocs.io/"
    description: "This is the official FSCrawler documentation."

aliases:
  - /64HZzX
---
You have plenty of Open Office, Microsoft Office, PDF, images… documents and you may want to be able to search for their metadata and content. How can you do that?

In this talk, David will explain how Apache Tika can be used for that and how to combine this fantastic library with Elastic Stack:

*
Elasticsearch [ingest-attachment plugin](https://www.elastic.co/guide/en/elasticsearch/plugins/current/ingest-attachment.html)

*
[FSCrawler](https://github.com/dadoonet/fscrawler)

*
[Workplace Search](https://www.elastic.co/workplace-search) connector for FSCrawler to have a ready to use and powerful user interface for your documents.

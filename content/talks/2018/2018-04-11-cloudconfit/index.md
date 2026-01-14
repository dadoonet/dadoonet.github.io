---
title: "Managing your black Friday logs"
conference:
  url: "https://2018.cloudconf.it/"
  name: "CloudConf.IT"
  city: "Turin"
  country: "Italy"
  country_code: "it"
  latitude: "45.070339"
  longitude: "7.686864"
author: David Pilato
avatar: /about/david_pilato.png
talk: Black Friday
date: 2018-04-11
lang: en
nolastmod: true
draft: false
pdf: "2018/2018-04-11-cloudconfit.pdf"


# Speaker specific fields
#youtube: ""
attendees: 450
notist: "dadoonet/TTEsrR"
aliases:
  - /TTEsrR
---
Monitoring an entire application is not a simple task, but with the right tools it is not a hard task either.

However, events like Black Friday can push your application to the limit, and even cause crashes. As the system is stressed, it generates a lot more logs, which may crash the monitoring system as well.

In this talk I will walk through the best practices when using the Elastic Stack to centralize and monitor your logs. I will also share some tricks to help you with the huge increase of traffic typical in Black Fridays.

## Q&A

> Last time I used ELK there was no easy way to do housekeeping (e.g: automatically expiring old logs from the index) Have you added such a feature, or are you planning to?

Have a look at curator. It's open source and built by elastic. But more importantly we will have index management feature in 7.0 which will simplify even more all that.

>You talked about a limit of 10 shards for node, collecting as in the istance 90days of logs with a daily index it will be hard to remain under that limit (we usually collect hundreds giga of data daily). Or the limit is just regarding the shards in a sing

It was just the limit we had for the given hardware we had. But you can have a hot/warm/cold architecture with elasticsearch. On the warm nodes, you can call the shrink API and reduce the number of shards, call force merge and then you will probably to st

> In your scenario with an Index per day, if traffic increases, is the suggested strategy to create a new Index with more shards and switch the alias?

Exactly. Even better have a look at the Rollover API which can do that for you (creating a new index based on the number of docs you have or after a given delay and switch the alias)

>Could not be a good idea to use kafka to decouple the pipeline and send logs to different logstash to perform different enrichments?

Totally a good idea if you want to scale out logstash nowadays. May be in the future, logstash will more act as a cluster.

>Is it possible to archive old logs offline and later use them for query purposes?

Yes. But to query them you will have first to restore them. Might be better to use the coming Rollup index feature in 7.0.

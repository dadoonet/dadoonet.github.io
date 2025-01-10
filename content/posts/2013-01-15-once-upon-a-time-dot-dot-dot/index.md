---
title: "Once upon a time..."
description: "2 years ago, I was looking for a way to make Hibernate search distributed on multiple nodes. My first idea was to store indexes in a single database shared by my nodes. Yes, it’s a stupid idea in term of performances but I would like to try to build it.

Digging for source code, I came to the JdbcDirectory class from the compass project. And I saw on the compass front page something talking about the future of Compass and Elasticsearch."
author: David Pilato
avatar: /about/david_pilato.png
tags:
  - career
  - culture
  - travels
categories:
  - culture
series:
  - career at elastic
date: 2013-01-15 20:00:00 +0200
nolastmod: true
cover: es1.png
draft: false
aliases:
  - /blog/2013/01/15/once-upon-a-time-dot-dot-dot/
  - /blog/2013-01-15-once-upon-a-time-dot-dot-dot/
---

> Once upon a time...

In fact 2 years ago, I was looking for a way to make Hibernate search distributed on multiple nodes. My first idea was to store indexes in a single database shared by my nodes. Yes, it’s a stupid idea in term of performances but I would like to try to build it.

Digging for source code, I came to the [JdbcDirectory class](http://www.compass-project.org/docs/2.0.1/api/org/apache/lucene/store/jdbc/JdbcDirectory.html) from the compass project. And I saw on the compass front page something talking about the future of Compass and Elasticsearch.

{{< figure src="es1.png" caption="The future of Compass and Elasticsearch" >}}

<!--more-->

Two clicks later, I discovered Elasticsearch. I downloaded it, started and said “WTF! How can it be?” This project solved all my concerns and adds even features I was not aware of in less than 30 seconds! I did not sleep during one full week, really! That was too much magical! After some hours, Elasticsearch was implemented in my project and was providing the first full text searches. I told to my colleagues that this project is so wonderful that I want to be involved if a company is created.

At this point, I was looking to contribute back to the project. But, I was not an Elasticsearch expert nor a Lucene one. I searched for French web content about it and found one or two articles. So I started to write some French content on [my personal blog]({{< ref "2011-03-09-la-recherche-elastique" >}}). I also started to create some plugins. The [RSS River](http://david.pilato.fr/rssriver/) was the first one. By the way, that was my first open source project.

I met Shay Banon the first time in June 2011 for a conference in Paris. He was doing a no-slide no-bullshit talk. Very impressive. It just works! I told him that as I can not contribute on the core project, I can try to talk about the project in France. He agreed and the French user group was born!

{{< figure src="es2.png" caption="Elasticsearch French Community" >}}

One year later, [my talk for Devoxx France](http://www.devoxx.com/display/FR12/ElasticSearch+++moteur+de+recherche+NoSQL+REST+JSON+taille+pour+le+cloud) was accepted and everything really started from here. The French user group grows now each day.

Some months later, the company Elasticsearch BV was created. It was really clear to me that I have to join. When you fall in love, you should marry! I met Shay once again at Devoxx 2012 and we talked about it, about what value I can add to Elasticsearch. And now, two years after the first day I discovered Elasticsearch my dreams comes true, just like in fairy tales!

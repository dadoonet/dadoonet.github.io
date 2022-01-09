---
title: "3 years! Time flies!"
#description: 
toc: true
authors:
  - David Pilato
tags:
  - career
  - culture
  - travels
categories:
  - culture
series:
  - career at elastic
date: 2016-01-12 08:37:00 +0100
lastmod: 2016-01-12 08:37:00 +0100
# featuredImage: blog/2016-03-17-and-the-beats-go-on/beats.png
draft: false
aliases:
  - /blog/2016/01/12/3-years-time-flies/
---

3 years! Can you imagine that? Already [3 years spent working at elastic]({{< ref "2015-01-19-once-upon-a-time-make-your-dreams-come-true" >}})? Time flies!

2015 has been an uncommon year for me.

Not because Marty Mc Fly and Doc Emmett Brown finally arrived...

{{< youtube Q0VGRlEJewA >}}

Not because, Han Solo, Leia and friends were finally back again...

{{< youtube wCc2v7izk8w >}}

But for technical and also personal reasons.

<!-- more -->

On a personal side, I had to deal with two major issues which cause some slow down in my professional activities. I had to cancel some conferences for instance.

And at such moments you realize how confortable it is to work for a human company. Each time the answer from my management was always the same:

> Family first David! Take all the time you need and tell us if we can assist you on anything.

It is so helpful when you can focus on solving your issues. I'm really thankful to the company board for this. Really. "**Family first**" are not only words. It's a reality at elastic.

## The evangelist work

I traveled. A lot. I gave less talks but I did 2 000 kilometers more than last year. Yeah. **50 000 kilometers** for 2015... Still a lot if you think that most of my traveling were in France or in Europe...

* 2 elastic events: [elastic{ON}'15](https://www.elastic.co/elasticon/2015/sf/highlights-reel) and [elastic{ON} Tour Paris'15](https://www.elastic.co/elasticon/tour/2015/paris).

**Both were fantastic**. When you are working on technical side you are far away from event organization. It was clearly a success, not by mistake, but because very talented people made all that happen. That was months of preparation for the team. It went super well.

It was also time to reveal the new identity of the company and `elasticsearch` became `elastic`.

It was my first time at San Francisco and I could enjoy visiting [our amazing new office in Mountain View](http://retaildesignblog.net/2015/05/30/elastic-office-by-garcia-tamjidi-architecture-design-mountain-view-california/comment-page-1/) and also do some sight seeing in SFO where my wife and I finally saw the well known "la maison bleue".

{{< youtube tDtXXlD98kw >}}

Well, I guess it's well known only in France! 😄

* 1 Webinar: [Advanced Search for your Legacy Application (French)](https://www.elastic.co/videos/advanced-search-legacy-application-french)
* 1 conference as a sponsor
* 7 [trainings](https://www.elastic.co/training). Don't miss our [next sessions in Paris](http://training.elastic.co/?courseId=0&city=PARIS)! I'll give the [Kibana 4 Workshop](http://training.elastic.co/class/Kibana/Paris/Feb06) with another colleague.
* 5 [meetups](http://www.meetup.com/elasticfr/). Come and say hello for [the next one](http://www.meetup.com/fr-FR/ElasticFR/events/227882863/)! We are now more than 1600 members!
* 26 [BBLs](http://www.brownbaglunch.fr/). Still one of my favorite moment. By the way, I started adding elasticsearch on the web site. Stay tuned! 😄
* 23 talks. Lot of conferences, including [Devoxx FR](http://www.devoxx.fr/), [Code Motion](http://www.codemotionworld.com/), [BDX.io](www.bdx.io)...

I think I spoke for more than **2 500 attendees**! I'm super happy on this because results are clearly visible in the company when we look for example at the requests on the web site per region or the [Google trends](http://www.google.fr/trends/explore?q=Elasticsearch#q=Elasticsearch&geo=FR%2C%20US%2C%20GB&date=1%2F2015%2012m&cmpt=geo&tz=Etc%2FGMT-1):

{{< figure src="google-trends.png" caption="Google Trends" >}}

On a side note, I also helped at [Devoxx4Kids France](http://www.devoxx4kids.org/france/). My children really enjoyed it and they are asking me every month about the next event! Count on me Devoxx4Kids team!

{{< figure src="devoxx4kids.jpg" caption="Devoxx4Kids" >}}

{{< youtube wzr6xXwCEKU >}}

I also wrote some [blog posts](https://www.elastic.co/blog/author/david-pilato), helped on translating to french some parts of our website...

## And as a developer?

I worked a lot this year on splitting elasticsearch repository in many maven modules. I wrote a [script](https://github.com/elastic/elasticsearch/commit/6024f89032c6f42c7a28211099587324abdb5858) which created a maven parent project, moved elasticsearch core code to a core module and then pulled plugins repository in plugins modules.

It was then applied in [June the 5th](https://github.com/elastic/elasticsearch/commits/5beed150ed0583e3bf71532bc1ff91bbc9bf042d).

I really enjoyed working on that because it now makes official plugins as first class citizen. They are now part of the release process, are automatically maintained as well by my co-workers.

And to be honest, it also reduces my workload. Releasing all plugins have always been time consuming. Now I can focus more on the code itself.

Bringing modularity in elasticsearch repo was a great thing and thanks to all my colleagues who enhanced the process. We now have a very nice release process!

I also worked a lot on splitting the packages in their [own distribution modules](https://github.com/elastic/elasticsearch/pull/11523).

I tried also to enhance the [Java API documentation](https://www.elastic.co/guide/en/elasticsearch/client/java-api/current/index.html). Well, step by step, I'm trying to add some content. For example, I added recently some documentation about the [AdminClient](https://www.elastic.co/guide/en/elasticsearch/client/java-api/master/java-admin.html). More to come!

## The devangelist team

When I started 3 years ago at elastic, there was only 10 employees including the 4 founders. Obviously we did not create an evangelist team at this moment. But it was clearly part of my job to [continue on advocacy work](https://www.elastic.co/blog/welcome-david).

And now, we have a team! We hired talented people over the world, in Asia, in US and in Europe. We all are doing some code and evangelism. So we called our team the `devangelist` team.

Well, my email signature is `Dev | Evangelist`. `|` is actually here the [Linux pipe character](https://en.wikipedia.org/wiki/Pipeline_(Unix)), you know, when the output of one process becomes the input of the next one. That's exactly what we are: passionnated coders with speaker skills... :)

We all met in Barcelona in September. Was great time!

{{< figure src="devangelist.jpg" caption="The devangelist team - Sept 2015" >}}

## The company

Growing from 10 to 300 people is something I never experienced before. It's a super interesting moment. And it's not that easy when you think about a distributed company with different countries and different cultures.

At the end [it works pretty well](https://www.glassdoor.fr/Avis/Elastic-Avis-E751551.htm?&countryRedirect=true) at elastic.

The language barrier is still a problem even after 3 years. Of course, I can understand better my colleagues; it basically depends on their accent! :P from 30% to 100%...

Well, as the company is also growing in France, 100% is when I'm speaking with my french colleagues!

So. 300 people. w00t! It's probably impossible to know now each person and I guess that for the coming elastic{ON}'16, we'll use our employee badges a lot!

## 2016

What is going to happen this year? I'm working on new talks now as the company is growing and releasing more and more tools. For example, I really need to test out all the [beats family](https://www.elastic.co/products/beats).

Also, I need to play with [TimeLion](https://www.elastic.co/blog/timelion-timeline). It looks a fantastic way to correlate time based data coming from different sources.

I started playing a lot with [found](https://www.elastic.co/found) in 2015, no need to say that I'll continue this year.

I can't wait for elastic{ON}'16! Super excited to meet again all my coworkers and see what is the crazy stuff they are building or thinking about!

And of course, I will enjoy the good balance I have between work time and family time and will continue to say to myself how much lucky I am.

I wish you fellows a very nice 2016 year and hope that 2016 will be more peaceful than 2015... But [the news today in Istanbul](http://www.bbc.com/news/world-europe-35290760) don't seem to prove me right. [I spoke there last year](https://voxxeddays.com/istanbul15/david-pilato-advanced-search-for-legacy-application-with-elasticsearch/), visited this historical and fantastic place... I'm so sad this is happening...

{{< figure src="istanbul.jpg" caption="😢" >}}

Of course, I'm also thinking of all people who died in 2015 in Paris and of all the wounded ones and their families.

{{< figure src="france.jpg" caption="😢" >}}

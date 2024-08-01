---
title: "Free Lunches for Opensource Engineers"
description: "When I started at elastic some years ago, we were a few people in the company and I was feeling pretty much alone in France. I found a way to share my passion, meet new people and help them to get started with Elasticsearch. That's called BBLs."
toc: true
authors:
  - David Pilato
tags:
  - bbl
  - brownbaglunch
  - conference
  - career
  - culture
categories:
  - culture
series:
  - career-at-elastic
date: 2024-07-31T19:17:27+02:00
lastmod: 2024-07-31T19:17:27+02:00
featuredImage: blog/2024-08-01-free-lunches-for-opensource-engineers/bbl.png
draft: false
---

When I started at elastic [some years ago](https://www.elastic.co/blog/welcome-david), we were a few people in the company and I was feeling pretty much alone in France. I&apos;d been hired to write some code, help people on the forum (now [discuss.elastic.co](https://discuss.elastic.co/)) and also continue evangelism efforts in France.

That has always been a good balance for me. I mean that staying in front of my computer all day long is not the ideal thing. I need to talk with real people in real life and not only over Zoom or Google Hangout.

I spoke one day with [David Gageot](https://github.com/dgageot) about that need and he told me that he would like to start doing BBL sessions. I asked: "*BBL? What is that*?"

## Brown Bag Lunches aka BBL

The brown bag lunch is the typical American bag you take out from a restaurant when you want to eat at your office.

The idea was quite simple:

- Find a host (a company)
- Find attendees
- Grab your knowledge
- Eat a sandwich

Some people also call them "Lunch and Learn" sessions.

I found that idea brilliant as it would exactly fill my needs in term of:

- meeting humans
- spreading the world about Elasticsearch

So I started a day after with a Tweet saying that I'd love to steal David's idea and run a BBL session in Paris:

{{< tweet user="dadoonet" id="275486949924548609" >}}

And [Romain Linsolas](https://github.com/linsolas) answered me that [he would be ok hosting a session about Elasticsearch!](https://twitter.com/romaintaz/status/275502151487332353).

{{< tweet user="romaintaz" id="275502151487332353" >}}

Deal!

## The 1st BBL at SocGen

So I gave [my very 1st BBL](https://twitter.com/romaintaz/status/288968491892088832). We were something like 15-20 attendees. It was a similar session of the one I gave at [Devoxx France a year before](https://www.youtube.com/watch?v=sxWTPruEWRU).

Feedback has been very positive and I found out 4 key points:

- For the **attendees**, it&apos;s a great way to attend a conference without having to sacrifice one or two days, or going to meetups in the evening.
- For the **team manager**, it&apos;s a great way to educate a team and because this is happening during the lunch break, it does not have any impact on the production.
- For the **company**, it&apos;s a great way to mix people from different services in the same room. I&apos;m always seeing people after a session talking to each other about their POC or project around Elasticsearch. Once I heard a guy from a project team telling me at the end: "*Ok. What you have shown us is super exciting and I&apos;d love to use that on one of my projects, but I&apos;m sure that the OPS team will refuse to manage an Elasticsearch cluster in production.*" Someone from the back of the room stood up and said: "*Listen. I&apos;m from the OPS team. I have been using the Elastic Stack for our logs for several months and we are so happy with it that it will be a pleasure to manage your cluster.*" Deal!
- For **myself**, it&apos;s a great way to meet people outside of a conference. It&apos;s a new group of people, and because you are giving a talk to a small number of people or at least to a single company, you build a very close relationship with them. Also, my strategy has always been to speak first to devs and ops instead of managers. In other words, a bottom-up strategy. When a CEO/CTO asks his team about Elasticsearch, the team already knows what it is and is not a barrier. So it&apos;s a big investment, time-wise, because you have to travel back and forth (remember that I&apos;m working remotely) and run the session. It&apos;s around 6 hours within a day but it is really worth it.

## What about a website?

Some other people started as well to run BBL in France. At some point [Romain Linsolas](https://github.com/linsolas), [Nathaniel Richand](https://github.com/nrichand), [Fran&#xE7;ois Sarradin](https://github.com/fsarradin) and myself found that we should have a website to reference all the speakers/sessions so companies would be able to contact us.

[brownbaglunch.fr](http://www.brownbaglunch.fr/) started that way. It&apos;s super easy to add a talk&#x2026; Well, it&apos;s super easy as soon as you are a developer because you need to `git commit` on GitHub a JSON document. :)

The website helped a lot with getting more visibility. I think I&apos;m getting 15 to 20% of my contacts through it.

We started to [enhance it](https://github.com/brownbaglunch/BrownBagLunch/pull/342) a bit as the number of speakers/talks have been growing dramatically. Sadly, I did not find time to finish the job yet but thanks to [CleverCloud](https://www.clever-cloud.com/) and [Elastic](https://elastic.co/) we have a [NodeJS GitHub hook](https://github.com/brownbaglunch/webhook) running on CleverCloud and anytime a PR is merged the NodeJS hook fetch the data, transform it and upload that inside [elastic cloud](https://cloud.elastic.co/). The goal is to add a cool search engine on top of brownbaglunch.fr capable to deal with typos, find speakers around you using geolocation features, filter by label, using faceted navigation, giving autocompletion&#x2026;

## 5 years later&#x2026;

I spoke with some of my colleagues about this and they started to organize BBL sessions in their respective countries. So I started to internationalize the website as well. We might want people to simply fork the original concept or host a global one for the entire world. We&apos;ll see where it goes.

Speaking at BBLs represents half of my evangelist activities. In 2017, I did it 17 times in Paris, Amiens, Lille&#x2026; I went to companies like [Universit&#xE9; Paris Descartes](https://twitter.com/dadoonet/status/833988800749658112), [Brinks](https://twitter.com/dadoonet/status/834844920133382145), [Center Parcs](https://twitter.com/dadoonet/status/869489728915218432), [Leroy Merlin](https://twitter.com/dadoonet/status/872767269880967168), [La Ruche qui dit Oui](https://twitter.com/dadoonet/status/884392325207740417)&#x2026;
Most of the time, I have around 15-20 attendees. Sometimes, companies don&apos;t have enough seats for everyone, so I&apos;m doing 2 separate sessions.
Sometimes, we have people attending the session remotely over Zoom or Google Hangout. Sometimes we do [a BBQ](https://twitter.com/dadoonet/status/642276926229491712) instead of a BBL&#x2026;

Sometimes I&apos;m getting super emotional as it can touch my heart really deeply.

I had the opportunity to speak at [Meetic](https://www.meetic.fr/) in 2014. For those who don&apos;t know Meetic, it&apos;s a dating web/mobile application available in many countries. It&apos;s Tinder-like, but Tinder was created years after Meetic.

I was super excited to speak there for a very personal reason. In 2004, after a divorce, I met my wife on Meetic and in 2007 we got a baby, Max. I&apos;d say that thanks to this website (in 2004, there was no mobile application!), my life changed totally.

You can find a picture of Max searching for logs here!

![Max searching for logs][1]

One of the BBL attendees was working at Meetic in 2004 so I was super thankful and it was a great pleasure to share my knowledge with the team.
I heard later that [Meetic is now using Elasticsearch](https://event.afup.org/forumphp2017-interview-sebastien-le-gall/), which is even better!

## Seeds, Harvest

Speaking at BBLs is a great opportunity to share your knowledge, your experience with a community and to make growing happen even faster. At BBLs, I find a lot of people who are building a POC or running a project in production already. And they are happy to share their story with the community at meetups, even better, host the meetups and write blogs.

In term of evangelism activity, we have seen that the number of downloads we are getting from France is super high. This means a lot to me. All those attendees I spoke to are starting to test the open source Elastic Stack. I&apos;m calling them seeds. And as they get more successful in a few days or weeks, they surely move to production.

In term of business, the presales/sales team then only has to explain how the commercial features in [X-Pack](https://www.elastic.co/products/x-pack) add value on top of the Elastic Stack.  These days, features like [machine learning](https://www.elastic.co/products/x-pack/machine-learning), [security](https://www.elastic.co/products/x-pack/security), and [Elastic Cloud Enterprise](https://www.elastic.co/cloud/enterprise) are getting a lot of traction. In a sense, the sales team has just to "harvest" all those seeds. 
As a farmer, you just need to be patient as it can take months if not years before we get commercially engaged but at the end it eventually happens.

## Get involved!

It&apos;s now your turn!

If you want to have an Elastic engineer speaking within your company, just [drop us a note](https://www.elastic.co/community/contact) and we will find someone for sure in your area. As a distributed company in more than 25 countries, it&apos;s easy to find someone in your community.

If you have an interest and want to share your knowledge, share your own open source project, or build a community, just [edit this brownbaglunch JSON document](https://github.com/brownbaglunch/bblfr_data/edit/gh-pages/baggers.js), send a pull request, and you&apos;re done!

Bon app&#xE9;tit !


  [1]: https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltcee64867b1ff4c0e/659db6ade1b99e0c5d9bfa81/photo-blog-pilato-free-lunch-for-open-source-engineers.png


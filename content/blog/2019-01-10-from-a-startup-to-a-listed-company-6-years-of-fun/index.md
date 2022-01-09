---
title: "From a startup to a listed company. 6 years of fun!"
#description: 
toc: true
authors:
  - David Pilato
tags:
  - career
  - elasticsearch
categories:
  - elasticsearch
  - tutorial
series:
  - career at elastic
date: '2019-01-10'
lastmod: '2019-01-10'
draft: false
aliases:
  - /blog/2019/01/10/from-a-startup-to-a-listed-company-6-years-of-fun/
---

When I joined Elastic (formerly Elasticsearch) it was a startup with 10 employees + the founders. As one of those first employees I was invited (with #elkie and my wife) to the NYSE event where Elastic went listed as `ESTC` symbol.

> Some of us there (Rashid, Karel, Myself, Igor, Costin, Luca, Clinton). Yeah. You are not probably used to see us wearing a suit! :)

If you want to read again my story, it's there:

* January 2013: [Once upon a time...]({{< ref "2013-01-15-once-upon-a-time-dot-dot-dot" >}})
* January 2014: [Once upon a time: a year later...]({{< ref "2014-01-10-once-upon-a-time-a-year-later-dot-dot-dot" >}})
* January 2015: [Once upon a time: Make your dreams come true]({{< ref "2015-01-19-once-upon-a-time-make-your-dreams-come-true" >}})
* January 2016: [3 years! Time flies!]({{< ref "2016-01-12-3-years-time-flies" >}})
* January 2017: [4 years at elastic!]({{< ref "2017-01-10-4-years-at-elastic" >}})
* January 2018: [5 years. What a milestone!]({{< ref "2018-01-10-5-years-what-a-milestone" >}})

Before speaking about what happened last year, I'd like to modify [the way I'm ingesting my personal data in elasticsearch]({{< ref "2018-01-10-5-years-what-a-milestone" >}}) by using the real city name when I'm speaking in France. Why this? Because anytime I'm speaking in Paris or suburbs, I'm actually writing `Paris` in my report which is inaccurate.

Instead, I'd really like to have the real city name... How can I do this? Well, I do have the exact geo location points of each event (which is something I'm writing manually for now)... If you are a frequent visitor of this blog, that should ring a bell, right?

In 2018, I wrote some blog posts about transforming geo points to exact address:

* [Importing Bano dataset with Logstash]({{< ref "2018-03-22-enriching-your-postal-addresses-with-elastic-stack-part-1" >}})
* [Using Logstash to lookup for addresses in Bano index]({{< ref "2018-03-23-enriching-your-postal-addresses-with-elastic-stack-part-2" >}})
* [Using Logstash to enrich an existing dataset with Bano]({{< ref "2018-03-24-enriching-your-postal-addresses-with-elastic-stack-part-3" >}})

Let's use that now!

<!-- more -->

## Upgrading the cluster

As usual, let's start by upgrading the cluster... Well, just few clics and I'm all set for `6.5.3`...

{{< figure src="cloud.jpg" caption="Upgrade to 6.5.3" >}}

## Importing Bano dataset

I just followed the instructions in [Importing Bano dataset with Logstash blog post]({{< ref "2018-03-22-enriching-your-postal-addresses-with-elastic-stack-part-1" >}}) but I just modified the `elasticsearch` output to be:

```ruby
elasticsearch {
  "template_name" => "bano"
  "template_overwrite" => true
  "template" => "${SOURCE_DIR}/bano.json"
  "index" => ".bano-${REGION}"
  "document_id" => "%{[id]}"
  "hosts" => ["${ELASTICSEARCH_URL}"]
  "user" => "elastic"
  "password" => "${ELASTICSEARCH_PASSWORD}"
}
```

In my shell script, I just defined:

```sh
export ELASTICSEARCH_URL=https://MY-CLUSTER-ID.europe-west1.gcp.cloud.es.io:9243
export ELASTICSEARCH_PASSWORD=MY-PASSWORD
```

## Enriching existing data

We have seen in ["5 years. What a milestone!" blog post]({{< ref "2018-01-10-5-years-what-a-milestone" >}}) that we have now an index per year with documents looking like:

```json
{
  "_index" : "talks-2017",
  "_type" : "doc",
  "_id" : "27",
  "_score" : 0.7971689,
  "_source" : {
    "number_of_attendees" : 8,
    "country" : "France",
    "distance" : 80,
    "city" : "PARIS",
    "type" : "Training",
    "@timestamp" : "2017-05-15T00:00:00.000+02:00",
    "name" : "ES Core OPS",
    "location" : {
      "lon" : 2.2489867,
      "lat" : 48.89566
    }
  }
}
```

This training did not happen exactly in Paris so we need to read it again, try to get the exact city name and then update the document.

## Using a Logstash pipeline

Let's start with a Logstash pipeline which reads all data from elasticsearch and write it back to the same cluster using another index name:

```ruby
input {
  elasticsearch {
    "hosts" => ["${ELASTICSEARCH_URL}"]
    "user" => "elastic"
    "password" => "${ELASTICSEARCH_PASSWORD}"
    "index" => "talks-*"
    "docinfo" => true
  }
}

filter {
}

output {
  elasticsearch {
    "hosts" => ["${ELASTICSEARCH_URL}"]
    "user" => "elastic"
    "password" => "${ELASTICSEARCH_PASSWORD}"
    "index" => "new-%{[@metadata][_index]}"
    "document_type" => "%{[@metadata][_type]}"
    "document_id" => "%{[@metadata][_id]}"
  }
  stdout { codec => rubydebug }
}
```

I'm starting Logstash with the following script:

```sh
#!/usr/bin/env bash

export ELASTICSEARCH_URL=https://MY-CLUSTER-ID.europe-west1.gcp.cloud.es.io:9243
export ELASTICSEARCH_PASSWORD=MY-PASSWORD

logstash-6.5.3/bin/logstash -f update-with-bano.conf
```

## Doing lookups in BANO indices

We have seen that in [Using Logstash to lookup for addresses in Bano index]({{< ref "2018-03-23-enriching-your-postal-addresses-with-elastic-stack-part-2" >}}). Let's do it here.

We first create the `search-by-geo.json` file:

```json
{
  "size": 1,
  "query": {
    "bool": {
      "filter": {
        "geo_distance": {
          "distance": "2km",
          "location": {
            "lat": %{[location][lat]},
            "lon": %{[location][lon]}
          }
        }
      }
    }
  },
  "sort": [
    {
      "_geo_distance": {
        "location": {
          "lat": %{[location][lat]},
          "lon": %{[location][lon]}
        }
      }
    }
  ],
  "_source": ["address.city"]
}
```

We can use it in the filter part:

```ruby
filter {
  elasticsearch {
    "query_template" => "search-by-geo.json"
    "hosts" => [ "${ELASTICSEARCH_BANO_URL}" ]
    "user" => "elastic"
    "password" => "${ELASTICSEARCH_BANO_PASSWORD}"
    "index" => ".bano"
    "fields" => {
      "[address][city]" => "city_after"
    }
  }

  mutate {
    "remove_field" => [ "number_of_talks", "@version", "host" ]
    "capitalize" => [ "city", "city_after" ]
  }
}
```

Once everything is running fine, we can actually index within the same index we have been reading the data from and remove the debug output:

```ruby
output {
  elasticsearch {
    "hosts" => ["${ELASTICSEARCH_URL}"]
    "user" => "elastic"
    "password" => "${ELASTICSEARCH_PASSWORD}"
    "index" => "%{[@metadata][_index]}"
    "document_type" => "%{[@metadata][_type]}"
    "document_id" => "%{[@metadata][_id]}"
  }
}
```

## Some Kibana checks

If we create a simple visualization to compare `city` and `city_after`, we can see that some transformation happened.

{{< figure src="kibana-city-fix.jpg" caption="Fix cities" >}}

If we zoom a bit to `Paris`, we can see that actually Paris was Paris but also Saint-Cloud, Poissy...

{{< figure src="kibana-city-fix-paris.jpg" caption="Fix cities Paris" >}}

Also `Carrières-sous-poissy`... But wait. I never spoke there!

Visualizing data is important. I mean **really important**. It makes obvious when something is wrong within your dataset. And this happened here.

Lot of geo points were wrong in my dataset meaning that after applying the transformations, some city name were absolutely not related to the places I've been speaking. As I said before, I entered the geo location points manually in my report and I did some bad copy and paste...

After some manual modifications, I ended up with this list of new cities when Paris was defined:

{{< figure src="kibana-city-fix-paris-2.jpg" caption="Fix cities Paris" >}}

Here is a list for cities in France which are not Paris:

{{< figure src="kibana-city-fix-paris-not.jpg" caption="Fix cities Not Paris" >}}

## Analyzing data

Let's have a final look at this 6th year of speaker activities...

{{< figure src="kibana-talks-distance.jpg" caption="Talks and distance" >}}

I gave less talks this year but covered even more kilometers.

This is mainly due because I went to San Francisco (US), New York (US), Montreal (CA) and  Bangalore (IN) to name a few.

{{< figure src="kibana-where.jpg" caption="Where in the world" >}}

Note that when I'm recording a distance, I'm recording the real distance I made to get there and not the distance to France. For example, when I went to Montreal, because I was in San Francisco, the distance I entered in my spreadsheet is only the distance from Montreal to France and not both ways added as I was yet in USA.

{{< figure src="kibana-countries-distance.jpg" caption="Distance and countries" >}}

## How did I feel it?

To be very honest, I was super exhausted at the end of this year. My manager has been telling me during the whole year that I should may be slow down a bit and that he was very concerned that I should take care of myself to avoid any start of burn out period. Which is something I really like in this company. People do care about other people. Your environment should be a safe place to work.

It does not mean that you can't have any pressure but it can't be a constant pressure all year long and that you need to find the right balance between the company and your personal life.

So I looked back at the Kibana dashboard:

{{< figure src="kibana-per-week.jpg" caption="Talks per week" >}}

I've not been travelling that much but I was like one or two days per week not sleeping at home in 2018. And while I was speaking to other speakers, I realized that this was the cause of my strain. Also, my son started saying that I was not really at home to help him...

Travelling 2 days per week is actually like travelling a full week. You have to organize the travel, prepare the talk, check everything, travel, speak, travel back and rest then. That's taking almost the full week.

In fact, when you go in another city or worse in another country, your brain has to constantly adapt itself to new environment, new rules, other language, etc... Adding to this that one important part of an evangelist is to engage with people (community or course, attendees, other speakers, conference organizers, colleagues...).

I felt like it was not super efficient.

## Consequences for 2019

I want to try another model for this year. I'm not sure yet how this will work but here is the deal. I want to travel up to one full week per month but only the same week, not including exceptions which might always happen, but let's say that's a general rule.

For example, here are the first weeks I'll be on the road (I mean "not sleeping at home") in 2019:

* January 21st - 25th
* February 18th - 22nd
* March 11th - 15th
* April 8th - 12th
* May 13th - 17th

This has some consequences for conferences also. I have to say "no" sadly unless the conference or event is happening nearby, ie. in Paris.

This has also some good consequences. As I'll be at home for 3 weeks. While here, I'll be able to focus on new content, preparing new talks, writing more blog posts, recording more webinars and also test all the cool features our fantastic team is working on.

Probably also with more focus on the french territory.

I will evaluate the situation in June and adjust if needed. Stay tuned!

---
title: "5 years. What a milestone!"
#description: 
toc: true
authors:
  - David Pilato
tags:
  - culture
  - career
  - travels
  - beats
  - elasticsearch
  - elastic-cloud
categories:
  - culture
  - tutorial
series:
  - career at elastic
date: 2018-01-10 09:00:00 +0100
lastmod: 2018-01-10 09:00:00 +0100
# featuredImage: assets/images/covers/new/logstash.png
draft: false
aliases:
  - /blog/2018/01/10/5-years-what-a-milestone/
---

What a milestone! Can you imagine how changed the company in the last 5 years?
From 10 employees when I joined to more than 700 now!

If you want to read again my story, it's there:

* 2013: [Once upon a time...]({{< ref "2013-01-15-once-upon-a-time-dot-dot-dot" >}})
* 2014: [Once upon a time: a year later...]({{< ref "2014-01-10-once-upon-a-time-a-year-later-dot-dot-dot" >}})
* 2015: [Once upon a time: Make your dreams come true]({{< ref "2015-01-19-once-upon-a-time-make-your-dreams-come-true" >}})
* 2016: [3 years! Time flies!]({{< ref "2016-01-12-3-years-time-flies" >}})
* 2017: [4 years at elastic!]({{< ref "2017-01-10-4-years-at-elastic" >}})

Before speaking about what happened the last 5 years for me, let's modify a bit [the script I wrote last year]({{< ref "2017-01-10-4-years-at-elastic" >}}).

<!-- more -->

## Upgrading the cluster

What I'd like to see now, is my activity over years. But first of all, I want to upgrade my existing cloud instance to the lastest version available: `6.1.1`.
Because, I've been using `5.2.2`, I first need to upgrade to `5.6.5`.

{{< figure src="upgrade1.png" caption="Choosing version 5.6.5" >}}

Kind of magic, elastic cloud is starting a new instance, with elasticsearch 5.6.5, moving my old data to this new cluster and then switching off the old cluster.

{{< figure src="upgrade2.png" caption="Upgrade in progress" >}}

I just have to click one other button to upgrade Kibana as well to the right version.

{{< figure src="upgrade3.png" caption="Upgrading Kibana" >}}

Just go to the Upgrade Assistant and apply what is recommended.

{{< figure src="upgrade4.png" caption="Upgrade assistant" >}}

The reindex helper helps a lot doing that in one click.

{{< figure src="upgrade5.png" caption="Reindex helper" >}}

And now I'm ready for the big jump!

{{< figure src="upgrade6.png" caption="Choosing version 6.1.1" >}}

Et voilà!

{{< figure src="upgrade7.png" caption="Ready for 6.1.1" >}}

## Changing the ingestion layer

### CSV format changes

As I'd like to have more metrics, I changed a bit the CSV file format and I added a `country` field which will help to build some other statistics. Now the CSV is looking like:

```txt
;Talk;Nb;Date;Type;Country;Location;Coordinates;Distance;Total;Attendees
1;Metricbeat FR;1;09/01/2017;Webinar;France;CERGY;49.040068,2.0169159;0;0;100
2;ES Core OPS;1;10/01/2017;Training;France;PARIS;48.845316,2.3732776;50;100;20
3;ES Core DEV;1;11/01/2017;Training;France;PARIS;48.845316,2.3732776;100;200;20
4;maarch.org;1;17/01/2017;BBL;France;NANTERRE;48.8890776,2.195139;38;76;10
5;Incityz;1;26/01/2017;BBL;France;PARIS;48.8643677,2.3532333;40;80;15
```

### Changing the ingest pipeline

Which means that I need to adapt the `grok` processor I used to:

```json
{
  "grok": {
    "field": "message",
    "patterns": [
      "%{INT:id};%{DATA:name};%{INT:number_of_talks};%{DATA:date};%{DATA:type};%{DATA:city};%{DATA:location.lat},%{DATA:location.lon};%{INT};%{INT:distance};%{INT:number_of_attendees}"
    ]
  }
}
```

Also, I'd like to create one index per year. I'm adding the `date_index_name` processor to my pipeline:

```json
{
  "date_index_name": {
    "field": "@timestamp",
    "index_name_prefix": "talks-",
    "index_name_format": "yyyy",
    "date_rounding": "y"
  }
}
```

With this a talk given at `26/01/2017` will be indexed in `talks-2017`.

### Using index templates

Last year, I created manually the mapping for my index. But as I will have more and more indices, let's use an [index template](https://www.elastic.co/guide/en/elasticsearch/reference/6.1/indices-templates.html) now:

```json
PUT _template/talks
{
  "index_patterns": [
    "talks-*"
  ],
  "settings": {
  },
  "mappings": {
  },
  "aliases": {
  }
}
```

This template matches any index which name starts with `talks-`.

#### Index settings

Then I choose to change the default index settings as 1 shard will be enough and I don't need replicas as I have only one node:

```json
"settings": {
  "number_of_shards": 1,
  "number_of_replicas": 0
}
```

#### Index mapping

For the mapping, I change the `talk` type name to `doc` which is the recommended name. Remember that [types are going away](https://www.elastic.co/blog/removal-of-mapping-types-elasticsearch). Also, I add the `country` field.

```json
"mappings": {
  "doc": {
    "properties": {
      "@timestamp": {
        "type": "date"
      },
      "city": {
        "type": "text",
        "fields": {
          "keyword": {
            "type": "keyword"
          }
        }
      },
      "country": {
        "type": "text",
        "fields": {
          "keyword": {
            "type": "keyword"
          }
        }
      },
      "distance": {
        "type": "long"
      },
      "location": {
        "type": "geo_point"
      },
      "name": {
        "type": "text",
        "fields": {
          "keyword": {
            "type": "keyword"
          }
        }
      },
      "number_of_attendees": {
        "type": "long"
      },
      "number_of_talks": {
        "type": "long"
      },
      "type": {
        "type": "keyword"
      }
    }
  }
}
```

#### Alias

I don't want to use wildcards when searching in indices so I'm just adding my index to an alias named `talks`:

```json
"aliases": {
  "talks": {}
}
```

### Using filebeat 6.1.1

I [download the new version of filebeat](https://www.elastic.co/downloads/beats/filebeat) and change as well the filebeat configuration. I don't want to `cat` anymore my file but I'd like that filebeat process my CSV anytime I'm changing it or adding a new one in `/path/to/my/csv/files/`:

```yml
filebeat.prospectors:
- paths: ["/path/to/my/csv/files/*.csv"]
  document_type: doc
```

The connection to cloud instances has been simplified. I just need to copy and paste the `cloud.id` from my cloud interface and give my credentials:

```yml
cloud.id: COPY_THIS_FROM_CLOUD_UI
cloud.auth: USERNAME:PASSWORD
```

With filebeat 6.x, filebeat tries to automatically load templates in Elasticsearch and Kibana. Because I don't need that, I just disable this feature:

```yml
setup.template.enabled: false
```

I just have to launch filebeat now and let it work:

```sh
./filebeat -e
```

## Kibana analysis

I'm changing a bit the [Kibana dashboard](https://73531b275dde9af18f03de55b5d02fca.us-east-1.aws.found.io:9243/app/kibana#/dashboard/Talks) (demo / elastic). Well, 6.x is providing new cool features, so let's use that.

By the way, I'm changing my own made `kibana_reader` role for the `demo` user to the official `kibana_dashboard_only_user` role.
This is a super cool "Read Only mode" feature provided by X-Pack as it removes all the buttons you don't have access to anyway.

{{< figure src="kibana1.png" caption="Kibana read only mode" >}}

### 5 years of evangelism

Let's deep dive a bit now...

{{< figure src="kibana2-summary.png" caption="Summary" >}}

The last 5 years, I spent more than 265 000 kilometers in traveling to meet the community and share my passion with more than 16 000 persons. Probably more as I don't count the number of views of the videos you can watch on internet.

{{< figure src="kibana2-events-km.png" caption="Events and Kilometers" >}}

What we can see is that the number of events per year is almost the same (around 75 per year" >}} but I traveled more than 92 000 kilometers in 2017!

{{< figure src="kibana2-type.png" caption="Type of event" >}}

It's super obvious that I'm spending a lot of time doing BBLs. I wrote this year [a blog post about it](https://www.elastic.co/blog/free-lunch-for-open-source-engineers). It's super time consuming, you meet a few people, but it is really worth it as you reach a part of the community you don't normally meet at conferences. Obviously, you reach much more people when you give talks at conferences.

{{< figure src="kibana2-attendees-and-type.png" caption="Distribution of attendees per type of event" >}}

By the way, in my dataset, I'm using `Conference` type of event when I'm maning the booth and `Talk` when I'm giving a public talk.

Let's filter the dataset to see only my BBL activity:

{{< figure src="kibana2-bbl-only.png" caption="BBL only" >}}

We can see that I reduced that a bit this year which kind of make sense as the last 5 years I already spoke in almost 130 companies, mostly in France. I probably need to reach now companies I never spoke to or other territories.

{{< figure src="kibana2-bbl-location.png" caption="BBL locations" >}}

This chart represents the farest countries I've been to and the number of events I attended there.

{{< figure src="kibana2-distance.png" caption="Events by distance" >}}

No real surprise here. I'm speaking mostly in France. But wait... What is this `United Arab Emirates` with 0 kilometers?
Actually I gave a talk remotely for a [Hadoop United Arab Emirates User Group](https://www.meetup.com/Hadoop-User-Group-UAE/events/219512233/?_cookie-check=5nTt5MFXvQbSB29Z). That was from home... :D

### Focus on 2017

{{< figure src="kibana3-2017-overview.png" caption="Overview of 2017" >}}

In 2017, I spoke to around 3 250 person at 72 events. Almost 2 events per week. And because of very long trips, the average number of kilometers per trip has been more than 1 200 kilometers...

{{< figure src="kibana3-2017.png" caption="2017" >}}

I gave 4 talks in Poland, 3 in Canada, 2 in Belarus, Morocco and Netherlands. The "orange" vertical bar chart does not include obviously France. 😉

Here are the main locations I've been to in Europe this year.

{{< figure src="kibana3-2017-europe.png" caption="2017 in Europe" >}}

### Is it only pleasant?

Traveling is nice. Really nice. Speaking in other language than your mother tongue is also exciting.
Meeting new people, sharing your love to the community, getting the love from the community is super pleasant.

But. I did not realize before this year how much exhausting traveling is. Yes, you go to nice hotels, visit cool places, but all that has a price. You are not at home. Your brain needs to change its context everytime. You don't have your habits. You need sometime to fix family issues remotely. It's hard. Not the same "hard" as being at a factory and producing beans tin can but another kind of hard.

I'm fortunate enough working in the best company ever. Sometimes my manager is asking me to slow down a bit and make sure I'm spending enough time with my family and not missing important family dates. Yeah love comes from the community but from your colleagues as well!

I helped hiring some colleagues in 2017. They know now that I was telling the truth about how much working at elastic is a dreamed job!

### What's next?

2018... That is going to be a super interesting year. I said that we are more than 700 people now. Which means that a lot of work, new features, new products is coming constantly...
For example, in 2017, we joined our forces with [Swiftype](https://www.elastic.co/solutions/site-search). I can't wait to test it and eventually propose new talks about that field which is closed to my heart.

We celebrated the [5th anniversary of BBLs](https://www.elastic.co/blog/free-lunch-for-open-source-engineers) at Société Générale on January 9th.
And I already have booked part of my 2018 year (from January to July). I know I'll be going this year to:

* Orléans
* [Montpellier](https://www.jug-montpellier.org/)
* [Grenoble](http://snowcamp.io/fr/)
* [Elastic{ON} Paris](https://www.elastic.co/elasticon/tour/2017/paris)
* [Elastic{ON} Munich](https://www.elastic.co/elasticon/tour/2017/munich)
* [Stockholm](https://www.jfokus.se/jfokus/)
* [Elastic{ON} San Francisco](https://www.elastic.co/elasticon/conf/2018/sf)
* [Montréal](https://confoo.ca/en/yul2018/)
* [Bucharest](https://voxxeddays.com/romania/bucharest/2018-03-22/)
* [Turin](http://2018.cloudconf.it/)
* [Devoxx FR 2018](http://devoxx.fr/)
* [Bangalore](http://www.developermarch.com/developersummit/)
* [Nice](http://www.sophiaconf.fr/)

So if you are around, please come and meet! If you want to organize a BBL in your company, just [ping me on Twitter](https://twitter.com/dadoonet)!

Happy 2018!

## Full code

The full pipeline:

```json
PUT _ingest/pipeline/talks
{
  "processors": [
    {
      "grok": {
        "field": "message",
        "patterns": [
          "%{INT:id};%{DATA:name};%{INT:number_of_talks};%{DATA:date};%{DATA:type};%{DATA:city};%{DATA:location.lat},%{DATA:location.lon};%{INT};%{INT:distance};%{INT:number_of_attendees}"
        ]
      }
    },
    {
      "date": {
        "field": "date",
        "target_field": "@timestamp",
        "formats": [
          "dd/MM/yyyy"
        ],
        "timezone": "Europe/Paris"
      }
    },
    {
      "set": {
        "field": "_id",
        "value": "{{id}}"
      }
    },
    {
      "remove": {
        "field": "message"
      }
    },
    {
      "remove": {
        "field": "beat"
      }
    },
    {
      "remove": {
        "field": "offset"
      }
    },
    {
      "remove": {
        "field": "source"
      }
    },
    {
      "remove": {
        "field": "date"
      }
    },
    {
      "remove": {
        "field": "id"
      }
    },
    {
      "convert": {
        "field": "number_of_attendees",
        "type": "integer"
      }
    },
    {
      "convert": {
        "field": "distance",
        "type": "integer"
      }
    },
    {
      "convert": {
        "field": "location.lon",
        "type": "float"
      }
    },
    {
      "convert": {
        "field": "location.lat",
        "type": "float"
      }
    },
    {
      "convert": {
        "field": "number_of_talks",
        "type": "integer"
      }
    },
    {
      "date_index_name": {
        "field": "@timestamp",
        "index_name_prefix": "talks-",
        "index_name_format": "yyyy",
        "date_rounding": "y"
      }
    }
  ]
}
```

The index template:

```json
PUT _template/talks
{
  "index_patterns": [
    "talks-*"
  ],
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 0
  },
  "mappings": {
    "doc": {
      "properties": {
        "@timestamp": {
          "type": "date"
        },
        "city": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword"
            }
          }
        },
        "country": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword"
            }
          }
        },
        "distance": {
          "type": "long"
        },
        "location": {
          "type": "geo_point"
        },
        "name": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword"
            }
          }
        },
        "number_of_attendees": {
          "type": "long"
        },
        "number_of_talks": {
          "type": "long"
        },
        "type": {
          "type": "keyword"
        }
      }
    }
  },
  "aliases": {
    "talks": {}
  }
}
```

The `filebeat.yml` configuration:

```yml
filebeat.prospectors:
- paths: ["/path/to/my/csv/files/*.csv"]
  document_type: doc

processors:
- drop_event:
    when:
      regexp:
          message: "^;.*$"

cloud.id: COPY_THIS_FROM_CLOUD_UI
cloud.auth: USERNAME:PASSWORD

output.elasticsearch.index: "talks"
output.elasticsearch.pipeline: "talks"

setup.template.enabled: false
```

---
title: "4 years at elastic!"
description: "This post is starting to become a long series 😊

Yeah! That's amazing! I just spent 4 years working at elastic and I'm starting
my happy 5th year! 🎉"
author: David Pilato
avatar: /about/david_pilato.png
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
date: 2017-01-09 18:15:00 +0100
nolastmod: true
draft: false
cover: featured.png
aliases:
  - /blog/2017/01/10/4-years-at-elastic/
  - /blog/2017-01-10-4-years-at-elastic/
---

This post is starting to become a long series 😊

Yeah! That's amazing! I just spent 4 years working at elastic and I'm starting
my happy 5th year!

If you want to read again my story, it's there:

* 2013: [Once upon a time...]({{< ref "2013-01-15-once-upon-a-time-dot-dot-dot" >}})
* 2014: [Once upon a time: a year later...]({{< ref "2014-01-10-once-upon-a-time-a-year-later-dot-dot-dot" >}})
* 2015: [Once upon a time: Make your dreams come true]({{< ref "2015-01-19-once-upon-a-time-make-your-dreams-come-true" >}})
* 2016: [3 years! Time flies!]({{< ref "2016-01-12-3-years-time-flies" >}})

This year, I will celebrate this by writing a new tutorial...

<!--more-->

Why this???

Actually I have always been reporting the last years some numbers about the evangelist part of my job but I always found bad not using the tools we are building for that.

To build my yearly report, I'm actually collecting in a Numbers document (Numbers is like Excel on MacOS) all the travels I'm doing during a year.

Basically, I have a document which looks like this.

{{< figure src="numbers.png" caption="Talks Trips in 2016" >}}

It would be better if I can get from it some statistics, or display on a map where I'm speaking the most frequently, or may be filter by [BBL]({{< ref "2024-08-01-free-lunches-for-opensource-engineers" >}}) type of event...

Anyone is aware of a nice project which can give me all that?

Well, if you are reading this blog the answer is pretty much obvious. Let's use the [elastic stack](https://www.elastic.co/products) for that!

## From CSV to JSON

I exported my Numbers sheet to a CSV file so I have something like this now:

```txt
;Talk;Nb;Date;Type;Location;Coordinates;Distance;Total;Attendees
1;SnowCamp;1;20/01/2016;Workshop;GRENOBLE;45.190531,5.713413;627;1254;20
2;SnowCamp;1;21/01/2016;Talk;GRENOBLE;45.190652,5.767197;0;0;50
3;Louis Vuitton;1;26/01/2016;BBL;PARIS;48.860952,2.342081;50;100;16
4;Meetup Paris Data Geek;1;28/01/2016;Talk;PARIS;48.8788901,2.3294209;50;100;90
5;Meetup ES FR;1;03/02/2016;Meetup;PARIS;48.8753439,2.3358584;50;100;100
6;Kantar Media;1;04/02/2016;BBL;PARIS;48.8880874,2.231051;50;100;15
7;Meetup CERN;1;08/02/2016;Talk;GENEVE;46.2521574,6.0312076;592;1184;100
8;Live AMA (french);1;09/02/2016;Webinar;CERGY;49.0408975,2.0157605;0;0;20
9;elastic{ON};0;16/02/2016;Conference;SAN FRANCISCO;37.7772284,-122.391211;9400;18800;20
10;Company All Hands;0;20/01/2017;Company;LAKE TAHOE;38.9578871,-119.9442902;302;604;0
11;Prisma Media;1;01/03/2016;BBL;GENNEVILLIERS;48.918442,2.2953263;40;80;10
```

I need to produce a JSON document from each line.

I could do this myself but I know a tool which is super straightforward to stream the content of file to an elasticsearch cluster... Got it as well? Yeah! [Filebeat](https://www.elastic.co/products/beats/filebeat) FTW!

Let's [download it](https://www.elastic.co/downloads/beats/filebeat):

```sh
wget https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-5.1.1-darwin-x86_64.tar.gz
tar xzf filebeat-5.1.1-darwin-x86_64.tar.gz
mv filebeat-5.1.1-darwin-x86_64 filebeat-5.1.1
# ^^^ Yeah I prefer shorter names :)
cd filebeat-5.1.1
```

Let's have a look at the configuration file `filebeat.yml`.. It basically contains:

```yml
filebeat.prospectors:
- input_type: log
  paths:
    - /var/log/*.log

output.elasticsearch:
  hosts: ["localhost:9200"]
```

Instead of reading from a file here, let's just send the data with a `cat ../talks_2016.csv | ./filebeat` command.
So we will use `input_type` `stdin` instead of `log`.

```yml
filebeat.prospectors:
- input_type: stdin
```

I also want to change the document type to `talk` instead of `log`:

```yml
filebeat.prospectors:
- input_type: stdin
  document_type: talk
```

I need to download [elasticsearch](https://www.elastic.co/products/elasticsearch), [Kibana](https://www.elastic.co/products/kibana) and install all that now on my server.
And secure it with [X-Pack](https://www.elastic.co/products/x-pack)...

Oh wait! Let's just use a [cloud instance](https://www.elastic.co/cloud) which is ready to use!

## Connecting to elastic cloud

In your cloud configuration page, just copy the URL of your cluster. It's something like `https://your-cluster-id.us-east-1.aws.found.io:9243/`.

Then change the `filebeat.yml` file to use this cluster:

```yml
output.elasticsearch:
  hosts: ["your-cluster-id.us-east-1.aws.found.io:9243"]
  protocol: "https"
  username: "elastic"
  password: "changeme"
```

> [!NOTE]
> You have to modify `changeme` which is a default password for local elasticsearch instances but fortunately not on cloud! 😊

Let's also change the default index name. Here, I'll send all my documents to a `talks` index:

```yml
output.elasticsearch:
  index: "talks"
```

And start! I'm using `-e` option to see what is happening behind the scene.

```sh
cat ../talks_2016.csv | ./filebeat -e
```

Sadly you can't use `-once` option for now because of [a race issue](https://github.com/elastic/beats/issues/3315) when using `stdin` so you need to press `CTRL+C` when done.

If you open your kibana instance and go to the console, you can run:

```json
GET talks/_search
```

Have a look at one of the produced documents:

```json
{
  "_index": "talks",
  "_type": "talk",
  "_id": "AVmDDwY2MqKKvpoCuhya",
  "_score": 1,
  "_source": {
    "@timestamp": "2017-01-09T11:49:18.008Z",
    "beat": {
      "hostname": "MacBook-Pro-6.local",
      "name": "MacBook-Pro-6.local",
      "version": "5.1.1"
    },
    "input_type": "stdin",
    "message": "9;elastic{ON};0;16/02/2016;Conference;SAN FRANCISCO;37.7772284,-122.391211;9400;18800;20",
    "offset": 0,
    "source": "",
    "type": "talk"
  }
}
```

We typically need to cleanup things a bit...

## Node Ingest to the rescue

If you never heard about Node Ingest, you can read the introduction of my article about [writing your own ingest plugin]({{< ref "2016-07-28-creating-an-ingest-plugin-for-elasticsearch" >}}).

### Parsing CSV with Grok

Here I'll will use a [Grok processor](https://www.elastic.co/guide/en/elasticsearch/reference/current/grok-processor.html) first to extract some data from the `message` field:

```json
{
  "grok": {
    "field": "message",
    "patterns": [ "%{INT:id};%{DATA:name};%{INT:number_of_talks};%{DATA:date};%{DATA:type};%{DATA:city};%{DATA:location.lat},%{DATA:location.lon};%{INT};%{INT:distance};%{INT:number_of_attendees}" ]
  }
}
```

Let's simulate that:

```json
POST _ingest/pipeline/_simulate
{
  "pipeline" : {
    "processors": [
      {
       "grok": {
         "field": "message",
         "patterns": [ "%{INT:id};%{DATA:name};%{INT:number_of_talks};%{DATA:date};%{DATA:type};%{DATA:city};%{DATA:location.lat},%{DATA:location.lon};%{INT};%{INT:distance};%{INT:number_of_attendees}" ]
       }
      }
    ]
  },
  "docs" : [
    {
      "_index": "talks",
      "_type": "talk",
      "_id": "AVmDDwY2MqKKvpoCuhya",
      "_score": 1,
      "_source": {
        "@timestamp": "2017-01-09T11:49:18.008Z",
        "beat": {
          "hostname": "MacBook-Pro-6.local",
          "name": "MacBook-Pro-6.local",
          "version": "5.1.1"
        },
        "input_type": "stdin",
        "message": "9;elastic{ON};0;16/02/2016;Conference;SAN FRANCISCO;37.7772284,-122.391211;9400;18800;20",
        "offset": 0,
        "source": "",
        "type": "talk"
      }
    }
  ]
}
```

It now gives:

```json
{
  "_id": "AVmDDwY2MqKKvpoCuhya",
  "_index": "talks",
  "_type": "talk",
  "_source": {
    "date": "16/02/2016",
    "number_of_attendees": "20",
    "offset": 0,
    "city": "SAN FRANCISCO",
    "input_type": "stdin",
    "source": "",
    "message": "9;elastic{ON};0;16/02/2016;Conference;SAN FRANCISCO;37.7772284,-122.391211;9400;18800;20",
    "type": "Conference",
    "@timestamp": "2017-01-09T11:49:18.008Z",
    "beat": {
      "hostname": "MacBook-Pro-6.local",
      "name": "MacBook-Pro-6.local",
      "version": "5.1.1"
    },
    "name": "elastic{ON}",
    "location": {
      "lon": "-122.391211",
      "lat": "37.7772284"
    },
    "id": "9",
    "number_of_talks": "0",
    "distance_total": "18800"
  },
  "_ingest": {
    "timestamp": "2017-01-09T13:13:04.519+0000"
  }
}
```

### Change the document id

We just have to use a [set processor](https://www.elastic.co/guide/en/elasticsearch/reference/current/set-processor.html):

```json
{ "set": { "field": "_id", "value": "{% raw %}{{id}}{% endraw %}" } }
```

This will change the metadata of our document from:

```json
{
  "_id": "AVmDDwY2MqKKvpoCuhya",
  "_index": "talks",
  "_type": "talk",
  "_source": { /* source */ },
  "_ingest": { "timestamp": "2017-01-09T13:13:04.519+0000" }
}
```

to

```json
{
  "_id": "9",
  "_index": "talks",
  "_type": "talk",
  "_source": { /* source */ },
  "_ingest": { "timestamp": "2017-01-09T13:13:04.519+0000" }
}
```

### Reconciliate the date

We need to convert the `date` field wich has a format of `dd/MM/yyyy` to an actual json date. Let's do it with a [date processor](https://www.elastic.co/guide/en/elasticsearch/reference/current/date-processor.html):

```json
{ "date" : {
    "field" : "date",
    "target_field" : "@timestamp",
    "formats" : ["dd/MM/yyyy"],
    "timezone" : "Europe/Paris"
} }
```

We now have:

```json
{
  "date": "16/02/2016",
  "number_of_attendees": "20",
  "offset": 0,
  "distance": "18800",
  "city": "SAN FRANCISCO",
  "input_type": "stdin",
  "source": "",
  "message": "9;elastic{ON};0;16/02/2016;Conference;SAN FRANCISCO;37.7772284,-122.391211;9400;18800;20",
  "type": "Conference",
  "@timestamp": "2016-02-16T00:00:00.000+01:00",
  "beat": {
    "name": "MacBook-Pro-6.local",
    "version": "5.1.1",
    "hostname": "MacBook-Pro-6.local"
  },
  "name": "elastic{ON}",
  "location": {
    "lon": "-122.391211",
    "lat": "37.7772284"
  },
  "id": "9",
  "number_of_talks": "0"
}
```

As you can see `"date": "16/02/2016"` generated `"@timestamp": "2016-02-16T00:00:00.000+01:00"`.

### Removing non needed fields

We want to remove here `message`, `beat`, `input_type`, `offset`, `source`, `date` and `id`. We are going to use a [remove processor](https://www.elastic.co/guide/en/elasticsearch/reference/current/remove-processor.html):

```json
{ "remove": { "field": "message" } },
{ "remove": { "field": "beat" } },
{ "remove": { "field": "input_type" } },
{ "remove": { "field": "offset" } },
{ "remove": { "field": "source" } },
{ "remove": { "field": "date" } },
{ "remove": { "field": "id" } }
```

It is looking better:

```json
{
  "number_of_attendees": "20",
  "distance": "18800",
  "city": "SAN FRANCISCO",
  "type": "Conference",
  "@timestamp": "2016-02-16T00:00:00.000+01:00",
  "name": "elastic{ON}",
  "location": {
    "lon": "-122.391211",
    "lat": "37.7772284"
  },
  "number_of_talks": "0"
}
```

### Transform to numeric values

We have some fields which are numerics but extracted as strings by Grok: `number_of_attendees`, `distance`, `location.lon`, `location.lat`, `number_of_talks`.
[Convert processor](https://www.elastic.co/guide/en/elasticsearch/reference/current/convert-processor.html) will help us here:

```json
{ "convert": { "field" : "number_of_attendees", "type": "integer" } },
{ "convert": { "field" : "distance", "type": "integer" } },
{ "convert": { "field" : "location.lon", "type": "float" } },
{ "convert": { "field" : "location.lat", "type": "float" } },
{ "convert": { "field" : "number_of_talks", "type": "integer" } }
```

It now gives:

```json
{
  "number_of_attendees": 20,
  "distance": 18800,
  "city": "SAN FRANCISCO",
  "type": "Conference",
  "@timestamp": "2016-02-16T00:00:00.000+01:00",
  "name": "elastic{ON}",
  "location": {
    "lon": -122.39121,
    "lat": 37.77723
  },
  "number_of_talks": 0
}
```

### Register the pipeline

We are going to create a pipeline named `talks`:

```json
PUT _ingest/pipeline/talks
{
  "processors": [
    { "grok": { "field": "message",
        "patterns": [ "%{INT:id};%{DATA:name};%{INT:number_of_talks};%{DATA:date};%{DATA:type};%{DATA:city};%{DATA:location.lat},%{DATA:location.lon};%{INT};%{INT:distance};%{INT:number_of_attendees}" ]
    } },
    { "date" : {
        "field" : "date",
        "target_field" : "@timestamp",
        "formats" : ["dd/MM/yyyy"],
        "timezone" : "Europe/Paris"
    } },
    { "set": { "field": "_id", "value": "{% raw %}{{id}}{% endraw %}" } },
    { "remove": { "field": "message" } },
    { "remove": { "field": "beat" } },
    { "remove": { "field": "input_type" } },
    { "remove": { "field": "offset" } },
    { "remove": { "field": "source" } },
    { "remove": { "field": "date" } },
    { "remove": { "field": "id" } },
    { "convert": { "field" : "number_of_attendees", "type": "integer" } },
    { "convert": { "field" : "distance", "type": "integer" } },
    { "convert": { "field" : "location.lon", "type": "float" } },
    { "convert": { "field" : "location.lat", "type": "float" } },
    { "convert": { "field" : "number_of_talks", "type": "integer" } }
  ]
}
```

### Send documents to this pipeline

We need to tell filebeat to use our `talks` pipeline. We can configure that in `filebeat.yml`:

```yml
output.elasticsearch:
  pipeline: "talks"
```

### Remove header and footer

If we run our configuration, we will see some errors:

```txt
2017/01/09 14:37:44.824640 client.go:436: INFO Bulk item insert failed (i=0, status=500): {"type":"exception","reason":"java.lang.IllegalArgumentException: java.lang.IllegalArgumentException: Provided Grok expressions do not match field value: [;Talk;Nb;Date;Type;Location;Coordinates;Distance;Total;Attendees]","caused_by":{"type":"illegal_argument_exception","reason":"java.lang.IllegalArgumentException: Provided Grok expressions do not match field value: [;Talk;Nb;Date;Type;Location;Coordinates;Distance;Total;Attendees]","caused_by":{"type":"illegal_argument_exception","reason":"Provided Grok expressions do not match field value: [;Talk;Nb;Date;Type;Location;Coordinates;Distance;Total;Attendees]"}},"header":{"processor_type":"grok"}}
```

Indeed we are sending 2 lines we would like to ignore actually:

The header:

```txt
;Talk;Nb;Date;Type;Location;Coordinates;Distance;Total;Attendees
```

And the footer:

```txt
;;75;;;;0;27491;54802;4403
```

We can tell filebeat to ignore those lines using a [drop_event processor](https://www.elastic.co/guide/en/beats/filebeat/5.1/drop-event.html) in case a given [regex condition](https://www.elastic.co/guide/en/beats/filebeat/5.1/configuration-processors.html#condition-regexp) is met:

```yml
processors:
- drop_event:
    when:
      regexp:
          message: "^;.*$"
```

### Mapping

Let's see what our current mapping is with a `GET talks/_mapping`.
We can see that `location` field is not mapped as a `geo_point` so let's fix that:

```json
DELETE talks
PUT talks
{
  "talks": {
    "mappings": {
      "talk": {
        "properties": {
          "@timestamp": {
            "type": "date"
          },
          "city": {
            "type": "text",
            "fields": {
              "keyword": {
                "type": "keyword",
                "ignore_above": 256
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
                "type": "keyword",
                "ignore_above": 256
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
  }
}
```

Now we are done. So we can start again filebeat:

```sh
cat ../talks_2016.csv | ./filebeat -e
```

## Kibana

First we need to create our index pattern:

{{< figure src="index-pattern.png" caption="Index Pattern" >}}

In Kibana, we can see some activity already over 2016:

{{< figure src="discover-2016.png" caption="Discover 2016" >}}

We can easily notice that I totally stopped doing evangelism during the summer. I think that if we look at the number of commits in GitHub we can probably find an inverted diagram. 😊

We can now create a dashboard:

{{< figure src="dashboard.png" caption="Dashboard" >}}

Neat, right?

My main activity is in Europe:

{{< figure src="europe.png" caption="Europe" >}}

And a big part of it is close to Paris:

{{< figure src="paris.png" caption="Paris" >}}

You can [open this dashboard](https://73531b275dde9af18f03de55b5d02fca.us-east-1.aws.found.io/app/kibana#/dashboard/Talks) (username: `demo`, password: `elastic`) if you wish and look if I was close to you over the last year 😊

## Conclusion

Evangelism is part of my activity. It also includes a lot of presence on <https://discuss.elastic.co>:

{{< figure src="discuss.png" caption="Discuss activity the last years" >}}

The other part is of course code, specifically on [elasticsearch](https://github.com/elastic/elasticsearch).

{{< figure src="github.png" caption="Git commits for elasticsearch in 2016" >}}

The company has now more than 400 employees. It's becoming harder and harder if not impossible to recall all people names.

We have a great success and our stack is now used almost everywhere. When I'm doing BBL talks, I can see that almost everytime I have an attendee who is saying to his colleagues:

> Oh yeah, it is powerful! We are actually using it already to solve this problem.

And that's just begining I'm telling you!

{{< figure src="keep-calm.png" caption="Keep Calm" >}}

## Complete filebeat.yml file

For the record, here is a copy of the complete `filebeat.yml` I used:

```yml
filebeat.prospectors:
- input_type: stdin
  document_type: talk

processors:
- drop_event:
    when:
      regexp:
          message: "^;.*$"

output.elasticsearch:
output.elasticsearch:
  hosts: ["your-cluster-id.us-east-1.aws.found.io:9243"]
  protocol: "https"
  username: "elastic"
  password: "changeme"
  index: "talks"
  pipeline: "talks"
```

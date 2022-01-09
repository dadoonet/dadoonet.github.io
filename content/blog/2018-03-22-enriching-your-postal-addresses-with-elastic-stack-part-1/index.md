---
title: "Enriching your postal addresses with Elastic stack - part 1"
#description: 
toc: true
authors:
  - David Pilato
tags:
  - logstash
  - elasticsearch
categories:
  - tutorial
series:
  - bano
date: 2018-03-22 15:31:49 +0100
lastmod: 2018-03-22 15:31:49 +0100
featuredImage: assets/images/series/bano.png
draft: false
aliases:
  - /blog/2018/03/22/enriching-your-postal-addresses-with-elastic-stack-part-1/
---

This blog post is part of a series of 3:

* [Importing Bano dataset with Logstash]({{< ref "2018-03-22-enriching-your-postal-addresses-with-elastic-stack-part-1" >}})
* [Using Logstash to lookup for addresses in Bano index]({{< ref "2018-03-23-enriching-your-postal-addresses-with-elastic-stack-part-2" >}})
* [Using Logstash to enrich an existing dataset with Bano]({{< ref "2018-03-24-enriching-your-postal-addresses-with-elastic-stack-part-3" >}})

I'm not really sure why, but I love the postal address use case.
Often in my career I had to deal with that information.
Very often the information is not well formatted so it's hard to find the information you need when you have as an input a not so nice dataset.

Let's take a simple use case. I have a user in my database like:

```json
{
  "name": "Joe Smith",
  "address": {
    "number": "23",
    "street_name": "r verdiere",
    "city": "rochelle",
    "country": "France"
  }
}
```

If you live in France you might notice that this address is fairly incomplete.
If we want to send a letter to `Joe`, it's going to be hard.

Also, I'd really like to display on a map, where my customers are located in France.

On the other way around, let's say I'm collecting data from a mobile application where I'm meeting friends and I'd like to remember automatically what was the address of the location last time we met. Basically I have data like:

```json
{
  "name": "Joe Smith",
  "location": {
    "lat": 46.15735,
    "lon": -1.1551
  }
}
```

And I would like to get back the postal address matching this location.

What can we do for that?

We need something to enrich the existing data by fixing the address and providing actual coordinates or the other way back.

<!-- more -->

## Bano

We can use something like the [Google Map API](https://developers.google.com/maps/) for that and do an external call anytime we need, but I see 2 major pain points here:

* We need to communicate with an external service and may be your company policy does not allow sending to an internet service some private data like your customers data.
* You might suffer from some latency anytime you want to call that external service on which you can't really have any knob to make it faster. Speed light is speed light and crossing the ocean may be will always include some latency.

We need something local then. In France, we are super lucky because we have a public dataset named [BANO](http://openstreetmap.fr/bano) as `Base d'Adresses NatiOnale` (National Address Database) provided under the [Open Street Map](http://openstreetmap.fr) umbrella.

This project exports everyday [the list of known addresses](http://bano.openstreetmap.fr/data/) anywhere in France. Here is an extraction of what you can have:

```sh
-rw-r--r--@ 1 dpilato  staff   11183891 27 nov 02:03 bano-88.csv
-rw-r--r--@ 1 dpilato  staff   25014545 27 nov 02:04 bano-85.csv
-rw-r--r--@ 1 dpilato  staff    3888078 27 nov 02:04 bano-971.csv
-rw-r--r--@ 1 dpilato  staff   12107391 27 nov 02:04 bano-92.csv
-rw-r--r--@ 1 dpilato  staff    3443396 27 nov 02:04 bano-972.csv
-rw-r--r--@ 1 dpilato  staff    1218424 27 nov 02:05 bano-973.csv
-rw-r--r--@ 1 dpilato  staff     455986 27 nov 02:05 bano-976.csv
-rw-r--r--@ 1 dpilato  staff   21634994 27 nov 02:05 bano-91.csv
-rw-r--r--@ 1 dpilato  staff   15848802 27 nov 02:05 bano-93.csv
-rw-r--r--@ 1 dpilato  staff   14779208 27 nov 02:05 bano-94.csv
-rw-r--r--@ 1 dpilato  staff   17515805 27 nov 02:06 bano-95.csv
-rw-r--r--@ 1 dpilato  staff   17713007 27 nov 02:07 bano-974.csv
-rw-r--r--@ 1 dpilato  staff   71133336 27 nov 02:08 bano-59.csv
```

Each CSV file correspond to a subdivision of France that we call a department. It's like a region but smaller. Bigger than a city though.

### Download Bano CSV files

I wrote a simple shell script to download locally all the files I needed but you can directly consume from Logstash one CSV file with an http_poller plugin.

```sh
#!/bin/bash
set -e

download () {
  wget http://bano.openstreetmap.fr/data/$1 --timestamping --directory-prefix=bano-data -c --no-verbose --show-progress
}

DEPTS=95
for i in {01..19} $(seq 21 $DEPTS) {971..974} {976..976} ; do 
  DEPT=$(printf %02d $i)
  echo Downloading bano department $DEPT
  download bano-$DEPT.csv
done
```

> What is happening with numbers here?

Well, France is a moving country. Sometimes departments are merged all together which probably explains why we don't have anymore a department `20`.
Some department of France are also located far far away from the french metropolitan area. Those are labelled as `97x`.

Nothing can be simple in France 😅.

### Loading elasticsearch

Let's now parse the data and load that in elasticsearch, so we will be able to search for addresses.

If we look at one of the CSV file, we can see:

```txt
976030950H-26,26,RUE DISMA,97660,Bandrélé,CAD,-12.891701,45.202652
976030950H-28,28,RUE DISMA,97660,Bandrélé,CAD,-12.891900,45.202700
976030950H-30,30,RUE DISMA,97660,Bandrélé,CAD,-12.891781,45.202535
976030950H-32,32,RUE DISMA,97660,Bandrélé,CAD,-12.892005,45.202564
976030950H-3,3,RUE DISMA,97660,Bandrélé,CAD,-12.892444,45.202135
976030950H-34,34,RUE DISMA,97660,Bandrélé,CAD,-12.892068,45.202450
976030950H-4,4,RUE DISMA,97660,Bandrélé,CAD,-12.892446,45.202367
976030950H-5,5,RUE DISMA,97660,Bandrélé,CAD,-12.892461,45.202248
976030950H-6,6,RUE DISMA,97660,Bandrélé,CAD,-12.892383,45.202456
976030950H-8,8,RUE DISMA,97660,Bandrélé,CAD,-12.892300,45.202555
976030950H-9,9,RUE DISMA,97660,Bandrélé,CAD,-12.892355,45.202387
976030951J-103,103,RTE NATIONALE 3,97660,Bandrélé,CAD,-12.893639,45.201696
  \_ ID         |   \_ Street Name |         \     \_ Source  \_ Geo point
                |                  |          \
                |_ Street Number   |_ Zipcode  \_ City Name
```

#### Writing the Logstash pipeline

As everytime I'm writing a Logstash pipeline, I'm always starting with a basic configuration file, let's call it `bano-data.conf`:

```ruby
input { 
  stdin { } 
}

filter {
}

output {
  stdout { codec => json }
}
```

Let's run it:

```sh
head -1 | logstash-6.2.3/bin/logstash -f bano-data.conf
```

This gives something like:

```json
{ 
  "message":"976030951J-103,103,RTE NATIONALE 3,97660,Bandrélé,CAD,-12.893639,45.201696",
  "@timestamp":"2017-12-05T16:00:00.000PST", 
  "@version":1, 
  "host":"MacBook-Pro-David.local"
}
```

Let's add our `csv-filter` plugin as we already saw in [Exploring Capitaine Train dataset]({{< ref "2015-04-28-exploring-capitaine-train-dataset" >}}):

```ruby
csv {
  separator => ","
  columns => [
    "id","number","street_name","zipcode","city","source","latitude","longitude"
  ]
  remove_field => [ "message", "@version", "@timestamp", "host" ]
}
```

That's now producing:

```json
{ 
  "source":"CAD", 
  "id":"976030951J-103", 
  "number":"103", 
  "street_name":"RTE NATIONALE 3", 
  "zipcode":"97660", 
  "city":"Bandrélé", 
  "latitude":"-12.893639", 
  "longitude":"45.201696" 
}
```

Let's rename and convert some fields with the `mutate-filter` plugin:

```ruby
mutate {
  convert => { "longitude" => "float" }
  convert => { "latitude" => "float" }
  rename => {
    "longitude" => "[location][lon]"
    "latitude" => "[location][lat]"
    "number" => "[address][number]"
    "street_name" => "[address][street_name]"
    "zipcode" => "[address][zipcode]"
    "city" => "[address][city]"
  }
  replace => {
    "region" => "${REGION}"
  }
}
```

I'll explain a bit later where this `${REGION}` value is coming from.
But basically, I want to store here the department number the address is coming from.

This now gives:

```json
{ 
  "source":"CAD",
  "id":"976030951J-103",
  "region":"976",
  "address":{
    "number":"103", 
    "street_name":"RTE NATIONALE 3", 
    "zipcode":"97660", 
    "city":"Bandrélé"
  },
  "location":{
    "lat":-12.893639,
    "lon":45.201696
  }
}
```

We are almost done. Let's load elasticsearch now by adding our `elasticsearch-output` plugin:

```ruby
elasticsearch {
  "template_name" => "bano"
  "template_overwrite" => true
  "template" => "bano.json"
  "index" => ".bano-${REGION}"
  "document_id" => "%{[id]}"
}
```

Few things to explore in that last code sample:

* We are providing an index template for elasticsearch.
* We are setting the `_index` name to `.bano-${REGION}`. Again, we will explain later where this value is coming from.
* We are setting the document `_id` to the `id` provided within the bano dataset.

#### Bano index template

As you can notice, we are using an index template here named `bano` which is loaded by logstash anytime the `elasticsearch` plugin starts. Using `template_overwrite` helps overwriting the template anytime you want to change some rules. Of course, overwriting an index template does not update the existing indices. So basically you will need to drop the existing indices and parse again the bano data with Logstash.

Let's describe what this index template contains:

```json
{
  "template": ".bano-*", 
  "settings": { /* ... */ },
  "mappings": { /* ... */ },
  "aliases" : { /* ... */ }
}
```

This template will be applied anytime we have an index which name starts with  `.bano-`. We will then apply 3 following parts:

* `settings`: for index settings
* `mappings`: for document mapping
* `aliases`: for virtual indices (aka aliases)

The `settings` part is the following:

```json
{
  "template": ".bano-*", 
  "settings": {
    "index.number_of_shards": 1, 
    "index.number_of_replicas": 0,
    "index.analysis": {
      "analyzer": {
        "bano_analyzer": {  
          "type": "custom", 
          "tokenizer": "standard", 
          "filter" : [ "lowercase", "asciifolding" ]
        },
        "bano_street_analyzer": {
          "type": "custom", 
          "tokenizer": "standard", 
          "filter" : [ "lowercase", "asciifolding", "bano_synonym" ]
        }
      },
      "filter": {
        "bano_synonym": {
          "type": "synonym",
          "synonyms": [
            "bd => boulevard",
            "av => avenue",
            "r => rue",
            "rte => route"
          ]
        }
      }
    }
  },
  "mappings": { /* ... */ },
  "aliases" : { /* ... */ }
}
```

Here, we want one single shard per index (per department) which is more than enough. We don't want replicas as we will be running that on a single node. Note that the number of replicas can be set dynamically so after the ingestion of the bano data, we can always increase this value if we decide to have a bigger cluster.

We are then defining two analyzers. The first one, `bano_analyzer`, is a kind of a `standard` analyzer but with addition of an `asciifolding` token filter which will transform at index time and search time all the french diatrics like for example `é`, `è`, `ê` to their ascii equivalent value: `e`.

The second analyzer named `bano_street_analyzer` adds also some synonyms. Indeed, when I looked at some values we have in the bano dataset, I found that sometimes the same type of street has different type names. Like `av` for `avenue`.
The `synonym` token filter will definitely help to normalize that.

As it will be used also at search time, it will help if for example a call center operator type `bd` instead of `boulevard` as it will be also normalized to the right value.

The `mappings` part is the following:

```json
{
  "template": ".bano-*", 
  "settings": { /* ... */ },
  "mappings": {
    "doc": {
      "properties" : {
        "address": {
          "properties" : {
            "city": {
              "type": "text",
              "analyzer": "bano_analyzer",
              "fields": {
                "keyword": {
                  "type": "keyword"
                }
              }
            },
            "number": {
              "type": "keyword"
            },
            "street_name": {
              "type": "text",
              "analyzer": "bano_street_analyzer"
            },
            "zipcode": {
              "type": "keyword"
            }
          }
        },
        "region": {
          "type": "keyword"
        },
        "id": {
          "type": "keyword"
        },
        "source": {
          "type": "keyword"
        },
        "location": {
          "type": "geo_point"
        }
      }
    }
  },
  "aliases" : { /* ... */ }
}
```

Everything is pretty much obvious here. For some fields we are using a `keyword` data type as we just want to run exact match or aggregations.
The `street_name` is using the `bano_street_analyzer` we saw before.
`city` is indexed twice:

* As `city` field to perform full text search on it.
* As `city.keyword` field to perform a terms aggregation on it.

Finally `location` is a `geo_point` type.

The `aliases` part is the following:

```json
{
  "template": ".bano-*", 
  "settings": { /* ... */ },
  "mappings": { /* ... */ },
  "aliases" : {
    ".bano" : {}
  }
}
```

It means that if we don't know the department when we have to search, we can search in `.bano` virtual index which will behind the scene query all bano indices. Of course, we could have been using a wildcard when searching as well like:

```json
GET .bano-*/_search
```

#### Loading data

To launch our importation, let's write a shell script:

```sh
import_region () {
    export REGION=$1
    FILE=bano-data/bano-$REGION.csv
    curl -XDELETE localhost:9200/.bano-$REGION?pretty
    cat $FILE | logstash-6.2.3/bin/logstash -f bano-data.conf
}

DEPTS=95
for i in {01..19} $(seq 21 $DEPTS) {971..974} {976..976} ; do
    DEPT=$(printf %02d $i)
    import_region $DEPT
done
```

We are using here the same tricks for the strange department numbers.
In `import_region` we are exporting the department number as `REGION` system property which logstash is then able to use.

For each CSV file, we basically:

* Remove the existing index if any
* cat the content of the file and send the content to Logstash

We could have been a bit smarter and we could have been using instead an `http` input plugin which just waits for documents coming on port `8080`. We will cover that in a next section.

It took something like 2 hours and a half to inject the data on my laptop but I now have data ready...

## Bano statistics

So what do we have now?

```json
GET _cat/indices/.bano*?v&h=index,docs.count,store.size
```

Gives (only the first lines are shown here):

```txt
index     docs.count store.size
.bano-80      204930     20.7mb
.bano-50      160820     16.4mb
.bano-60      241276     24.6mb
.bano-34      308056     30.9mb
```

How many addresses do we have?

```json
GET .bano/_search
{
  "size": 0
}
```

Gives:

```json
{
  "took": 24,
  "timed_out": false,
  "_shards": {
    "total": 99,
    "successful": 99,
    "skipped": 0,
    "failed": 0
  },
  "hits": {
    "total": 16402853,
    "max_score": 0,
    "hits": []
  }
}
```

So we have `16.402.853` addresses.

Let's look at that from Kibana. Here I built really simple visualizations.

{{< figure src="bano-regions.png" caption="Distribution of Bano addresses by department number" >}}

{{< figure src="bano-fr.png" caption="Map of Bano addresses for France Metropolitan" >}}

{{< figure src="bano-dom.png" caption="Map of Bano addresses for some France Overseas Departments" >}}

{{< figure src="bano-lr.png" caption="Map of Bano addresses near by La Rochelle" >}}

{{< figure src="bano-cities.png" caption="Top cities (in number of known addresses" >}}

No surprise in this list. It's common to say that biggest cities in term of population are:

* Paris
* Marseille
* Toulouse
* Bordeaux
* Nantes

## Next steps

Have a look at the [next post]({{< ref "2018-03-23-enriching-your-postal-addresses-with-elastic-stack-part-2" >}}) to see how you can now use that dataset to perform address correction and transformation.

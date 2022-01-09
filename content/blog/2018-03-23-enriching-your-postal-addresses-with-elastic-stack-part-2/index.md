---
title: "Enriching your postal addresses with Elastic stack - part 2"
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
date: 2018-03-23 10:20:28 +0200
lastmod: 2018-03-23 10:20:28 +0200
# featuredImage: assets/images/covers/new/logstash.png
draft: false
aliases:
  - /blog/2018/03/23/enriching-your-postal-addresses-with-elastic-stack-part-2/
---

This blog post is part of a series of 3:

* [Importing Bano dataset with Logstash]({{< ref "2018-03-22-enriching-your-postal-addresses-with-elastic-stack-part-1" >}})
* [Using Logstash to lookup for addresses in Bano index]({{< ref "2018-03-23-enriching-your-postal-addresses-with-elastic-stack-part-2" >}})
* [Using Logstash to enrich an existing dataset with Bano]({{< ref "2018-03-24-enriching-your-postal-addresses-with-elastic-stack-part-3" >}})

In the [previous post]({{< ref "2018-03-22-enriching-your-postal-addresses-with-elastic-stack-part-1" >}}), we described how we indexed data coming from the [BANO project](http://openstreetmap.fr/bano) so we now have indices containing all the french postal addresses.

Let's see what we can do now with this dataset.

<!-- more -->

## Searching for addresses

Good. Can we use a search engine to search?

```json
GET .bano/_search?search_type=dfs_query_then_fetch
{
  "size": 1,
  "query": {
    "bool": {
      "should": [
        {
          "match": {
            "address.number": "23"
          }
        },
        {
          "match": {
            "address.street_name": "r verdiere"
          }
        },
        {
          "match": {
            "address.city": "rochelle"
          }
        }

      ]
    }
  }
}
```

This gives us back:

```json
{
  "took": 170,
  "timed_out": false,
  "_shards": {
    "total": 99,
    "successful": 99,
    "skipped": 0,
    "failed": 0
  },
  "hits": {
    "total": 10380977,
    "max_score": 23.681055,
    "hits": [
      {
        "_index": ".bano-17",
        "_type": "doc",
        "_id": "173008250H-23",
        "_score": 23.681055,
        "_source": {
          "address": {
            "zipcode": "17000",
            "number": "23",
            "city": "La Rochelle",
            "street_name": "Rue Verdière"
          },
          "location": {
            "lon": -1.155167,
            "lat": 46.157353
          },
          "id": "173008250H-23",
          "source": "C+O",
          "region": "17"
        }
      }
    ]
  }
}
```

This takes `170ms` on my machine but it can be faster if we know in advance the department number. So we can optimize the number of shards to hit:

```json
GET .bano-17/_search?search_type=dfs_query_then_fetch
{
  // Same query
}
```

It now gives the same result but much faster:

```json
{
  "took": 6,
  "timed_out": false,
  "_shards": {
    "total": 1,
    "successful": 1,
    "skipped": 0,
    "failed": 0
  },
  "hits": {
    "total": 212872,
    "max_score": 18.955963,
    "hits": [
      {
        "_index": ".bano-17",
        "_type": "doc",
        "_id": "173008250H-23",
        "_score": 18.955963,
        "_source": {
          "address": {
            "zipcode": "17000",
            "number": "23",
            "city": "La Rochelle",
            "street_name": "Rue Verdière"
          },
          "location": {
            "lon": -1.155167,
            "lat": 46.157353
          },
          "id": "173008250H-23",
          "source": "C+O",
          "region": "17"
        }
      }
    ]
  }
}
```

Note that this query is finding `212.872` addresses but the most relevant one is the one we are searching for. Yeah, relevancy is one of the key points of a search engine.

### Searching by geo point

We know that we can also have to search by a geo point.

Let's do a naive approach first. We search for all the points in the dataset but we want to sort by distance from the point we have as an input. Which means that the first point we are getting back is the closest address:

```json
GET .bano/_search
{
  "size": 1, 
  "sort": [
    {
      "_geo_distance": {
        "location": {
          "lat": 46.15735,
          "lon": -1.1551
        }
      }
    }
  ]
}
```

This gives:

```json
{
  "took": 403,
  "timed_out": false,
  "_shards": {
    "total": 99,
    "successful": 99,
    "skipped": 0,
    "failed": 0
  },
  "hits": {
    "total": 16402853,
    "max_score": null,
    "hits": [
      {
        "_index": ".bano-17",
        "_type": "doc",
        "_id": "173008250H-23",
        "_score": null,
        "_source": {
          "address": {
            "zipcode": "17000",
            "number": "23",
            "city": "La Rochelle",
            "street_name": "Rue Verdière"
          },
          "location": {
            "lon": -1.155167,
            "lat": 46.157353
          },
          "id": "173008250H-23",
          "source": "C+O",
          "region": "17"
        },
        "sort": [
          5.176690615711886
        ]
      }
    ]
  }
}
```

Few things to note here. First, we asked for:

```json
{
  "lat": 46.15735,
  "lon": -1.1551  
}
```

We are getting back another point. Of course, Bano does not have every single centimer but just addresses:

```json
{
  "lat": 46.157353,
  "lon": -1.155167
}
```

Second thing, the total number of hits we are doing the sort on: `16.402.853`, the full dataset that is. Which has a consequence on the response time: `403ms`.

We can easily assume that when we are looking for an address, we will most likely be able to find one in an area of may be 2 kilometers around the point. So instead of sorting all the points, we can just filter first by distance the dataset:

```json
GET .bano/_search
{
  "size": 1,
  "query": {
    "bool": {
      "filter": {
        "geo_distance": {
          "distance": "1km",
          "location": {
            "lat": 46.15735,
            "lon": -1.1551
          }
        }
      }
    }
  },
  "sort": [
    {
      "_geo_distance": {
        "location": {
          "lat": 46.15735,
          "lon": -1.1551
        }
      }
    }
  ]
}
```

This gives back the same point but with a different header:

```json
{
  "took": 45,
  "timed_out": false,
  "_shards": {
    "total": 99,
    "successful": 99,
    "skipped": 0,
    "failed": 0
  },
  "hits": {
    "total": 4467,
    "max_score": null,
    "hits": [ /* ... */ ]
  }
}
```

`45ms` because we dramatically reduced the number of points to sort to `4.467`.

And if we know the department, that can be even better:

```json
GET .bano-17/_search
{
  // Same query
}
```

We now have a really decent response time. Note that filesystem cache plays a great role here as well:

```json
{
  "took": 2,
  "timed_out": false,
  "_shards": {
    "total": 1,
    "successful": 1,
    "skipped": 0,
    "failed": 0
  }
}
```

So we know how to query the data.
Let's use all that to read an existing dataset and enrich it with Logstash.

## Building incrementally a Logstash enrichment pipeline

If you have been following this blog, I'm always starting with a default pipeline like this (`bano-enrich.conf` file):

```ruby
input { 
  stdin { } 
}

filter {
}

output {
  stdout { codec => rubydebug }
}
```

It's simple to use as you just the run:

```sh
head -1 mydata | bin/logstash -f bano-enrich.conf
```

So far so good. But what is the problem?

Anytime you change your configuration and you want to test it, you need to send the same command line again. Which is not an issue. Your terminal has probably an history :).

The problem is the time taken by Logstash to start the process (the JVM and Logstash initialization itself). On my laptop, it can take around 20 seconds.

And this is not super developer friendly in my opinion.

Let me share a small trick to make that better. Use the `http-input-plugin` instead:

```ruby
input {
  http { }
}
```

This will start an HTTP server running on 8080 port which you can use by running something like:

```sh
curl -XPOST "localhost:8080" -H "Content-Type: application/json" -d '{
  "test_case": "Address with text",
  "name": "Joe Smith",
  "address": {
    "number": "23",
    "street_name": "r verdiere",
    "city": "rochelle",
    "country": "France"
  }
}'
```

What is the difference? Well, because you are not using stdin, you can ask logstash to hot reload your pipeline anytime you save a new version of the file:

```sh
bin/logstash -r -f bano-enrich.conf
```

Then, when you update the `bano-enrich.conf`, you can see in logs:

```txt
[2018-03-24T11:06:17,680][INFO ][logstash.pipelineaction.reload] Reloading pipeline {"pipeline.id"=>:main}
[2018-03-24T11:06:18,007][INFO ][logstash.pipeline        ] Pipeline has terminated {:pipeline_id=>"main", :thread=>"#<Thread:0x457a565f run>"}
[2018-03-24T11:06:18,082][INFO ][logstash.pipeline        ] Starting pipeline {:pipeline_id=>"main", "pipeline.workers"=>4, "pipeline.batch.size"=>125, "pipeline.batch.delay"=>50}
[2018-03-24T11:06:18,122][INFO ][logstash.pipeline        ] Pipeline started succesfully {:pipeline_id=>"main", :thread=>"#<Thread:0x6d4b91c4 sleep>"}
[2018-03-24T11:06:18,133][INFO ][logstash.agent           ] Pipelines running {:count=>2, :pipelines=>[".monitoring-logstash", "main"]}
```

So less than 1 second to reload the pipeline. That's a huge win!

## Sending our first data

Let's call again our sample. I actually created a `samples.sh` script which allows me to add more use cases:

```sh
curl -XPOST "localhost:8080" -H "Content-Type: application/json" -d '{
  "test_case": "Address with text",
  "name": "Joe Smith",
  "address": {
    "number": "23",
    "street_name": "r verdiere",
    "city": "rochelle",
    "country": "France"
  }
}'
```

Running it gives:

```ruby
{
     "test_case" => "Address with text",
      "@version" => "1",
          "host" => "0:0:0:0:0:0:0:1",
    "@timestamp" => 2018-03-24T09:09:58.749Z,
          "name" => "Joe Smith",
       "address" => {
               "city" => "rochelle",
        "street_name" => "r verdiere",
             "number" => "23",
            "country" => "France"
    },
       "headers" => {
         "content_length" => "158",
         "request_method" => "POST",
           "content_type" => "application/json",
              "http_host" => "localhost:8080",
           "request_path" => "/",
        "http_user_agent" => "curl/7.54.0",
            "request_uri" => "/",
           "http_version" => "HTTP/1.1",
            "http_accept" => "*/*"
    }
}
```

## Calling Elasticsearch with addresses

We saw at the begining of this post how we can query elasticsearch to get meaningful data from our bano dataset.

Let's just connect it with logstash by using the `elasticsearch-filter-plugin`:

```ruby
elasticsearch {
  query_template => "search-by-name.json"
  index => ".bano"
  fields => {
    "location" => "[location]"
    "address" => "[address]"
  }
  remove_field => ["headers", "host", "@version", "@timestamp"]
}
```

Let's explain some new parameters we have never spoke about.

`query_template` helps to write an elasticsearch query within an external file instead of having to flatten it inside the logstash configuration. That makes the code more readable but has a drawback. When you update the `search-by-name.json` Logstash [does not detect this "change"](https://github.com/logstash-plugins/logstash-filter-elasticsearch/issues/90) and does not update the pipeline. So have to fake it by doing a super small change in the pipeline to be reloading again.

Here is the content of the `search-by-name.json` file:

```json
{
  "size": 1,
  "query":{
    "bool": {
      "should": [
        {
          "match": {
            "address.number": "%{[address][number]}"
          }
        },
        {
          "match": {
            "address.street_name": "%{[address][street_name]}"
          }
        },
        {
          "match": {
            "address.city": "%{[address][city]}"
          }
        }
      ]
    }
  }
}
```

This looks familiar right?

`index` is the elasticsearch index or alias we want to query. Here we want to query `.bano` alias.

`fields` are the fields we want to extract from the elasticsearch response to populate our "event" (or document if you prefer).

Running again `samples.sh` gives:

```ruby
{
    "test_case" => "Address with text",
     "location" => {
        "lon" => -1.155167,
        "lat" => 46.157353
    },
         "name" => "Joe Smith",
      "address" => {
               "city" => "La Rochelle",
        "street_name" => "Rue Verdière",
            "zipcode" => "17000",
             "number" => "23"
    }
}
```

Great! It works!

## Calling Elasticsearch with geo points

But we have another use case. We also want to be able to search by location with a document like the following which I add to `samples.sh` script:

```sh
curl -XPOST "localhost:8080" -H "Content-Type: application/json" -d '{
  "test_case": "Address with geo",
  "location": {
    "lat": 46.15735,
    "lon": -1.1551
  }
}'
```

Running it gives:

```ruby
{
    "test_case" => "Address with geo",
     "location" => {
        "lat" => 46.15735,
        "lon" => -1.1551
    }
}
```

We need to add some conditionals in the pipeline so we can now search using another `query_template`:

```ruby
if [location][lat] and [location][lon] {
  # We search by distance in that case
  elasticsearch {
    query_template => "search-by-geo.json"
    index => ".bano"
    fields => {
      "location" => "[location]"
      "address" => "[address]"
    }
    remove_field => ["headers", "host", "@version", "@timestamp"]
  }
} else {
  # We search by address in that case
  elasticsearch {
    query_template => "search-by-name.json"
    index => ".bano"
    fields => {
      "location" => "[location]"
      "address" => "[address]"
    }
    remove_field => ["headers", "host", "@version", "@timestamp"]
  }
}
```

The `search-by-geo.json` template is also looking familiar:

```json
{
  "size": 1,
  "query": {
    "bool": {
      "filter": {
        "geo_distance": {
          "distance": "1km",
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
  ]
}
```

Running our samples again gives now:

```ruby
{
    "test_case" => "Address with geo",
     "location" => {
        "lon" => -1.155167,
        "lat" => 46.157353
    },
      "address" => {
               "city" => "La Rochelle",
        "street_name" => "Rue Verdière",
            "zipcode" => "17000",
             "number" => "23"
    }
}
```

## Optimizing the queries

We have also seen that it can be really unefficient to read the whole dataset every time. If we have the department number, we can probably help elasticsearch by querying the right index instead of all indices.

Let's assume that the zipcode or part of the zipcode is provided in the input event. For example, let's add the following use cases to our `samples.sh`:

```sh
curl -XPOST "localhost:8080" -H "Content-Type: application/json" -d '{
  "test_case": "Address with geo and zipcode",
  "address": {
    "zipcode": "17000"
  },
  "location": {
    "lat": 46.15735,
    "lon": -1.1551
  }
}'
curl -XPOST "localhost:8080" -H "Content-Type: application/json" -d '{
  "test_case": "Address with geo and partial zipcode",
  "address": {
    "zipcode": "17"
  },
  "location": {
    "lat": 46.15735,
    "lon": -1.1551
  }
}'
```

Let's check first (before calling elasticsearch) if we have a zipcode and if so, let's build a `dept` temporary field which we truncate to keep only the 2 first digits. This is the department number in France:

```ruby
if [address][zipcode] {
  mutate { add_field => { "dept" => "%{[address][zipcode]}" } }
  truncate { 
    fields => ["dept"]
    length_bytes => 2
  }
}
```

Then, let's create an `index_suffix` field:

```ruby
mutate { add_field => { "index_suffix" => "-%{dept}" } }
```

But if there is no `zipcode`, we need to add some default values:

```ruby
else {
  mutate { add_field => { "dept" => "" } }
  mutate { add_field => { "index_suffix" => "" } }
}
```

So far, so good. But wait, I mentioned that nothing can be that simple in France. And yeah... We have departments with 3 digits! o_O

Fortunately, they ate all starting with `97`. So we need to take that into account as well:

```ruby
if [address][zipcode] {
  mutate { add_field => { "dept" => "%{[address][zipcode]}" } }
  truncate { 
    fields => ["dept"]
    length_bytes => 2
  }
  if [dept] == "97" {
    mutate { replace => { "dept" => "%{[address][zipcode]}" } }
    truncate { 
      fields => ["dept"]
      length_bytes => 3
    }
  }
  mutate { add_field => { "index_suffix" => "-%{dept}" } }
} else {
  mutate { add_field => { "dept" => "" } }
  mutate { add_field => { "index_suffix" => "" } }
}
```

We can now change the index name with:

```ruby
index => ".bano%{index_suffix}"
```

And also remove to temporary fields we created:

```ruby
remove_field => ["headers", "host", "@version", "@timestamp", "index_suffix", "dept"]
```

At the end we check that we have no regression, specifically with department `974`

```sh
curl -XPOST "localhost:8080" -H "Content-Type: application/json" -d '{
  "test_case": "Address with geo and zipcode in 974",
  "address": {
    "zipcode": "97400"
  },
  "location": {
    "lat": -21.214204,
    "lon": 55.361034
  }
}'
```

Which indeed gives us the right value:

```ruby
{
    "test_case" => "Address with geo and zipcode in 974",
     "location" => {
        "lon" => 55.361034,
        "lat" => -21.214204
    },
      "address" => {
               "city" => "Les Avirons",
        "street_name" => "Chemin des Acacias",
            "zipcode" => "97425",
             "number" => "13"
    }
}
```

## Next steps

Have a look at the [next post]({{< ref "2018-03-24-enriching-your-postal-addresses-with-elastic-stack-part-3" >}}) to see how you can now use this technique to enrich your existing data.

## The full logtstash pipeline

Here is the full pipeline I ended up with:

```ruby
input {
  http { }
}

filter {
  if [address][zipcode] {
    mutate { add_field => { "dept" => "%{[address][zipcode]}" } }
    truncate { 
      fields => ["dept"]
      length_bytes => 2
    }
    if [dept] == "97" {
      mutate { replace => { "dept" => "%{[address][zipcode]}" } }
      truncate { 
        fields => ["dept"]
        length_bytes => 3
      }
    }
    mutate { add_field => { "index_suffix" => "-%{dept}" } }
  } else {
    mutate { add_field => { "dept" => "" } }
    mutate { add_field => { "index_suffix" => "" } }
  }

  if [location][lat] and [location][lon] {
    elasticsearch {
      query_template => "search-by-geo.json"
      index => ".bano"
      fields => {
        "location" => "[location]"
        "address" => "[address]"
      }
      remove_field => ["headers", "host", "@version", "@timestamp", "index_suffix", "dept"]
    }
  } else {
    elasticsearch {
      query_template => "search-by-name.json"
      index => ".bano"
      fields => {
        "location" => "[location]"
        "address" => "[address]"
      }
      remove_field => ["headers", "host", "@version", "@timestamp", "index_suffix", "dept"]
    }
  }
}

output {
  stdout { codec => rubydebug }
}
```

---
title: "Reindex elasticsearch with Logstash"
#description: 
toc: true
authors:
  - David Pilato
tags:
  - elasticsearch
  - logstash
  - reindex
categories:
  - tutorial
date: 2015-05-20 11:03:29 +0200
# featuredImage: blog/2016-03-17-and-the-beats-go-on/beats.png
draft: false
aliases:
  - /blog/2015/05/20/reindex-elasticsearch-with-logstash/
---

Sometimes, you would like to reindex your data to change your mapping or to change your index settings or to move from one server to another or to one cluster to another (think about multiple data centers for example).

For the later you can use [Snapshot and Restore](https://www.elastic.co/guide/en/elasticsearch/reference/current/modules-snapshots.html) feature but if you need to change any index settings, you need something else.

With Logstash [1.5.0](https://www.elastic.co/blog/logstash-1-5-0-ga-released), you can now do it super easily using [elasticsearch input](https://www.elastic.co/guide/en/logstash/current/plugins-inputs-elasticsearch.html) and [elasticsearch output](https://www.elastic.co/guide/en/logstash/current/plugins-outputs-elasticsearch.html).

Let's do it!

<!-- more -->

## The old cluster

Let's say you have already elasticsearch 1.5.2 up and running on `localhost:9200` with cluster name `old`.

```sh
bin/elasticsearch --cluster.name=old
```

The cluster has an existing index named `person`. It has 5 shards and 1 million documents.

{{< figure src="sense01.png" caption="sense" >}}

## The new cluster

Let's start a new cluster. It will run on `localhost:9201` with cluster name `new`:

```sh
bin/elasticsearch --cluster.name=new
```

It's empty:

```sh
curl -XGET "http://localhost:9201/person"
```

```json
{
   "error": "IndexMissingException[[person] missing]",
   "status": 404
}
```

## Installing logstash

So let's download and install logstash 1.5.0:

```sh
wget http://download.elastic.co/logstash/logstash/logstash-1.5.0.tar.gz
tar xzf logstash-1.5.0.tar.gz
cd logstash-1.5.0
```

Now we can define our logstash config file `logstash.conf`:

```ruby
input {
  # We read from the "old" cluster
  elasticsearch {
    hosts => [ "localhost" ]
    port => "9200"
    index => "person"
    size => 500
    scroll => "5m"
    docinfo => true
  }
}

output {
  # We write to the "new" cluster
  elasticsearch {
    host => "localhost"
    port => "9201"
    protocol => "http"
    index => "%{[@metadata][_index]}"
    index_type => "%{[@metadata][_type]}"
    document_id => "%{[@metadata][_id]}"
  }
  # We print dots to see it in action
  stdout {
    codec => "dots"
  }
}
```

## Run and fix

Run it:

```sh
bin/logstash -f logstash.conf
```

### Check and fix documents

What does it produce?

```sh
curl -XGET "http://localhost:9200/person/person/AU1wqyQWZJKU8OibfxgH"
```

```json
{
   "_index": "person",
   "_type": "person",
   "_id": "AU1wqyQWZJKU8OibfxgH",
   "_version": 1,
   "found": true,
   "_source": {
      "name": "Tali Elyne",
      "dateOfBirth": "1955-05-03",
      "gender": "female",
      "children": 2,
      "marketing": {
         "cars": null,
         "shoes": null,
         "toys": null,
         "fashion": null,
         "music": null,
         "garden": null,
         "electronic": null,
         "hifi": null,
         "food": 846
      },
      "address": {
         "country": "Germany",
         "zipcode": "0099",
         "city": "Bonn",
         "countrycode": "DE",
         "location": [
            7.075943707068682,
            50.72883500730124
         ]
      }
   }
}
```

Let's compare that with the other cluster:

```sh
curl -XGET "http://localhost:9201/person/person/AU1wqyQWZJKU8OibfxgH"
```

```json
{
   "_index": "person",
   "_type": "person",
   "_id": "AU1wqyQWZJKU8OibfxgH",
   "_version": 1,
   "found": true,
   "_source": {
      "name": "Tali Elyne",
      "dateOfBirth": "1955-05-03",
      "gender": "female",
      "children": 2,
      "marketing": {
         "cars": null,
         "shoes": null,
         "toys": null,
         "fashion": null,
         "music": null,
         "garden": null,
         "electronic": null,
         "hifi": null,
         "food": 846
      },
      "address": {
         "country": "Germany",
         "zipcode": "0099",
         "city": "Bonn",
         "countrycode": "DE",
         "location": [
            7.075943707068682,
            50.72883500730124
         ]
      },
      "@version": "1",
      "@timestamp": "2015-05-20T09:53:44.089Z"
   }
}
```

Logstash has just added `@version` and `@timestamp` fields. We might want to filter them out using [Mutate filter plugin](http://www.elastic.co/guide/en/logstash/current/plugins-filters-mutate.html) and its [remove_field](http://www.elastic.co/guide/en/logstash/current/plugins-filters-mutate.html#plugins-filters-mutate-remove_field):

```ruby
filter {
  mutate {
    remove_field => [ "@timestamp", "@version" ]
  }
}
```

### Check and fix mapping

Actually, logstash reads here the `_source` field from existing documents and reinject them directly into a new cluster. But logstash does not take care at all about mappings.

If we compare the old mapping and the new one, here is what we get:

```sh
curl -XGET "http://localhost:9200/person/person/_mapping"
```

```json
{
   "person": {
      "mappings": {
         "person": {
            "properties": {
               "address": {
                  "properties": {
                     "city": {
                        "type": "string",
                        "index": "not_analyzed"
                     },
                     "country": {
                        "type": "string",
                        "index": "not_analyzed"
                     },
                     "countrycode": {
                        "type": "string",
                        "index": "not_analyzed"
                     },
                     "location": {
                        "type": "geo_point"
                     },
                     "zipcode": {
                        "type": "string"
                     }
                  }
               },
               "children": {
                  "type": "long"
               },
               "dateOfBirth": {
                  "type": "date",
                  "format": "dateOptionalTime"
               },
               "gender": {
                  "type": "string",
                  "index": "not_analyzed"
               },
               "marketing": {
                  "properties": {
                     "cars": {
                        "type": "long"
                     },
                     "electronic": {
                        "type": "long"
                     },
                     "fashion": {
                        "type": "long"
                     },
                     "food": {
                        "type": "long"
                     },
                     "garden": {
                        "type": "long"
                     },
                     "hifi": {
                        "type": "long"
                     },
                     "music": {
                        "type": "long"
                     },
                     "shoes": {
                        "type": "long"
                     },
                     "toys": {
                        "type": "long"
                     }
                  }
               },
               "name": {
                  "type": "string"
               }
            }
         }
      }
   }
}
```

```sh
curl -XGET "http://localhost:9201/person/person/_mapping"
```

```json
{
   "person": {
      "mappings": {
         "person": {
            "properties": {
               "address": {
                  "properties": {
                     "city": {
                        "type": "string"
                     },
                     "country": {
                        "type": "string"
                     },
                     "countrycode": {
                        "type": "string"
                     },
                     "location": {
                        "type": "double"
                     },
                     "zipcode": {
                        "type": "string"
                     }
                  }
               },
               "children": {
                  "type": "long"
               },
               "dateOfBirth": {
                  "type": "date",
                  "format": "dateOptionalTime"
               },
               "gender": {
                  "type": "string"
               },
               "marketing": {
                  "properties": {
                     "cars": {
                        "type": "long"
                     },
                     "electronic": {
                        "type": "long"
                     },
                     "fashion": {
                        "type": "long"
                     },
                     "food": {
                        "type": "long"
                     },
                     "garden": {
                        "type": "long"
                     },
                     "hifi": {
                        "type": "long"
                     },
                     "music": {
                        "type": "long"
                     },
                     "shoes": {
                        "type": "long"
                     },
                     "toys": {
                        "type": "long"
                     }
                  }
               },
               "name": {
                  "type": "string"
               }
            }
         }
      }
   }
}
```

We can see some obvious differences!

```json
 "location": {
    "type": "geo_point"
 }
```

```json
 "location": {
    "type": "double"
 }
```

So we can fix that by creating first the mapping we want to apply before indexing any data. At this point you can obviously change the original mapping to whatever you want. For example, change an analyzer.
You can also define new settings for your index. By default, elasticsearch creates 5 shards and 1 replica for each shard. But once again, you can control that:

```sh
curl -XDELETE "http://localhost:9201/person"
curl -XPUT "http://localhost:9201/person" -d'
{
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 0
  }
}'
curl -XPUT "http://localhost:9201/person/person/_mapping" -d'
{
  "person": {
    "properties": {
      "address": {
        "properties": {
          "city": {
            "type": "string",
            "index": "not_analyzed"
          },
          "country": {
            "type": "string",
            "index": "not_analyzed"
          },
          "countrycode": {
            "type": "string",
            "index": "not_analyzed"
          },
          "location": {
            "type": "geo_point"
          },
          "zipcode": {
            "type": "string"
          }
        }
      },
      "children": {
        "type": "long"
      },
      "dateOfBirth": {
        "type": "date",
        "format": "dateOptionalTime"
      },
      "gender": {
        "type": "string",
        "index": "not_analyzed"
      },
      "marketing": {
        "properties": {
          "cars": {
            "type": "long"
          },
          "electronic": {
            "type": "long"
          },
          "fashion": {
            "type": "long"
          },
          "food": {
            "type": "long"
          },
          "garden": {
            "type": "long"
          },
          "hifi": {
            "type": "long"
          },
          "music": {
            "type": "long"
          },
          "shoes": {
            "type": "long"
          },
          "toys": {
            "type": "long"
          }
        }
      },
      "name": {
        "type": "string"
      }
    }
  }
}'
```

And now, you can reindex your data again!

```sh
bin/logstash -f logstash.conf
```

{{< figure src="sense02.png" caption="sense" >}}

## Changing index or type names

Note that you can of course reindex in another index name if you want to, change the type name, even the id! 😀

```ruby
  elasticsearch {
    host => "localhost"
    port => "9201"
    protocol => "http"
    index => "europe_people"
    index_type => "someone"
    document_id => "%{[@metadata][_id]}"
  }
```

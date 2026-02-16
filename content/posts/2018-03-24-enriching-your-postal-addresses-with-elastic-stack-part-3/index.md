---
title: "Enriching your postal addresses with Elastic stack - part 3"
description: "In this blog post, we will see how to enrich an existing dataset with Bano."
author: David Pilato
avatar: /about/david_pilato.avif
tags:
  - beats
  - logstash
  - elasticsearch
categories:
  - tutorial
series:
  - bano
date: '2018-03-24'
nolastmod: true
draft: false
cover: featured.avif
aliases:
  - /blog/2018/03/24/enriching-your-postal-addresses-with-elastic-stack-part-3/
  - /blog/2018-03-24-enriching-your-postal-addresses-with-elastic-stack-part-3/
---

This blog post is part of a series of 3:

* [Importing Bano dataset with Logstash]({{< ref "2018-03-22-enriching-your-postal-addresses-with-elastic-stack-part-1" >}})
* [Using Logstash to lookup for addresses in Bano index]({{< ref "2018-03-23-enriching-your-postal-addresses-with-elastic-stack-part-2" >}})
* [Using Logstash to enrich an existing dataset with Bano]({{< ref "2018-03-24-enriching-your-postal-addresses-with-elastic-stack-part-3" >}})

In the [previous post]({{< ref "2018-03-23-enriching-your-postal-addresses-with-elastic-stack-part-2" >}}), we described how we can transform a postal address to a normalized one with also the geo location point or transform a geo location point to a postal address.

Let's say we have an existing dataset we want to enrich.

We will consider 3 scenarios:

* We have a CSV file
* We have a Relational Database, MySQL
* We have data in elasticsearch

Let's see how to enrich those datasets.

<!--more-->

## Enriching the CSV file

Anytime I have to read a file from Logstash, I actually like a lot using filebeat for that.

So I changed the input part of Logstash and instead of using an `http-input` plugin, I'm now using a `beat-input` plugin:

```ruby
input {
  beats {
    port => 5044
  }
}
```

In `filebeat.yml` file, I just configured this:

```yml
filebeat.prospectors:
- type: log
  paths:
    - /path/to/data/*.csv
  close_eof: true
output.logstash:
  hosts: ["localhost:5044"]
```

And I also added the x-pack monitoring to get some insights about the pipeline execution:

```yml
xpack.monitoring.enabled: true
xpack.monitoring.elasticsearch:
  hosts: ["localhost:9200"]
```

I created a naive load test like this where I'm doing 10 iterations fo processing the data:

```sh
cd filebeat*
time for i in `seq 1 10`;
do
  echo Launch $i
  rm data/registry ; ./filebeat --once
done
cd -
```

Here is the dataset I have as an input:

```sh
$ wc -l data/person_dataset.csv 
    2499 data/person_dataset.csv
```

So around 2500 lines.

Data looks like this:

```txt
3,Joe Smith,2000-11-15 23:00:00.000000,male,3,Paris,France,FR,47.26917867489252,-1.5316220472168889,44000
24,Nail Louisa,1980-05-02 22:00:00.000000,male,3,Nantes,France,FR,47.18584787904486,-1.6181576666034811,44000
36,Lison Nola,1985-09-23 22:00:00.000000,female,3,Nantes,France,FR,47.168657958748916,-1.5826229006751034,44000
45,Selena Sidonie,1964-10-18 23:00:00.000000,female,0,Paris,France,FR,48.82788569687699,2.2706737741614242,75000
```

We need to parse the data with a csv filter:

```ruby
csv {
  columns => ["id","name","dateOfBirth","gender","children","[address][city]","[address][country]","[address][countrycode]","[location][lat]","[location][lon]","[address][zipcode]"]
  convert => {
    "children" => "integer"
    "[location][lat]" => "float"
    "[location][lon]" => "float"
  }
  remove_field => ["host", "@version", "@timestamp","beat","source","tags","offset","prospector","message"]
}
```

Here, because we have as an input the geo location points, we will use the slowest strategy that we saw in the previous post: sorting by geo distance.

To make sure I'm slowing down that much the pipeline, I replaced the stdout codec with `dots`:

```ruby
output {
  stdout { codec => dots }
}
```

It took `3m3.842s` to do the 10 runs.
Which means around 18 seconds to enrich 2500 documents, so around 140 documents per second.

Not that bad.

If we look at the Logstash monitoring, we can see that the event latency is around 20-40ms.

{{< figure src="ls-monitoring.avif" caption="Logstash Monitoring" >}}

{{< figure src="ls-pipeline.avif" caption="Logstash Pipeline" >}}

We can easily spot the bottleneck.

{{< figure src="ls-es-filter.avif" caption="Elasticsearch Filter Plugin" >}}

 Doing lookups in Elasticsearch is indeed slowing down our process here but not that much I would say (34ms per event in average). Pretty much acceptable for an ETL operation. That's one of the reason doing slow operations in Logstash is much better than doing that in Elasticsearch directly as an ingest pipeline as the ingest pipeline is called during the indexing operation and having long running index operation will probably start to fill up the indexing queue of elasticsearch.

## Connecting other datasources

You can also imagine reading from another source than a CSV with filebeat but directly read your existing data which exist in a SQL database for example with a `jdbc-input` plugin.

It would look like something close to:

```ruby
jdbc {
  jdbc_driver_library => "mysql-connector-java-6.0.6.jar"
  jdbc_driver_class => "com.mysql.cj.jdbc.Driver"
  jdbc_connection_string => "jdbc:mysql://127.0.0.1:3306/person?useSSL=false"
  jdbc_user => "root"
  jdbc_password => ""
  schedule => "* * * * *"
  parameters => { "country" => "France" }
  statement => "SELECT p.id, p.name, p.dateOfBirth, p.gender, p.children, a.city, a.country, a.countrycode, a.lat, a.lon, a.zipcode FROM Person p, Address a WHERE a.id = p.address_id AND a.country = :country AND p.id > :sql_last_value"
   use_column_value => true
   tracking_column => "id"
}
```

We can also connect to elasticsearch an enrich existing data which are yet available in one index with the `elasticsearch-input` plugin.

You now have all the tools to do similar address conversion/enrichment. Note that you can use any dataset available.
My plan is to index some other open data sources in elasticsearch and try to cover more countries than France.

Stay tuned!

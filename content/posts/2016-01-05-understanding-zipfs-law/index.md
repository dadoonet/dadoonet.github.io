---
title: "Understanding Zipf's law"
description: "I just discovered a nice video which explains the Zipf's law. I'm wondering if I can index the french lexique from Université de Savoie and find some funny things based on that..."
author: David Pilato
avatar: /about/david_pilato.png
tags:
  - elasticsearch
  - logstash
  - kibana
categories:
  - tutorial
date: 2016-01-05 12:13:02 +0100
nolastmod: true
cover: featured.png
draft: false
aliases:
  - /blog/2016/01/05/understanding-zipfs-law/
  - /blog/2016-01-05-understanding-zipfs-law/
---

I just discovered a nice video which explains the [Zipf's law](https://en.wikipedia.org/wiki/Zipf%27s_law).

{{< youtube fCn8zs912OE >}}

I'm wondering if I can index the [french lexique from Université de Savoie](http://www.lexique.org/) and find some funny things based on that...

<!--more-->

## Download french words

```sh
wget http://www.lexique.org/listes/liste_mots.txt
head -20 liste_mots.txt
```

What do we have?

It's a CSV file (tabulation as separator):

```txt
1_graph 8_frantfreqparm
0 279.84
1 612.10
2 1043.90
3 839.32
4 832.23
5 913.87
6 603.42
7 600.61
8 908.03
9 1427.45
a 4294.90
aa  0.55
aaah  0.29
abaissa 1.45
abaissai  0.06
abaissaient 0.26
abaissait 1.29
abaissant 2.39
abaisse 5.39
```

The first line is the title. Other lines are really easy to understand:

* term
* frequency

## Convert to JSON

I'll use logstash 2.1.1 for this.

```sh
wget https://download.elastic.co/logstash/logstash/logstash-2.1.1.tar.gz
tar xzf logstash-2.1.1.tar.gz
```

As usual, I'm starting from a blank logstash configuration file, `zipf.conf`:

```ruby
input { stdin {} }

filter {}

output { stdout { codec => rubydebug } }
```

I check that everything runs fine:

```sh
head -20 liste_mots.txt | logstash-2.1.1/bin/logstash -f zipf.conf
```

It gives:

```txt
Settings: Default filter workers: 2
Logstash startup completed
{
       "message" => "1_graph\t8_frantfreqparm",
      "@version" => "1",
    "@timestamp" => "2016-01-05T11:33:16.269Z",
          "host" => "MacBook-Pro.local"
}
...
{
       "message" => "abaisse\t5.39",
      "@version" => "1",
    "@timestamp" => "2016-01-05T11:33:16.275Z",
          "host" => "MacBook-Pro.local"
}
Logstash shutdown completed
```

### Parse CSV lines

We have a CSV file so we should use here the [CSV filter plugin](http://www.elastic.co/guide/en/logstash/current/plugins-filters-csv.html):

```ruby
csv {
    separator => "\t"
    columns => [ "term", "frequency" ]
}
```

Note that you have to use the actual tab (ASCII character code 9) and not `\t`!

It now gives:

```ruby
{
       "message" => "abaisse\t5.39",
      "@version" => "1",
    "@timestamp" => "2016-01-05T13:47:52.374Z",
          "host" => "MacBook-Pro.local",
          "term" => "abaisse",
     "frequency" => "5.39"
}
```

### Cleanup

We need to ignore the first line as it contains column names:

```ruby
if [term] == "1_graph" {
  drop {}
}
```

And we can also mutate the `frequency` field to become actually a number and remove non needed fields:

```ruby
mutate {
  convert => { "frequency" => "float" }
  remove_field => [ "message", "@version", "@timestamp", "host" ]
}
```

We have now:

```ruby
{
  "term" => "abaisse",
  "frequency" => 5.39
}
```

We still have a format issue as the original file is not encoded with `UTF-8`.

For example `accompagné` gives:

```ruby
{
  "term" => "accompagn\\xE9\\t15.65"
}
```

With some logstash warnings:

```txt
Received an event that has a different character encoding than you configured. {:text=>"ab\\xEEm\\xE9es\\t0.42", :expected_charset=>"UTF-8", :level=>:warn}
```

Looking at what the browser detected it looks like we have "Windows-1252" encoding here:

{{< figure src="chrome.png" caption="Encoding" >}}

So we need to tell logstash how to parse stdin:

```ruby
input { 
  stdin {
    codec => line {
      "charset" => "Windows-1252"
    }
  }
}
```

## Index and analyze

I'm going to use my [found](https://found.elastic.co/#clusters/) instance here. In seconds, I have up and running my elasticsearch cluster with kibana, all with the latest versions.

I just have to define my security settings, and configure logstash again.

```ruby
output {
  stdout { codec => dots }
  elasticsearch {
    ssl => true
    hosts => [ "MYCLUSTERONFOUND.found.io:9243" ]
    index => "zipf"
    document_type => "french"
    template => "zipf_template.json"
    template_name => "zipf"
    user => "admin"
    password => "mygeneratedpassword"
  }
}
```

We need a template here as we don't want to analyze our `term` field. Let's define `zipf_template.json`:

```json
{
  "order" : 0,
  "template" : "zipf",
  "settings" : {
    "index" : {
      "refresh_interval" : "5s",
      "number_of_shards" : 1,
      "number_of_replicas" : 0
    }
  },
  "mappings" : {
    "french" : {
      "properties" : {
        "term" : {
          "type" : "string",
          "index": "not_analyzed"
        }
      }
    }
  }
}
```

And now, run it on all the dataset and wait for its completion:

```sh
cat liste_mots.txt | logstash-2.1.1/bin/logstash -f zipf.conf
```

## Most and less frequent french terms

According to this dataset, we can extract some information with Kibana:

{{< figure src="all-terms.png" caption="All french terms" >}}

We can see that obviously terms like `de`, `la` and `et` are very frequent but we use rarely the terms `compassions`, `croulante` and `croulantes`.

What? We have almost no "compassion" in France? Actually we do, but we use really often the singular form not the plural! Searching for `compassion*` in Kibana shows it:

{{< figure src="compassion.png" caption="compassion* terms" >}}

I also looked at terms starting with `ch`. It gives:

{{< figure src="starts-with-ch.png" caption="ch* terms" >}}

`chez`, `chaque` and `chose` are really common terms. I don't know what `chabler`, `chaboisseaux` and `chabots` actually mean! :D

## Zipf Law

Let's build a final visualization and see if we can have a curve like the one exposed in the video.

{{< figure src="zipf.png" caption="Zipf's Law" >}}

I changed the graph options and used a log Y Axis scale and also increased the number of terms to 1000.

{{< figure src="zipf-log.png" caption="Zipf's Law Log Axis" >}}

Well. It looks close.

I think I should now try to index an actual french book to see how it compares with this data source...

Stay tuned 😀

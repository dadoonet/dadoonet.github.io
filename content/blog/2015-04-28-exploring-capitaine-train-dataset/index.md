---
title: "Exploring Capitaine Train dataset"
#description: 
toc: true
authors:
  - David Pilato
tags:
  - elasticsearch
  - logstash
  - kibana
  - dataset
categories:
  - tutorial
date: 2015-04-28 13:31:34 +0200
lastmod: 2015-04-28 13:31:34 +0200
# featuredImage: blog/2015-05-19-using-js-auth-with-found-cluster/found_byelastic_logo_512x185.png
draft: false
aliases:
  - /blog/2015/04/28/exploring-capitaine-train-dataset/
---

Recently I saw a tweet where [Capitaine Train](https://www.capitainetrain.com/) team started to open data they have collected and enriched or corrected.

{{< tweet user="capitainetrain" id="591184013034938368" >}}

I decided to play a bit with [ELK stack](https://www.elastic.co/products) and create a simple recipe which can be used with any other `CSV` like data.

<!-- more -->

## Prerequisites

You will need:

* [Logstash](https://www.elastic.co/downloads/logstash): I'm using [1.5.0-rc3](https://download.elastic.co/logstash/logstash/logstash-1.5.0-rc3.tar.gz).
* [Elasticsearch](https://www.elastic.co/downloads/elasticsearch): I'm using  [1.5.2](https://download.elastic.co/elasticsearch/elasticsearch/elasticsearch-1.5.2.tar.gz)
* [Kibana](https://www.elastic.co/downloads/kibana): I'm using [4.0.2 Mac version](https://download.elastic.co/kibana/kibana/kibana-4.0.2-darwin-x64.tar.gz)

## Download the dataset

```sh
wget https://raw.githubusercontent.com/capitainetrain/stations/master/stations.csv
```

What does it look like?

```sh
head -3 stations.csv
```

```txt
id;name;slug;uic;uic8_sncf;longitude;latitude;parent_station_id;is_city;country;is_main_station;time_zone;is_suggestable;sncf_id;sncf_is_enabled;idtgv_id;idtgv_is_enabled;db_id;db_is_enabled;idbus_id;idbus_is_enabled;ouigo_id;ouigo_is_enabled;trenitalia_id;trenitalia_is_enabled;ntv_id;ntv_is_enabled;info:fr;info:en;info:de;info:it;same_as
1;Château-Arnoux—St-Auban;chateau-arnoux-st-auban;;;6.0016250000;44.0817900000;;t;FR;f;Europe/Paris;f;FRAAA;t;;f;;f;;f;;f;;f;;f;;;;;
2;Château-Arnoux—St-Auban;chateau-arnoux-st-auban;8775123;87751230;5.997342;44.061499;1;f;FR;t;Europe/Paris;t;FRCAA;t;;f;8700156;f;;f;;f;;f;;f;;;;;
```

So it's a CSV file containing some information that might worth to explore:

* `name`: obviously the name of the train station
* `longitude` and `latitude`: location
* `country`: the country ISO code (2 letters)
* `xxx_is_enabled`: true if `xxx` offer exists in the current train station (1 letter boolean value)

## Processing with logstash

Let's start with a blank logstash configuration file `station.conf` which will process our [standard input](http://www.elastic.co/guide/en/logstash/current/plugins-inputs-stdin.html) and print it on [standard output](http://www.elastic.co/guide/en/logstash/current/plugins-outputs-stdout.html) using [ruby debug codec](http://www.elastic.co/guide/en/logstash/current/plugins-codecs-rubydebug.html):

```rb
input {
   stdin {}
}

filter {
}

output {
   stdout { codec => rubydebug }
}
```

Launch this a first time and make sure logstash is working fine:

```sh
head -2 station.csv | bin/logstash -f station.conf
```

You should see something like:

```rb
Logstash startup completed
{
       "message" => "id;name;slug;uic;uic8_sncf;longitude;latitude;parent_station_id;is_city;country;is_main_station;time_zone;is_suggestable;sncf_id;sncf_is_enabled;idtgv_id;idtgv_is_enabled;db_id;db_is_enabled;idbus_id;idbus_is_enabled;ouigo_id;ouigo_is_enabled;trenitalia_id;trenitalia_is_enabled;ntv_id;ntv_is_enabled;info:fr;info:en;info:de;info:it;same_as",
      "@version" => "1",
    "@timestamp" => "2015-04-27T11:31:14.329Z",
          "host" => "MacBook-Air-de-David-2.local"
}
{
       "message" => "1;Château-Arnoux—St-Auban;chateau-arnoux-st-auban;;;6.0016250000;44.0817900000;;t;FR;f;Europe/Paris;f;FRAAA;t;;f;;f;;f;;f;;f;;f;;;;;",
      "@version" => "1",
    "@timestamp" => "2015-04-27T11:31:14.330Z",
          "host" => "MacBook-Air-de-David-2.local"
}
Logstash shutdown completed
```

### CSV parsing

We have a CSV file so we should use here the [CSV filter plugin](http://www.elastic.co/guide/en/logstash/current/plugins-filters-csv.html) and define [`separator`](http://www.elastic.co/guide/en/logstash/current/plugins-filters-csv.html#plugins-filters-csv-separator) as `;` instead of default `,` and also define the name of fields we want to generate instead of default `column_1`, `column_2`... using [`columns` parameter](http://www.elastic.co/guide/en/logstash/current/plugins-filters-csv.html#plugins-filters-csv-columns):

```rb
csv {
    separator => ";"
    columns => [
      "id","name","slug","uic","uic8_sncf","longitude","latitude","parent_station_id","is_city","country",
      "is_main_station","time_zone","is_suggestable","sncf_id","sncf_is_enabled","idtgv_id","idtgv_is_enabled",
      "db_id","db_is_enabled","idbus_id","idbus_is_enabled","ouigo_id","ouigo_is_enabled",
      "trenitalia_id","trenitalia_is_enabled","ntv_id","ntv_is_enabled","info_fr",
      "info_en","info_de","info_it","same_as"
    ]
}
```

When running it again, it now generates a more strutured data:

```rb
Logstash startup completed
{
              "message" => [
    [0] "id;name;slug;uic;uic8_sncf;longitude;latitude;parent_station_id;is_city;country;is_main_station;time_zone;is_suggestable;sncf_id;sncf_is_enabled;idtgv_id;idtgv_is_enabled;db_id;db_is_enabled;idbus_id;idbus_is_enabled;ouigo_id;ouigo_is_enabled;trenitalia_id;trenitalia_is_enabled;ntv_id;ntv_is_enabled;info:fr;info:en;info:de;info:it;same_as"
],
             "@version" => "1",
           "@timestamp" => "2015-04-27T11:40:57.936Z",
                 "host" => "MacBook-Air-de-David-2.local",
                   "id" => "id",
                 "name" => "name",
                 "slug" => "slug",
                  "uic" => "uic",
            "uic8_sncf" => "uic8_sncf",
            "longitude" => "longitude",
             "latitude" => "latitude",
    "parent_station_id" => "parent_station_id",
              "is_city" => "is_city",
              "country" => "country",
      "is_main_station" => "is_main_station",
            "time_zone" => "time_zone",
       "is_suggestable" => "is_suggestable",
              "sncf_id" => "sncf_id",
      "sncf_is_enabled" => "sncf_is_enabled",
             "idtgv_id" => "idtgv_id",
     "idtgv_is_enabled" => "idtgv_is_enabled",
                "db_id" => "db_id",
        "db_is_enabled" => "db_is_enabled",
             "idbus_id" => "idbus_id",
     "idbus_is_enabled" => "idbus_is_enabled",
             "ouigo_id" => "ouigo_id",
     "ouigo_is_enabled" => "ouigo_is_enabled",
        "trenitalia_id" => "trenitalia_id",
"trenitalia_is_enabled" => "trenitalia_is_enabled",
               "ntv_id" => "ntv_id",
       "ntv_is_enabled" => "ntv_is_enabled",
              "info_fr" => "info:fr",
              "info_en" => "info:en",
              "info_de" => "info:de",
              "info_it" => "info:it",
              "same_as" => "same_as"
}
{
              "message" => [
    [0] "1;Château-Arnoux—St-Auban;chateau-arnoux-st-auban;;;6.0016250000;44.0817900000;;t;FR;f;Europe/Paris;f;FRAAA;t;;f;;f;;f;;f;;f;;f;;;;;"
],
             "@version" => "1",
           "@timestamp" => "2015-04-27T11:40:57.938Z",
                 "host" => "MacBook-Air-de-David-2.local",
                   "id" => "1",
                 "name" => "Château-Arnoux—St-Auban",
                 "slug" => "chateau-arnoux-st-auban",
                  "uic" => nil,
            "uic8_sncf" => nil,
            "longitude" => "6.0016250000",
             "latitude" => "44.0817900000",
    "parent_station_id" => nil,
              "is_city" => "t",
              "country" => "FR",
      "is_main_station" => "f",
            "time_zone" => "Europe/Paris",
       "is_suggestable" => "f",
              "sncf_id" => "FRAAA",
      "sncf_is_enabled" => "t",
             "idtgv_id" => nil,
     "idtgv_is_enabled" => "f",                "db_id" => nil,
        "db_is_enabled" => "f",
             "idbus_id" => nil,
     "idbus_is_enabled" => "f",
             "ouigo_id" => nil,
     "ouigo_is_enabled" => "f",
        "trenitalia_id" => nil,
"trenitalia_is_enabled" => "f",
               "ntv_id" => nil,
       "ntv_is_enabled" => "f",
              "info_fr" => nil,
              "info_en" => nil,
              "info_de" => nil,
              "info_it" => nil,
              "same_as" => nil
}
```

### Skip header

We can see that we are still parsing the header so it will be sent to elasticsearch which is obviously something we dont want. We can use [Logstash conditionals](http://www.elastic.co/guide/en/logstash/current/configuration.html#conditionals) for that and [Drop filter plugin](http://www.elastic.co/guide/en/logstash/current/plugins-filters-drop.html):

```rb
if [id] == "id" {
 drop { }
} else {
 # continue processing data
}
```

### Remove duplicated fields

We can see that we have some duplicated contents and some fields are not really needed for our use case:

```rb
      "message" => [
    [0] "id;name;slug;uic;uic8_sncf;longitude;latitude;parent_station_id;is_city;country;is_main_station;time_zone;is_suggestable;sncf_id;sncf_is_enabled;idtgv_id;idtgv_is_enabled;db_id;db_is_enabled;idbus_id;idbus_is_enabled;ouigo_id;ouigo_is_enabled;trenitalia_id;trenitalia_is_enabled;ntv_id;ntv_is_enabled;info:fr;info:en;info:de;info:it;same_as"
],
     "@version" => "1",
   "@timestamp" => "2015-04-27T11:40:57.936Z",
      "host" => "MacBook-Air-de-David-2.local"
```

 So we can remove `message`, `@version` and `@timestamp` using [Mutate filter plugin](http://www.elastic.co/guide/en/logstash/current/plugins-filters-mutate.html) and its [remove_field](http://www.elastic.co/guide/en/logstash/current/plugins-filters-mutate.html#plugins-filters-mutate-remove_field). You can put that in the `else` part:

```rb
mutate {
 remove_field => [ "message", "host", "@timestamp", "@version" ]
}
```

### Convert numbers to numbers

We have seen that the CSV plugin has generated `latitude` and `longitude` fields as strings:

```rb
"longitude" => "6.0016250000",
 "latitude" => "44.0817900000",
```

Using the mutate filter, we can [convert](http://www.elastic.co/guide/en/logstash/current/plugins-filters-mutate.html#plugins-filters-mutate-convert) our fields to `float`:

```rb
mutate {
 convert => { "longitude" => "float" }
 convert => { "latitude" => "float" }
}
```

This will now output:

```rb
"longitude" => 6.001625,
 "latitude" => 44.08179,
```

### Build a location data structure

Elasticsearch uses a specific data structure called [geo_point](http://www.elastic.co/guide/en/elasticsearch/reference/current/mapping-geo-point-type.html) to deal with geographic location coordinates.

So a point should look like:

```js
"location": {
 "lat": x.xxx,
 "lon": y.yyy
}
```

It means that we need to change our `latitude` and `longitude` fields to inner fields inside a new `location` field. We can use `mutate` [`rename` parameter](http://www.elastic.co/guide/en/logstash/current/plugins-filters-mutate.html#plugins-filters-mutate-rename) for this:

```rb
mutate {
 rename => {
  "longitude" => "[location][lon]" 
  "latitude" => "[location][lat]" 
 }
}
```

This now produces:

```rb
             "location" => {
    "lon" => 6.001625,
    "lat" => 44.08179
}
```

### Convert booleans to booleans`^H^H^H^H^H^H^H^H` strings

We have a lot of fields which looks as boolean fields like:

```rb
          "is_city" => "t",
  "is_main_station" => "f",
   "is_suggestable" => "f",
  "sncf_is_enabled" => "t",
 "idtgv_is_enabled" => "f",
```

Sadly, the mutate convert parameter does not support yet `boolean` option. It will be merged really soon with [#22](https://github.com/logstash-plugins/logstash-filter-mutate/pull/22).

For now, we are going to use [elasticsearch boolean parsing](http://www.elastic.co/guide/en/elasticsearch/reference/current/mapping-core-types.html#boolean) which can detect a `false` value if provided as `"false"`, `"off"` and `"no"`.

To do that, we can use [`gsub` mutate parameter](http://www.elastic.co/guide/en/logstash/current/plugins-filters-mutate.html#plugins-filters-mutate-gsub):

```rb
mutate {
 gsub => [
  "is_city", "t", "true",
  "is_city", "f", "false",
  "is_main_station", "t", "true",
  "is_main_station", "f", "false",
  "is_suggestable", "t", "true",
  "is_suggestable", "f", "false",
  "sncf_is_enabled", "t", "true",
  "sncf_is_enabled", "f", "false",
  "idtgv_is_enabled", "t", "true",
  "idtgv_is_enabled", "f", "false",
  "db_is_enabled", "t", "true",
  "db_is_enabled", "f", "false",
  "idbus_is_enabled", "t", "true",
  "idbus_is_enabled", "f", "false",
  "ouigo_is_enabled", "t", "true",
  "ouigo_is_enabled", "f", "false",
  "trenitalia_is_enabled", "t", "true",
  "trenitalia_is_enabled", "f", "false",
  "ntv_is_enabled", "t", "true",
  "ntv_is_enabled", "f", "false"
 ]
}
```

It will now transform our booleans to:

```rb
          "is_city" => "true",
  "is_main_station" => "false",
   "is_suggestable" => "false",
  "sncf_is_enabled" => "true",
 "idtgv_is_enabled" => "false",
```

## Indexing into elasticsearch

Now we have our data generated:

```rb
{
                       "id" => "1",
                     "name" => "Château-Arnoux—St-Auban",
                     "slug" => "chateau-arnoux-st-auban",
                      "uic" => nil,
                "uic8_sncf" => nil,
        "parent_station_id" => nil,
                  "is_city" => "true",
                  "country" => "FR",
          "is_main_station" => "false",
                "time_zone" => "Europe/Paris",
           "is_suggestable" => "false",
                  "sncf_id" => "FRAAA",
          "sncf_is_enabled" => "true",
                 "idtgv_id" => nil,
         "idtgv_is_enabled" => "false",
                    "db_id" => nil,
            "db_is_enabled" => "false",
                 "idbus_id" => nil,
         "idbus_is_enabled" => "false",
                 "ouigo_id" => nil,
         "ouigo_is_enabled" => "false",
            "trenitalia_id" => nil,
    "trenitalia_is_enabled" => "false",
                   "ntv_id" => nil,
           "ntv_is_enabled" => "false",
                  "info_fr" => nil,
                  "info_en" => nil,
                  "info_de" => nil,
                  "info_it" => nil,
                  "same_as" => nil,
                 "location" => {
        "lon" => 6.001625,
        "lat" => 44.08179
    }
}
```

Let's say that you have already elasticsearch up and running:

```sh
bin/elasticsearch
```

### Defining our mapping

We need to create the right mapping to define our fields. As we have a lot of fields named with `*_is_enabled` or `is_*` we can use an [index template](http://www.elastic.co/guide/en/elasticsearch/reference/current/indices-templates.html) to define those automatically as booleans when field name is `*is_*`.
Also, it's definitely better to use `not_analyzed` strings to do aggregations so we can define a sub field `raw` which is not analyzed at index time for each string field.

This would lead us to the following index template `stations_template.json`:

```js
{
  "template": "stations",
  "order":    1, 
  "settings": {
    "number_of_shards": 1 
  },
  "mappings": {
    "station": { 
      "dynamic_templates": [
         {
            "string_fields": {
               "mapping": {
                  "index": "analyzed",
                  "omit_norms": true,
                  "type": "string",
                  "fields": {
                     "raw": {
                        "index": "not_analyzed",
                        "ignore_above": 256,
                        "type": "string"
                     }
                  }
               },
               "match_mapping_type": "string",
               "match": "*"
            }
         }, {
            "boolean_fields": {
               "mapping": {
                  "type": "boolean"
               },
               "match": "*is_*"
            }
         }
      ],
      "_all": {
        "enabled": false
      },
      "properties": {
       "location": {
          "type": "geo_point"
        }
      }
    }
  }
}
```

### Connect logstash and elasticsearch

We are going to obviously use [elasticsearch output plugin](http://www.elastic.co/guide/en/logstash/current/plugins-outputs-elasticsearch.html) to send our data to elasticsearch cluster. We will:

* use `http` protocol
* index our data in `stations` index and use `station` type
* extract elasticsearch `_id` field from `id` event field
* use our `stations` template defined in `stations_template.json` local file

Let's add this as an `output` in our logstash configuration file:

```rb
elasticsearch {
 protocol => "http"
 host => "localhost"
 index => "stations"
 index_type => "station"
 document_id => "%{id}"
 template => "stations_template.json"
 template_name => "stations"
}
```

Test again as usual and you should be able to see your document in elasticsearch:

```sh
curl "http://localhost:9200/stations/station/_search?pretty"
```

```json
{
   "took": 1,
   "timed_out": false,
   "_shards": {
      "total": 1,
      "successful": 1,
      "failed": 0
   },
   "hits": {
      "total": 1,
      "max_score": 1,
      "hits": [
         {
            "_index": "sncf",
            "_type": "gare",
            "_id": "1",
            "_score": 1,
            "_source": {
               "id": "1",
               "name": "Château-Arnoux—St-Auban",
               "slug": "chateau-arnoux-st-auban",
               "uic": null,
               "uic8_sncf": null,
               "parent_station_id": null,
               "is_city": "true",
               "country": "FR",
               "is_main_station": "false",
               "time_zone": "Europe/Paris",
               "is_suggestable": "false",
               "sncf_id": "FRAAA",
               "sncf_is_enabled": "true",
               "idtgv_id": null,
               "idtgv_is_enabled": "false",
               "db_id": null,
               "db_is_enabled": "false",
               "idbus_id": null,
               "idbus_is_enabled": "false",
               "ouigo_id": null,
               "ouigo_is_enabled": "false",
               "trenitalia_id": null,
               "trenitalia_is_enabled": "false",
               "ntv_id": null,
               "ntv_is_enabled": "false",
               "info_fr": null,
               "info_en": null,
               "info_de": null,
               "info_it": null,
               "same_as": null,
               "location": {
                  "lon": 6.001625,
                  "lat": 44.08179
               }
            }
         }
      ]
   }
}
```

### Inject them all

It's now time to inject all data we have.
Instead of debugging each line, we can change the `stdout` codec to [`dots`](http://www.elastic.co/guide/en/logstash/current/plugins-codecs-dots.html) instead of `rubydebug`.

At the end, here is our logstash configuration file:

```rb
input {
 stdin {}
}

filter {
 csv {
     separator => ";"
     columns => [
       "id","name","slug","uic","uic8_sncf","longitude","latitude","parent_station_id","is_city","country",
       "is_main_station","time_zone","is_suggestable","sncf_id","sncf_is_enabled","idtgv_id","idtgv_is_enabled",
       "db_id","db_is_enabled","idbus_id","idbus_is_enabled","ouigo_id","ouigo_is_enabled",
       "trenitalia_id","trenitalia_is_enabled","ntv_id","ntv_is_enabled","info_fr",
       "info_en","info_de","info_it","same_as"
     ]
 }

 if [id] == "id" {
  drop { }
 } else {
     mutate {
   remove_field => [ "message", "host", "@timestamp", "@version" ]
     }

  mutate {
   convert => { "longitude" => "float" }
   convert => { "latitude" => "float" }
  }

  mutate {
   rename => {
    "longitude" => "[location][lon]" 
    "latitude" => "[location][lat]" 
   }
  }

  mutate {
   gsub => [
    "is_city", "t", "true",
    "is_city", "f", "false",
    "is_main_station", "t", "true",
    "is_main_station", "f", "false",
    "is_suggestable", "t", "true",
    "is_suggestable", "f", "false",
    "sncf_is_enabled", "t", "true",
    "sncf_is_enabled", "f", "false",
    "idtgv_is_enabled", "t", "true",
    "idtgv_is_enabled", "f", "false",
    "db_is_enabled", "t", "true",
    "db_is_enabled", "f", "false",
    "idbus_is_enabled", "t", "true",
    "idbus_is_enabled", "f", "false",
    "ouigo_is_enabled", "t", "true",
    "ouigo_is_enabled", "f", "false",
    "trenitalia_is_enabled", "t", "true",
    "trenitalia_is_enabled", "f", "false",
    "ntv_is_enabled", "t", "true",
    "ntv_is_enabled", "f", "false"
   ]
  }

 }
}

output {
 stdout { codec => dots }
 elasticsearch {
  protocol => "http"
  host => "localhost"
  index => "stations"
  index_type => "station"
  document_id => "%{id}"
  template => "stations_template.json"
  template_name => "stations"
 }
}
```

Let's use it:

```sh
cat station.csv | bin/logstash -f station.conf
```

At the end, check that everything has been correctly indexed:

```sh
curl "http://localhost:9200/sncf/gare/_search?pretty&size=0"
```

```json
{
   "took": 1,
   "timed_out": false,
   "_shards": {
      "total": 1,
      "successful": 1,
      "failed": 0
   },
   "hits": {
      "total": 21461,
      "max_score": 0,
      "hits": []
   }
}
```

## Kibana FTW

Start your kibana instance, [open kibana](http://0.0.0.0:5601).

### Settings

Configure your `stations` index:

{{< figure src="settings-set-index.png" caption="Set index name" >}}

### Discover your data

If not already set, define in `discover` your `stations` index:

{{< figure src="discover-set-index.png" caption="Set index name" >}}

Then choose fields you want to display:

{{< figure src="discover-set-fields.png" caption="Set fields" >}}

And save your search:

{{< figure src="discover-save-search.png" caption="Save your search" >}}

### Visualize your data

Create a new visualization and choose `Pie chart`:

{{< figure src="visualize-pie-chart.png" caption="Create visualisation" >}}

Select your saved search:

{{< figure src="visualize-pie-choose-search.png" caption="Select saved search" >}}

Split the slices using `country.raw` field so you will display number of train stations broken per country code.

{{< figure src="visualize-pie-final.png" caption="Final Pie" >}}

Save your visualization and create a new `Pie chart` on `idtgv_is_enabled` field:

{{< figure src="visualize-pie-idtgv.png" caption="IDTGV stations" >}}

Save your visualization and create a new `Tile map`:

{{< figure src="visualize-tile.png" caption="Create visualization" >}}

Select a `Geohash` aggregation on `location` field and increase `Precision` to `4`:

{{< figure src="visualize-tile-final.png" caption="Tile map" >}}

Don't forget to save it!

You can build as many visualization you need.

### Put them all on the same page

Open `Dashboard` and add all your visualizations:

{{< figure src="dashboard-add-vis.png" caption="Select visualizations" >}}

And your saved search:

{{< figure src="dashboard-add-search.png" caption="Add a saved search" >}}

Arrange your dashboard and play with it!

{{< figure src="dashboard-final-1.png" caption="The final dashboard" >}}

For example, if you click on `FR` in the country pie and then select `T` on IDTGV pie, you will be able to display all IDTGV stations located in France.

{{< figure src="dashboard-idtgv.png" caption="IDTGV stations in France" >}}

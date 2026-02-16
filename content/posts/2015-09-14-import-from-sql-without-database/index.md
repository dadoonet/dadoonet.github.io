---
title: "Importing from a database without a database"
description: "Recently, I got a database MySQL dump and I was thinking of importing it into elasticsearch. The first idea which pops up was: install MySQL, import the database, read the database with Logstash and import into elasticsearch, drop the database, uninstall MySQL. Well. I found that some of the steps are really not needed."
author: David Pilato
avatar: /about/david_pilato.avif
tags:
  - elasticsearch
  - logstash
  - mysql
  - sql
categories:
  - tutorial
date: 2015-09-14 11:05:00 +0200
nolastmod: true
draft: false
aliases:
  - /blog/2015/09/14/import-from-sql-without-database/
  - /blog/2015-09-14-import-from-sql-without-database/
---

Recently, I got a database MySQL dump and I was thinking of importing it into elasticsearch.

The first idea which pops up was:

* install MySQL
* import the database
* read the database with Logstash and import into elasticsearch
* drop the database
* uninstall MySQL

Well. I found that some of the steps are really not needed.

I can actually use [ELK stack](https://www.elastic.co/products) and create a simple recipe which can be used to import SQL dump scripts without needing to actually load the data to a database and then read it again from the database.

Let's do it!

<!--more-->

## Parsing SQL script with logstash

I exported some data from a MySQL example database I have. You can download the same [data](https://gist.github.com/dadoonet/2e83d126e5a5666598b1).

### SQL Insert script

Our objects are split on 3 tables but we are not going to do joins here. We will only import data from `Person` table.

Let's look at the important lines of the script:

```sql
--
-- Table structure for table `Person`
--

DROP TABLE IF EXISTS `Person`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Person` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `children` int(11) DEFAULT NULL,
  `dateOfBirth` datetime DEFAULT NULL,
  `gender` varchar(255) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `reference` varchar(255) DEFAULT NULL,
  `address_id` int(11) DEFAULT NULL,
  `marketing_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FK_tagx64iglr1dxpalbgothv83r` (`address_id`),
  KEY `FK_j4ifv49erkwul9jruu15o40r4` (`marketing_id`),
  CONSTRAINT `FK_j4ifv49erkwul9jruu15o40r4` FOREIGN KEY (`marketing_id`) REFERENCES `Marketing` (`id`),
  CONSTRAINT `FK_tagx64iglr1dxpalbgothv83r` FOREIGN KEY (`address_id`) REFERENCES `Address` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10001 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Person`
--

LOCK TABLES `Person` WRITE;
/*!40000 ALTER TABLE `Person` DISABLE KEYS */;
INSERT INTO `Person` VALUES (1,4,'1944-07-21 00:00:00','male','Joe Smith','0',1,1),...,(10000,0,'2009-09-10 00:00:00','female','Stephanie Rebecca','9999',10000,10000);
/*!40000 ALTER TABLE `Person` ENABLE KEYS */;
```

Two important sections in this file:

* `CREATE TABLE` gives us all column titles
* `INSERT INTO` are our data

In a real backup with much more data than that, you will probably have more than one single `INSERT INTO` line.

We basically need here to ignore the first 108 lines of our backup at first.

Let's look then at the first line:

```sh
cat person.sql | head -109 | tail -1
```

```sql
INSERT INTO `Person` VALUES (1,4,'1944-07-21 00:00:00','male','Joe Smith','0',1,1),...,(10000,0,'2009-09-10 00:00:00','female','Stephanie Rebecca','9999',10000,10000);
```

### Read it with logstash

What we need to do here is to split each line with the following pattern:

```sql
INSERT INTO `Person` VALUES (DATA),(DATA),***,(DATA);
```

We can create a `mysql.conf` for logstash to parse this. As usual, start with an "empty" one:

```ruby
input { stdin {} }

filter {
}

output { stdout { codec => rubydebug } }
```

Then, let's ignore the `INSERT INTO ...` part and extract the data in a new field named `extracted_sql`. Let's use a [grok filter](https://www.elastic.co/guide/en/logstash/current/plugins-filters-grok.html) for that:

```ruby
grok {
  match => {
    "message" => "INSERT INTO \`Person\` VALUES (%{GREEDYDATA:extracted_sql})"
  }
  remove_field => "message"
}
```

Execute it:

```sh
cat person.sql | head -109 | tail -1 | bin/logstash -f mysql.conf
```

It gives something like this:

```ruby
{
         "@version" => "1",
       "@timestamp" => "2015-09-14T07:32:43.495Z",
             "host" => "MacBook-Air-de-David.local",
    "extracted_sql" => "(..),..(..);
}
```

We now need to split `extracted_sql` in multiple events. Let's add a [split filter](https://www.elastic.co/guide/en/logstash/current/plugins-filters-split.html):

```ruby
split {
  terminator => "),("
  field => "extracted_sql"
}
```

Launch again and it now gives one event per table line:

```ruby
{
         "@version" => "1",
       "@timestamp" => "2015-09-14T07:38:34.489Z",
             "host" => "MacBook-Air-de-David.local",
    "extracted_sql" => "1,4,'1944-07-21 00:00:00','male','Joe Smith','0',1,1"
}
// ...
{
         "@version" => "1",
       "@timestamp" => "2015-09-14T07:37:25.729Z",
             "host" => "MacBook-Air-de-David.local",
    "extracted_sql" => "8906,3,'1958-12-17 00:00:00','male','Gautier Titouan','8905',8906,8906"
}
// ...
{
         "@version" => "1",
       "@timestamp" => "2015-09-14T07:38:34.489Z",
             "host" => "MacBook-Air-de-David.local",
    "extracted_sql" => "10000,0,'2009-09-10 00:00:00','female','Stephanie Rebecca','9999',10000,10000"
}
```

Sounds like we have now a CSV structure... We can either use a [CSV filter](https://www.elastic.co/guide/en/logstash/current/plugins-filters-csv.html) or a [GROK filter](https://www.elastic.co/guide/en/logstash/current/plugins-filters-grok.html).

Grok gives more flexibility because it helps to define the right data type you want for each field. The CSV filter can not directly do it [at the moment](https://github.com/logstash-plugins/logstash-filter-csv/pull/7). Grok can do it but it's based on regular expressions and it's a way slower than the CSV filter which is optimized to parse CSV content. So I'm trading here flexibility and ease to use for performance.

```ruby
csv {
  source => "extracted_sql"
  quote_char => "'"
  columns => [ "id", 
    "children", "dateOfBirth", "gender", "name", 
    "reference", "address_id", "marketing_id" ]
  remove_field => "extracted_sql"
}
```

### Deal with NULL

If you have to deal with `NULL` values, just add before the CSV filter:

```ruby
mutate {
    gsub => [
      "extracted_sql", "NULL", ""
    ]
}
```

### Select a timestamp

We also have some dates in various formats:

```ruby
   "@timestamp" => "2015-09-14T07:38:34.489Z",
  "dateOfBirth" => "2009-09-10 00:00:00"
```

`dateOfBirth` is obviously the creation date. `@timestamp` is as always the internal logstash timestamp. We want `dateOfBirth` to become our event date.

```ruby
date {
    match => [ "dateOfBirth", "YYYY-MM-DD HH:mm:ss" ]
    remove_field => "dateOfBirth"
}
```

### Drop the header

Nice so far. But what about the header part?

Well we have our first `grok` pattern which tries to parse `INSERT ...` so if it fails, it will generate a `_grokparsefailure` tag. We can drop each line which contains that:

```ruby
# Just after the grok filter
if "_grokparsefailure" in [tags] {
  drop { }
} 
```

We can now run our logstash configuration on the full file:

```sh
cat person.sql | bin/logstash -f mysql.conf
```

### Cleanup

We output for now:

```ruby
{
        "@version" => "1",
      "@timestamp" => "1967-01-17T23:00:00.000Z",
            "host" => "MacBook-Air-de-David.local",
              "id" => "9999",
        "children" => "1",
          "gender" => "female",
            "name" => "Laetitia Lois",
       "reference" => "9998",
      "address_id" => "9999",
    "marketing_id" => "9999"
}
```

We don't need to keep `@version` and `host` fields:

```rb
mutate {
  remove_field => [ "@version", "host" ]
}
```

It gives:

```ruby
{
      "@timestamp" => "1967-01-17T23:00:00.000Z",
              "id" => "9999",
        "children" => "1",
          "gender" => "female",
            "name" => "Laetitia Lois",
       "reference" => "9998",
      "address_id" => "9999",
    "marketing_id" => "9999"
}
```

## Connect to elasticsearch

Not the hardest part. But may be because I'm practicing elasticsearch for almost 5 years :)!

For new comers, you have to:

* [download](https://www.elastic.co/downloads/elasticsearch). 1.7.1 was the latest at this moment.
* unzip: `tar xzf elasticsearch-1.7.1.tar.gz`
* install [marvel](https://www.elastic.co/products/marvel/): `bin/plugin install elasticsearch/marvel/latest`
* launch: `bin/elasticsearch`

And connect logstash...

```ruby
output {
  elasticsearch {
    host => "localhost"
    port => "9200"
    protocol => "http"
    index => "persons-%{+YYYY}"
    document_type => "person"
    document_id => "%{id}"
    template => "person.json"
    template_name => "person"
  }

  stdout {
    codec => "dots"
  }
}
```

> [!NOTE]
> We send documents grouped by year in an index named `persons-YEAR4DIGITS`, using type `person` and with the original `id` as the document `_id`.

`person.json` file contains our template. We define that we use 1 single shard, that we don't need `_all` field and some other settings:

```json
{
  "template": "persons-*",
  "order":    1, 
  "settings": {
    "number_of_shards": 1 
  },
  "mappings": {
    "_default_" : {
       "_all" : {"enabled" : false},
       "dynamic_templates" : [ {
         "string_fields" : {
           "match" : "*",
           "match_mapping_type" : "string",
           "mapping" : {
             "type" : "string", "index" : "analyzed", "omit_norms" : true,
               "fields" : {
                 "raw" : {"type": "string", "index" : "not_analyzed", "ignore_above" : 256}
               }
           }
         }
       } ]
    },
    "person": { 
      "properties": {
        "id": {
          "type": "long",
          "index": "no"
        }
      }
    }
  }
}
```

Launch!

```sh
cat person.sql | bin/logstash -f mysql.conf
```

If you want to increase the injection rate, just add more workers to logstash:

```sh
cat person.sql | bin/logstash -f mysql.conf -w 2
```

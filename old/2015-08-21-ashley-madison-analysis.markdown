---
layout: post
title: "Ashley Madison analysis"
date: 2015-08-21 10:31:18 +0200
comments: true
image: /images/covers/logstash.png
categories: 
- elasticsearch
- logstash
---


Recently I saw a tweet where Ashley Madison databased was leaked and published on Tor.

<center><blockquote class="twitter-tweet" lang="fr"><p lang="en" dir="ltr">I was looking for a new dataset to play with... :) <a href="http://t.co/z3YsS0E97b">http://t.co/z3YsS0E97b</a></p>&mdash; David Pilato (@dadoonet) <a href="https://twitter.com/dadoonet/status/633965502415683584">2015/08/19</a></blockquote></center>

I decided to play a bit with [ELK stack](https://www.elastic.co/products) and create a simple recipe which can be used to import SQL dump scripts without needing to actually load the data to a database and then read it again from the database.

Let"s do it!

<!-- more -->

## Parsing members with logstash

### SQL Insert script

Let"s look at a first interesting file `am_am.dump.gz`:

```sh
gzcat am_am.dump.gz | head -86
```

```sql
-- MySQL dump 10.13  Distrib 5.5.33, for Linux (x86_64)
--
-- Host: localhost    Database: am
-- ------------------------------------------------------
-- Server version	5.5.33-31.1-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE="+00:00" */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE="NO_AUTO_VALUE_ON_ZERO" */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table "am_am_member"
--

DROP TABLE IF EXISTS "am_am_member";
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE "am_am_member" (
  "id" int(11) NOT NULL AUTO_INCREMENT,
  "createdon" timestamp NULL DEFAULT NULL,
  "createdby" int(11) DEFAULT NULL,
  "updatedon" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  "updatedby" int(11) DEFAULT NULL,
  "admin" int(11) DEFAULT NULL,
  "status" int(11) DEFAULT NULL,
  "account_type" int(11) DEFAULT NULL,
  "membership_status" int(11) DEFAULT NULL,
  "ad_source" int(11) NOT NULL DEFAULT "0",
  "profile_number" int(11) DEFAULT NULL,
  "nickname" varchar(16) DEFAULT NULL,
  "first_name" varchar(24) DEFAULT NULL,
  "last_name" varchar(24) DEFAULT NULL,
  "street1" varchar(70) DEFAULT NULL,
  "street2" varchar(70) DEFAULT NULL,
  "city" varchar(28) DEFAULT NULL,
  "zip" varchar(16) DEFAULT NULL,
  "state" int(11) DEFAULT NULL,
  "latitude" double NOT NULL DEFAULT "0",
  "longitude" double NOT NULL DEFAULT "0",
  "country" int(11) DEFAULT NULL,
  "phone" varchar(24) DEFAULT NULL,
  "work_phone" varchar(24) DEFAULT NULL,
  "mobile_phone" varchar(24) DEFAULT NULL,
  "gender" int(11) DEFAULT NULL,
  "dob" date DEFAULT NULL,
  "profile_caption" varchar(64) DEFAULT NULL,
  "profile_ethnicity" int(11) DEFAULT NULL,
  "profile_weight" int(11) DEFAULT NULL,
  "profile_height" int(11) DEFAULT NULL,
  "profile_bodytype" int(11) DEFAULT NULL,
  "profile_smoke" int(11) DEFAULT NULL,
  "profile_drink" int(11) DEFAULT NULL,
  "profile_initially_seeking" int(11) DEFAULT NULL,
  "profile_relationship" int(11) DEFAULT NULL,
  "pref_opento" varchar(164) NOT NULL DEFAULT "",
  "pref_opento_other" varchar(28) DEFAULT NULL,
  "pref_opento_abstract" mediumtext NOT NULL,
  "pref_turnsmeon" varchar(164) NOT NULL DEFAULT "",
  "pref_turnsmeon_other" varchar(28) DEFAULT NULL,
  "pref_turnsmeon_abstract" mediumtext,
  "pref_lookingfor" varchar(164) NOT NULL DEFAULT "",
  "pref_lookingfor_other" varchar(28) DEFAULT NULL,
  "pref_lookingfor_abstract" mediumtext,
  "main_photo" int(11) DEFAULT NULL,
  "security_question" int(1) NOT NULL DEFAULT "0",
  "security_answer" varchar(32) NOT NULL DEFAULT "",
  PRIMARY KEY ("id"),
  KEY "status_lookup" ("status"),
  KEY "updatedon" ("updatedon")
) ENGINE=InnoDB AUTO_INCREMENT=36993336 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table "am_am_member"
--

LOCK TABLES "am_am_member" WRITE;
/*!40000 ALTER TABLE "am_am_member" DISABLE KEYS */;
INSERT INTO "am_am_member" VALUES (/* ... stripped for clarity */),(/* ... */),/* ... */(/* ... */);
```

The important section in this file is obviously the `CREATE TABLE` part. So we have all column titles.

We basically need here to ignore the first 85 lines. 

Let"s look then at the first line:

```sh
gzcat am_am.dump.gz | head -86 | tail -1
```

```sql
INSERT INTO `am_am_member` VALUES 
	(9,"2002-01-17 02:15:08",0,"2011-10-14 13:47:31",20,2,2,1,1,0,19630,"Rational","XXXX","XXXXX","39 XXXXX Ave.","Suite XXX","Toronto","M2P1R4",33,40.768479,-73.960718,1,"416-487-2210","1234567","",2,"1963-12-21","I May Be Spoken 4 But I Speak 4 Myself.",1,65772,173,2,1,1,5,2,"|11|18|","Sugar babe wanted","I love to spoil. Open to shopping sprees, fine dining, travel, romantic get-a-ways...let me take care of you.","|11|4|14|26|27|18|28|","","Slim 18-25 gets my attention.","|37|7|33|51|34|","","Preferably someone local. No drama or unreasonable relationship expectations from me or you. Mutual respect and absolute discretion a must.",0,4,"XXXX"),
	(10,"2002-01-17 02:22:35",0,"2011-10-14 13:47:31",10,2,3,2,2,0,19631,"Sensuous Kitten","XXXX","XXXXX","876 XXXX Ave","",...
```

Hiding here some data as they are nominative.

Note that everything is on a single line. So we somehow a bulk of data per line. We have around `9827` of those lines.

### Read it with logstash

What we need to do here is to split each line with the following pattern:

```sql
INSERT INTO `am_am_member` VALUES (DATA),(DATA),***,(DATA);
```

We can create a `ashley-member_details.conf` for logstash to parse this. As usual, start with an "empty" one:

```rb
input {	stdin {} }

filter {
}

output { stdout { codec => rubydebug } }
```

Then, let"s ignore the `INSERT INTO ...` part and extract the data in a new field named `extracted_sql`. Add a first [grok filter](https://www.elastic.co/guide/en/logstash/current/plugins-filters-grok.html):

```rb
grok {
	match => {
		"message" => "INSERT INTO \`am_am_member\` VALUES (%{GREEDYDATA:extracted_sql})"
	}
	remove_field => "message"
}
```

Execute it:

```sh
gzcat am_am.dump.gz | head -86 | tail -1 | bin/logstash -f ashley-member_details.conf
```

It gives something like this:

```rb
{
         "@version" => "1",
       "@timestamp" => "2015-08-21T12:27:59.394Z",
             "host" => "MacBook-Air-de-David.local",
    "extracted_sql" => "(..),..(..);
}
```

We now need to split `extracted_sql` in multiple events. Let"s add a [split filter](https://www.elastic.co/guide/en/logstash/current/plugins-filters-split.html):

```rb
split {
	terminator => "),("
	field => "extracted_sql"
}
```

Launch again and it now gives one event per table line:

```rb
{
         "@version" => "1",
       "@timestamp" => "2015-08-21T12:33:00.314Z",
             "host" => "MacBook-Air-de-David.local",
    "extracted_sql" => "(9,"2002-01-17 02:15:08",0, ..."
}
{
         "@version" => "1",
       "@timestamp" => "2015-08-21T12:33:00.314Z",
             "host" => "MacBook-Air-de-David.local",
    "extracted_sql" => "10,"2002-01-17 02:22:35",0,..."
}
...
{
         "@version" => "1",
       "@timestamp" => "2015-08-21T12:33:00.314Z",
             "host" => "MacBook-Air-de-David.local",
    "extracted_sql" => "2296,"2002-03-19 22:08:30",0,...);"
}
```


**TODO**  NULL VALUES

```
1118521,'2006-10-11 20:08:10',0,'2011-10-17 16:30:44',0,2,2,NULL,NULL,6,NULL,'Play dough',NULL,NULL,NULL,NULL,'Levittown','19054',39,40.16834,-74.822181,1,NULL,NULL,NULL,2,'1973-01-10','Anything but typical',1,102060,183,6,2,0,1,2,'','','','','','','','','',NULL,2,'Benjamin'
```


Note that we still have some "noise" for the first event (starts with `(`) and for the last one (ends with `);`).

I first started to split what we have in `extracted_sql` using a [CSV filter](http://www.elastic.co/guide/en/logstash/current/plugins-filters-csv.html) but I finally did some grok again.

Why this? Because grok plugin offers today more flexibility than the csv plugin. The CSV plugin basically generates everything as string. But then you have to use the convert plugin to convert one by one each number to a number type within the event. Also with grok, it's super easy to ignore `(` and `);` using regular expressions.

So I added: 

```rb
grok {
	match => { 
		"extracted_sql" => "\(?%{NUMBER:id:int},'%{GREEDYDATA:createdon}',%{NUMBER:createdby:int},'%{GREEDYDATA:updatedon}',%{NUMBER:updatedby:int},%{NUMBER:admin:int},%{NUMBER:status:int},%{NUMBER:account_type:int},%{NUMBER:membership_status:int},%{NUMBER:ad_source:int},%{NUMBER:profile_number:int},'%{GREEDYDATA:nickname}','%{GREEDYDATA:first_name}','%{GREEDYDATA:last_name}','%{GREEDYDATA:street1}','%{GREEDYDATA:street2}','%{GREEDYDATA:city}','%{GREEDYDATA:zip}',%{NUMBER:state},%{NUMBER:[location][latitude]:float},%{NUMBER:[location][longitude]:float},%{NUMBER:country:int},'%{GREEDYDATA:phone}','%{GREEDYDATA:work_phone}','%{GREEDYDATA:mobile_phone}',%{NUMBER:gender:int},'%{GREEDYDATA:dob}','%{GREEDYDATA:[profile][caption]}',%{NUMBER:[profile][ethnicity]:int},%{NUMBER:[profile][weight]:int},%{NUMBER:[profile][height]:int},%{NUMBER:[profile][bodytype]:int},%{NUMBER:[profile][smoke]:int},%{NUMBER:[profile][drink]:int},%{NUMBER:[profile][initially_seeking]:int},%{NUMBER:[profile][relationship]:int},'%{GREEDYDATA:[pref][opento]}','%{GREEDYDATA:[pref][opento_other]}','%{GREEDYDATA:[pref][opento_abstract]}','%{GREEDYDATA:[pref][turnsmeon]}','%{GREEDYDATA:[pref][turnsmeon_other]}','%{GREEDYDATA:[pref][turnsmeon_abstract]}','%{GREEDYDATA:[pref][lookingfor]}','%{GREEDYDATA:[pref][lookingfor_other]}','%{GREEDYDATA:[pref][lookingfor_abstract]}',%{NUMBER:main_photo:int},%{NUMBER:security_question:int},'%{GREEDYDATA:security_answer}'\)?\;?" 
	}
	remove_field => "extracted_sql"
	}
```

Let's look in details at some fields...

`latitude` and `longitude` are obviously geo points. So we can first convert them on the fly as floats and store the result in an adapted field, ready for elasticsearch.

So we write: `%{NUMBER:[location][lat]:float},%{NUMBER:[location][lon]:float}`.
It will produce something like:

```rb
"location" => {
	"lat" => 32.8365,
	"lon" => 96.7764
}
```

Same for every field named `profile_*`, instead of the flat datastructure, we can use an inner object here:

```rb
"profile" => {
	          "caption" => "Sensual, attached, handsome and very orally talented... looking!",
	        "ethnicity" => 1,
	           "weight" => 97524,
	           "height" => 183,
	         "bodytype" => 2,
	            "smoke" => 1,
	            "drink" => 2,
	"initially_seeking" => 5,
	     "relationship" => 2
}
```

Same for `pref_`:

```rb
"pref" => {
             "opento" => "|1|5|15|16|18|19|23|",
    "opento_abstract" => "I could be reached",
          "turnsmeon" => "|3|5|10|11|12|14|17|18|20|22|23|27|28|29|",
         "lookingfor" => "|7|9|10|11|12|14|19|21|27|28|29|31|34|37|38|42|43|47|48|49|"
}
```

We will need to understand and probably replace this list of numbers as a real list of meaningful strings.

### Select a timestamp

We also have some dates in various formats:

```rb
   "@timestamp" => "2015-08-21T14:40:26.698Z",
    "createdon" => "2002-03-19 21:42:33",
    "updatedon" => "2011-10-14 15:47:29",
          "dob" => "1967-10-22",
```

`createdon` is obviously the creation date. `updatedon` should be the last time the profile has been updated. `dob` looks like the date of birth. `@timestamp` is as always the internal logstash timestamp.
We should select one of our dates to become our `@timestamp`. The best date in my opinion is `createdon` here.

```rb
date {
    match => [ "createdon", "YYYY-MM-DD HH:mm:ss" ]
    remove_field => "createdon"
}
```

We will keep other dates in their current format and will deal with formats in elasticsearch itself.

### Change numerical values by meaningful text

`gender` field has 2 values:

* `1` means woman
* `2` means man

We can change the value using conditionals:

```rb
if [gender] == 1 {
	mutate {
		replace => { "gender" => "female" }
	}
} else if [gender] == 2 {
	mutate {
		replace => { "gender" => "male" }
	}
} else {
	mutate {
		replace => { "gender" => "unknown" }
	}
}
```

`country` is a numeric value. What does it mean?

After having injected some data, you can do some reverse engineering using elasticsearch. Let's do that:

```json
GET ashley-*/_search
{
  "size": 0, 
  "aggs": {
    "country": {
      "terms": {
        "field": "country",
        "size": 250
      },
      "aggs": {
        "city": {
          "terms": {
            "field": "city.raw",
            "size": 1
          }
        }
      }
    }
  }
}
```
 
It shows:

```json
"buckets": [
{
   "key": 2,
   "doc_count": 56359,
   "city": {
      "doc_count_error_upper_bound": 978,
      "sum_other_doc_count": 42390,
      "buckets": [
         {
            "key": "Toronto",
            "doc_count": 13969
         }
      ]
   }
},
{
   "key": 1,
   "doc_count": 2888,
   "city": {
      "doc_count_error_upper_bound": 24,
      "sum_other_doc_count": 2813,
      "buckets": [
         {
            "key": "New York",
            "doc_count": 75
         }
      ]
   }
},
{
   "key": 0,
   "doc_count": 2,
   "city": {
      "doc_count_error_upper_bound": 0,
      "sum_other_doc_count": 0,
      "buckets": []
   }
},
{
   "key": 3,
   "doc_count": 1,
   "city": {
      "doc_count_error_upper_bound": 0,
      "sum_other_doc_count": 0,
      "buckets": [
         {
            "key": "London",
            "doc_count": 1
         }
      ]
   }
}
]
```


### Cleanup

Let's remove also non needed fields, such as:

* `@version`
* `host`

```rb
mutate {
	remove_field => [ "@version", "host" ]
}
```

### Drop the header

Nice so far. But what about the header part?

Well we have our first `grok` pattern which tries to parse `INSERT ...` so if it fails, it will generate a `_grokparsefailure` tag. We can drop each line which contains that:

```rb
# Just after the first grok filter
if "_grokparsefailure" in [tags] {
	drop { }
} 
```

At the end our documents look like:

```json
{
   "@timestamp":"2002-01-19T20:42:33.000Z",
   "id":2295,
   "createdby":0,
   "updatedon":"2011-10-14 15:47:29",
   "updatedby":11,
   "admin":2,
   "status":2,
   "account_type":1,
   "membership_status":2,
   "ad_source":0,
   "profile_number":21889,
   "nickname":"XXXXXX",
   "first_name":"XXXXX",
   "last_name":"XXXX",
   "street1":"XXXX XXXXX Rd",
   "city":"Victoria",
   "zip":"XXX XXX",
   "state":"58",
   "location":{
      "latitude":48.4333,
      "longitude":123.3667
   },
   "country":2,
   "phone":"XXXXXXXX",
   "mobile_phone":"XXXXXXXXX",
   "gender":2,
   "dob":"YYYY-MM-DD",
   "profile":{
      "caption":"Talk to me",
      "ethnicity":1,
      "weight":88452,
      "height":183,
      "bodytype":2,
      "smoke":1,
      "drink":2,
      "initially_seeking":4,
      "relationship":3
   },
   "pref":{
      "opento":"|1|5|15|16|18|19|23|",
      "opento_abstract":"I could be reached",
      "turnsmeon":"|3|5|10|11|12|14|17|18|20|22|23|27|28|29|",
      "lookingfor":"|7|9|10|11|12|14|19|21|27|28|29|31|34|37|38|42|43|47|48|49|"
   },
   "main_photo":0,
   "security_question":0
}
```

# Connect to elasticsearch

Not the hardest part. But may be because I'm practicing elasticsearch for almost 5 years :)!

For new comers, you have to:

* [download](https://www.elastic.co/downloads/elasticsearch). 1.7.1 was the latest at this moment.
* unzip: `tar xzf elasticsearch-1.7.1.tar.gz`
* install [marvel](https://www.elastic.co/products/marvel/): `bin/plugin install elasticsearch/marvel/latest`
* launch: `bin/elasticsearch`

And connect logstash...

```rb
output {
  elasticsearch {
    host => "localhost"
    port => "9200"
    protocol => "http"
    index => "ashley-%{+YYYY}"
    document_type => "person"
    document_id => "%{id}"
    template => "ashley_template.json"
    template_name => "ashley"
  }

  stdout {
    codec => "dots"
  }
}
```

Note that we send documents grouped by year in an index named `ashley-YEAR4DIGITS`, using type `person` and with the original `id` as the document `_id`.

`ashley_template.json` file contains our template. We define that we use 1 single shard, that we don't need `_all` field and some other settings:

```json
{
  "template": "ashley-*",
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
        },
        "location": {
          "type": "geo_point"
        },
        "updatedon": {
          "type": "date",
          "format": "yyyy-MM-dd HH:mm:ss",
          "ignore_malformed": true
        },
        "dob": {
          "type": "date",
          "format": "yyyy-MM-dd",
          "ignore_malformed": true
        }
      }
    }
  }
}
```

Launch!

```sh
gunzip am_am.dump.gz
cat am_am.dump | bin/logstash -f ashley-member_details.conf -w 2
```

What is this `-w 2`? Well, I have 4 processors on my machine, so I'll use 2 workers for logstash.






---
title: "Next movie to watch based on recommendation"
#description: 
toc: true
authors:
  - David Pilato
tags:
  - elasticsearch
  - mahout
  - recommandation
categories:
  - tutorial
date: 2015-09-17 14:42:05 +0200
lastmod: 2015-09-17 14:42:05 +0200
# featuredImage: blog/2016-03-17-and-the-beats-go-on/beats.png
draft: false
aliases:
  - /blog/2015/09/17/next-movie-to-watch-based-on-recommendation/
---

This article is based on [Recommender System with Mahout and Elasticsearch tutorial](https://www.mapr.com/products/mapr-sandbox-hadoop/tutorials/recommender-tutorial) created by [MapR](https://www.mapr.com).

It now uses the [20M MovieLens dataset](http://grouplens.org/datasets/movielens/) which contains: 20 million ratings and 465 000 tag applications applied to 27 000 movies by 138 000 users and was released in 4/2015.
The format with this recent version has changed a bit so I needed to adapt the existing scripts to the new format.

<!-- more -->

## Prerequisites

* Download the [20M MovieLens dataset](http://grouplens.org/datasets/movielens/). Unzip it. You'll get a `ml-20m` dir.
* Install [elasticsearch](http://www.elastic.co/guide/en/elasticsearch/guide/current/index.html)
* Install [Mahout](http://mahout.apache.org/)
* Install [MapR sandbox](https://www.mapr.com/products/mapr-sandbox-hadoop) (optional)

## Step 1: generate Mahout dataset with recommandations

The `ml-20m/ratings.csv` file looks like:

```txt
userId,movieId,rating,timestamp
1,2,3.5,1112486027
1,29,3.5,1112484676
1,32,3.5,1112484819
1,47,3.5,1112484727
1,50,3.5,1112484580
1,112,3.5,1094785740
1,151,4.0,1094785734
1,223,4.0,1112485573
1,253,4.0,1112484940
```

We use a python script `01-generateMahout.py` to generate a bulk file for elasticsearch:

```python
import re
count=0
with open('ml-20m/ratings.csv','r') as csv_file:
   content = csv_file.readlines()
   for line in content:
        fixed = re.sub(",", "\t", line).rstrip()
        splitted = fixed.split("\t")
        if splitted[0]<>"userId":
            print '%s' % fixed
```

Execute:

```sh
python 01-generateMahout.py > ratings.mahout
```

`ratings.mahout` now contains:

```txt
1 2 3.5 1112486027
1 29 3.5 1112484676
1 32 3.5 1112484819
1 47 3.5 1112484727
1 50 3.5 1112484580
1 112 3.5 1094785740
1 151 4.0 1094785734
1 223 4.0 1112485573
1 253 4.0 1112484940
1 260 4.0 1112484826
```

## Step 2: run Mahout on recommandation dataset

```sh
mahout/apache-mahout-distribution-0.11.0/bin/mahout itemsimilarity \
  --input ratings.mahout \
  --output ratings.ml \
  --similarityClassname SIMILARITY_LOGLIKELIHOOD \
  --booleanData TRUE \
  --tempDir tmp
```

`ratings.ml/part-r-00000` contains:

```txt
1 9 0.9213700644458795
1 287 0.9517320394600995
1 538 0.9364996182501258
1 1060 0.9431549395675928
1 1100 0.926317994961507
1 1248 0.9393274329597747
1 1306 0.9294993147867059
1 1381 0.921063088822617
1 1767 0.932077384608552
1 2048 0.926317994961507
```

## Step 3: generate elasticsearch dataset with movies

Unzip it. You should see `ml-20m/movies.csv` file. It looks like:

```txt
movieId,title,genres
1,Toy Story (1995),Adventure|Animation|Children|Comedy|Fantasy
2,Jumanji (1995),Adventure|Children|Fantasy
3,Grumpier Old Men (1995),Comedy|Romance
4,Waiting to Exhale (1995),Comedy|Drama|Romance
5,Father of the Bride Part II (1995),Comedy
6,Heat (1995),Action|Crime|Thriller
7,Sabrina (1995),Comedy|Romance
8,Tom and Huck (1995),Adventure|Children
9,Sudden Death (1995),Action
```

We use a python script `03-generateJson.py` to generate a bulk file for elasticsearch:

```python
import re
import json
count=0
with open('ml-20m/movies.csv','r') as csv_file:
   content = csv_file.readlines()
   for line in content:
        fixed = re.sub(",", "\t", line).rstrip().split("\t")
        if fixed[0]<>"movieId":
          if len(fixed)==3:
            title = re.sub(" \(.*\)$", "", re.sub('"','', fixed[1]))
            genre = fixed[2].split('|')
            print '{ "create" : { "_index" : "bigmovie", "_type" : "film", "_id" : "%s" } }' %  fixed[0]
            print '{ "id": "%s", "title" : "%s", "year":"%s" , "genre":%s }' % (fixed[0],title, fixed[1][-5:-1], json.dumps(genre))
```

Execute:

```sh
python 03-generateJson.py > movies.json
```

`movies.json` now contains:

```json
{ "create" : { "_index" : "bigmovie", "_type" : "film", "_id" : "1" } }
{ "id": "1", "title" : "Toy Story", "year":"1995" , "genre":["Adventure", "Animation", "Children", "Comedy", "Fantasy"] }
{ "create" : { "_index" : "bigmovie", "_type" : "film", "_id" : "2" } }
{ "id": "2", "title" : "Jumanji", "year":"1995" , "genre":["Adventure", "Children", "Fantasy"] }
{ "create" : { "_index" : "bigmovie", "_type" : "film", "_id" : "3" } }
{ "id": "3", "title" : "Grumpier Old Men", "year":"1995" , "genre":["Comedy", "Romance"] }
{ "create" : { "_index" : "bigmovie", "_type" : "film", "_id" : "4" } }
{ "id": "4", "title" : "Waiting to Exhale", "year":"1995" , "genre":["Comedy", "Drama", "Romance"] }
{ "create" : { "_index" : "bigmovie", "_type" : "film", "_id" : "5" } }
{ "id": "5", "title" : "Father of the Bride Part II", "year":"1995" , "genre":["Comedy"] }
```

## Step 4: generate elasticsearch update with recommandations

Using `ratings.ml/part-r-00000` we have generated earlier, we can now generate an update script for elasticsearch.

We use a python script `04-generateUpdate.py` to generate the bulk file:

```python
import fileinput
from string import join
import json
import csv
import json
### read the output from MAHOUT and collect into hash ###
with open('ratings.ml/part-r-00000','r') as csv_file:
    csv_reader = csv.reader(csv_file,delimiter='\t')
    old_id = ""
    indicators = []
    update = {"update" : {"_id":""}}
    doc = {"doc" : {"indicators":[], "numFields":0}}
    for row in csv_reader:
        id = row[0]
        if (id != old_id and old_id != ""):
            update["update"]["_id"] = old_id
            doc["doc"]["indicators"] = indicators
            doc["doc"]["numFields"] = len(indicators)
            print(json.dumps(update))
            print(json.dumps(doc))
            indicators = [row[1]]
        else:
            indicators.append(row[1])
        old_id = id
```

Execute:

```sh
python 04-generateUpdate.py > updates.json
```

`updates.json` now contains:

```json
{"update": {"_id": "1"}}
{"doc": {"indicators": ["9", "287", "538", "1060", "1100", "1248", "1306", "1381", "1767", "2048", "2056", "2161", "2259", "2283", "2380", "2416", "2605", "2798", "2814", "2988", "3114", "3264", "3616", "3720", "3783", "3912", "3948", "3996", "4711", "4963", "6148", "6408", "6659", "6711", "7442", "7481", "8493", "8915", "9005", "26631", "26812", "27395", "42728", "43396", "43556", "45179", "45499", "45722", "46322", "47423", "47997", "49822", "51709", "52435", "52806", "52950", "53460", "57274", "57946", "58299", "62662", "62999", "65982", "68952", "71464", "73808", "74624", "79139", "79541", "79681", "79695", "82459", "82931", "85056", "85131", "88235", "89190", "89347", "91995", "92420", "93295", "93363", "93547", "93766", "95223", "96144", "96407", "97070", "97913", "98243", "98809", "102407", "102903", "103433", "105181", "105959", "106002", "106565", "108120", "109487", "111362", "112705"], "numFields": 102}}
{"update": {"_id": "2"}}
{"doc": {"indicators": ["13", "42", "54", "73", "103", "141", "152", "155", "248", "257", "304", "542", "543", "688", "754", "785", "879", "1020", "1175", "1265", "1489", "1590", "1869", "2045", "2090", "2092", "2099", "2135", "2173", "2278", "2294", "2322", "2377", "2587", "2616", "2672", "2687", "2989", "3159", "3448", "3710", "3717", "3763", "3821", "3825", "3889", "3972", "4005", "4207", "4293", "4958", "4974", "5055", "5159", "5265", "5463", "5582", "5628", "5784", "5785", "5833", "5970", "6196", "6210", "6548", "6663", "8528", "8814", "26527", "33004", "33679", "34532", "37058", "38867", "39231", "43727", "45668", "48304", "48997", "49280", "50160", "50442", "52241", "52283", "53550", "54278", "55241", "55768", "56915", "58103", "58154", "59016", "59336", "61729", "64497", "65514", "68324", "71205", "74297", "74545", "82602", "83758", "84954", "86190", "88814", "89308", "89753", "91542", "95207", "102553", "109366", "110562", "127136"], "numFields": 113}}
```

## Step 5: import in elasticsearch

```sh
curl -XDELETE 'http://0.0.0.0:9200/bigmovie?pretty'
curl -XPUT 'http://0.0.0.0:9200/bigmovie?pretty' -d '
{
  "mappings": {
    "film" : {
      "properties" : {
        "numFields" : { "type": "integer" },
        "genre": { "type": "string", "index": "not_analyzed" }
      }
    }
  }
}'
curl -s -XPOST '0.0.0.0:9200/_bulk' --data-binary @movies.json; echo
curl -s -XPOST '0.0.0.0:9200/bigmovie/film/_bulk' --data-binary @updates.json; echo
```

## Step 6: play with the dataset

Let's pick a movie named `superman`:

```json
GET bigmovie/_search
{
  "query": {
    "match": {
      "title": "superman"
    }
  },
  "fields":["title","genre", "year"]
}
```

One of the movie I loved. Note its `_id` (`2641`):

```json
{
    "_index": "bigmovie",
    "_type": "film",
    "_id": "2641",
    "_score": 4.83445,
    "fields": {
       "title": [
          "Superman II"
       ],
       "genre": [
          "Action",
          "Sci-Fi"
       ],
       "year": [
          "1980"
       ]
    }
}
```

Searching for `batman`:

```json
GET bigmovie/_search
{
  "query": {
    "match": {
      "title": "batman"
    }
  },
  "fields":["title","genre", "year"]
}
```

`Batman Begins` is a good one! (`_id`:`33794`)

```json
{
    "_index": "bigmovie",
    "_type": "film",
    "_id": "33794",
    "_score": 4.604375,
    "fields": {
       "title": [
          "Batman Begins"
       ],
       "genre": [
          "Action",
          "Crime",
          "IMAX"
       ],
       "year": [
          "2005"
       ]
    }
}
```

What other users could recommand me now?

```json
GET /bigmovie/film/_search?pretty
{
  "query": {
     "bool": {
       "must": [ { "match": { "indicators":"2641 33794"} } ],
       "must_not": [ { "ids": { "values": ["2641", "33794"] } } ]
     }
  },
  "fields":["title","genre", "year"]
}
```

I'm getting back:

```json
{
   "took": 4,
   "timed_out": false,
   "_shards": {
      "total": 5,
      "successful": 5,
      "failed": 0
   },
   "hits": {
      "total": 72,
      "max_score": 0.51542056,
      "hits": [
         {
            "_index": "bigmovie",
            "_type": "film",
            "_id": "32535",
            "_score": 0.51542056,
            "fields": {
               "title": [
                  "No One Writes to the Colonel"
               ],
               "genre": [
                  "Drama"
               ],
               "year": [
                  "1999"
               ]
            }
         },
         {
            "_index": "bigmovie",
            "_type": "film",
            "_id": "2101",
            "_score": 0.3404896,
            "fields": {
               "title": [
                  "Squanto: A Warrior's Tale"
               ],
               "genre": [
                  "Adventure",
                  "Drama"
               ],
               "year": [
                  "1994"
               ]
            }
         },
         {
            "_index": "bigmovie",
            "_type": "film",
            "_id": "539",
            "_score": 0.2979284,
            "fields": {
               "title": [
                  "Sleepless in Seattle"
               ],
               "genre": [
                  "Comedy",
                  "Drama",
                  "Romance"
               ],
               "year": [
                  "1993"
               ]
            }
         },
         {
            "_index": "bigmovie",
            "_type": "film",
            "_id": "2533",
            "_score": 0.29684773,
            "fields": {
               "title": [
                  "Escape from the Planet of the Apes"
               ],
               "genre": [
                  "Action",
                  "Sci-Fi"
               ],
               "year": [
                  "1971"
               ]
            }
         },
         {
            "_index": "bigmovie",
            "_type": "film",
            "_id": "1849",
            "_score": 0.27565312,
            "fields": {
               "title": [
                  "Prince Valiant"
               ],
               "genre": [
                  "Adventure"
               ],
               "year": [
                  "1997"
               ]
            }
         },
         {
            "_index": "bigmovie",
            "_type": "film",
            "_id": "2412",
            "_score": 0.27565312,
            "fields": {
               "title": [
                  "Rocky V"
               ],
               "genre": [
                  "Action",
                  "Drama"
               ],
               "year": [
                  "1990"
               ]
            }
         },
         {
            "_index": "bigmovie",
            "_type": "film",
            "_id": "2640",
            "_score": 0.27565312,
            "fields": {
               "title": [
                  "Superman"
               ],
               "genre": [
                  "Action",
                  "Adventure",
                  "Sci-Fi"
               ],
               "year": [
                  "1978"
               ]
            }
         },
         {
            "_index": "bigmovie",
            "_type": "film",
            "_id": "2291",
            "_score": 0.26844263,
            "fields": {
               "title": [
                  "Edward Scissorhands"
               ],
               "genre": [
                  "Drama",
                  "Fantasy",
                  "Romance"
               ],
               "year": [
                  "1990"
               ]
            }
         },
         {
            "_index": "bigmovie",
            "_type": "film",
            "_id": "8807",
            "_score": 0.26844263,
            "fields": {
               "title": [
                  "Harold and Kumar Go to White Castle"
               ],
               "genre": [
                  "Adventure",
                  "Comedy"
               ],
               "year": [
                  "2004"
               ]
            }
         },
         {
            "_index": "bigmovie",
            "_type": "film",
            "_id": "4370",
            "_score": 0.2622487,
            "fields": {
               "title": [
                  "A.I. Artificial Intelligence"
               ],
               "genre": [
                  "Adventure",
                  "Drama",
                  "Sci-Fi"
               ],
               "year": [
                  "2001"
               ]
            }
         }
      ]
   }
}
```

I now know what I should look next! :)

## Step 6+: recommend titles, not ids

For now we recommend movies by looking first at other movies based on their ids.
My goal is to create an interface on top of elasticsearch, actually I'll use Kibana and directly enter a movie name, a category or whatever and find the TOP10 recommended movies.

Stay tuned!

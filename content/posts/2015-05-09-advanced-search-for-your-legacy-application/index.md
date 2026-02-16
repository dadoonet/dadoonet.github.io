---
title: "Advanced search for your Legacy application"
description: "How to add a real search engine for your legacy application"
author: David Pilato
avatar: /about/david_pilato.avif
tags:
  - elasticsearch
  - hibernate
  - sql
  - conference
categories:
  - tutorial
date: 2015-05-09 14:15:05 +0300
nolastmod: true
cover: featured.avif
draft: false
aliases:
  - /blog/2015/05/09/advanced-search-for-your-legacy-application/
  - /blog/2015-05-09-advanced-search-for-your-legacy-application/
---

I gave recently a [talk at Voxxed Istanbul 2015]({{< ref "talks/2015/2015-05-09-voxxed-istanbul" >}}) and I'd like to share here the story of this talk.

The talk was about adding a real search engine for your legacy application.
Here "legacy" means an application which is still using SQL statements to execute search requests.

{{< speakerdeck 14b4a923983d4fdd93a2cc218f0deee7 >}}

<!--more-->

Our current CRM application can visualize our customers. Each person is represented as a `Person` bean and have some properties like `name`, `dateOfBirth`, `children`, `country`, `city` and some metrics related to the number of clicks each person did on the `car` or `food` buttons on our mobile application (center of interests that is).

{{< figure src="beans.avif" caption="Java Beans" >}}

Our database schema is quite similar.

{{< figure src="tables.avif" caption="Database tables" >}}

## Running the existing code

The existing code is available on [Github](https://github.com/dadoonet/legacy-search):

```sh
git clone https://github.com/dadoonet/legacy-search.git
git checkout 00-legacy
```

You need to have:

* Maven
* JDK7 or higher
* Postgresql up and running

Modify `src/main/resources/hibernate.cfg.xml` file to reflect your own postgresql settings:

```xml
<!-- Database connection settings -->
<property name="hibernate.connection.url">jdbc:postgresql://localhost:5432/dpilato</property>
<property name="hibernate.connection.username">dpilato</property>
<property name="hibernate.connection.password"></property>
```

Start the server using jetty:

```sh
mvn clean install
mvn jetty:run
```

Then open your browser at <http://0.0.0.0:8080/>. You should see that our database is empty.

Click on the [init tab](http://0.0.0.0:8080/#/init) and inject 10000 random persons.

{{< figure src="00-inject.avif" caption="Injecting 10 000 documents" >}}

[Home page](http://0.0.0.0:8080/#/) now gives you your 10 000 persons back.

{{< figure src="00-search-all.avif" caption="Searching all" >}}

Note that you can search within `name`, `country` and `city` fields.

{{< figure src="00-search-jo.avif" caption="Searching for jo" >}}

The [Advanced Search tab](http://0.0.0.0:8080/#/advanced) allows to run more specific searches using a more classic search form with 3 fields.

{{< figure src="00-search-advanced.avif" caption="Searching for joe, england, plymouth" >}}

## Connecting to elasticsearch

### Using an ETL or a JDBC River

You can use an ETL and to read again your database and inject documents in elasticsearch. But you have to think of keeping all the things in sync. For example, when you want to remove an object from the database, you need to deal with that to remove it as well from elasticsearch. You can potentially use a technical table to do that which will contain something like a date, the id of the person which has been modified and the type of action, like `upsert` or `delete`.

This way the ETL can read again the same table every x minutes and do what is needed and also remove from this technical table all objects that has been processed so far.

Remember that reading again a database might have a cost on the database especially if you have a complicated model with collections of collections of collections of attributes.

And also, if you need to propose to your user real-time search or near real-time search, that won't be possible with an ETL which runs every x minutes.

The exact same thing applies to the [JDBC river](https://github.com/jprante/elasticsearch-river-jdbc) although it's a very well written component, it's still an ETL but running inside an elasticsearch node. Also consider that [rivers have been deprecated](https://www.elastic.co/blog/deprecating_rivers) and will be removed in the future.

### Direct connection

So, my favorite way to deal with that and by the way reduce the overall complexity is by modifying directly the existing application. When you are about to write a bean to the database, you can reuse the exact same bean which is already loaded in memory, serialize it to JSON and send it to elasticsearch.

### Adding elasticsearch

You first need to add elasticsearch library to your `pom.xml` file:

```xml
<!-- Elasticsearch -->
<dependency>
  <groupId>org.elasticsearch</groupId>
  <artifactId>elasticsearch</artifactId>
  <version>1.5.2</version>
</dependency>
```

Create a new `ElasticsearchDao` class in the `dao` package:

```java
// We are using RESTX framework here so it's a restx.factory.Component annotation
@Component
public class ElasticsearchDao {
  final private ObjectMapper mapper;
  final private Client esClient;

  @Inject
  public ElasticsearchDao(ObjectMapper mapper) {
    this.mapper = mapper;
    this.esClient = null; // TODO add a client
  }

  public void save(Person person) throws Exception {
    // TODO implement
  }

  public void delete(String reference) throws Exception {
    // TODO implement
  }

  public SearchResponse search(QueryBuilder query, Integer from, Integer size) {
    // TODO implement
    return null;
  }
}
```

Inject this class in `PersonService`:

```java
public class PersonService {
  // ...
  private final ElasticsearchDao elasticsearchDao;

  @Inject
  public PersonService(PersonDao personDao, SearchDao searchDao,
                       HibernateService hibernateService,
                       ElasticsearchDao elasticsearchDao,
                       ObjectMapper mapper, DozerBeanMapper dozerBeanMapper) {
    // ...
    this.elasticsearchDao = elasticsearchDao;
  }
// ...
}
```

Call elasticsearch DAO save and delete methods from the service layer:

```java
public Person save(Person person) {
  // ...
  Person personDb = personDao.save(person);
  // Add here the call to delete method
  try {
    elasticsearchDao.save(person);
  } catch (Exception e) {
    logger.error("Houston, we have a problem!", e);
  }
  // ...
}
```

```java
public boolean delete(String id) {
  // ...
  personDao.delete(person);
  // Add here the call to delete method
  try {
    elasticsearchDao.delete(person.getReference());
  } catch (Exception e) {
    logger.error("Houston, we have a problem!", e);
  }
  // ...
}
```

Note that we choose here to simply log the error and not fail the transaction because we want to make sure that our bean is stored in the database.
You could potentially want to rollback the current transaction and keep both systems consistent.

Here we just log so it will be the responsability of our OPS team to deal with errors and reinject missing documents.
You could also think of sending errors in another table or in a message queue system to process them later.

### Create a client

Let's implement our dao. First we need to create a client to connect to a running elasticsearch cluster:

```java
this.esClient = new TransportClient()
  .addTransportAddress(
    // We will connect locally on default transport port 9300
    new InetSocketTransportAddress("127.0.0.1", 9300));
```

We are using here a `TransportClient` but you can use also a `NodeClient`. See [this article (french)]({{< ref "2012-02-13-quel-client-java-pour-elasticsearch" >}}).

### Save an object

Then, implement our `save` method:

```java
// We use Jackson to generate a JSON document from our bean
byte[] bytes = mapper.writeValueAsBytes(person);

// We execute an index operation
esClient.index(
  new IndexRequest(
      "person",              // Index name
      "person",              // Our document type
      person.getReference()  // We provide a unique _id for this doc
    )
    .source(bytes)           // We provide the JSON content
  ).get();                   // We execute and get back the response
```

### Remove an object

`delete` method is quite similar:

```java
esClient.delete(
  new DeleteRequest(
    "person",       // Index name
    "person",       // Our document type
    reference)      // The document we want to remove
  ).get();          // We execute and get back the response
```

### Using bulk

But this is not the more efficient way for doing that. In order to have a much faster injection time, please use bulk. Bulk allows to add a set of requests and process the bulk every `x` seconds or every `y` documents.

Instead of writing all the logic by yourself you can easily use the `BulkProcessor` class which has been designed for that. Add it to the `ElasticsearchDao` class:

```java
final private BulkProcessor bulkProcessor;
```

In the contructor, add:

```java
this.bulkProcessor = BulkProcessor.builder(esClient, new BulkProcessor.Listener() {
  @Override
  public void beforeBulk(long executionId, BulkRequest request) { }

  @Override
  public void afterBulk(long executionId, BulkRequest request, BulkResponse response) { }

  @Override
  public void afterBulk(long executionId, BulkRequest request, Throwable failure) { }
})
  .setBulkActions(10000) // We flush every 10 000 requests
  .setFlushInterval(TimeValue.timeValueSeconds(5)) // Or every 5 seconds
  .build();
```

Replace in the `save` method:

```java
esClient.index(
  new IndexRequest(
      "person",              // Index name
      "person",              // Our document type
      person.getReference()  // We provide a unique _id for this doc
    )
    .source(bytes)           // We provide the JSON content
  ).get();                   // We execute and get back the response
```

by

```java
bulkProcessor.add(
  new IndexRequest(
      "person",              // Index name
      "person",              // Our document type
      person.getReference()  // We provide a unique _id for this doc
    )
    .source(bytes)           // We provide the JSON content
  );
```

Same for `delete`:

```java
bulkProcessor.add(
  new DeleteRequest(
    "person",       // Index name
    "person",       // Our document type
    reference)      // The document we want to remove
  );
```

### Searching for documents

So far, we can save and delete documents but we need to adapt our search to this as it's still using the SQL search.

We have already created a skeleton for the `search` method in the `ElasticsearchDao` class. Let's implement it!

```java
return esClient.prepareSearch("person") // We search in "person" index
  .setTypes("person")                   // We only want "person" documents
  .setQuery(query)                      // We pass the query
  .setFrom(from)                        // We set the pagination (from)
  .setSize(size)                        // We set the page size
  .get();                               // We execute, get back the result and return it
```

In `PersonService` we can create the Query we need for our fulltext search.

```java
public String search(String q, String f_country, String f_date, Integer from, Integer size) {
  QueryBuilder query;
  // If the user does not provide any text to query, let's match all documents
  if (!Strings.hasText(q)) {
    query = QueryBuilders.matchAllQuery();
  } else {
    query = QueryBuilders.simpleQueryStringQuery(q) // What we are searching for
      .field("name")                                // in name field
      .field("gender")                              // in gender field
      .field("address.country")                     // in address.country field
      .field("address.city");                       // in address.city field
  }
  // We execute our Dao
  SearchResponse response = elasticsearchDao.search(query, from, size);
  // We return here the result as a JSON document as we have an AngularJS webapp
  return response.toString();
}
```

Same for advanced search:

```java
public String advancedSearch(String name, String country, String city, Integer from, Integer size) {
  QueryBuilder query;

  // If the user does not provide any text to query, let's match all documents
  if (!Strings.hasText(name) && !Strings.hasText(country) && !Strings.hasText(city)) {
    query = QueryBuilders.matchAllQuery();
  } else {
    // Otherwise we will run a boolean query
    BoolQueryBuilder boolQueryBuilder = QueryBuilders.boolQuery();
    if (Strings.hasText(name)) {
      // If name parameter is set, its content must match name field
      boolQueryBuilder.must(
              QueryBuilders.matchQuery("name", name)
      );
    }
    if (Strings.hasText(country)) {
      // If country parameter is set, its content must match name field
      boolQueryBuilder.must(
              QueryBuilders.matchQuery("address.country", country)
      );
    }
    if (Strings.hasText(city)) {
      // If city parameter is set, its content must match name field
      boolQueryBuilder.must(
              QueryBuilders.matchQuery("address.city", city)
      );
    }

    query = boolQueryBuilder;
  }

  // We execute our Dao
  SearchResponse response = elasticsearchDao.search(query, from, size);
  // We return here the result as a JSON document as we have an AngularJS webapp
  return response.toString();
}
```

### Running it

Have a look at the final result in branch `02-bulk`.

```sh
git checkout 02-bulk
```

We are now ready to run it.

```sh
mvn clean install
mvn jetty:run
```

Download, install and start elasticsearch:

```sh
wget https://download.elastic.co/elasticsearch/elasticsearch/elasticsearch-1.5.2.tar.gz
tar xzf elasticsearch-1.5.2.tar.gz
# Install marvel
elasticsearch-1.5.2/bin/plugin -install elasticsearch/marvel/latest
# Start elasticsearch
elasticsearch-1.5.2/bin/elasticsearch
```

[Initialize 10000 persons](http://0.0.0.0:8080/#/init) and look at the effect in [marvel](http://127.0.0.1:9200/_plugin/marvel/).

{{< figure src="02-marvel.avif" caption="Marvel 10k documents" >}}

Try now [to search for](http://0.0.0.0:8080/) `j`, `jo` or `joe`. What's wrong?
Searching for `j` or `jo` does not match any document but `joe` gives expected results.

> Why this?

Because elasticsearch analyze your text at index and search times and compare then tokens.
In the inverted index, for the first name `Joe`, we have actually indexed `joe`. And `j` is different than `joe`. Same for `jo`. But `joe` equals `joe` so a document which contains `Joe` will match the query.

Same goes for advanced search. Searching for a country `fran` won't match but the full term `france` would match.

If you want to learn more about the analysis process, I'd suggest you read the fantastic [Mapping and Analysis chapter](https://www.elastic.co/guide/en/elasticsearch/guide/current/mapping-analysis.html) of the official elasticsearch user guide.

> Can we fix that?

For sure, we can use a [wildcard query](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-wildcard-query) or a [prefix query](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-prefix-query) but this is really inefficient! Please, don't do that! 😀

## Fix the mapping

Give a look [in sense](http://127.0.0.1:9200/_plugin/marvel/sense/index.html) at the generated mapping:

```json
GET person/person/_mapping
```

It gives

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
                        "properties": {
                           "lat": {
                              "type": "double"
                           },
                           "lon": {
                              "type": "double"
                           }
                        }
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
               },
               "reference": {
                  "type": "string"
               }
            }
         }
      }
   }
}
```

As you can imagine, we are using here all defaults to elasticsearch. So we are using a [standard analyzer](https://www.elastic.co/docs/reference/text-analysis/analysis-standard-analyzer) for example to analyze our text.

Let's say that instead of indexing `joe`, we want also to index `j` and `jo`. We can do that using a [edge ngram tokenfilter](https://www.elastic.co/docs/reference/text-analysis/analysis-edgengram-tokenizer). To do that, you need to create your own analyzer. It can be done when you create your index by providing settings:

```json
{
    "analysis": {
        "analyzer": {
            "ngram": {
                "filter": [
                    "lowercase"
                ], 
                "tokenizer": "ngram_tokenizer"
            }
        }, 
        "tokenizer": {
            "ngram_tokenizer": {
                "max_gram": "10", 
                "min_gram": "1", 
                "token_chars": [
                    "letter", 
                    "digit"
                ], 
                "type": "edgeNGram"
            }
        }
    }
}
```

We have defined here a `ngram` analyzer which will lowercase the content we need to index and will produce grams for each token (up to 10 characters).

Now, we need to force the mapping instead of letting elasticsearch automatically guessing for us.

For example let's look at our `name` field. It looks like this by default:

```json
"name": {
  "type": "string"
}
```

We can now change its analyzer:

```json
"name": {
  "type": "string",
  "analyzer": "ngram"
}
```

But at search time, searching for `joe` will also return unexpected results such as `jane`. Why this? Because by default, we use the same analyzer at search time and index time.
`joe` is once again analyzed at search time and produces `j`, `jo` and `joe`.
`jane` has been indexed as `j`, `ja`, `jan` and `jane`. `j` from `joe` equals `j` from `jane`!

In this use case, a user who enters `joe` is probably looking for someone named `joe` so we should only use a `lowercase` filter. The [simple analyzer](https://www.elastic.co/docs/reference/text-analysis/analysis-simple-analyzer) does that perfectly. Let's use it:

```json
"name": {
  "type": "string",
  "index_analyzer": "ngram",
  "search_analyzer": "simple"
}
```

If for some reason, you want to keep the "old" (standard) analyzer as well and index the same field in different ways, you can use the multifield feature of elasticsearch and write:

```json
"name": {
  "type": "string",
  "fields": {
    "autocomplete" : {
      "type": "string",
      "index_analyzer": "ngram",
      "search_analyzer": "simple"
    }
  }
}
```

It means that if you search in `name` you will use the standard analyzer. But if you search in `name.autocomplete`, you will use the expected behavior we have just described.

And you can do that for all other fields...

> Why not indexing all fields in a single field?

Instead of searching in `name`, `address.country`, `address.city` and `gender` fields, we can create at index time a new field on the fly using the very cool [copy_to feature](https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping-core-types.html#copy-to):

```json
"name": {
  "type": "string",
  "copy_to": "fulltext"
}
```

You can define analyzer you want to use for this new field:

```json
"fulltext" : {
  "type" : "string",
  "index_analyzer": "ngram",
  "search_analyzer": "simple"
}
```

At the end, you full mapping will become:

```json
{
    "person": {
        "_all": {
            "enabled": false
        }, 
        "properties": {
            "address": {
                "properties": {
                    "city": {
                        "copy_to": "fulltext", 
                        "fields": {
                            "autocomplete": {
                                "index_analyzer": "ngram", 
                                "search_analyzer": "simple", 
                                "type": "string"
                            }
                        }, 
                        "type": "string"
                    }, 
                    "country": {
                        "copy_to": "fulltext", 
                        "fields": {
                            "autocomplete": {
                                "index_analyzer": "ngram", 
                                "search_analyzer": "simple", 
                                "type": "string"
                            }
                        }, 
                        "type": "string"
                    }, 
                    "countrycode": {
                        "type": "string"
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
                "format": "dateOptionalTime", 
                "type": "date"
            }, 
            "fulltext": {
                "index_analyzer": "ngram", 
                "search_analyzer": "simple", 
                "type": "string"
            }, 
            "gender": {
                "copy_to": "fulltext", 
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
                "copy_to": "fulltext", 
                "fields": {
                    "autocomplete": {
                        "index_analyzer": "ngram", 
                        "search_analyzer": "simple", 
                        "type": "string"
                    }
                }, 
                "type": "string"
            }, 
            "reference": {
                "type": "string"
            }
        }
    }
}
```

Note that we also disabled `_all` field as we won't use it and defined `location` field as a `geo_point`.

## Elasticsearch Beyonder

You can of course use your client to create your index with the settings we have defined and then create a new type `person` which will use the mapping we created.

[Elasticsearch Beyonder](https://github.com/dadoonet/elasticsearch-beyonder) project will do that *automagically* for you if they don't exist already by reading what you have in the classloader.

By convention, it will search in your classloader for a `/elasticsearch` resource. If it contains a directory, that will be the index name. If this directory contains a `_settings.json` file, it will use it to put the settings when creating the index.
Then for each other `.json` file, it will create a new type based on the file name and will apply the mapping defined in it.

In our case, we will create in `src/main/resources`:

```txt
resources/
├── elasticsearch
│   └── person
│       ├── _settings.json
│       └── person.json
```

Let's now add Beyonder project in our `pom.xml` file:

```xml
<dependency>
  <groupId>fr.pilato.elasticsearch</groupId>
  <artifactId>elasticsearch-beyonder</artifactId>
  <version>1.5.0</version>
</dependency>
```

To use it, just after you have created your client in `ElasticsearchDao` constructor, you can use it by calling:

```java
try {
  ElasticsearchBeyonder.start(esClient);
} catch (Exception e) {
  logger.warn("can not create index and mappings", e);
}
```

## Modify search queries

Instead of searching in all fields we can now search in `fulltext` field:

```java
query = QueryBuilders.simpleQueryStringQuery(q)
  .field("fulltext");
```

But we can also play with relevancy here. Let's say that a user has the name `France` but lives in `Germany` and another one is `Joe` living in `France`. We want to make sure that in that case the first one will appear at the first position. Let's search also in `name` field and boost the score by a factor 3 in case it matches:

```java
query = QueryBuilders.simpleQueryStringQuery(q)
  .field("fulltext");
  .field("name", 3.0f);
```

We can also modify our advanced search and use now `.autocomplete` subfields:

```java
BoolQueryBuilder boolQueryBuilder = QueryBuilders.boolQuery();
if (Strings.hasText(name)) {
  boolQueryBuilder.must(
    QueryBuilders.matchQuery("name.autocomplete", name)
  );
}
if (Strings.hasText(country)) {
  boolQueryBuilder.must(
    QueryBuilders.matchQuery("address.country.autocomplete", country)
  );
}
if (Strings.hasText(city)) {
  boolQueryBuilder.must(
    QueryBuilders.matchQuery("address.city.autocomplete", city)
  );
}
```

To run that, first delete your existing documents with SENSE to have Beyonder creating again index and type:

```json
DELETE person
```

And restart the application, inject 10 000 documents and search for `j` and then for `joe`.

{{< figure src="03-search-j.avif" caption="Searching for J" >}}

It works as it was working before we started! `\o/`

## But it will slow down my application, right?

I have this question very often when doing talks.

Indeed. Adding something to your current injection process might slow it down. But is elasticsearch really the thing you need to optimize first?

Let's run a small test about that.

In our `PersonService#save` method, we can try to disable database operation and only keep indexing operation.

```java
public Person save(Person person) {
  try {
    elasticsearchDao.save(person);
  } catch (Exception e) {
    logger.error("Houston, we have a problem!", e);
  }
  return person;
}
```

Restart. And now inject 10 000 documents. You might not see that it has been done as it was so fast... So inject 1 000 000 documents now. You should see that you are injecting must faster without the database then with the database. On my laptop, it's from around 200 docs per second to around 10 000 docs per second. Ok, I have SSD drives but this gives you an idea.

It means that basically elasticsearch won't slow down that much your process.

## Faceted navigation

Let's do something even more interesting. Let's try to add a [faceted navigation](https://en.wikipedia.org/wiki/Faceted_search).
We want to display our result set broken per 10 years (`by_year`) and also get the repartition of our result set per country (`by_country`).

Everything was [already coded on the interface](https://github.com/dadoonet/legacy-search/blob/202bbb3d3b02aa648ec05e47e14155297be9ceb6/src/main/frontend/src/components/Search.tsx#L152). So we just have to provide the aggregation result now...

Let's modify `ElasticsearchDao#search` method:

```java
public SearchResponse search(QueryBuilder query, Integer from, Integer size) {
  return esClient.prepareSearch("person")
    .setTypes("person")
    .setQuery(query)
    // We add the by_country aggregation
    .addAggregation(
      AggregationBuilders.terms("by_country").field("address.country")
    )
    // We add the by_year aggregation
    .addAggregation(
      AggregationBuilders.dateHistogram("by_year")
        .field("dateOfBirth")
        .minDocCount(0)
        .interval(DateHistogram.Interval.YEAR)
        .extendedBounds("1940", "2009")
        .format("YYYY")
    )
    .setFrom(from)
    .setSize(size)
    .get();
}
```

Relaunching will now give you the following.

{{< figure src="04-faceted-1.avif" caption="Faceted results" >}}

Let say you now want to click on a country to filter results or on a decade.

Change `PersonService#search` with the following code.

```java
public String search(String q, String f_country, String f_date, Integer from, Integer size) {
  QueryBuilder query;
  if (!Strings.hasText(q)) {
    query = QueryBuilders.matchAllQuery();
  } else {
    query = QueryBuilders.simpleQueryStringQuery(q)
      .field("fulltext")
      .field("name", 3.0f);
  }

  // If the user defined a country filter or a date filter
  if (Strings.hasText(f_country) || Strings.hasText(f_date)) {
    // Create a And Filter
    AndFilterBuilder andFilter = FilterBuilders.andFilter();
    if (Strings.hasText(f_country)) {
      // If needed filter by country
      andFilter.add(FilterBuilders.termFilter("address.country", f_country));
    }
    if (Strings.hasText(f_date)) {
      // Or by decade
      String endDate = "" + (Integer.parseInt(f_date) + 10);
      andFilter.add(FilterBuilders.rangeFilter("dateOfBirth").gte(f_date).lt(endDate));
    }

    // Wrap the existing query and the new filter in a Filtered query
    query = QueryBuilders.filteredQuery(query, andFilter);
  }

  SearchResponse response = elasticsearchDao.search(query, from, size);
  return response.toString();
}
```

You can now filter your results!

{{< figure src="04-faceted-2.avif" caption="Filtered results" >}}

## Understand your dataset

> Ok. We have 1 000 000 documents. What do they look like?

We can change our first aggregation and create an aggregation tree.
So for each country, we want to break down our data to [almost every 10 years (3659 days)](https://github.com/elastic/elasticsearch/issues/8939) and for each "decade" get the average number of children.

```java
public SearchResponse search(QueryBuilder query, Integer from, Integer size) {
  return esClient.prepareSearch("person")
    .setTypes("person")
    .setQuery(query)
    .addAggregation(
      AggregationBuilders.terms("by_country").field("address.country")
        .subAggregation(AggregationBuilders.dateHistogram("by_year")
          .field("dateOfBirth")
          .minDocCount(0)
          .interval(DateHistogram.Interval.days(3652))
          .extendedBounds("1940", "2009")
          .format("YYYY")
          .subAggregation(
            AggregationBuilders.avg("avg_children").field("children")
          )
        )
    )
    .addAggregation(
      AggregationBuilders.dateHistogram("by_year")
        .field("dateOfBirth")
        .minDocCount(0)
        .interval(DateHistogram.Interval.YEAR)
        .extendedBounds("1940", "2009")
        .format("YYYY")
    )
    .setFrom(from)
    .setSize(size)
    .get();
}
```

Also add the compute tab in `index.html`.

```html
<li><a href="/#/compute">Compute</a></li>
```

You can run the final version using `05-compute` branch:

```sh
git checkout 05-compute
mvn clean install
mvn jetty:run
```

Opening [Compute tab](http://0.0.0.0:8080/#/compute) now gives you more knowledge about your dataset.

{{< figure src="05-compute.avif" caption="Compute results" >}}

## Conclusion

So we have migrated our search part of our application to a search engine instead of using search features provided by our datastore. We are keeping our source of truth in the SQL database but you could also imagine migrating from the legacy datastore to a NoSQL one if you need/want to.

What would happen in case of failure? For example, let say you want to stop your elasticsearch cluster for whatever reason. All index operation will failed and you will have to deal with that by yourself.

If you want to introduce an asynchronous indexing process, you could image to push your JSON documents to a message queue system and instead of writing by yourself the code which will read from the message queue, push to elasticsearch, deal with failures, you can use [Logstash](https://www.elastic.co/products/logstash) and one of its [input plugins](https://www.elastic.co/guide/en/logstash/current/input-plugins.html), for example:

* [Kafka](https://www.elastic.co/guide/en/logstash/current/plugins-inputs-kafka.html)
* [RabbitMQ](https://www.elastic.co/guide/en/logstash/current/plugins-inputs-rabbitmq.html)
* [Redis](https://www.elastic.co/guide/en/logstash/current/plugins-inputs-redis.html)

You can also scale out Logstash on multiple nodes if you need more injection power.

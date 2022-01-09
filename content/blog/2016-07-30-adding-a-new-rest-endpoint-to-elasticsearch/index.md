---
title: "Adding a new REST endpoint to elasticsearch"
#description: 
toc: true
authors:
  - David Pilato
tags:
  - java
  - elasticsearch
  - plugin
categories:
  - tutorial
series:
  - plugin for elasticsearch v5
date: 2016-07-30 14:50:00 +0200
lastmod: 2016-07-30 14:50:00 +0200
# featuredImage: assets/images/covers/new/logstash.png
draft: false
aliases:
  - /blog/2016/07/30/adding-a-new-rest-endpoint-to-elasticsearch/
---

**NOTE:** This article is now outdated. Please read [Adding a new REST endpoint to elasticsearch (Updated for GA)]({{< ref "2016-10-19-adding-a-new-rest-endpoint-to-elasticsearch-updated-for-ga" >}}) instead!

This blog post is part of a series which will teach you:

* [How to write a plugin for elasticsearch 5.0 using Maven]({{< ref "2016-07-27-creating-a-plugin-for-elasticsearch-5-dot-0-using-maven" >}}).
* How to add a new REST endpoint plugin to elasticsearch 5.0 (what you are reading now).
* How I wrote the `ingest-bano` plugin which will be hopefully released soonish. In this plugin, new REST endpoints have been added.

Imagine that you wish to add a new REST endpoint so you can send requests like:

```sh
curl -XGET "http://localhost:9200/_hello?name=David&pretty"

# Or

curl -XGET "http://localhost:9200/_hello/David&pretty"

# Or

curl -XGET "http://localhost:9200/_hello?pretty" -d '{
    "name": "David"
}'

# Or

curl -XPOST "http://localhost:9200/_hello?pretty" -d '{
    "name": "David"
}'
```

And you want to get back something like:

```json
{
    "message": "Hello David!"
}
```

Without any parameter:

```sh
curl -XGET "http://localhost:9200/_hello?pretty"
```

It should return:

```json
{
    "message": "Hello World!"
}
```

Or get back a list of existing indices and the number of documents for a given type of indices with:

```sh
curl -XGET http://localhost:9200/_bano
```

Let's see how to implement that!

<!-- more -->

With what we saw [in the previous article]({{< ref "2016-07-27-creating-a-plugin-for-elasticsearch-5-dot-0-using-maven" >}}), we now have a Plugin skeleton ready to host our REST endpoint code.
We also have seen [how to create real integration tests]({{< ref "2016-07-29-elasticsearch-real-integration-tests" >}}).

We are now all set to implement the REST endpoint and be able to test it with a REST Client.

## Rest Handler

### Rest Handler skeleton

Basically, we will extend the `BaseRestHandler` class. Let's create a `RestHelloAction` in `src/main/java/org/elasticsearch/ingest/bano/`:

```java
public class RestHelloAction extends BaseRestHandler {

    @Inject
    public RestHelloAction(Settings settings, RestController controller) {
        super(settings);
        // Register your handlers here
    }

    @Override
    protected void handleRequest(RestRequest request, RestChannel channel, NodeClient client) throws Exception {
        // Implement the REST logic here
    }
}
```

### Register endpoints

In the constructor, we can define when this class will be called:

```java
@Inject
public RestHelloAction(Settings settings, RestController controller) {
    super(settings);
    controller.registerHandler(GET, "/_hello", this);
}
```

Here we are expecting a `GET` request on `/_hello` endpoint.

### Register the REST handler

We need to define the REST handler in the plugin:

```java
@Override
public List<Class<? extends RestHandler>> getRestHandlers() {
    return Collections.singletonList(RestHelloAction.class);
}
```

### Test the endpoint

We have to add some "hacks" to the default integration tests. Let's create a `BanoRestIT` in
`src/test/java/org/elasticsearch/ingest/bano/`. Note that it extends `AbstractITCase`, which we have
have seen [previously]({{< ref "2016-07-29-elasticsearch-real-integration-tests" >}}):

```java
public class BanoRestIT extends AbstractITCase {
}
```

Let's now implement our first test:

```java
public void testHelloWorld() throws Exception {
    Response response = client.performRequest("GET", "/_hello");
    assertThat(entityAsMap(response), hasEntry("message", "Hello World!"));
}
```

### Implement handleRequest

As we did not implemented the REST logic yet, this test will obviously fail. Let's fix that in `RestHelloAction`.

First, we will send back a JSON object to the user. Elasticsearch provides `XContent` classes to deal
with this.
We can create a class which will represent our response:

```java
class Message implements ToXContent {

    private final String name;

    public Message(String name) {
        if (name == null) {
            this.name = "World";
        } else {
            this.name = name;
        }
    }

    @Override
    public XContentBuilder toXContent(XContentBuilder builder, Params params) throws IOException {
        return builder.field("message", "Hello " + name + "!");
    }
}
```

This class implements `ToXContent` so it provides a `toXContent` method where we build the actual JSON response.

Then, we implement `handleRequest` method:

```java
@Override
protected void handleRequest(RestRequest request, RestChannel channel, NodeClient client) throws Exception {
    RestToXContentListener<ToXContent> listener = new RestToXContentListener<>(channel);
    listener.onResponse(new Message(null));
}
```

## Dealing with parameters

### Query Parameters

We want to support:

```sh
curl -XGET "http://localhost:9200/_hello?name=David&pretty"
```

Let's first implement a test for it (yeah! I love test driven development):

```java
public void testHelloDaviddWithQueryParameters() throws Exception {
    Response response = client.performRequest("GET", "/_hello?name=David");
    assertThat(entityAsMap(response), hasEntry("message", "Hello David!"));
}
```

And fix the test in `handleRequest` method...

```java
protected void handleRequest(RestRequest request, RestChannel channel, NodeClient client) throws Exception {
    RestToXContentListener<ToXContent> listener = new RestToXContentListener<>(channel);
    String name = request.param("name");
    listener.onResponse(new Message(name));
}
```

### Parameters in URL

We want to support:

```sh
curl -XGET "http://localhost:9200/_hello/David&pretty"
```

Let's again implement a test for it:

```java
public void testHelloDavidWithURLParameters() throws Exception {
    Response response = client.performRequest("GET", "/_hello/David");
    assertThat(entityAsMap(response), hasEntry("message", "Hello David!"));
}
```

It will send back an error `400 (Bad Request)` as this URL pattern does not exist.
Let's add it in the `RestHelloAction` constructor by registering now:

```java
controller.registerHandler(GET, "/_hello/{name}", this);
```

`name` will be the placeholder for this parameter. Well. That's cool. We don't need to change the implementation!

### Parameters as JSON documents

We want to support:

```sh
curl -XGET "http://localhost:9200/_hello?pretty" -d '{
    "name": "David"
}'

# Or

curl -XPOST "http://localhost:9200/_hello?pretty" -d '{
    "name": "David"
}'
```

That's a good practice to support both as some clients don't support `GET` with body.

```java
public void testHelloDavidWithGetBody() throws Exception {
    Response response = client.performRequest("GET", "/_hello",
            Collections.emptyMap(), new StringEntity("{\"name\":\"David\"}"));
    assertThat(entityAsMap(response), hasEntry("message", "Hello David!"));
}

public void testHelloDavidWithPostBody() throws Exception {
    Response response = client.performRequest("POST", "/_hello",
            Collections.emptyMap(), new StringEntity("{\"name\":\"David\"}"));
    assertThat(entityAsMap(response), hasEntry("message", "Hello David!"));
}
```

We need in `handleRequest` to extract the name from the body:

```java
public void handleRequest(RestRequest request, RestChannel channel, NodeClient client) throws Exception {
    RestToXContentListener<ToXContent> listener = new RestToXContentListener<>(channel);
    String name = request.param("name");

    if (name == null && request.content().length() > 0) {
        // Let's try to find the name from the body
        Map<String, Object> map = XContentHelper.convertToMap(request.content(), false).v2();
        if (map.containsKey("name")) {
            name = (String) map.get("name");
        }
    }

    listener.onResponse(new Message(name));
}
```

And we also need to register the `POST` request. Let's add it in the `RestHelloAction` constructor by
registering now:

```java
controller.registerHandler(POST, "/_hello", this);
```

Et voilà!

## Calling elasticsearch client

You can also call elasticsearch client to perform some tasks and then send the result back to the caller.

Here for example, we want to call:

```sh
curl -XGET http://localhost:9200/_bano
```

And get back an array containing the list of all indices starting with `.bano` in the cluster:

```json
{
    "bano": [
        ".bano-17",
        ".bano-95",
        ".bano-29"
    ]
}
```

### Add a test

As usual, we start adding a test:

```java
public void testBano() throws Exception {
    // We first create some indices
    int numIndices = randomIntBetween(1, 10);
    for (int i = 0; i < numIndices; i++) {
        client.performRequest("PUT", "/.bano-" + i);
    }
    // We create some other indices
    int numOtherIndices = randomIntBetween(1, 10);
    for (int i = 0; i < numOtherIndices; i++) {
        client.performRequest("PUT", "/" + randomAsciiOfLengthBetween(6, 10).toLowerCase(Locale.getDefault()));
    }

    client.performRequest("GET", "/_cluster/health", Collections.singletonMap("wait_for_status", "yellow"));

    Response response = client.performRequest("GET", "/_bano");
    Map<String, Object> responseMap = entityAsMap(response);
    assertThat(responseMap, hasKey("bano"));
    List<String> bano = (List<String>) responseMap.get("bano");
    for (int i = 0; i < numIndices; i++) {
        assertThat(bano, hasItem(".bano-" + i));
    }
}
```

The test generates a random number of indices starting with `.bano` plus some other unrelated indices.

Let's now create a new `RestBanoAction` as we did for `RestHelloAction`:

```java
public class RestBanoAction extends BaseRestHandler {

    @Inject
    public RestBanoAction(Settings settings, RestController controller) {
        super(settings);
        controller.registerHandler(GET, "/_bano", this);
    }

    @Override
    protected void handleRequest(RestRequest request, RestChannel channel, NodeClient client) throws Exception {
    }
}
```

We register it in the plugin:

```java
public List<Class<? extends RestHandler>> getRestHandlers() {
return Arrays.asList(
        RestHelloAction.class,
        RestBanoAction.class);
}
```

Let's implement the logic in `handleRequest`:

```java
@Override
public void handleRequest(RestRequest request, RestChannel channel, NodeClient client) throws Exception {
    RestToXContentListener<ToXContent> listener = new RestToXContentListener<>(channel);

    client.admin().indices().prepareGetIndex()
            .setIndices(".bano*")
            .execute(new ActionListener<GetIndexResponse>() {
        @Override
        public void onResponse(GetIndexResponse getIndexResponse) {
            Indices indices = new Indices();
            for (String index : getIndexResponse.getIndices()) {
                indices.addIndex(index);
            }
            listener.onResponse(indices);
        }

        @Override
        public void onFailure(Exception e) {
            listener.onFailure(e);
        }
    });
}
```

As you can see, we don't block the thread here as we are using a Listener which is called once
the request in the cluster is over.
This is **extremly important** in the context of elasticsearch as it frees the network socket which can
hold other requests and is not blocked by the current one.

If everything goes well, `onResponse` method will be called. Otherwise we will call `onFailure`.

`Indices` is a new class as we have seen before which will help us to serialize to JSON the response:

```java
class Indices implements ToXContent {

    private final List<String> indices;

    public Indices() {
        indices = new ArrayList<>();
    }

    public void addIndex(String index) {
        indices.add(index);
    }

    @Override
    public XContentBuilder toXContent(XContentBuilder builder, Params params) throws IOException {
        builder.startArray("bano");
        for (String index : indices) {
            builder.value(index);
        }
        return builder.endArray();
    }
}
```

## What's next?

In a coming blog post, I'll explain how to create an ingest plugin which will helps you to transform a french postal address to geo coordinates or the other way around. We will use what we have just seen to add some administrative tasks like automatically create our datasources in elasticsearch
(download CSV files from bano website, extract, transform to JSON and index in elasticsearch).

Stay tuned!

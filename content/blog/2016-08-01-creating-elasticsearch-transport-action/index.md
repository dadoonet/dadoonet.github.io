---
title: "Creating Elasticsearch Transport Action"
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
date: 2016-08-01 17:33:29 +0200
lastmod: 2016-08-01 17:33:29 +0200
# featuredImage: assets/images/covers/new/logstash.png
draft: false
aliases:
  - /blog/2016/08/01/creating-elasticsearch-transport-action/
---

**NOTE:** This article is now outdated. Please read [Creating Elasticsearch Transport Action (Updated for GA)]({{< ref "2016-10-20-creating-elasticsearch-transport-action-updated-for-ga" >}}) instead!

This blog post is part of a series which will teach you:

* [How to write a plugin for elasticsearch 5.0 using Maven]({{< ref "2016-07-27-creating-a-plugin-for-elasticsearch-5-dot-0-using-maven" >}}).
* [How to add a new REST endpoint plugin to elasticsearch 5.0]({{< ref "2016-07-30-adding-a-new-rest-endpoint-to-elasticsearch" >}}).
* How to use Transport Action classes  (what you are reading now).
* How I wrote the `ingest-bano` plugin which will be hopefully released soonish. In this plugin, new REST endpoints have been added.

In [the previous article]({{< ref "2016-07-30-adding-a-new-rest-endpoint-to-elasticsearch" >}}), we discovered how to add a REST plugin.
It was a simple implementation as in `RestHelloAction` class we wrote something like:

```java
public void handleRequest(RestRequest request, RestChannel channel, NodeClient client) throws Exception {
    RestToXContentListener<ToXContent> listener = new RestToXContentListener<>(channel);
    String name = request.param("name");
    listener.onResponse(new Message(name));
}
```

But actually, you will probably like to execute some actions against a Node, call some internal services...
So the implementation we wrote needs to be modified a bit.

<!-- more -->

## Concepts

Before going further, we need to understand some of the concepts and roles behind some classes:

* `Action`: defines an action against a Node. It has a unique name and methods which provides a `RequestBuilder` object and a `Response` object
* `ActionRequest`: represents the request which must be executed (parameters basically). It should be serializable as its execution could potentially be executed on another node in the cluster (depends on your implementation). Imagine you have a Client Node which proxies the execution to the actual cluster. The REST layer will build a Request which will be sent to the cluster.
* `ActionRequestBuilder`: manages all the asynchronous aspects (Future, Listeners...)
* `ActionResponse`: the object which is sent back to the REST Layer. It also needs to be serializable.
* `TransportAction`: where the execution is actually launched.

So basically, the REST layer gets a REST requests, transforms it in an `ActionRequest` which is forwarded to a `TransportAction` where the implementation logic is executed (or called). Then an `ActionResponse` object is created and sent back to the REST layer.
The REST layer serialize it as JSON and gives back the response as JSON to the user.

## Action Request

We have a parameter coming from the REST layer which is either a String or a JSON content.
[See the previous article]({{< ref "2016-07-30-adding-a-new-rest-endpoint-to-elasticsearch" >}}) if needed.

Let's create a `HelloRequest` class:

```java
public class HelloRequest extends ActionRequest<HelloRequest> {
    private String name;

    public void setName(String name) {
        this.name = name;
    }

    public void setRestContent(BytesReference restContent) {
        // Let's try to find the name from the body
        Map<String, Object> map = XContentHelper.convertToMap(restContent, false).v2();
        if (map.containsKey("name")) {
            name = (String) map.get("name");
        }
    }

    public String getName() {
        return name;
    }

    @Override
    public ActionRequestValidationException validate() {
        return null;
    }
}
```

`validate()` method is called to validate a request before it's sent to a Node.
You could imagine here having mandatory fields or parameters for example and fail the request
if not provided. For example (we won't implement that in our example):

```java
@Override
public ActionRequestValidationException validate() {
    ActionRequestValidationException validationException = null;
    if (name == null) {
        validationException = new ActionRequestValidationException();
        validationException.addValidationError("You must provide a name");
        return validationException;
    }
    return null;
}
```

As we want to ActionRequest being serializable, let's implement the serialization layer:

```java
@Override
public void readFrom(StreamInput in) throws IOException {
    super.readFrom(in);
    name = in.readOptionalString();
}

@Override
public void writeTo(StreamOutput out) throws IOException {
    super.writeTo(out);
    out.writeOptionalString(name);
}
```

## Action Response

So we have the request. Let's build the response and create a `HelloResponse`:

```java
public class HelloResponse extends ActionResponse {

    private String message;

    public HelloResponse() {
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public String getMessage() {
        return message;
    }

    @Override
    public void readFrom(StreamInput in) throws IOException {
        super.readFrom(in);
        message = in.readOptionalString();
    }

    @Override
    public void writeTo(StreamOutput out) throws IOException {
        super.writeTo(out);
        out.writeOptionalString(message);
    }
}
```

This class will hold our response message. It can be serializable between nodes
because we implemented again `readFrom(StreamInput)` and `writeTo(StreamOutput)` methods.

But that's not enough to serialize it as a JSON response. To do that, we need to implement
`ToXContent` interface and add `toXContent(XContentBuilder, Params)` method:

```java
public class HelloResponse extends ActionResponse implements ToXContent {
    // ...

    @Override
    public XContentBuilder toXContent(XContentBuilder builder, Params params) throws IOException {
        return builder.field("message", message);
    }
}
```

## Action Request Builder

We have to extend `ActionRequestBuilder` class. Let's do it and create `HelloRequestBuilder` class:

```java
public class HelloRequestBuilder extends ActionRequestBuilder<HelloRequest, HelloResponse, HelloRequestBuilder> {

    public HelloRequestBuilder(ElasticsearchClient client, Action<HelloRequest, HelloResponse, HelloRequestBuilder> action) {
        super(client, action, new HelloRequest());
    }

}
```

This looks quite easy... You have to know that a lot of magic is happening here behind the scene.
We will see what it brings in tests.

## Action

We have everything now to define our `Action` class. We create a `HelloAction`

```java
public class HelloAction extends Action<HelloRequest, HelloResponse, HelloRequestBuilder> {

    public static final HelloAction INSTANCE = new HelloAction();
    public static final String NAME = "cluster:admin/hello";

    private HelloAction() {
        super(NAME);
    }

    @Override
    public HelloResponse newResponse() {
        return new HelloResponse();
    }

    @Override
    public HelloRequestBuilder newRequestBuilder(ElasticsearchClient elasticsearchClient) {
        return new HelloRequestBuilder(elasticsearchClient, INSTANCE);
    }
}
```

The `NAME` is a unique identifier. It helps a node to know which TransportAction class should be executed.
Also, this name is used in the context of [X-Pack Security](https://www.elastic.co/guide/en/x-pack/current/xpack-security.html) to filter what users can and can not do.

## Transport Action

This is where the actual execution really happens. Let's create here a `TransportHelloAction` class.
It extends `HandledTransportAction` so our new action will be automatically registered in the `TransportService`.

```java
public class TransportHelloAction extends HandledTransportAction<HelloRequest, HelloResponse> {

    @Inject
    public TransportHelloAction(Settings settings, ThreadPool threadPool, ActionFilters actionFilters,
                                IndexNameExpressionResolver resolver, TransportService transportService) {
        super(settings, HelloAction.NAME, threadPool, transportService, actionFilters, resolver, HelloRequest::new);
    }

    @Override
    protected void doExecute(HelloRequest request, ActionListener<HelloResponse> listener) {
        // Implement here
    }
}
```

When the action `cluster:admin/hello` is called, `doExecute()` will be called.
So you can implement the logic there. Or you can also delegate it to a service.

For example, if you want to run something against the search service, you just have
to inject the `SearchService` class in the constructor, define a field which points to it
and then call the search service in `doExecute`. You can call more than one service here if you wish.

But here for our example, we will still keep it simple:

```java
@Override
protected void doExecute(HelloRequest request, ActionListener<HelloResponse> listener) {
    try {
        String name = request.getName();
        if (name == null) {
            name = "World";
        }
        HelloResponse response = new HelloResponse();
        response.setMessage("Hello " + name + "!");
        listener.onResponse(response);
    } catch (Exception e) {
        listener.onFailure(e);
    }
}
```

As you can see (even if it does not make sense here), you can also call the `onFailure()` method
if you want to send an error to the caller.

## Modify the REST layer

In [the previous article]({{< ref "2016-07-30-adding-a-new-rest-endpoint-to-elasticsearch" >}}), we wrote
all the logic in our `RestHelloAction` class and `Message` inner class:

```java
@Override
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

Let's replace all that now with:

```java
@Override
public void handleRequest(RestRequest restRequest, RestChannel channel, NodeClient client) throws Exception {
    HelloRequest request = new HelloRequest();

    String name = restRequest.param("name");
    if (name != null) {
        request.setName(name);
    } else if (restRequest.hasContent()){
        request.setRestContent(restRequest.content());
    }

    client.execute(HelloAction.INSTANCE, request, new RestToXContentListener<>(channel));
}
```

Basically, we create a `HelloRequest` object and just execute it on the cluster.
Easy, right?

## Register the action

Last but not least, we need to tell the plugin about this new action.
In `IngestBanoPlugin`, we add this method:

```java
@Override
public List<ActionHandler<? extends ActionRequest<?>, ? extends ActionResponse>> getActions() {
    return Collections.singletonList(new ActionHandler<>(HelloAction.INSTANCE, TransportHelloAction.class));
}
```

We are basically associating here our `HelloAction` with its `TransportHelloAction` class.

## Add transport layer tests

Our REST tests are still working but now we execute our logic within a Node instead of on the REST layer.
But we can test if the transport layer is actually working as expected.

To achieve this goal we can add a new JUnit Test which extends `ESIntegTestCase`:

```java
@ESIntegTestCase.ClusterScope(transportClientRatio = 0.9)
public class TransportHelloTest extends ESIntegTestCase {
    @Override
    protected Collection<Class<? extends Plugin>> nodePlugins() {
        return Collections.singletonList(IngestBanoPlugin.class);
    }

    @Override
    protected Collection<Class<? extends Plugin>> transportClientPlugins() {
        return Collections.singletonList(IngestBanoPlugin.class);
    }
}
```

In this class, we set that we want to have 90% of the time a TransportClient.
Rest of the time, we will have a NodeClient.
We also define plugins that we need to load in every node and in the Transport Client as well.

Then we can add our first test:

```java
public void testHelloWithFuture() throws ExecutionException, InterruptedException {
    HelloRequest request = new HelloRequest();
    request.setName("David");
    ActionFuture<HelloResponse> future = client().execute(HelloAction.INSTANCE, request);

    // Do something else if you wish...

    HelloResponse response = future.get();
    assertThat(response.getMessage(), is("Hello David!"));
}
```

Even simpler:

```java
public void testHelloWithFutureInlined() throws ExecutionException, InterruptedException {
    HelloRequest request = new HelloRequest();
    request.setName("David");
    HelloResponse response = client().execute(HelloAction.INSTANCE, request).get();
    assertThat(response.getMessage(), is("Hello David!"));
}
```

We can also use a listener.

```java
public void testHelloWithListener() throws ExecutionException, InterruptedException {
    HelloRequest request = new HelloRequest();
    request.setName("David");

    final Boolean[] success = {false};

    client().execute(HelloAction.INSTANCE, request, new ActionListener<HelloResponse>() {
        @Override
        public void onResponse(HelloResponse helloResponse) {
            assertThat(helloResponse.getMessage(), is("Hello David!"));
            success[0] = true;
        }

        @Override
        public void onFailure(Exception e) {
            fail("We got an error: " + e.getMessage());
        }
    });

    awaitBusy(() -> success[0]);
}
```

## What about our Bano REST action?

We can do the same thing for the `RestBanoAction` class.
Remember [it was]({{< ref "2016-07-30-adding-a-new-rest-endpoint-to-elasticsearch" >}}):

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

Let's replace all that with:

```java
@Override
public void handleRequest(RestRequest restRequest, RestChannel channel, NodeClient client) throws Exception {
    BanoRequest request = new BanoRequest();

    String dept = restRequest.param("dept");
    if (dept != null) {
        request.setDept(dept);
    }

    client.execute(BanoAction.INSTANCE, request, new RestToXContentListener<>(channel));
}
```

A `BanoRequest` basically just contains a `dept` field.
A `BanoResponse` is providing a list in a very similar way as the previous `Indices` inner class we wrote.
In `IngestBanoPlugin`, we just have to register the new action with:

```java
@Override
public List<ActionHandler<? extends ActionRequest<?>, ? extends ActionResponse>> getActions() {
    return Arrays.asList(
            new ActionHandler<>(HelloAction.INSTANCE, TransportHelloAction.class),
            new ActionHandler<>(BanoAction.INSTANCE, TransportBanoAction.class));
}
```

The TransportBanoAction is:

```java
public class TransportBanoAction extends HandledTransportAction<BanoRequest, BanoResponse> {

    private final ClusterService clusterService;

    @Inject
    public TransportBanoAction(Settings settings, ThreadPool threadPool, ActionFilters actionFilters,
                               IndexNameExpressionResolver resolver, TransportService transportService,
                               ClusterService clusterService) {
        super(settings, BanoAction.NAME, threadPool, transportService, actionFilters, resolver, BanoRequest::new);
        this.clusterService = clusterService;
    }

    @Override
    protected void doExecute(BanoRequest request, ActionListener<BanoResponse> listener) {
        String indices = ".bano-";

        if (request.getDept() != null) {
            indices += request.getDept();
        } else {
            indices += "*";
        }

        BanoResponse response = new BanoResponse();

        try {
            GetIndexRequest indexRequest = new GetIndexRequest().indices(indices);
            String[] concreteIndices = indexNameExpressionResolver.concreteIndexNames(clusterService.state(), indexRequest);

            for (String index : concreteIndices) {
                response.addIndex(index);
            }

            listener.onResponse(response);
        } catch (IndexNotFoundException e) {
            listener.onResponse(response);
        } catch (Exception e) {
            listener.onFailure(e);
        }
    }
}
```

Note that we injected here the `ClusterService` as we need it to retrieve the indices.

Cherry on the cake, we can test that with JUnit as we have seen before:

```java
@ESIntegTestCase.ClusterScope(transportClientRatio = 0.9)
public class TransportBanoTest extends ESIntegTestCase {

    @Override
    protected Collection<Class<? extends Plugin>> nodePlugins() {
        return Collections.singletonList(IngestBanoPlugin.class);
    }

    @Override
    protected Collection<Class<? extends Plugin>> transportClientPlugins() {
        return Collections.singletonList(IngestBanoPlugin.class);
    }

    private int numIndices;

    @Before
    public void createIndices() {
        // We first create some indices
        numIndices = randomIntBetween(1, 10);
        for (int i = 0; i < numIndices; i++) {
            createIndex(".bano-" + i);
        }

        // We create some manual indices
        createIndex(".bano-17", ".bano-29", ".bano-95");

        // We create some other indices
        int numOtherIndices = randomIntBetween(1, 10);
        for (int i = 0; i < numOtherIndices; i++) {
            createIndex(randomAsciiOfLengthBetween(6, 10).toLowerCase(Locale.getDefault()));
        }

        ensureYellow();
    }

    public void testBanoNoDept() throws ExecutionException, InterruptedException {
        BanoRequest request = new BanoRequest();
        BanoResponse response = client().execute(BanoAction.INSTANCE, request).get();
        for (int i = 0; i < numIndices; i++) {
            assertThat(response.getIndices(), hasItem(".bano-" + i));
        }
        assertThat(response.getIndices(), hasItem(".bano-17"));
        assertThat(response.getIndices(), hasItem(".bano-29"));
        assertThat(response.getIndices(), hasItem(".bano-95"));
    }

    public void testBanoOneDept() throws ExecutionException, InterruptedException {
        BanoRequest request = new BanoRequest();
        request.setDept("17");
        BanoResponse response = client().execute(BanoAction.INSTANCE, request).get();
        assertThat(response.getIndices(), iterableWithSize(1));
        assertThat(response.getIndices(), hasItem(".bano-17"));
    }

    public void testBanoNonExistingDept() throws ExecutionException, InterruptedException {
        BanoRequest request = new BanoRequest();
        request.setDept("idontbelieverandomizedtestingwillgeneratethat");
        BanoResponse response = client().execute(BanoAction.INSTANCE, request).get();
        assertThat(response.getIndices(), iterableWithSize(0));
    }
}
```

## What's next?

Et voilà!

In a next post, we will discover how we can use the Task Management API to execute long running tasks
which can be run on a cluster, can be monitored and stopped if needed.

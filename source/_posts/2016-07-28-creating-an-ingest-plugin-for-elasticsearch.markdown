---
layout: post
title: "Creating an Ingest plugin for elasticsearch"
date: 2016-07-28 10:55:29 +0200
comments: true
image: /images/covers/new/elasticsearch.png
categories: 
- elasticsearch
---

This blog post is part of a series which will teach you:

* [How to write a plugin for elasticsearch 5.0 using Maven]({% post_url 2016-07-27-creating-a-plugin-for-elasticsearch-5-dot-0-using-maven %}).
* How to write an ingest plugin for elasticsearch 5.0 (what you are reading now).
* How I wrote the `ingest-bano` plugin which will be hopefully released soonish.

Today, we will focus on writing an Ingest plugin for elasticsearch.

> Hey! Wait! You wrote `Ingest`? What is that?

Ingest is a new feature coming in elasticsearch 5.0. It helps you to transform your data on the fly
while injecting it into elasticsearch. Read more in [elastic blog post](https://www.elastic.co/blog/ingest-node-a-clients-perspective).

If you know me and my work before I joined elastic, I have always been in love with data crawling and transformation as
I wrote myself some plugins called [rivers](https://www.elastic.co/blog/deprecating-rivers).

<!-- more -->

With what we saw [in the previous article]({% post_url 2016-07-27-creating-a-plugin-for-elasticsearch-5-dot-0-using-maven %}), we now have a Plugin skeleton ready to host our Ingest code.

But first, let's describe a bit more what `Ingest` actually is.

## Ingest

> If you already know Ingest feature, you can skip this section.

With Ingest, you can:

* define a pipeline
* simulate a pipeline
* use a pipeline at index time to transform data on the fly

The pipeline is used to define all the actions you can perform on a source document.
Each action is performed by a processor. A processor basically takes a document as input, transform it then outputs a new version of the document.

A lot of core processors [already exists in elasticsearch 5.0](https://www.elastic.co/guide/en/elasticsearch/reference/master/ingest-processors.html)
and I can imagine that as this feature will be more and more popular, new processor will be added by the community, either in core or as plugins.

### Define a pipeline

Let's look at one of them: the [Lowercase processor](https://www.elastic.co/guide/en/elasticsearch/reference/master/lowercase-processor.html).

As you can imagine, the goal is to simply provide a lowercase version of a given field.

Let say that you define an ingest pipeline `lowercase-example` like this:

```sh
curl -XPUT localhost:9200/_ingest/pipeline/lowercase-example -d '{
  "processors" : [
    {
      "lowercase" : {
        "field": "message"
      }
    }
  ]
}'
```

### Simulate a pipeline

You can use the `_simulate` endpoint to simulate a pipeline without the need of
actually creating a pipeline and indexing a document.

```sh
curl -XGET "localhost:9200/_ingest/pipeline/_simulate?pretty" -d '{
  "pipeline" : {
    "processors" : [
	    {
	      "lowercase" : {
	        "field": "foo"
	      }
	    }
    ]
  },
  "docs" : [
    {
      "_source" : {
        "foo" : "This test CONTAINS also UPPER-CASE chars"
      }
    }
  ]
}'
```

This gives:

```json
{
  "_index" : "test",
  "_type" : "doc",
  "_id" : "1",
  "_version" : 1,
  "found" : true,
  "_source" : {
    "foo" : "this test contains also upper-case chars"
  }
}
```

### Transform a document on the fly

Well. That's easy. Just add the `pipeline` URL parameter to your index operation.

```sh
curl -XPUT "localhost:9200/test/doc/1?pipeline=lowercase-example&pretty" -d '{
  "foo" : "This test CONTAINS also UPPER-CASE chars"
}'
``` 

If you look at what has been really sent to elasticsearch as `_source` field:

```sh
curl -XGET "localhost:9200/test/doc/1?pretty"
```

You will see that the document has been transformed:

```json
{
  "_index" : "test",
  "_type" : "doc",
  "_id" : "1",
  "_version" : 1,
  "found" : true,
  "_source" : {
    "foo" : "this test contains also upper-case chars"
  }
}
```

## Coding our own processor

Well. This is why you are reading this article, right? Time to do it!

### Processor skeleton

So you have basically to write a class which extends `AbstractProcessor`.
Here we add a `BanoProcessor` in `src/main/java/org/elasticsearch/ingest/bano/`

```java
package org.elasticsearch.ingest.bano;

import org.elasticsearch.ingest.AbstractProcessor;
import org.elasticsearch.ingest.IngestDocument;

public final class BanoProcessor extends AbstractProcessor {

    public final static String NAME = "bano";

    protected BanoProcessor(String tag) {
        super(tag);
    }

    @Override
    public String getType() {
        return NAME;
    }

    @Override
    public void execute(IngestDocument ingestDocument) throws Exception {
        // Implement your logic code here
    }
}
```

`getType()` gives the processor name. So you will be able to write a pipeline like:

```sh
curl -XPUT localhost:9200/_ingest/pipeline/bano-example -d '{
  "processors" : [
    {
      "bano" : { }
    }
  ]
}'
```

`execute(IngestDocument)` is where you will implement all the logic. Transformation of data that is.

For now, the processor we just defined won't do anything. It will leave the source document as is.

### Register the processor

We need to tell elasticsearch that this processor exists.
To do that we need to provide a factory which implements `Processor.Factory`:

```java
public static final class BanoFactory implements Processor.Factory {
    @Override
    public Processor create(Map<String, Processor.Factory> processorFactories, String tag, Map<String, Object> config) 
    				throws Exception {
        return new BanoProcessor(tag);
    }
}
```

* `processorFactories` gives you access to other processors which may be created inside this processor
* `tag` is the [tag for the processor](https://www.elastic.co/guide/en/elasticsearch/reference/master/ingest-processors.html). 
It can be used when you define a processor in a pipeline.
* `config` gives you access to the configuration for the pipeline. We will cover that in a next section.

Note that you can create this class as an inner class of the BanoProcessor class itself.

We now need to tell the plugin that it will provide Ingest plugin features by implementing `IngestPlugin` interface and
overriding the `getProcessors` method:

```java
public class IngestBanoPlugin extends Plugin implements IngestPlugin {
    @Override
    public Map<String, Processor.Factory> getProcessors(Processor.Parameters parameters) {
        return Collections.singletonMap("bano", new BanoProcessor.BanoFactory());
    }
}
```

### Test the processor

We can now add more tests to check that our processor can be used in a pipeline.

We can create a new integration test class `BanoProcessorIntegrationTest` in `src/test/java/org/elasticsearch/ingest/bano/`:

```java
package org.elasticsearch.ingest.bano;

import org.elasticsearch.action.ingest.SimulateDocumentBaseResult;
import org.elasticsearch.action.ingest.SimulatePipelineResponse;
import org.elasticsearch.common.bytes.BytesReference;
import org.elasticsearch.ingest.IngestDocument;
import org.elasticsearch.plugins.Plugin;
import org.elasticsearch.test.ESIntegTestCase;

import java.util.Collection;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;

import static org.elasticsearch.common.xcontent.XContentFactory.jsonBuilder;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.instanceOf;
import static org.hamcrest.Matchers.nullValue;

public class BanoProcessorIntegrationTest extends ESIntegTestCase {

    @Override
    protected Collection<Class<? extends Plugin>> nodePlugins() {
        return Collections.singleton(IngestBanoPlugin.class);
    }

    public void testSimulateProcessor() throws Exception {
        BytesReference bytes = jsonBuilder().startObject()
                .startObject("pipeline")
                    .startArray("processors")
                        .startObject()
                            .startObject("bano")
                            .endObject()
                        .endObject()
                    .endArray()
                .endObject()
                .startArray("docs")
                    .startObject()
                        .field("_index", "index")
                        .field("_type", "type")
                        .field("_id", "id")
                        .startObject("_source")
                            .field("foo", "bar")
                        .endObject()
                    .endObject()
                .endArray()
                .endObject().bytes();

        SimulatePipelineResponse response = client().admin().cluster().prepareSimulatePipeline(bytes).get();
        assertThat(response.getResults().size(), equalTo(1));
        assertThat(response.getResults().get(0), instanceOf(SimulateDocumentBaseResult.class));
        SimulateDocumentBaseResult simulateDocumentBaseResult = (SimulateDocumentBaseResult) response.getResults().get(0);
        Map<String, Object> source = new HashMap<>();
        source.put("foo", "bar");
        IngestDocument ingestDocument = new IngestDocument("index", "type", "id", null, null, null, null, source);
        assertThat(simulateDocumentBaseResult.getIngestDocument().getSourceAndMetadata(), equalTo(ingestDocument.getSourceAndMetadata()));
        assertThat(simulateDocumentBaseResult.getFailure(), nullValue());
    }
}
```

This test basically sends a JSON document `{"foo":"bar"}` to the simulate pipeline method and check that we get back the same
content as we did not transform yet anything.

Note that this test might fail with elasticsearch 5.0.0-alpha5 because of [this bug](https://github.com/elastic/elasticsearch/pull/19650).
This is by the way why I love the Randomized Testing framework! :)

## Implement the logic

Now that we are all set, we can enrich our documents in `BanoProcessor#execute(IngestDocument)` method.
As an example, we are going to copy the value existing in field `foo` to a new field named `new_foo`.

So if we have a document like:

```json
{
	"foo": "bar"
}
```

It should become:

```json
{
	"foo": "bar",
	"new_foo": "bar"
}
```

Implementation will be:

```java
@Override
public void execute(IngestDocument ingestDocument) throws Exception {
    if (ingestDocument.hasField("foo")) {
        ingestDocument.setFieldValue("new_foo", ingestDocument.getFieldValue("foo", String.class));
    }
}
```

Of course, we need to modify our test now as we expect a new field in our document:

```java
Map<String, Object> source = new HashMap<>();
source.put("foo", "bar");
source.put("new_foo", "bar");
IngestDocument ingestDocument = new IngestDocument("index", "type", "id", null, null, null, null, source);
assertThat(simulateDocumentBaseResult.getIngestDocument().getSourceAndMetadata(), equalTo(ingestDocument.getSourceAndMetadata()));
```

## Make it more flexible

Well, we are reading the original value from `foo` which is hardcoded here.
And we are writing to `new_foo` which is also hardcoded.

Let's fix that by adding 2 optional settings for our processor:

* `source`: source field, defaults to `"foo"`
* `target`: target field, defaults to `"new_" + source`

Let's change our constructor for BanoProcessor and add 2 private fields:

```java
private final String sourceField;
private final String targetField;

protected BanoProcessor(String tag, String sourceField, String targetField) {
    super(tag);
    this.sourceField = sourceField;
    this.targetField = targetField;
}
```

Use them in `execute(IngestDocument)` method:

```java
@Override
public void execute(IngestDocument ingestDocument) throws Exception {
    if (ingestDocument.hasField(sourceField)) {
        ingestDocument.setFieldValue(targetField, ingestDocument.getFieldValue(sourceField, String.class));
    }
}
```

Change now the `BanoFactory` class:

```java
@Override
public Processor create(Map<String, Processor.Factory> processorFactories, String tag, Map<String, Object> config) throws
        Exception {
    String source = readStringProperty(NAME, tag, config, "source", "foo");
    String target = readStringProperty(NAME, tag, config, "target", "new_" + source);

    return new BanoProcessor(tag, source, target);
}
```

Note that `readStringProperty` method comes from `org.elasticsearch.ingest.ConfigurationUtils` class.

If you run the existing test, it should pass as we are using all default values.
We can add a new test which checks that we can read from another field than `foo`, here `anotherfoo`:

```java
public void testSimulateProcessorConfigSource() throws Exception {
	BytesReference bytes = jsonBuilder().startObject()
	        .startObject("pipeline")
	            .startArray("processors")
	                .startObject()
	                    .startObject("bano")
	                        .field("source", "anotherfoo")
	                    .endObject()
	                .endObject()
	            .endArray()
	        .endObject()
	        .startArray("docs")
	            .startObject()
	                .field("_index", "index")
	                .field("_type", "type")
	                .field("_id", "id")
	                .startObject("_source")
	                    .field("anotherfoo", "bar")
	                .endObject()
	            .endObject()
	        .endArray()
	        .endObject().bytes();

	SimulatePipelineResponse response = client().admin().cluster().prepareSimulatePipeline(bytes).get();
	assertThat(response.getResults().size(), equalTo(1));
	assertThat(response.getResults().get(0), instanceOf(SimulateDocumentBaseResult.class));
	SimulateDocumentBaseResult simulateDocumentBaseResult = (SimulateDocumentBaseResult) response.getResults().get(0);
	Map<String, Object> source = new HashMap<>();
	source.put("anotherfoo", "bar");
	source.put("new_anotherfoo", "bar");
	IngestDocument ingestDocument = new IngestDocument("index", "type", "id", null, null, null, null, source);
	assertThat(simulateDocumentBaseResult.getIngestDocument().getSourceAndMetadata(), equalTo(ingestDocument.getSourceAndMetadata()));
	assertThat(simulateDocumentBaseResult.getFailure(), nullValue());
}
```

Also test that you can write to another target field:

```java
public void testSimulateProcessorConfigTarget() throws Exception {
    BytesReference bytes = jsonBuilder().startObject()
            .startObject("pipeline")
                .startArray("processors")
                    .startObject()
                        .startObject("bano")
                            .field("source", "anotherfoo")
                            .field("target", "another_new_foo")
                        .endObject()
                    .endObject()
                .endArray()
            .endObject()
            .startArray("docs")
                .startObject()
                    .field("_index", "index")
                    .field("_type", "type")
                    .field("_id", "id")
                    .startObject("_source")
                        .field("anotherfoo", "bar")
                    .endObject()
                .endObject()
            .endArray()
            .endObject().bytes();

    SimulatePipelineResponse response = client().admin().cluster().prepareSimulatePipeline(bytes).get();
    assertThat(response.getResults().size(), equalTo(1));
    assertThat(response.getResults().get(0), instanceOf(SimulateDocumentBaseResult.class));
    SimulateDocumentBaseResult simulateDocumentBaseResult = (SimulateDocumentBaseResult) response.getResults().get(0);
    Map<String, Object> source = new HashMap<>();
    source.put("anotherfoo", "bar");
    source.put("another_new_foo", "bar");
    IngestDocument ingestDocument = new IngestDocument("index", "type", "id", null, null, null, null, source);
    assertThat(simulateDocumentBaseResult.getIngestDocument().getSourceAndMetadata(), equalTo(ingestDocument.getSourceAndMetadata()));
    assertThat(simulateDocumentBaseResult.getFailure(), nullValue());
}
```

## Remove the source field

We can also add another option to remove the source field as we copied the content we want to the target field.
Let's add a new `remove` boolean option:

```java
// ...
private final Boolean removeOption;

protected BanoProcessor(String tag, String sourceField, String targetField, Boolean removeOption) {
		// ...
    this.removeOption = removeOption;
}

@Override
public void execute(IngestDocument ingestDocument) throws Exception {
    if (ingestDocument.hasField(sourceField)) {
        ingestDocument.setFieldValue(targetField, ingestDocument.getFieldValue(sourceField, String.class));
        if (removeOption) {
            ingestDocument.removeField(sourceField);
        }
    }
}

public static final class BanoFactory implements Processor.Factory {
    @Override
    public Processor create(Map<String, Processor.Factory> processorFactories, String tag, Map<String, Object> config) throws
            Exception {
				// ...
        Boolean remove = readBooleanProperty(NAME, tag, config, "remove", false);

        return new BanoProcessor(tag, source, target, remove);
    }
}
```

Existing tests should still work.
Let's add another test:

```java
public void testSimulateProcessorConfigRemove() throws Exception {
    BytesReference bytes = jsonBuilder().startObject()
            .startObject("pipeline")
                .startArray("processors")
                    .startObject()
                        .startObject("bano")
                            .field("remove", true)
                        .endObject()
                    .endObject()
                .endArray()
            .endObject()
            .startArray("docs")
                .startObject()
                    .field("_index", "index")
                    .field("_type", "type")
                    .field("_id", "id")
                    .startObject("_source")
                        .field("foo", "bar")
                    .endObject()
                .endObject()
            .endArray()
            .endObject().bytes();

    SimulatePipelineResponse response = client().admin().cluster().prepareSimulatePipeline(bytes).get();
    assertThat(response.getResults().size(), equalTo(1));
    assertThat(response.getResults().get(0), instanceOf(SimulateDocumentBaseResult.class));
    SimulateDocumentBaseResult simulateDocumentBaseResult = (SimulateDocumentBaseResult) response.getResults().get(0);
    Map<String, Object> source = new HashMap<>();
    source.put("new_foo", "bar");
    IngestDocument ingestDocument = new IngestDocument("index", "type", "id", null, null, null, null, source);
    assertThat(simulateDocumentBaseResult.getIngestDocument().getSourceAndMetadata(), equalTo(ingestDocument.getSourceAndMetadata()));
    assertThat(simulateDocumentBaseResult.getFailure(), nullValue());
}
```

## What's next?

In a coming blog post, I'll explain how to create an ingest plugin which will helps you to transform a french postal address to geo coordinates or the other way around.

Stay tuned!

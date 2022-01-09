---
title: "Creating a plugin for elasticsearch 5.0 using Maven"
#description: 
toc: true
authors:
  - David Pilato
tags:
  - java
  - maven
  - elasticsearch
  - plugin
categories:
  - tutorial
series:
  - plugin for elasticsearch v5
date: 2016-07-27 16:00:27 +0200
lastmod: 2016-07-27 16:00:27 +0200
# featuredImage: assets/images/covers/new/logstash.png
draft: false
aliases:
  - /blog/2016/07/27/creating-a-plugin-for-elasticsearch-5-dot-0-using-maven/
---

**NOTE:** This article is now outdated. Please read [Creating a plugin for elasticsearch 5.0 using Maven (Updated for GA)]({{< ref "2016-10-16-creating-a-plugin-for-elasticsearch-5-dot-0-using-maven-updated-for-ga" >}}) instead!

Elasticsearch 5.0 [switched to Gradle in October 2015](https://github.com/elastic/elasticsearch/issues/13930).

You can obviously write a plugin using Gradle if you wish and you could benefit from all the goodies elasticsearch team wrote
when it comes to integration tests and so on.

My colleague, Alexander Reelsen aka [Spinscale on Twitter](http://twitter.com/spinscale), wrote
[a super nice template](https://github.com/spinscale/cookiecutter-elasticsearch-ingest-processor) if
you wish to create an Ingest plugin for 5.0.

> Hey! Wait! You wrote `Ingest`? What is that?

Ingest is a new feature coming in elasticsearch 5.0. It helps you to transform your data on the fly
while injecting it into elasticsearch. Read more in [elastic blog post](https://www.elastic.co/blog/ingest-node-a-clients-perspective).

If you know me and my work before I joined elastic, I have always been in love with data crawling and transformation as
I wrote myself some plugins called [rivers](https://www.elastic.co/blog/deprecating-rivers).

This blog post is part of a series which will teach you:

* How to write a plugin for elasticsearch 5.0 using Maven (what you are reading now).
* [How to write an ingest plugin for elasticsearch 5.0]({{< ref "2016-07-28-creating-an-ingest-plugin-for-elasticsearch" >}}).
* How I wrote the `ingest-bano` plugin which will be hopefully released soonish.

<!-- more -->

Let's get started!

**Note**: this article applies to elasticsearch 5.0.0 alpha 5. It might
be not applicable for newer versions as APIs could change.

## Create a skeleton

### Create Maven skeleton

Create in your new project directory, let say `ingest-bano`, a `pom.xml` file:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>fr.pilato.elasticsearch.ingest</groupId>
    <artifactId>ingest-bano</artifactId>
    <version>5.0.0-alpha5-SNAPSHOT</version>
    <name>Plugin: Ingest: BANO</name>
    <description>BANO Ingest Plugin for elasticsearch</description>

</project>
```

## Add elasticsearch core dependency

Just add `org.elasticsearch:elasticsearch:5.0.0-alpha5` as a `provided` dependency:

```xml
<properties>
    <elasticsearch.version>5.0.0-alpha5</elasticsearch.version>
</properties>

<dependencies>
    <dependency>
        <groupId>org.elasticsearch</groupId>
        <artifactId>elasticsearch</artifactId>
        <version>${elasticsearch.version}</version>
        <scope>provided</scope>
    </dependency>
</dependencies>
```

Why `provided`? Actually our plugin will run **in** elasticsearch. So elasticsearch
is already provided here.

### Add plugin descriptor file

As explained in [Plugin developer reference](https://www.elastic.co/guide/en/elasticsearch/plugins/master/plugin-authors.html#_plugin_descriptor_file),
you need to provide a `plugin-descriptor.properties` which must be assembled with your plugin artifact in the `elasticsearch` dir.

Create this file in `src/main/resources`:

```properties
description=${project.description}.
version=${project.version}
name=${project.artifactId}
classname=org.elasticsearch.ingest.bano.IngestBanoPlugin
java.version=1.8
elasticsearch.version=${elasticsearch.version}
```

It does not need to be added to the project classes but only packaged within the ZIP file.
Let's tell Maven to do that!

We create a file `src/main/assemblies/plugin.xml` with:

```xml
<?xml version="1.0"?>
<assembly>
    <id>plugin</id>
    <formats>
        <format>zip</format>
    </formats>
    <includeBaseDirectory>false</includeBaseDirectory>
    <files>
        <file>
            <source>${project.basedir}/src/main/resources/plugin-descriptor.properties</source>
            <outputDirectory>elasticsearch</outputDirectory>
            <filtered>true</filtered>
        </file>
    </files>
    <dependencySets>
        <dependencySet>
            <outputDirectory>elasticsearch</outputDirectory>
            <useProjectArtifact>true</useProjectArtifact>
            <useTransitiveFiltering>true</useTransitiveFiltering>
        </dependencySet>
    </dependencySets>
</assembly>
```

Note that we are filtering `plugin-descriptor.properties` file which means that at package time
all Maven placeholders will be replaced by their needed values.

We don't want to add this file in our JAR so we tell that to Maven in the `pom.xml`:

```xml
<build>
    <resources>
        <resource>
            <directory>src/main/resources</directory>
            <filtering>false</filtering>
            <excludes>
                <exclude>*.properties</exclude>
            </excludes>
        </resource>
    </resources>
</build>
```

We need to declare the maven assembly plugin now:

```xml
<build>
  <!-- ... -->
  <plugins>
      <plugin>
          <groupId>org.apache.maven.plugins</groupId>
          <artifactId>maven-assembly-plugin</artifactId>
          <version>2.6</version>
          <configuration>
              <appendAssemblyId>false</appendAssemblyId>
              <outputDirectory>${project.build.directory}/releases/</outputDirectory>
              <descriptors>
                  <descriptor>${basedir}/src/main/assemblies/plugin.xml</descriptor>
              </descriptors>
          </configuration>
          <executions>
              <execution>
                  <phase>package</phase>
                  <goals>
                      <goal>single</goal>
                  </goals>
              </execution>
          </executions>
      </plugin>
  </plugins>
</build>
```

### Configure Compiler plugin for Java 8

Because we want to use Java 8, we need to configure the compiler plugin:

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-compiler-plugin</artifactId>
    <version>3.3</version>
    <configuration>
        <source>1.8</source>
        <target>1.8</target>
    </configuration>
</plugin>
```

### Create Plugin class skeleton

Create an empty plugin class in `src/main/java/org/elasticsearch/ingest/bano/`.

```java
package org.elasticsearch.ingest.bano;

import org.elasticsearch.plugins.Plugin;

public class IngestBanoPlugin extends Plugin {

}
```

## Add test infrastructure

Elasticsearch provides a nice test framework which can be reused to run some tests.

Let's add it to our project:

```xml
<dependency>
    <groupId>org.elasticsearch.test</groupId>
    <artifactId>framework</artifactId>
    <version>${elasticsearch.version}</version>
    <scope>test</scope>
</dependency>
<dependency>
    <groupId>net.java.dev.jna</groupId>
    <artifactId>jna</artifactId>
    <version>4.1.0</version>
    <scope>test</scope>
</dependency>
<dependency>
    <groupId>log4j</groupId>
    <artifactId>log4j</artifactId>
    <version>1.2.17</version>
    <scope>test</scope>
</dependency>
```

Let's add the fantastic Randomized Testing framework:

```xml
<plugin>
    <!-- we skip surefire to work with randomized testing above -->
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-surefire-plugin</artifactId>
    <version>2.9</version>
    <configuration>
        <skipTests>true</skipTests>
    </configuration>
</plugin>
<plugin>
    <groupId>com.carrotsearch.randomizedtesting</groupId>
    <artifactId>junit4-maven-plugin</artifactId>
    <version>2.3.3</version>

    <configuration>
        <assertions enableSystemAssertions="false">
            <enable/>
        </assertions>

        <listeners>
            <report-text />
        </listeners>
    </configuration>

    <executions>
        <execution>
            <id>unit-tests</id>
            <phase>test</phase>
            <goals>
                <goal>junit4</goal>
            </goals>
        </execution>
    </executions>
</plugin>
```

Add a default `log4j.xml` in `src/test/resources`:

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE log4j:configuration SYSTEM "log4j.dtd">
<log4j:configuration>

    <appender name="console" class="org.apache.log4j.ConsoleAppender">
        <layout class="org.apache.log4j.PatternLayout">
            <param name="ConversionPattern" value="[%d{ISO8601}][%-5p][%-25c] %m%n" />
        </layout>
    </appender>

    <root>
        <level value="INFO" />
        <appender-ref ref="console" />
    </root>

</log4j:configuration>
```

We can now extend `ESIntegTestCase` class to run integration tests. You can create a `BanoPluginIntegrationTest`
class in `src/test/java/org/elasticsearch/ingest/bano/`:

```java
package org.elasticsearch.ingest.bano;

import org.elasticsearch.action.admin.cluster.node.info.NodeInfo;
import org.elasticsearch.action.admin.cluster.node.info.NodesInfoResponse;
import org.elasticsearch.plugins.Plugin;
import org.elasticsearch.plugins.PluginInfo;
import org.elasticsearch.test.ESIntegTestCase;

import java.util.Collection;
import java.util.Collections;

import static org.hamcrest.Matchers.is;

public class BanoPluginIntegrationTest extends ESIntegTestCase {

    @Override
    protected Collection<Class<? extends Plugin>> nodePlugins() {
        return Collections.singleton(IngestBanoPlugin.class);
    }

    public void testPluginIsLoaded() throws Exception {
        NodesInfoResponse response = client().admin().cluster().prepareNodesInfo().setPlugins(true).get();
        for (NodeInfo nodeInfo : response.getNodes()) {
            boolean pluginFound = false;
            for (PluginInfo pluginInfo : nodeInfo.getPlugins().getPluginInfos()) {
                if (pluginInfo.getName().equals(IngestBanoPlugin.class.getName())) {
                    pluginFound = true;
                    break;
                }
            }
            assertThat(pluginFound, is(true));
        }
    }
}
```

When you run this class, a cluster of a random number of nodes is started using random Locale settings.
The plugin we just created is added to nodes using `nodePlugins()` class.

So we just have to use the plugin as we want now. In this example, we are just testing that the plugin is
actually loaded on every node.

## Build the plugin

Just run:

```sh
mvn clean install
```

You will get in `target/releases` the distribution file.

## Install the plugin

If you have an elasticsearch 5.0.0-alpha5 version somewhere, you can install this plugin with:

```sh
bin/elasticsearch-plugin install file:///path/to/target/releases/ingest-bano-5.0.0-alpha5-SNAPSHOT.zip
```

Then you can start elasticsearch with `bin/elasticsearch`  and check in logs that the plugin is loaded.

You are now all set!

## Next?

In a coming blog post, I'll explain [how to write an Ingest plugin]({{< ref "2016-07-28-creating-an-ingest-plugin-for-elasticsearch" >}}) based on the skeleton we just built and also [how to create real integration tests]({{< ref "2016-07-29-elasticsearch-real-integration-tests" >}}).

But note that this skeleton can be used for [whatever purpose](https://www.elastic.co/guide/en/elasticsearch/plugins/master/index.html):

* [Generic Action plugins]({{< ref "2016-08-01-creating-elasticsearch-transport-action" >}})
* Analysis plugins
* Discovery plugins
* Repository plugins
* [REST plugins]({{< ref "2016-07-30-adding-a-new-rest-endpoint-to-elasticsearch" >}})
* Native Script plugins
* Security plugins
* [Ingest plugins]({{< ref "2016-07-28-creating-an-ingest-plugin-for-elasticsearch" >}})
* ...

Your imagination is now the limit! :)

Stay tuned!

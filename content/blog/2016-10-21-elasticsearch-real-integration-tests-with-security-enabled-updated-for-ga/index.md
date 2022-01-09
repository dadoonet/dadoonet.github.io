---
title: "Elasticsearch real integration tests with security enabled (Updated for GA)"
#description: 
toc: true
authors:
  - David Pilato
tags:
  - maven
  - ant
  - test
  - elasticsearch
  - plugin
categories:
  - tutorial
series:
  - plugin for elasticsearch v5 updated
date: 2016-10-21 18:24:37 +0200
lastmod: 2016-10-21 18:24:37 +0200
# featuredImage: assets/images/covers/new/logstash.png
draft: false
aliases:
  - /blog/2016/10/21/elasticsearch-real-integration-tests-with-security-enabled-updated-for-ga/
---

**NOTE:** This article is an updated version of [Elasticsearch real integration tests with security enabled]({{< ref "2016-08-03-elasticsearch-real-integration-tests-with-security-enabled" >}})

In a recent post we have seen [how to create real integration tests]({{< ref "2016-10-18-elasticsearch-real-integration-tests-updated-for-ga" >}}).
Those tests launch a real elasticsearch cluster, then run some tests you write with JUnit or your favorite test framework
then stop the cluster.

But sometimes, you may want to add existing plugins in your integration test cluster.

For example, you might want to use [X-Pack](https://www.elastic.co/downloads/x-pack) to bring fantastic features such as:

* Security
* Alerting
* Monitoring
* Graph
* Reporting

Let's see how you can do that with Maven and Ant again...

<!-- more -->

## Copy the plugins from elastic maven repository

First, let's add elastic maven repository in our `pom.xml`.

```xml
<repositories>
    <repository>
        <id>elastic-releases</id>
        <name>Elastic Maven Repository</name>
        <url>http://artifacts.elastic.co/maven/</url>
    </repository>
</repositories>
```

We can add a new `execution` to the `maven-dependency-plugin` we already defined.
The goal is to copy all plugins we need to a `target/integration-tests/plugins` directory.

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-dependency-plugin</artifactId>
    <version>2.10</version>
    <executions>
        <!-- ... -->
        <execution>
            <id>integ-setup-dependencies-plugins</id>
            <phase>pre-integration-test</phase>
            <goals>
                <goal>copy</goal>
            </goals>
            <configuration>
                <skip>${skipIntegTests}</skip>
                <artifactItems>
                    <artifactItem>
                        <groupId>org.elasticsearch.plugin</groupId>
                        <artifactId>x-pack</artifactId>
                        <version>${elasticsearch.version}</version>
                        <type>zip</type>
                    </artifactItem>
                </artifactItems>
                <useBaseVersion>true</useBaseVersion>
                <outputDirectory>${project.build.directory}/integration-tests/plugins</outputDirectory>
            </configuration>
        </execution>
    </executions>
</plugin>
```

Here we are just copying `x-pack` but you can add [as many plugins](https://www.elastic.co/guide/en/elasticsearch/plugins/master/index.html)
as you need.

## Modify ANT scripts

First we will need some additional features for ANT so we add `ant-contrib`
in `maven-antrun-plugin`:

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-antrun-plugin</artifactId>
    <version>1.8</version>
    <!-- ... -->
    <dependencies>
        <dependency>
            <groupId>ant-contrib</groupId>
            <artifactId>ant-contrib</artifactId>
            <version>1.0b3</version>
            <exclusions>
                <exclusion>
                    <groupId>ant</groupId>
                    <artifactId>ant</artifactId>
                </exclusion>
            </exclusions>
        </dependency>
    </dependencies>
</plugin>
```

In out ANT script, we add in the header:

```xml
<project name="integration-tests"
         xmlns:if="ant:if"
         xmlns:unless="ant:unless"
         xmlns:ac="antlib:net.sf.antcontrib">
```

### Install other plugins

We need first to extract the plugin name from its file name.
I used the great [regex101 online tester](https://regex101.com/) tool to find the right
regular expression and came to:

```xml
<taskdef resource="net/sf/antcontrib/antcontrib.properties" />

<macrodef name="convert-plugin-name">
    <attribute name="file"/>
    <attribute name="outputproperty"/>
    <sequential>
        <local name="file.base"/>
        <basename file="@{file}" property="file.base"/>
        <propertyregex property="@{outputproperty}" input="${file.base}" regexp="^(.*)-[0-9].*\.zip" select="\1" />
    </sequential>
</macrodef>
```

To install the plugins, we modify `start-external-cluster-with-plugin` target:

```xml
<target name="start-external-cluster-with-plugin" depends="setup-workspace">
    <install-plugin name="${project.artifactId}" file="${project.build.directory}/releases/${project.artifactId}-${project.version}.zip"/>
    <ac:for param="file">
        <path>
            <fileset dir="${project.build.directory}/integration-tests/plugins"/>
        </path>
        <sequential>
            <local name="plugin.name"/>
            <convert-plugin-name file="@{file}" outputproperty="plugin.name"/>
            <install-plugin name="${plugin.name}" file="@{file}"/>
        </sequential>
    </ac:for>

    <startup-elasticsearch/>
</target>
```

It executes the following steps:

* Install the plugin we are currently creating
* Install every single plugin which is available in `target/integration-tests/plugins`
* Launch elasticsearch

### Authentification

When you install `x-pack`, your cluster is automatically secured. Well, it can cause
some problems when you run your tests or want to check that the cluster is running.
Because you need to be authenticated.

You could potentially create with ant again a user but fortunately `x-pack` comes
with a default user `elastic` and a `changeme` password, so we just have to use that.

In our ant script, it means that we need to adapt a bit our code:

```xml
<macrodef name="waitfor-elasticsearch">
    <attribute name="port"/>
    <attribute name="timeoutproperty"/>
    <attribute name="username"/>
    <attribute name="password"/>
    <sequential>
        <echo>Waiting for elasticsearch to become available on port @{port}...</echo>
        <waitfor maxwait="30" maxwaitunit="second"
                 checkevery="500" checkeveryunit="millisecond"
                 timeoutproperty="@{timeoutproperty}">
            <socket server="127.0.0.1" port="@{port}"/>
        </waitfor>
        <echo>Elasticsearch is running on port @{port}...</echo>
        <echo>Check that we can authenticate with user @{username}/@{password}...</echo>
        <local name="temp.file"/>
        <tempfile property="temp.file" destdir="${java.io.tmpdir}" deleteonexit="false"/>
        <get src="http://127.0.0.1:@{port}/" dest="${temp.file}"
             username="@{username}" password="@{password}" verbose="true" retries="10" ignoreerrors="true"/>
        <echo>We can access http://127.0.0.1:@{port}/...</echo>
    </sequential>
</macrodef>
```

Then when we call this macro, we pass the username and password:

```xml
<local name="failed.to.start"/>
<waitfor-elasticsearch port="@{es.http.port}"
                       timeoutproperty="failed.to.start"
                       username="${integ.security.username}"
                       password="${integ.security.password}"
/>
```

Which we just have to define in our `pom.xml` as properties:

```xml
<integ.security.username>elastic</integ.security.username>
<integ.security.password>changeme</integ.security.password>
```

## Using REST authentication

In our `AbstractITCase`, we need to change how we create our REST client and provide a `CredentialsProvider`:

```java
@BeforeClass
public static void startRestClient() {
    final CredentialsProvider credentialsProvider = new BasicCredentialsProvider();
    credentialsProvider.setCredentials(AuthScope.ANY, new UsernamePasswordCredentials("elastic", "changeme"));

    client = RestClient.builder(new HttpHost("127.0.0.1", HTTP_TEST_PORT))
            .setHttpClientConfigCallback(httpClientBuilder -> httpClientBuilder.setDefaultCredentialsProvider(credentialsProvider))
            .build();

    // ...
}
```

And... We're done!

Just run:

```sh
mvn install -DskipUnitTests=true
```

And see the result.

It will create the plugin ZIP, copy elasticsearch to `target/integration-tests/binaries` and `x-pack` to `target/integration-tests/plugins`:

```txt
[INFO] --- maven-assembly-plugin:2.6:single (default) @ ingest-bano ---
[INFO] Reading assembly descriptor: /Users/dpilato/Documents/Elasticsearch/dev/blog-tests/ingest-bano/src/main/assemblies/plugin.xml
[INFO] Building zip: /Users/dpilato/Documents/Elasticsearch/dev/blog-tests/ingest-bano/target/releases/ingest-bano-5.0.0.zip
[INFO]
[INFO] --- maven-dependency-plugin:2.10:copy (integ-setup-dependencies) @ ingest-bano ---
[INFO] Configured Artifact: org.elasticsearch.distribution.zip:elasticsearch:5.0.0:zip
[INFO] org.elasticsearch.distribution.zip:elasticsearch:5.0.0:zip already exists in /Users/dpilato/Documents/Elasticsearch/dev/blog-tests/ingest-bano/target/integration-tests/binaries
[INFO]
[INFO] --- maven-dependency-plugin:2.10:copy (integ-setup-dependencies-plugins) @ ingest-bano ---
[INFO] Configured Artifact: org.elasticsearch.plugin:x-pack:5.0.0:zip
[INFO] org.elasticsearch.plugin:x-pack:5.0.0:zip already exists in /Users/dpilato/Documents/Elasticsearch/dev/blog-tests/ingest-bano/target/integration-tests/plugins
[INFO]
```

Then it will unzip elasticsearch, install `ingest-bano` and `x-pack`. Then start the cluster:

```txt
[INFO] --- maven-antrun-plugin:1.8:run (integ-setup) @ ingest-bano ---
[INFO] Executing tasks

main:

stop-external-cluster:

setup-workspace:
   [delete] Deleting directory /Users/dpilato/Documents/Elasticsearch/dev/blog-tests/ingest-bano/target/integration-tests/run
    [unzip] Expanding: /Users/dpilato/Documents/Elasticsearch/dev/blog-tests/ingest-bano/target/integration-tests/binaries/elasticsearch-5.0.0.zip into /Users/dpilato/Documents/Elasticsearch/dev/blog-tests/ingest-bano/target/integration-tests/run

start-external-cluster-with-plugin:
     [echo] Installing plugin ingest-bano...
    [mkdir] Created dir: /Users/dpilato/Documents/Elasticsearch/dev/blog-tests/ingest-bano/target/integration-tests/run/tmp/null223436133
<?xml version="1.0" encoding="UTF-8"?>
<exec script="elasticsearch-plugin">
  <arg value="install" />
  <arg value="file:/Users/dpilato/Documents/Elasticsearch/dev/blog-tests/ingest-bano/target/releases/ingest-bano-5.0.0.zip" />
</exec>
[elasticsearch-plugin] Plugins directory [/Users/dpilato/Documents/Elasticsearch/dev/blog-tests/ingest-bano/target/integration-tests/run/elasticsearch-5.0.0/plugins] does not exist. Creating...
[elasticsearch-plugin] -> Downloading file:/Users/dpilato/Documents/Elasticsearch/dev/blog-tests/ingest-bano/target/releases/ingest-bano-5.0.0.zip
[elasticsearch-plugin]
[elasticsearch-plugin] -> Installed ingest-bano
     [echo] Installing plugin x-pack...
    [mkdir] Created dir: /Users/dpilato/Documents/Elasticsearch/dev/blog-tests/ingest-bano/target/integration-tests/run/tmp/null463986480
<?xml version="1.0" encoding="UTF-8"?>
<exec script="elasticsearch-plugin">
  <arg value="install" />
  <arg value="file:/Users/dpilato/Documents/Elasticsearch/dev/blog-tests/ingest-bano/target/integration-tests/plugins/x-pack-5.0.0.zip" />
</exec>
[elasticsearch-plugin] -> Downloading file:/Users/dpilato/Documents/Elasticsearch/dev/blog-tests/ingest-bano/target/integration-tests/plugins/x-pack-5.0.0.zip
[elasticsearch-plugin]
[elasticsearch-plugin] @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
[elasticsearch-plugin] @     WARNING: plugin requires additional permissions     @
[elasticsearch-plugin] @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
[elasticsearch-plugin] * java.lang.RuntimePermission accessClassInPackage.com.sun.activation.registries
[elasticsearch-plugin] * java.lang.RuntimePermission getClassLoader
[elasticsearch-plugin] * java.lang.RuntimePermission setContextClassLoader
[elasticsearch-plugin] * java.lang.RuntimePermission setFactory
[elasticsearch-plugin] * java.security.SecurityPermission createPolicy.JavaPolicy
[elasticsearch-plugin] * java.security.SecurityPermission getPolicy
[elasticsearch-plugin] * java.security.SecurityPermission putProviderProperty.BC
[elasticsearch-plugin] * java.security.SecurityPermission setPolicy
[elasticsearch-plugin] * java.util.PropertyPermission * read,write
[elasticsearch-plugin] * java.util.PropertyPermission sun.nio.ch.bugLevel write
[elasticsearch-plugin] * javax.net.ssl.SSLPermission setHostnameVerifier
[elasticsearch-plugin] See http://docs.oracle.com/javase/8/docs/technotes/guides/security/permissions.html
[elasticsearch-plugin] for descriptions of what these permissions allow and the associated risks.
[elasticsearch-plugin] -> Installed x-pack
     [echo] Starting up external cluster...
     [echo] running Elasticsearch 5.0.0 or superior
    [mkdir] Created dir: /Users/dpilato/Documents/Elasticsearch/dev/blog-tests/ingest-bano/target/integration-tests/run/tmp/null1562972688
<?xml version="1.0" encoding="UTF-8"?>
<exec script="elasticsearch">
  <arg value="-Epidfile=/Users/dpilato/Documents/Elasticsearch/dev/blog-tests/ingest-bano/target/integration-tests/run/es.pid" />
  <arg value="-Ecluster.name=elasticsearch_integration" />
  <arg value="-Ehttp.port=9400" />
  <arg value="-Etransport.tcp.port=9500" />
  <arg value="-Enetwork.host=127.0.0.1" />
</exec>
     [echo] Waiting for elasticsearch to become available on port 9400...
     [echo] Elasticsearch is running on port 9400...
     [echo] Check that we can authenticate with user elastic/changeme...
      [get] Getting: http://127.0.0.1:9400/
      [get] To: /var/folders/r_/r14sy86n2zb91jyz1ptb5b4w0000gn/T/null600789717
.
     [echo] We can access http://127.0.0.1:9400/...
[elasticsearch] [2016-08-03 19:36:57,508][INFO ][node                     ] [] initializing ...
[elasticsearch] [2016-08-03 19:36:57,570][INFO ][env                      ] [hQWaRT2] using [1] data paths, mounts [[/ (/dev/disk1)]], net usable_space [32.5gb], net total_space [464.7gb], spins? [unknown], types [hfs]
[elasticsearch] [2016-08-03 19:36:57,570][INFO ][env                      ] [hQWaRT2] heap size [1.9gb], compressed ordinary object pointers [true]
[elasticsearch] [2016-08-03 19:36:57,571][INFO ][node                     ] [hQWaRT2] node name [hQWaRT2] derived from node ID; set [node.name] to override
[elasticsearch] [2016-08-03 19:36:57,572][INFO ][node                     ] [hQWaRT2] version[5.0.0], pid[24989], build[6b7d409/2016-07-29T07:51:41.648Z], OS[Mac OS X/10.11.6/x86_64], JVM[Oracle Corporation/Java HotSpot(TM) 64-Bit Server VM/1.8.0_60/25.60-b23]
[elasticsearch] [2016-08-03 19:36:58,569][INFO ][io.netty.util.internal.PlatformDependent] Your platform does not provide complete low-level API for accessing direct buffers reliably. Unless explicitly requested, heap buffer will always be preferred to avoid potential system unstability.
[elasticsearch] [2016-08-03 19:36:58,953][INFO ][xpack.security.crypto    ] [hQWaRT2] system key [/Users/dpilato/Documents/Elasticsearch/dev/blog-tests/ingest-bano/target/integration-tests/run/elasticsearch-5.0.0/config/x-pack/system_key] has been loaded
[elasticsearch] [2016-08-03 19:36:58,970][INFO ][plugins                  ] [hQWaRT2] loaded module [aggs-matrix-stats]
[elasticsearch] [2016-08-03 19:36:58,970][INFO ][plugins                  ] [hQWaRT2] loaded module [ingest-common]
[elasticsearch] [2016-08-03 19:36:58,970][INFO ][plugins                  ] [hQWaRT2] loaded module [lang-expression]
[elasticsearch] [2016-08-03 19:36:58,971][INFO ][plugins                  ] [hQWaRT2] loaded module [lang-groovy]
[elasticsearch] [2016-08-03 19:36:58,971][INFO ][plugins                  ] [hQWaRT2] loaded module [lang-mustache]
[elasticsearch] [2016-08-03 19:36:58,971][INFO ][plugins                  ] [hQWaRT2] loaded module [lang-painless]
[elasticsearch] [2016-08-03 19:36:58,971][INFO ][plugins                  ] [hQWaRT2] loaded module [percolator]
[elasticsearch] [2016-08-03 19:36:58,971][INFO ][plugins                  ] [hQWaRT2] loaded module [reindex]
[elasticsearch] [2016-08-03 19:36:58,971][INFO ][plugins                  ] [hQWaRT2] loaded module [transport-netty3]
[elasticsearch] [2016-08-03 19:36:58,971][INFO ][plugins                  ] [hQWaRT2] loaded module [transport-netty4]
[elasticsearch] [2016-08-03 19:36:58,971][INFO ][plugins                  ] [hQWaRT2] loaded plugin [ingest-bano]
[elasticsearch] [2016-08-03 19:36:58,971][INFO ][plugins                  ] [hQWaRT2] loaded plugin [x-pack]
[elasticsearch] [2016-08-03 19:37:02,019][INFO ][node                     ] [hQWaRT2] initialized
[elasticsearch] [2016-08-03 19:37:02,019][INFO ][node                     ] [hQWaRT2] starting ...
[elasticsearch] [2016-08-03 19:37:02,025][WARN ][xpack.security.authc.file] [hQWaRT2] no users found in users file [/Users/dpilato/Documents/Elasticsearch/dev/blog-tests/ingest-bano/target/integration-tests/run/elasticsearch-5.0.0/config/x-pack/users]. use bin/x-pack/users to add users and role mappings
[elasticsearch] [2016-08-03 19:37:02,029][WARN ][xpack.security.authc.file] [hQWaRT2] no entries found in users_roles file [/Users/dpilato/Documents/Elasticsearch/dev/blog-tests/ingest-bano/target/integration-tests/run/elasticsearch-5.0.0/config/x-pack/users_roles]. use bin/xpack/users to add users and role mappings
[elasticsearch] [2016-08-03 19:37:02,296][INFO ][xpack.security.transport ] [hQWaRT2] publish_address {127.0.0.1:9500}, bound_addresses {127.0.0.1:9500}
[elasticsearch] [2016-08-03 19:37:02,301][WARN ][bootstrap                ] [hQWaRT2] initial heap size [268435456] not equal to maximum heap size [2147483648]; this can cause resize pauses and prevents mlockall from locking the entire heap
[elasticsearch] [2016-08-03 19:37:02,301][WARN ][bootstrap                ] [hQWaRT2] please set [discovery.zen.minimum_master_nodes] to a majority of the number of master eligible nodes in your cluster
[elasticsearch] [2016-08-03 19:37:05,373][INFO ][cluster.service          ] [hQWaRT2] new_master {hQWaRT2}{hQWaRT2TRvW8aYzm4uI51g}{dx2GKBz6QaGaDcbOVnuEqg}{127.0.0.1}{127.0.0.1:9500}, reason: zen-disco-elected-as-master ([0] nodes joined)
[elasticsearch] [2016-08-03 19:37:05,385][INFO ][http                     ] [hQWaRT2] publish_address {127.0.0.1:9400}, bound_addresses {127.0.0.1:9400}
[elasticsearch] [2016-08-03 19:37:05,386][INFO ][node                     ] [hQWaRT2] started
[elasticsearch] [2016-08-03 19:37:05,511][INFO ][gateway                  ] [hQWaRT2] recovered [0] indices into cluster_state
     [echo] External node started PID 24989
[INFO] Executed tasks
[INFO]
```

Then it will launch the tests as usual:

```txt
[INFO] --- junit4-maven-plugin:2.3.3:junit4 (integration-tests) @ ingest-bano ---
[INFO] <JUnit4> says 今日は! Master seed: 4CB5E1A5F9A89609
Executing 1 suite with 1 JVM.

Started J0 PID(25006@MacBook-Pro-4.local).
Suite: org.elasticsearch.ingest.bano.BanoPluginIT
  1> [2016-08-03 19:37:08,141][WARN ][org.elasticsearch.bootstrap] Unable to lock JVM Memory: error=78, reason=Function not implemented
  1> [2016-08-03 19:37:08,142][WARN ][org.elasticsearch.bootstrap] This can result in part of the JVM being swapped out.
  1> [2016-08-03 19:37:09,127][INFO ][it                       ] Integration tests ready to start... Cluster is running.
OK      0.11s | BanoPluginIT.testPluginIsLoaded
  1> [2016-08-03 19:37:09,243][INFO ][it                       ] Stopping integration tests against an external cluster
Completed [1/1] in 1.40s, 1 test

[INFO] JVM J0:     0.58 ..     2.36 =     1.78s
[INFO] Execution time total: 2.36 sec.
[INFO] Tests summary: 1 suite, 1 test
[INFO]
[INFO] --- maven-antrun-plugin:1.8:run (integ-teardown) @ ingest-bano ---
[INFO] Executing tasks

main:
```

And finally it will stop the cluster:

```txt
stop-external-cluster:
     [echo] Shutting down external node PID 24989
   [delete] Deleting: /Users/dpilato/Documents/Elasticsearch/dev/blog-tests/ingest-bano/target/integration-tests/run/es.pid
[INFO] Executed tasks
[INFO]
[INFO] --- maven-install-plugin:2.4:install (default-install) @ ingest-bano ---
[INFO] Installing /Users/dpilato/Documents/Elasticsearch/dev/blog-tests/ingest-bano/target/ingest-bano-5.0.0.jar to /Users/dpilato/.m2/repository/fr/pilato/elasticsearch/ingest/ingest-bano/5.0.0/ingest-bano-5.0.0.jar
[INFO] Installing /Users/dpilato/Documents/Elasticsearch/dev/blog-tests/ingest-bano/pom.xml to /Users/dpilato/.m2/repository/fr/pilato/elasticsearch/ingest/ingest-bano/5.0.0/ingest-bano-5.0.0.pom
[INFO] Installing /Users/dpilato/Documents/Elasticsearch/dev/blog-tests/ingest-bano/target/releases/ingest-bano-5.0.0.zip to /Users/dpilato/.m2/repository/fr/pilato/elasticsearch/ingest/ingest-bano/5.0.0/ingest-bano-5.0.0.zip
```

Et voilà! :)

```txt
[INFO] ------------------------------------------------------------------------
[INFO] BUILD SUCCESS
[INFO] ------------------------------------------------------------------------
[INFO] Total time: 21.124 s
[INFO] Finished at: 2016-08-03T19:37:09+02:00
[INFO] Final Memory: 32M/520M
[INFO] ------------------------------------------------------------------------
```

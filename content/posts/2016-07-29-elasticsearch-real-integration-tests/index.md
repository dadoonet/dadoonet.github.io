---
title: "Elasticsearch real integration tests"
#description:
author: David Pilato
avatar: /about/david_pilato.png
tags:
  - java
  - maven
  - ant
  - test
  - elasticsearch
  - plugin
categories:
  - tutorial
series:
  - plugin for elasticsearch v5
date: 2016-07-29 03:02:48 +0200
lastmod: 2016-10-18 03:02:48 +0200
draft: false
aliases:
  - /blog/2016/07/29/elasticsearch-real-integration-tests/
  - /blog/2016/10/18/elasticsearch-real-integration-tests-updated-for-ga/
  - /blog/2016-07-29-elasticsearch-real-integration-tests/
---

Integration tests... How do you run them?

Often, you are tempted to run services you want to test from JUnit for example.
In elasticsearch, you can extend `ESIntegTestCase` class which will start a cluster of a given
number of nodes.

```java
public class BanoPluginIntegrationTest extends ESIntegTestCase {
    public void testPluginIsLoaded() throws Exception {
        // Your code here
    }
}
```

But to be honest, the test you are running does not guarantee that you will have the same
result in production.

Why this? Because some services might be disabled, some others might be mocked.

Instead, running tests against a real cluster as the one you would install locally on your machine
is the way to go.

Let's see how you can do that with Maven...

<!--more-->

## How do we want to test?

Ideally, we want to:

* download elasticsearch 5.0.0 version
* unzip it
* install the plugin we are building if this is what we are doing
* install any other plugin we could need for the tests
* launch elasticsearch
* run our integration tests against this cluster
* stop the cluster at the end

We want to do that during maven integration test phase. No need to do that every time.
Also, we might want to be able to run the tests from our IDE against an external cluster we installed manually.

### Separated skipTests

If we want to be able to skip either unit tests or integration tests, we can
define 3 properties in our `pom.xml`:

```xml
<skipTests>false</skipTests>
<skipUnitTests>${skipTests}</skipUnitTests>
<skipIntegTests>${skipTests}</skipIntegTests>
```

### Writing a ANT script

Elasticsearch team wrote an ANT script to achieve some of the goals we described before.
You can read the original script I used [on github](https://github.com/elastic/elasticsearch/blob/2.4/dev-tools/src/main/resources/ant/integration-tests.xml).

You can put this `integration-tests.xml` file in `src/test/ant/` for example:

```xml
<?xml version="1.0"?>
<project name="integration-tests" xmlns:if="ant:if" xmlns:unless="ant:unless">
    <!-- our pid file for easy cleanup -->
    <property name="integ.pidfile" location="${project.build.directory}/integration-tests/run/es.pid"/>

    <!-- if this exists, ES is running (maybe) -->
    <available property="integ.pidfile.exists" file="${integ.pidfile}"/>

    <!-- name of our cluster, maybe needs changing -->
    <property name="integ.cluster.name" value="elasticsearch_integration"/>

    <!-- runs an OS script -->
    <macrodef name="run-script">
        <attribute name="script"/>
        <attribute name="spawn" default="false"/>
        <element name="nested" optional="true"/>
        <sequential>
            <local name="failonerror"/>
            <condition property="failonerror">
                <isfalse value="@{spawn}"/>
            </condition>

            <!-- create a temp CWD, to enforce that commands don't rely on CWD -->
            <local name="temp.cwd"/>
            <tempfile property="temp.cwd" destDir="${project.build.directory}/integration-tests/run/tmp" deleteonexit="true"/>
            <mkdir dir="${temp.cwd}"/>

            <!-- print commands we run -->
            <local name="script.base"/>
            <basename file="@{script}" property="script.base"/>
            <!-- crappy way to output, but we need it. make it nice later -->
            <echoxml><exec script="${script.base}"><nested/></exec></echoxml>
            <exec executable="cmd" osfamily="winnt" dir="${temp.cwd}" failonerror="${failonerror}" spawn="@{spawn}" taskname="${script.base}">
                <arg value="/c"/>
                <arg value="&quot;"/>
                <arg value="@{script}.bat"/>
                <nested/>
                <arg value="&quot;"/>
            </exec>

            <exec executable="bash" osfamily="unix" dir="${temp.cwd}" failonerror="${failonerror}" spawn="@{spawn}" taskname="${script.base}">
                <arg value="@{script}"/>
                <nested/>
            </exec>
        </sequential>
    </macrodef>

    <!-- extracts PID from file -->
    <macrodef name="extract-pid">
        <attribute name="file"/>
        <attribute name="property"/>
        <sequential>
            <loadfile srcFile="@{file}" property="@{property}">
                <filterchain>
                    <striplinebreaks/>
                </filterchain>
            </loadfile>
        </sequential>
    </macrodef>

    <!-- applies transformations to src and stores in dst -->
    <macrodef name="filter-property">
        <attribute name="src"/>
        <attribute name="dest"/>
        <element name="chain"/>
        <sequential>
            <loadresource property="@{dest}">
                <propertyresource name="@{src}"/>
                <filterchain>
                    <tokenfilter>
                        <chain/>
                    </tokenfilter>
                </filterchain>
            </loadresource>
        </sequential>
    </macrodef>

    <!-- waits for elasticsearch to start -->
    <macrodef name="waitfor-elasticsearch">
        <attribute name="port"/>
        <attribute name="timeoutproperty"/>
        <sequential>
            <echo>Waiting for elasticsearch to become available on port @{port}...</echo>
            <waitfor maxwait="30" maxwaitunit="second"
                     checkevery="500" checkeveryunit="millisecond"
                     timeoutproperty="@{timeoutproperty}">
                <http url="http://localhost:@{port}"/>
            </waitfor>
        </sequential>
    </macrodef>

    <scriptdef name="isGreater" language="javascript">
        <attribute name="v1"/>
        <attribute name="v2"/>
        <![CDATA[

            var i, l, d, s = false;

            a = attributes.get("v1").split('.');
            b = attributes.get("v2").split('.');
            l = Math.min(a.length, b.length);

            for (i=0; i<l; i++) {
                d = parseInt(a[i], 10) - parseInt(b[i], 10);
                if (d !== 0) {
                    project.setProperty("compare-result", d > 0);
                    s = true;
                    break;
                }
            }

            if(!s){
                d = a.length - b.length;
                project.setProperty("compare-result", d >= 0);
            }

            ]]>
    </scriptdef>

    <!-- start elasticsearch and wait until its ready -->
    <macrodef name="startup-elasticsearch">
        <attribute name="home" default="${project.build.directory}/integration-tests/run/elasticsearch-${elasticsearch.version}"/>
        <attribute name="spawn" default="true"/>
        <attribute name="es.cluster.name" default="${integ.cluster.name}"/>
        <attribute name="es.http.port" default="${integ.http.port}"/>
        <attribute name="es.transport.tcp.port" default="${integ.transport.port}"/>
        <attribute name="es.pidfile" default="${integ.pidfile}"/>
        <element name="additional-args" optional="true"/>
        <sequential>
            <!-- make sure no elasticsearch instance is currently running and listening on the port we need -->
            <fail message="This test expects port @{es.http.port} to be free but an elasticsearch instance is already running and listening on that port.
      Maybe the last test run did not manage to shut down the node correctly?
      You must kill it before tests can run.">
                <condition>
                    <socket server="localhost" port="@{es.http.port}"></socket>
                </condition>
            </fail>
            <!-- run bin/elasticsearch with args -->
            <echo>Starting up external cluster...</echo>
            <isGreater v1="${elasticsearch.version}" v2="5.0.0" />

            <echo if:true="${compare-result}">running Elasticsearch 5.0.0 or superior</echo>
            <echo unless:true="${compare-result}">running Elasticsearch &lt; 5.0.0</echo>

            <run-script script="@{home}/bin/elasticsearch"
                        spawn="@{spawn}">
                <nested>
                    <arg value="-Des.pidfile=@{es.pidfile}" unless:true="${compare-result}"/>
                    <arg value="-Des.cluster.name=@{es.cluster.name}" unless:true="${compare-result}"/>
                    <arg value="-Des.http.port=@{es.http.port}" unless:true="${compare-result}"/>
                    <arg value="-Des.transport.tcp.port=@{es.transport.tcp.port}" unless:true="${compare-result}"/>
                    <arg value="-Des.network.host=127.0.0.1" unless:true="${compare-result}"/>
                    <arg value="-Epidfile=@{es.pidfile}" if:true="${compare-result}"/>
                    <arg value="-Ecluster.name=@{es.cluster.name}" if:true="${compare-result}"/>
                    <arg value="-Ehttp.port=@{es.http.port}" if:true="${compare-result}"/>
                    <arg value="-Etransport.tcp.port=@{es.transport.tcp.port}" if:true="${compare-result}"/>
                    <arg value="-Enetwork.host=127.0.0.1" if:true="${compare-result}"/>
                    <additional-args/>
                </nested>
            </run-script>

            <!-- wait for startup -->
            <local name="failed.to.start"/>
            <waitfor-elasticsearch port="@{es.http.port}"
                                   timeoutproperty="failed.to.start"/>

            <!-- best effort, print console log. useful if it fails especially -->
            <local name="log.contents"/>
            <loadfile srcFile="@{home}/logs/@{es.cluster.name}.log"
                      property="log.contents"
                      failonerror="false"/>
            <echo message="${log.contents}" taskname="elasticsearch"/>

            <fail message="ES instance did not start" if="failed.to.start"/>

            <local name="integ.pid"/>
            <extract-pid file="@{es.pidfile}" property="integ.pid"/>
            <echo>External node started PID ${integ.pid}</echo>
        </sequential>
    </macrodef>

    <macrodef name="stop-node">
        <attribute name="es.pidfile" default="${integ.pidfile}"/>
        <sequential>
            <local name="integ.pid"/>

            <extract-pid file="@{es.pidfile}" property="integ.pid"/>
            <echo>Shutting down external node PID ${integ.pid}</echo>
            <!-- verify with jps that this actually is the correct pid.
            See if we can find the line "pid org.elasticsearch.bootstrap.Elasticsearch" in the output of jps -l.-->
            <local name="jps.pidline"/>
            <local name="jps.executable"/>
            <local name="environment"/>
            <property environment="environment"/>
            <property name="jps.executable" location="${environment.JAVA_HOME}/bin/jps"/>
            <exec executable="${jps.executable}" failonerror="true">
                <arg value="-l"/>
                <redirector outputproperty="jps.pidline">
                    <outputfilterchain>
                        <linecontains>
                            <contains value="${integ.pid} org.elasticsearch.bootstrap.Elasticsearch"/>
                        </linecontains>
                    </outputfilterchain>
                </redirector>
            </exec>
            <fail
                    message="pid file at @{es.pidfile} is ${integ.pid} but jps -l did not report any process with org.elasticsearch.bootstrap.Elasticsearch and this pid.
          Did you run mvn clean? Maybe an old pid file is still lying around.">
                <condition>
                    <equals arg1="${jps.pidline}" arg2=""/>
                </condition>
            </fail>

            <exec executable="taskkill" failonerror="true" osfamily="winnt">
                <arg value="/F"/>
                <arg value="/PID"/>
                <arg value="${integ.pid}"/>
            </exec>
            <exec executable="kill" failonerror="true" osfamily="unix">
                <arg value="-9"/>
                <arg value="${integ.pid}"/>
            </exec>
            <delete file="@{es.pidfile}"/>
        </sequential>
    </macrodef>

    <target name="stop-external-cluster" if="integ.pidfile.exists">
        <stop-node/>
    </target>

    <target name="setup-workspace" depends="stop-external-cluster">
        <sequential>
            <delete dir="${project.build.directory}/integration-tests/run"/>
            <unzip src="${project.build.directory}/integration-tests/binaries/elasticsearch-${elasticsearch.version}.zip"
                   dest="${project.build.directory}/integration-tests/run"/>
        </sequential>
    </target>

    <target name="start-external-cluster" depends="setup-workspace">
        <startup-elasticsearch/>
    </target>

    <!-- unzip integ test artifact, install plugin, then start ES -->
    <target name="start-external-cluster-with-plugin" depends="setup-workspace">
        <install-plugin name="${project.artifactId}" file="${project.build.directory}/releases/${project.artifactId}-${project.version}.zip"/>
        <startup-elasticsearch/>
    </target>

    <!-- installs a plugin into elasticsearch -->
    <macrodef name="install-plugin">
        <attribute name="home" default="${project.build.directory}/integration-tests/run/elasticsearch-${elasticsearch.version}"/>
        <attribute name="name"/>
        <attribute name="file"/>
        <sequential>
            <local name="url"/>
            <makeurl property="url" file="@{file}"/>

            <isGreater v1="${elasticsearch.version}" v2="5.0.0" />
            <property name="commandline" value="@{home}/bin/plugin" unless:true="${compare-result}"/>
            <property name="commandline" value="@{home}/bin/elasticsearch-plugin" if:true="${compare-result}"/>

            <!-- install plugin -->
            <echo>Installing plugin @{name}...</echo>
            <run-script script="${commandline}">
                <nested>
                    <arg value="install"/>
                    <arg value="${url}"/>
                </nested>
            </run-script>

            <fail message="did not find plugin installed as @{name}">
                <condition>
                    <not>
                        <resourceexists>
                            <file file="@{home}/plugins/@{name}"/>
                        </resourceexists>
                    </not>
                </condition>
            </fail>
        </sequential>
    </macrodef>
</project>
```

This script provides 3 main tasks:

* `start-external-cluster`: Unzip elasticsearch then starts a node
* `start-external-cluster-with-plugin`: Unzip elasticsearch, install a plugin then starts a node
* `stop-external-cluster`: Stop the running node

It also takes into account the version you are using as options/settings might change between major versions.
So this script has been tested against elasticsearch 1.x, 2.x and 5.x series.

### Download elasticsearch

You can use Maven dependency plugin for that.

Define some properties first:

```xml
<elasticsearch.groupid>org.elasticsearch.distribution.zip</elasticsearch.groupid>
<elasticsearch.version>5.0.0</elasticsearch.version>
<skipTests>false</skipTests>

<!-- For integration tests using ANT -->
<integ.http.port>9400</integ.http.port>
<integ.transport.port>9500</integ.transport.port>
```

Then add the dependency plugin:

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-dependency-plugin</artifactId>
    <version>2.10</version>
    <executions>
        <execution>
            <id>integ-setup-dependencies</id>
            <phase>pre-integration-test</phase>
            <goals>
                <goal>copy</goal>
            </goals>
            <configuration>
                <skip>${skipIntegTests}</skip>
                <artifactItems>
                    <artifactItem>
                        <groupId>${elasticsearch.groupid}</groupId>
                        <artifactId>elasticsearch</artifactId>
                        <version>${elasticsearch.version}</version>
                        <type>zip</type>
                    </artifactItem>
                </artifactItems>
                <useBaseVersion>true</useBaseVersion>
                <outputDirectory>${project.build.directory}/integration-tests/binaries</outputDirectory>
            </configuration>
        </execution>
    </executions>
</plugin>
```

This will get elasticsearch from you `.m2` local repository and if not available, it will downloaded from Maven central first.

### Launch ANT script

You can use Maven ant plugin:

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-antrun-plugin</artifactId>
    <version>1.8</version>
    <executions>
        <!-- start up external cluster -->
        <execution>
            <id>integ-setup</id>
            <phase>pre-integration-test</phase>
            <goals>
                <goal>run</goal>
            </goals>
            <configuration>
                <skip>${skipIntegTests}</skip>
                <target>
                    <ant antfile="src/test/ant/integration-tests.xml" target="start-external-cluster-with-plugin"/>
                </target>
            </configuration>
        </execution>
        <!-- shut down external cluster -->
        <execution>
            <id>integ-teardown</id>
            <phase>post-integration-test</phase>
            <goals>
                <goal>run</goal>
            </goals>
            <configuration>
                <skip>${skipIntegTests}</skip>
                <target>
                    <ant antfile="src/test/ant/integration-tests.xml" target="stop-external-cluster"/>
                </target>
            </configuration>
        </execution>
    </executions>
</plugin>
```

It will launch here the `start-external-cluster-with-plugin` task during before integration tests and `stop-external-cluster` after integration tests.

### Separate integration tests and unit tests

As I'm using the Randomized testing framework, here is what I wrote.

First, I'm disabling Maven surefire plugin:

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-surefire-plugin</artifactId>
    <version>2.19</version>
    <executions>
        <execution>
            <id>default-test</id>
            <phase>none</phase>
        </execution>
    </executions>
</plugin>
```

Then, I configure the randomizedtesting plugin:

```xml
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
            <inherited>true</inherited>
            <configuration>
                <skipTests>${skipUnitTests}</skipTests>
                <includes>
                    <include>**/*Test.class</include>
                </includes>
                <excludes>
                    <exclude>**/*$*</exclude>
                </excludes>
            </configuration>
        </execution>
        <execution>
            <id>integration-tests</id>
            <phase>integration-test</phase>
            <goals>
                <goal>junit4</goal>
            </goals>
            <inherited>true</inherited>
            <configuration>
                <skipTests>${skipIntegTests}</skipTests>
                <includes>
                    <include>**/*IT.class</include>
                </includes>
                <excludes>
                    <exclude>**/*$*</exclude>
                </excludes>
            </configuration>
        </execution>
    </executions>
</plugin>
```

You can see in the configuration that tests with name ending with `Test` are considered as unit tests.
Tests ending with `IT` will be launched only during integration tests phase. Note that we skip the tests
depending on `skipUnitTests` and `skipIntegTests`.

So running something like:

```sh
mvn clean install -DskipUnitTests
```

Will only launch integration tests.

### Adding profiles for 1.x and 2.x

You can use Maven profiles to be able to test any version you wish.
I choose to test only the latest version of each major branch:

```xml
<profiles>
    <profile>
        <id>es-1x</id>
        <properties>
            <elasticsearch.groupid>org.elasticsearch</elasticsearch.groupid>
            <elasticsearch.version>1.7.5</elasticsearch.version>
        </properties>
    </profile>
    <profile>
        <id>es-2x</id>
        <properties>
            <elasticsearch.groupid>org.elasticsearch.distribution.zip</elasticsearch.groupid>
            <elasticsearch.version>2.3.3</elasticsearch.version>
        </properties>
    </profile>
</profiles>
```

When you want to test against 5.x, just run:

```sh
mvn clean install
```

To test against 2.x, run:

```sh
mvn clean install -Pes-2x
```

To test against 1.x, run:

```sh
mvn clean install -Pes-1x
```

> This is theorical as for example the test framework does not exist in 1.7 and plugins from 2.0 must
> match the exact version they have built for.
> But if you are building a standalone application and want to test your application, this is the
> way to go. This is exactly what I did for [FSCrawler project](https://github.com/dadoonet/fscrawler).

## Write Integration tests

### Add Elasticsearch REST Client

Elasticsearch 5.0.0 comes with a new low level REST client.
We can use it to run our tests:

```xml
<dependency>
    <groupId>org.elasticsearch.client</groupId>
    <artifactId>rest</artifactId>
    <version>${elasticsearch.rest.version}</version>
    <scope>test</scope>
</dependency>
```

Note that we added a new maven property called `elasticsearch.rest.version`:

```xml
<properties>
    <elasticsearch.rest.version>5.0.0</elasticsearch.rest.version>
</properties>
```

Why is it another property than `${elasticsearch.version}` than the elasticsearch?
Actually if you run your tests against a 2.x or 1.x version, the REST client
does not exist for versions before 5.0. But it is compatible with older versions.
So when we use a profile `es-1x` or `es-2x`, we must stick with the version 5.x of
the REST plugin.

### Skip tests if no cluster

When we run from the IDE, we don't want to fail our tests because we did not start
an external cluster.

Let's build an abstract class for all our Integration tests:

```java
public abstract class AbstractITCase extends ESTestCase {
    protected static final Logger staticLogger = ESLoggerFactory.getLogger("it");
    protected final static int HTTP_TEST_PORT = 9400;
    protected static RestClient client;

    @BeforeClass
    public static void startRestClient() {
        client = RestClient.builder(new HttpHost("localhost", HTTP_TEST_PORT)).build();
        try {
            Response response = client.performRequest("GET", "/");
            Map<String, Object> responseMap = entityAsMap(response);
            assertThat(responseMap, hasEntry("tagline", "You Know, for Search"));
            staticLogger.info("Integration tests ready to start... Cluster is running.");
        } catch (IOException e) {
            // If we have an exception here, let's ignore the test
            staticLogger.warn("Integration tests are skipped: [{}]", e.getMessage());
            assumeThat("Integration tests are skipped", e.getMessage(), not(containsString("Connection refused")));
            staticLogger.error("Full error is", e);
            fail("Something wrong is happening. REST Client seemed to raise an exception.");
        }
    }

    @AfterClass
    public static void stopRestClient() throws IOException {
        if (client != null) {
            client.close();
            client = null;
        }
        staticLogger.info("Stopping integration tests against an external cluster");
    }
}
```

This class test before launching any test that a cluster is running on port `9400`.
If not, `assumeThat()` method will simply mark the test as ignored.

### Our first integration test

We want to test that the plugin is actually loaded. So we call the [Nodes Info API](https://www.elastic.co/guide/en/elasticsearch/reference/current/cluster-nodes-info.html).

```java
public class BanoPluginIT extends AbstractITCase {

    public void testPluginIsLoaded() throws Exception {

        Response response = client.performRequest("GET", "/_nodes/plugins");

        Map<String, Object> nodes = (Map<String, Object>) entityAsMap(response).get("nodes");
        for (String nodeName : nodes.keySet()) {
            boolean pluginFound = false;
            Map<String, Object> node = (Map<String, Object>) nodes.get(nodeName);
            List<Map<String, Object>> plugins = (List<Map<String, Object>>) node.get("plugins");
            for (Map<String, Object> plugin : plugins) {
                String pluginName = (String) plugin.get("name");
                if (pluginName.equals("ingest-bano")) {
                    pluginFound = true;
                    break;
                }
            }
            assertThat(pluginFound, is(true));
        }
    }
}
```

### Run the tests

Just start `mvn install` and let Maven do all the job!

```sh
$ mvn install
[INFO] Scanning for projects...
[INFO]
[INFO] ------------------------------------------------------------------------
[INFO] Building Plugin: Ingest: BANO 5.0.0-SNAPSHOT
[INFO] ------------------------------------------------------------------------
[INFO]
[INFO] --- maven-resources-plugin:2.6:resources (default-resources) @ ingest-bano ---
[INFO] Copying 0 resource
[INFO]
[INFO] --- maven-compiler-plugin:3.3:compile (default-compile) @ ingest-bano ---
[INFO] Nothing to compile - all classes are up to date
[INFO]
[INFO] --- maven-resources-plugin:2.6:testResources (default-testResources) @ ingest-bano ---
[INFO] Copying 1 resource
[INFO]
[INFO] --- maven-compiler-plugin:3.3:testCompile (default-testCompile) @ ingest-bano ---
[INFO] Nothing to compile - all classes are up to date
[INFO]
[INFO] --- junit4-maven-plugin:2.3.3:junit4 (unit-tests) @ ingest-bano ---
[INFO] <JUnit4> says ahoj! Master seed: 9C880DFF84F2A5FD
Executing 1 suite with 1 JVM.

# UNIT TESTS HERE

Completed [1/1] in 4.18s, 1 test

[INFO] JVM J0:     0.65 ..     5.47 =     4.82s
[INFO] Execution time total: 5.47 sec.
[INFO] Tests summary: 1 suite, 1 test
[INFO]
[INFO] --- maven-jar-plugin:2.4:jar (default-jar) @ ingest-bano ---
[INFO]
[INFO] --- maven-assembly-plugin:2.6:single (default) @ ingest-bano ---
[INFO] Reading assembly descriptor: /Users/dpilato/Documents/Elasticsearch/dev/blog-tests/ingest-bano/src/main/assemblies/plugin.xml
[INFO] Building zip: /Users/dpilato/Documents/Elasticsearch/dev/blog-tests/ingest-bano/target/releases/ingest-bano-5.0.0-SNAPSHOT.zip
[INFO]
[INFO] --- maven-dependency-plugin:2.10:copy (integ-setup-dependencies) @ ingest-bano ---
[INFO] Configured Artifact: org.elasticsearch.distribution.zip:elasticsearch:5.0.0:zip
[INFO] org.elasticsearch.distribution.zip:elasticsearch:5.0.0:zip already exists in /Users/dpilato/Documents/Elasticsearch/dev/blog-tests/ingest-bano/target/integration-tests/binaries
[INFO]
[INFO] --- maven-antrun-plugin:1.8:run (integ-setup) @ ingest-bano ---
[INFO] Executing tasks

main:

stop-external-cluster:

setup-workspace:
   [delete] Deleting directory /Users/dpilato/Documents/Elasticsearch/dev/blog-tests/ingest-bano/target/integration-tests/run
    [unzip] Expanding: /Users/dpilato/Documents/Elasticsearch/dev/blog-tests/ingest-bano/target/integration-tests/binaries/elasticsearch-5.0.0.zip into /Users/dpilato/Documents/Elasticsearch/dev/blog-tests/ingest-bano/target/integration-tests/run

start-external-cluster-with-plugin:
     [echo] Installing plugin ingest-bano...
    [mkdir] Created dir: /Users/dpilato/Documents/Elasticsearch/dev/blog-tests/ingest-bano/target/integration-tests/run/tmp/null463372788
<?xml version="1.0" encoding="UTF-8"?>
<exec script="elasticsearch-plugin">
  <arg value="install" />
  <arg value="file:/Users/dpilato/Documents/Elasticsearch/dev/blog-tests/ingest-bano/target/releases/ingest-bano-5.0.0.zip" />
</exec>
[elasticsearch-plugin] Plugins directory [/Users/dpilato/Documents/Elasticsearch/dev/blog-tests/ingest-bano/target/integration-tests/run/elasticsearch-5.0.0/plugins] does not exist. Creating...
[elasticsearch-plugin] -> Downloading file:/Users/dpilato/Documents/Elasticsearch/dev/blog-tests/ingest-bano/target/releases/ingest-bano-5.0.0-SNAPSHOT.zip
[elasticsearch-plugin]
[elasticsearch-plugin] -> Installed ingest-bano
     [echo] Starting up external cluster...
     [echo] running Elasticsearch 5.0.0 or superior
    [mkdir] Created dir: /Users/dpilato/Documents/Elasticsearch/dev/blog-tests/ingest-bano/target/integration-tests/run/tmp/null353022298
<?xml version="1.0" encoding="UTF-8"?>
<exec script="elasticsearch">
  <arg value="-Epidfile=/Users/dpilato/Documents/Elasticsearch/dev/blog-tests/ingest-bano/target/integration-tests/run/es.pid" />
  <arg value="-Ecluster.name=elasticsearch_integration" />
  <arg value="-Ehttp.port=9400" />
  <arg value="-Etransport.tcp.port=9500" />
  <arg value="-Enetwork.host=127.0.0.1" />
</exec>
     [echo] Waiting for elasticsearch to become available on port 9400...
[elasticsearch] [2016-07-29 01:54:01,457][INFO ][node                     ] [] initializing ...
[elasticsearch] [2016-07-29 01:54:01,526][INFO ][env                      ] [GTlhLM8] using [1] data paths, mounts [[/ (/dev/disk1)]], net usable_space [24.1gb], net total_space [464.7gb], spins? [unknown], types [hfs]
[elasticsearch] [2016-07-29 01:54:01,526][INFO ][env                      ] [GTlhLM8] heap size [1.9gb], compressed ordinary object pointers [true]
[elasticsearch] [2016-07-29 01:54:01,527][INFO ][node                     ] [GTlhLM8] node name [GTlhLM8] derived from node ID; set [node.name] to override
[elasticsearch] [2016-07-29 01:54:01,528][INFO ][node                     ] [GTlhLM8] version[5.0.0], pid[2942], build[0d2ccf0/2016-07-28T15:02:31.650Z], OS[Mac OS X/10.11.5/x86_64], JVM[Oracle Corporation/Java HotSpot(TM) 64-Bit Server VM/1.8.0_60/25.60-b23]
[elasticsearch] [2016-07-29 01:54:02,442][INFO ][io.netty.util.internal.PlatformDependent] Your platform does not provide complete low-level API for accessing direct buffers reliably. Unless explicitly requested, heap buffer will always be preferred to avoid potential system unstability.
[elasticsearch] [2016-07-29 01:54:02,472][INFO ][plugins                  ] [GTlhLM8] loaded module [aggs-matrix-stats]
[elasticsearch] [2016-07-29 01:54:02,473][INFO ][plugins                  ] [GTlhLM8] loaded module [ingest-common]
[elasticsearch] [2016-07-29 01:54:02,473][INFO ][plugins                  ] [GTlhLM8] loaded module [lang-expression]
[elasticsearch] [2016-07-29 01:54:02,473][INFO ][plugins                  ] [GTlhLM8] loaded module [lang-groovy]
[elasticsearch] [2016-07-29 01:54:02,473][INFO ][plugins                  ] [GTlhLM8] loaded module [lang-mustache]
[elasticsearch] [2016-07-29 01:54:02,473][INFO ][plugins                  ] [GTlhLM8] loaded module [lang-painless]
[elasticsearch] [2016-07-29 01:54:02,473][INFO ][plugins                  ] [GTlhLM8] loaded module [percolator]
[elasticsearch] [2016-07-29 01:54:02,473][INFO ][plugins                  ] [GTlhLM8] loaded module [reindex]
[elasticsearch] [2016-07-29 01:54:02,473][INFO ][plugins                  ] [GTlhLM8] loaded module [transport-netty3]
[elasticsearch] [2016-07-29 01:54:02,473][INFO ][plugins                  ] [GTlhLM8] loaded module [transport-netty4]
[elasticsearch] [2016-07-29 01:54:02,475][INFO ][plugins                  ] [GTlhLM8] loaded plugin [ingest-bano]
[elasticsearch] [2016-07-29 01:54:04,280][INFO ][node                     ] [GTlhLM8] initialized
[elasticsearch] [2016-07-29 01:54:04,280][INFO ][node                     ] [GTlhLM8] starting ...
[elasticsearch] [2016-07-29 01:54:04,374][INFO ][transport                ] [GTlhLM8] publish_address {127.0.0.1:9500}, bound_addresses {127.0.0.1:9500}
[elasticsearch] [2016-07-29 01:54:04,384][WARN ][bootstrap                ] [GTlhLM8] initial heap size [268435456] not equal to maximum heap size [2147483648]; this can cause resize pauses and prevents mlockall from locking the entire heap
[elasticsearch] [2016-07-29 01:54:04,384][WARN ][bootstrap                ] [GTlhLM8] please set [discovery.zen.minimum_master_nodes] to a majority of the number of master eligible nodes in your cluster
[elasticsearch] [2016-07-29 01:54:07,442][INFO ][cluster.service          ] [GTlhLM8] new_master {GTlhLM8}{GTlhLM8vRK2YltPhlJOgTA}{C2ab3gH0S9OonOtQNbkmxw}{127.0.0.1}{127.0.0.1:9500}, reason: zen-disco-elected-as-master ([0] nodes joined)
[elasticsearch] [2016-07-29 01:54:07,453][INFO ][http                     ] [GTlhLM8] publish_address {127.0.0.1:9400}, bound_addresses {127.0.0.1:9400}
[elasticsearch] [2016-07-29 01:54:07,453][INFO ][node                     ] [GTlhLM8] started
[elasticsearch] [2016-07-29 01:54:07,461][INFO ][gateway                  ] [GTlhLM8] recovered [0] indices into cluster_state
     [echo] External node started PID 2942
[INFO] Executed tasks
[INFO]
[INFO] --- junit4-maven-plugin:2.3.3:junit4 (integration-tests) @ ingest-bano ---
[INFO] <JUnit4> says jolly good day! Master seed: 781C148F31C34F3D
Executing 1 suite with 1 JVM.

Started J0 PID(2958@MacBook-Pro-4.local).
Suite: org.elasticsearch.ingest.bano.BanoPluginIT
  1> [2016-07-29 01:54:08,648][WARN ][org.elasticsearch.bootstrap] Unable to lock JVM Memory: error=78, reason=Function not implemented
  1> [2016-07-29 01:54:08,649][WARN ][org.elasticsearch.bootstrap] This can result in part of the JVM being swapped out.
  1> [2016-07-29 01:54:09,496][INFO ][it                       ] Integration tests ready to start... Cluster is running.
OK      0.10s | BanoPluginIT.testPluginIsLoaded
  1> [2016-07-29 01:54:09,603][INFO ][it                       ] Stopping integration tests against an external cluster
Completed [1/1] in 1.22s, 1 test

[INFO] JVM J0:     0.27 ..     2.04 =     1.77s
[INFO] Execution time total: 2.05 sec.
[INFO] Tests summary: 1 suite, 1 test
[INFO]
[INFO] --- maven-antrun-plugin:1.8:run (integ-teardown) @ ingest-bano ---
[INFO] Executing tasks

main:

stop-external-cluster:
     [echo] Shutting down external node PID 2942
   [delete] Deleting: /Users/dpilato/Documents/Elasticsearch/dev/blog-tests/ingest-bano/target/integration-tests/run/es.pid
[INFO] Executed tasks
[INFO]
[INFO] --- maven-install-plugin:2.4:install (default-install) @ ingest-bano ---
[INFO] Installing /Users/dpilato/Documents/Elasticsearch/dev/blog-tests/ingest-bano/target/ingest-bano-5.0.0-SNAPSHOT.jar to /Users/dpilato/.m2/repository/fr/pilato/elasticsearch/ingest/ingest-bano/5.0.0-SNAPSHOT/ingest-bano-5.0.0-SNAPSHOT.jar
[INFO] Installing /Users/dpilato/Documents/Elasticsearch/dev/blog-tests/ingest-bano/pom.xml to /Users/dpilato/.m2/repository/fr/pilato/elasticsearch/ingest/ingest-bano/5.0.0-SNAPSHOT/ingest-bano-5.0.0-SNAPSHOT.pom
[INFO] Installing /Users/dpilato/Documents/Elasticsearch/dev/blog-tests/ingest-bano/target/releases/ingest-bano-5.0.0-SNAPSHOT.zip to /Users/dpilato/.m2/repository/fr/pilato/elasticsearch/ingest/ingest-bano/5.0.0-SNAPSHOT/ingest-bano-5.0.0-SNAPSHOT.zip
[INFO] ------------------------------------------------------------------------
[INFO] BUILD SUCCESS
[INFO] ------------------------------------------------------------------------
[INFO] Total time: 22.102 s
[INFO] Finished at: 2016-07-29T01:54:10+02:00
[INFO] Final Memory: 31M/545M
[INFO] ------------------------------------------------------------------------
```

You can see at the end the execution of integration tests from this line:

```txt
[INFO] --- junit4-maven-plugin:2.3.3:junit4 (integration-tests) @ ingest-bano ---
```

Done!

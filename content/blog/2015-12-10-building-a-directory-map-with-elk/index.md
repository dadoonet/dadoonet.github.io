---
title: "Building a directory map with ELK"
#description: 
toc: true
authors:
  - David Pilato
tags:
  - elasticsearch
  - logstash
  - kibana
categories:
  - tutorial
date: 2015-12-10 09:28:15 +0100
lastmod: 2015-12-10 09:28:15 +0100
# featuredImage: blog/2016-03-17-and-the-beats-go-on/beats.png
draft: false
aliases:
  - /blog/2015/12/10/building-a-directory-map-with-elk/
---

I gave a [BBL talk](http://www.brownbaglunch.fr/) recently and while chatting with attendees, one of them told me a simple use case he covered with elasticsearch: indexing metadata files on a NAS with a simple `ls -lR` like command.
His need is to be able to search on a NAS for files when a user wants to restore a deleted file.

As you can imagine a search engine is super helpful when you have hundreds of millions files!

I found this idea great and this is by the way why I love speaking at conferences or in companies: you always get great ideas when you listen to others!

I decided then to adapt this idea using the ELK stack.

<!-- more -->

## Find the command line

As I'm running on MacOS, I need to install first [coreutils](https://makandracards.com/mmarschall/4445-change-time-format-when-using-ls-on-mac-osx) as I'm missing one cool parameter to the `ls` command: `--time-style`.

```sh
brew install coreutils
```

I'm starting with `find` and `ls` which offers here a nice way to display our filesystem from a given directory, `~/Documents` here.

```sh
find ~/Documents -type f -print0 | xargs -0 gls -l --time-style="+%Y-%m-%dT%H:%M:%S"
```

This gives something like:

```txt
-rw-r--r-- 1 dpilato staff   6148 2014-09-18T12:49:23 /Users/dpilato/Documents/Elasticsearch/tmp/es/.DS_Store
-rw-r--r-- 1 dpilato staff 110831 2013-01-28T08:47:27 /Users/dpilato/Documents/Elasticsearch/tmp/es/docs/Autoentreprise2012.pdf
-rw-r--r-- 1 dpilato staff 145244 2013-01-15T14:47:28 /Users/dpilato/Documents/Elasticsearch/tmp/es/meetups/Meetup.pdf
-rw-r--r-- 1 dpilato staff     11 2015-05-12T16:34:08 /Users/dpilato/Documents/Elasticsearch/tmp/es/test.txt
```

## Parse with logstash

Let's create a nice JSON document with logstash.

### Analyze current format

What is the format we have? Each line has two main parts separated by a space:

* metadata: `-rw-r--r-- 1 dpilato staff     11 2015-05-12T16:34:08`
* fullpath: `/Users/dpilato/Documents/Elasticsearch/tmp/es/test.txt`

metadata contains:

* `d` if path is a directory or `-` if file. We only print files so we have only `-`.
* `rwx` user rights: `r` for read, `w` for write and `x` for execution
* `r-x` group rights: same format as for user rights
* `r-x` other rights: same format as for user rights
* ` `: a blank
* `1`: number of links
* ` `: a blank
* `dpilato `: user name
* ` `: a blank
* `staff   `: group name
* ` `: a blank
* `    11`: file size. The text length depends on the biggest file we will find.
* ` `: a blank
* `2015-05-12T16:34:08`: last modification date.

### Grok it

I'm using [GROK Constructor](http://grokconstructor.appspot.com/) to incrementally build the grok pattern.

I'm ending up with:

```txt
[d-][r-][w-][x-][r-][w-][x-][r-][w-][x-] %{INT} %{USERNAME} %{USERNAME} %{SPACE}%{NUMBER} %{TIMESTAMP_ISO8601} %{GREEDYDATA}
```

Translating to [logstash grok filter](https://www.elastic.co/guide/en/logstash/current/plugins-filters-grok.html) and setting field names, it gives:

```txt
(?:d|-)(?<permission.user.read>[r-])(?<permission.user.write>[w-])(?<permission.user.execute>[x-])(?<permission.group.read>[r-])(?<permission.group.write>[w-])(?<permission.group.execute>[x-])(?<permission.other.read>[r-])(?<permission.other.write>[w-])(?<permission.other.execute>[x-]) %{INT:links:int} %{USERNAME:user} %{USERNAME:group} %{SPACE}%{NUMBER:size:int} %{TIMESTAMP_ISO8601:date} %{GREEDYDATA:name}
```

Let's test it!

I create a file `treemap.conf`:

```ruby
input { stdin {} }

filter {
  grok {
    match => { "message" => "(?:d|-)(?<permission.user.read>[r-])(?<permission.user.write>[w-])(?<permission.user.execute>[x-])(?<permission.group.read>[r-])(?<permission.group.write>[w-])(?<permission.group.execute>[x-])(?<permission.other.read>[r-])(?<permission.other.write>[w-])(?<permission.other.execute>[x-]) %{INT:links:int} %{USERNAME:user} %{USERNAME:group} %{SPACE}%{NUMBER:size:int} %{TIMESTAMP_ISO8601:date} %{GREEDYDATA:name}" }
  }
}

output { stdout { codec => rubydebug } }
```

Then I launch logstash:

```sh
find ~/Documents -type f -print0 | xargs -0 gls -l --time-style="+%Y-%m-%dT%H:%M:%S" | bin/logstash -f treemap.conf
```

It gives for the same line we discussed before:

```ruby
                 "message" => "-rw-r--r-- 1 dpilato staff     11 2015-05-12T16:34:08 /Users/dpilato/Documents/Elasticsearch/tmp/es/test.txt",
                "@version" => "1",
              "@timestamp" => "2015-12-11T11:27:06.386Z",
                    "host" => "MacBook-Air-de-David.local",
    "permission.user.read" => "r",
   "permission.user.write" => "w",
 "permission.user.execute" => "-",
   "permission.group.read" => "r",
  "permission.group.write" => "-",
"permission.group.execute" => "-",
   "permission.other.read" => "r",
  "permission.other.write" => "-",
"permission.other.execute" => "-",
                   "links" => 1,
                    "user" => "dpilato",
                   "group" => "staff",
                    "size" => 11,
                    "date" => "2015-05-12T16:34:08",
                    "name" => " /Users/dpilato/Documents/Elasticsearch/tmp/es/test.txt"
```

When I try to write permission properties to nested fields, I hit an [issue](https://github.com/logstash-plugins/logstash-filter-grok/issues/66). So I need to add some transformations.

### Fix permissions

As seen before, we want to write permissions to a nested data structure.
We can use the [mutate filter](https://www.elastic.co/guide/en/logstash/current/plugins-filters-mutate.html).

First, let's replace `rwx` values to `true` and `-` to `false`:

```ruby
mutate {
  gsub => [
    "permission.user.read", "r", "true",
    "permission.user.read", "-", "false",
    "permission.user.write", "w", "true",
    "permission.user.write", "-", "false",
    "permission.user.execute", "x", "true",
    "permission.user.execute", "-", "false",
    "permission.group.read", "r", "true",
    "permission.group.read", "-", "false",
    "permission.group.write", "w", "true",
    "permission.group.write", "-", "false",
    "permission.group.execute", "x", "true",
    "permission.group.execute", "-", "false",
    "permission.other.read", "r", "true",
    "permission.other.read", "-", "false",
    "permission.other.write", "w", "true",
    "permission.other.write", "-", "false",
    "permission.other.execute", "x", "true",
    "permission.other.execute", "-", "false"
  ]
}
```

It now gives:

```ruby
    "permission.user.read" => "true",
   "permission.user.write" => "true",
 "permission.user.execute" => "false",
   "permission.group.read" => "true",
  "permission.group.write" => "false",
"permission.group.execute" => "false",
   "permission.other.read" => "true",
  "permission.other.write" => "false",
"permission.other.execute" => "false",
```

We can mutate again those fields as actual booleans:

```ruby
mutate {
  rename => { "permission.user.read" => "[permission][user][read]" }
  rename => { "permission.user.write" => "[permission][user][write]" }
  rename => { "permission.user.execute" => "[permission][user][execute]" }
  rename => { "permission.group.read" => "[permission][group][read]" }
  rename => { "permission.group.write" => "[permission][group][write]" }
  rename => { "permission.group.execute" => "[permission][group][execute]" }
  rename => { "permission.other.read" => "[permission][other][read]" }
  rename => { "permission.other.write" => "[permission][other][write]" }
  rename => { "permission.other.execute" => "[permission][other][execute]" }
}
```

It now gives:

```ruby
    "permission" => {
         "user" => {
               "read" => "true",
              "write" => "true",
            "execute" => "false"
        },
        "group" => {
               "read" => "true",
              "write" => "false",
            "execute" => "false"
        },
        "other" => {
               "read" => "true",
              "write" => "false",
            "execute" => "false"
        }
    }
```

Let's now move to `booleans`. We can add that to the same latest mutate filter we just added:

```ruby
    convert => { "[permission][user][read]" => "boolean" }
    convert => { "[permission][user][write]" => "boolean" }
    convert => { "[permission][user][execute]" => "boolean" }
    convert => { "[permission][group][read]" => "boolean" }
    convert => { "[permission][group][write]" => "boolean" }
    convert => { "[permission][group][execute]" => "boolean" }
    convert => { "[permission][other][read]" => "boolean" }
    convert => { "[permission][other][write]" => "boolean" }
    convert => { "[permission][other][execute]" => "boolean" }
```

Et voilà!

```ruby
    "permission" => {
         "user" => {
               "read" => true,
              "write" => true,
            "execute" => false
        },
        "group" => {
               "read" => true,
              "write" => false,
            "execute" => false
        },
        "other" => {
               "read" => true,
              "write" => false,
            "execute" => false
        }
    }
```

### Date reconciliation

We have 2 fields related to a timestamp:

```ruby
  "@timestamp" => "2015-12-11T11:27:06.386Z",
        "date" => "2015-05-12T16:34:08"
```

The [date filter](https://www.elastic.co/guide/en/logstash/current/plugins-filters-date.html) will reconciliate the `@timestamp` field with the file date.

```ruby
date {
    match => [ "date", "ISO8601" ]
    remove_field => [ "date" ]
}
```

Timestamp is now correct:

```ruby
"@timestamp" => "2013-01-15T13:47:28.000Z",
```

### Cleanup

Some fields are now not needed anymore so we can simply remove them by adding a `remove_field` directive to our mutate filter:

```ruby
remove_field => [ "message", "host", "@version" ]
```

We are now all set to send the final data to elasticsearch!

```ruby
{
    "@timestamp" => "2015-05-12T14:34:08.000Z",
         "links" => 1,
          "user" => "dpilato",
         "group" => "staff",
          "size" => 11,
          "name" => "/Users/dpilato/Documents/Elasticsearch/tmp/es/test.txt",
    "permission" => {
         "user" => {
               "read" => true,
              "write" => true,
            "execute" => false
        },
        "group" => {
               "read" => true,
              "write" => false,
            "execute" => false
        },
        "other" => {
               "read" => true,
              "write" => false,
            "execute" => false
        }
    }
}
```

## Send to elasticsearch

As usual we just have to connect the [elasticsearch output](https://www.elastic.co/guide/en/logstash/current/plugins-outputs-elasticsearch.html):

```ruby
elasticsearch {
  index => "treemap-%{+YYYY.MM}"
  document_type => "file"
}
```

### Use a template

Actually, we don't want elasticsearch decide for us what the mapping would be. So let's use a template and pass it to logstash:

```ruby
elasticsearch {
  index => "treemap-%{+YYYY.MM}"
  document_type => "file"
  template => "treemap-template.json"
  template_name => "treemap"
}
```

### Index settings

In `treemap-template.json`, we will define the following index settings:

```json
"index" : {
  "refresh_interval" : "5s",
  "number_of_shards" : 1,
  "number_of_replicas" : 0
}
```

### Path Analyzer

Also, we need a [path tokenizer](https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis-pathhierarchy-tokenizer.html) to analyze the fullpath, so we define an analyzer in index settings:

```json
"analysis": {
  "analyzer": {
    "path-analyzer": {
      "type": "custom",
      "tokenizer": "path-tokenizer"
    }
  },
  "tokenizer": {
    "path-tokenizer": {
      "type": "path_hierarchy"
    }
  }
}
```

### Mapping

Let's disable the [_all feature](https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping-all-field.html).

```json
"_all": {
  "enabled": false
}
```

Also, we don't analyze string fields but for `name` field, we use our `path-analyzer`:

```json
"name" : {
  "type" : "string",
  "analyzer": "path-analyzer"
}
```

## Kibana

While I'm creating some visualizations, I'm also launching the full injection:

```sh
find ~/Documents -type f -print0 | xargs -0 gls -l --time-style="+%Y-%m-%dT%H:%M:%S" | bin/logstash -f treemap.conf
find ~/Applications -type f -print0 | xargs -0 gls -l --time-style="+%Y-%m-%dT%H:%M:%S" | bin/logstash -f treemap.conf
find ~/Desktop -type f -print0 | xargs -0 gls -l --time-style="+%Y-%m-%dT%H:%M:%S" | bin/logstash -f treemap.conf
find ~/Downloads -type f -print0 | xargs -0 gls -l --time-style="+%Y-%m-%dT%H:%M:%S" | bin/logstash -f treemap.conf
find ~/Dropbox -type f -print0 | xargs -0 gls -l --time-style="+%Y-%m-%dT%H:%M:%S" | bin/logstash -f treemap.conf
find ~/Movies -type f -print0 | xargs -0 gls -l --time-style="+%Y-%m-%dT%H:%M:%S" | bin/logstash -f treemap.conf
find ~/Music -type f -print0 | xargs -0 gls -l --time-style="+%Y-%m-%dT%H:%M:%S" | bin/logstash -f treemap.conf
find ~/Pictures -type f -print0 | xargs -0 gls -l --time-style="+%Y-%m-%dT%H:%M:%S" | bin/logstash -f treemap.conf
find ~/Public -type f -print0 | xargs -0 gls -l --time-style="+%Y-%m-%dT%H:%M:%S" | bin/logstash -f treemap.conf
```

And finally, I can build my visualization...

{{< figure src="kibana1.png" caption="My hard disk" >}}

Please don't tell to my boss that I have more music files than work files (in term of disk space)! :D

## Complete files

For the record (in case you want to replay all that)...

### Logstash

`treemap.conf` file:

```ruby
input { stdin {} }
  
filter {
  grok {
    match => { "message" => "(?:d|-)(?<permission.user.read>[r-])(?<permission.user.write>[w-])(?<permission.user.execute>[x-])(?<permission.group.read>[r-])(?<permission.group.write>[w-])(?<permission.group.execute>[x-])(?<permission.other.read>[r-])(?<permission.other.write>[w-])(?<permission.other.execute>[x-]) %{INT:links:int} %{USERNAME:user} %{USERNAME:group} %{SPACE}%{NUMBER:size:int} %{TIMESTAMP_ISO8601:date} %{GREEDYDATA:name}" }
  }

  mutate {
    gsub => [
      "permission.user.read", "r", "true",
      "permission.user.read", "-", "false",
      "permission.user.write", "w", "true",
      "permission.user.write", "-", "false",
      "permission.user.execute", "x", "true",
      "permission.user.execute", "-", "false",
      "permission.group.read", "r", "true",
      "permission.group.read", "-", "false",
      "permission.group.write", "w", "true",
      "permission.group.write", "-", "false",
      "permission.group.execute", "x", "true",
      "permission.group.execute", "-", "false",
      "permission.other.read", "r", "true",
      "permission.other.read", "-", "false",
      "permission.other.write", "w", "true",
      "permission.other.write", "-", "false",
      "permission.other.execute", "x", "true",
      "permission.other.execute", "-", "false"
    ]
  }

  mutate {
    rename => { "permission.user.read" => "[permission][user][read]" }
    rename => { "permission.user.write" => "[permission][user][write]" }
    rename => { "permission.user.execute" => "[permission][user][execute]" }
    rename => { "permission.group.read" => "[permission][group][read]" }
    rename => { "permission.group.write" => "[permission][group][write]" }
    rename => { "permission.group.execute" => "[permission][group][execute]" }
    rename => { "permission.other.read" => "[permission][other][read]" }
    rename => { "permission.other.write" => "[permission][other][write]" }
    rename => { "permission.other.execute" => "[permission][other][execute]" }

    convert => { "[permission][user][read]" => "boolean" }
    convert => { "[permission][user][write]" => "boolean" }
    convert => { "[permission][user][execute]" => "boolean" }
    convert => { "[permission][group][read]" => "boolean" }
    convert => { "[permission][group][write]" => "boolean" }
    convert => { "[permission][group][execute]" => "boolean" }
    convert => { "[permission][other][read]" => "boolean" }
    convert => { "[permission][other][write]" => "boolean" }
    convert => { "[permission][other][execute]" => "boolean" }

    remove_field => [ "message", "host", "@version" ]
  }

  date {
    match => [ "date", "ISO8601" ]
    remove_field => [ "date" ]
  }
}

output { 
  stdout { codec => dots } 
  elasticsearch {
    index => "treemap-%{+YYYY.MM}"
    document_type => "file"
    template => "treemap-template.json"
    template_name => "treemap"
  }
}
```

### Template

`treemap-template.json` file:

```json
{
  "order" : 0,
  "template" : "treemap-*",
  "settings" : {
    "index" : {
      "refresh_interval" : "5s",
      "number_of_shards" : 1,
      "number_of_replicas" : 0
    },
    "analysis": {
      "analyzer": {
        "path-analyzer": {
          "type": "custom",
          "tokenizer": "path-tokenizer"
        }
      },
      "tokenizer": {
        "path-tokenizer": {
          "type": "path_hierarchy"
        }
      }
    }
  },
  "mappings" : {
    "file" : {
      "_all": {
        "enabled": false
      },
      "properties" : {
        "@timestamp" : {
          "type" : "date",
          "format" : "strict_date_optional_time||epoch_millis"
        },
        "group" : {
          "type" : "string",
          "index": "not_analyzed"
        },
        "links" : {
          "type" : "long"
        },
        "name" : {
          "type" : "string",
          "analyzer": "path-analyzer"
        },
        "permission" : {
          "properties" : {
            "group" : {
              "properties" : {
                "execute" : {
                  "type" : "boolean"
                },
                "read" : {
                  "type" : "boolean"
                },
                "write" : {
                  "type" : "boolean"
                }
              }
            },
            "other" : {
              "properties" : {
                "execute" : {
                  "type" : "boolean"
                },
                "read" : {
                  "type" : "boolean"
                },
                "write" : {
                  "type" : "boolean"
                }
              }
            },
            "user" : {
              "properties" : {
                "execute" : {
                  "type" : "boolean"
                },
                "read" : {
                  "type" : "boolean"
                },
                "write" : {
                  "type" : "boolean"
                }
              }
            }
          }
        },
        "size" : {
          "type" : "long"
        },
        "user" : {
          "type" : "string",
          "index": "not_analyzed"
        }
      }
    }
  },
  "aliases" : { 
    "files" : {}
  }
}
```

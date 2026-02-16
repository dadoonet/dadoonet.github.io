---
title: "Using JS Auth with found cluster"
description: "Using Found by elastic cluster helps a lot to have a ready to use and managed elasticsearch cluster. But I ran into an issue when you secure it and use the elasticsearch javascript client."
author: David Pilato
avatar: /about/david_pilato.avif
tags:
  - elasticsearch
  - found
  - js
categories:
  - tutorial
date: 2015-05-19 17:06:22 +0200
nolastmod: true
draft: false
cover: featured.avif
aliases:
  - /blog/2015/05/19/using-js-auth-with-found-cluster/
  - /blog/2015-05-19-using-js-auth-with-found-cluster/
---

Using [Found by elastic](https://www.found.no/) cluster helps a lot to have a ready to use and managed elasticsearch cluster.

I started my own cluster yesterday to power [brownbaglunch.fr](https://www.brownbaglunch.fr/) website (work in progress) and it was ready to use after some clicks!

**It's a kind of magic!**

{{< youtube 0p_1QSUsbsM >}}

But I ran into an issue when you secure it and use the [elasticsearch javascript client](https://www.elastic.co/guide/en/elasticsearch/client/javascript-api/current/index.html).

<!--more-->

## Creating your cluster

{{< figure src="found-1.avif" caption="Found Console" >}}

## Adding ACL

By default, your cluster is opened but you can fix that by opening "Access Control" menu.
Found proposes a default configuration which generates two users and restrict some access.

```yaml
# Deny everyone by default, as authentication is required.
# Deny is the default also if no "default" is specified,
# so it's only necessary to specify it if you want the
# default to be "allow".
default: deny

auth:
  users:
    searchonly: searchonlypassword
    readwrite: readwritepassword

rules:
  - paths:
      # Match all search requests.
      - '/_search|/([^_/]+/_search)|/[^_/]+/[^_/]+/_search'
    conditions:
      - basic_auth:
          users: [searchonly]
    action: allow

  # Also, allow any GET-request.
  - paths: ['.*']
    conditions:
      - basic_auth:
          users:
            - searchonly
      - method:
          verbs: [GET]
    action: allow

  # Allow everything for the readwrite-user
  - paths: ['.*']
    conditions:
      - basic_auth:
          users:
            - readwrite
# Uncomment the following if you want to require SSL.
#      - ssl:
#          require: true
    action: allow
```

## Create your javascript application

```html
<!DOCTYPE html>
<html>
  <head>
    <script src="https://cdn.rawgit.com/elastic/bower-elasticsearch-js/12ec0b8ee6d776e077b160e6dd6fc2e1b5818a86/elasticsearch.min.js"></script>
  </head>
  <body>
    <script>
      var login = "readwrite";
      var password = "readwritepassword";
      var hostname = "youclusteraddress.foundcluster.com";
      
      var client = new elasticsearch.Client({
        hosts: [
          {
            host: hostname,
            auth: login + ':' + password
          } 
        ]
      });
      
      client.cluster.health().then(done, done);
      
      function done(resp) {
        console.log(resp);
      }
    </script>
  </body>
</html>
```

If you run it, you will get something like:

```txt
elasticsearch.min.js:18 OPTIONS http://youclusteraddress.foundcluster.com:9200/_cluster/health 401 (Unauthorized)26.d.request @ elasticsearch.min.js:18c @ elasticsearch.min.js:1842.j.applyArgs @ elasticsearch.min.js:18k @ elasticsearch.min.js:11(anonymous function) @ elasticsearch.min.js:11
bblfr_elasticsearch.dev/:1 XMLHttpRequest cannot load http://youclusteraddress.foundcluster.com:9200/_cluster/health. Invalid HTTP status code 401
elasticsearch.min.js:18 ERROR: 2015-05-19T14:47:01Z
  Error: Request error, retrying -- Request failed to complete.
      at d.29.d.error (http://bblfr_elasticsearch.dev/lib/elasticsearch.min.js:18:15537)
      at d (http://bblfr_elasticsearch.dev/lib/elasticsearch.min.js:18:22917)
      at XMLHttpRequest.26.d.request.d.onreadystatechange (http://bblfr_elasticsearch.dev/lib/elasticsearch.min.js:18:9781)
```

## Modify ACL

The javascript client needs to discuss with found using `OPTIONS` verb. So you basically need to add:

```yaml
  - paths:
      - '.*'
    conditions:
      - method:
          verbs: [OPTIONS]
    action: allow
```

Running the same code will now work as expected!

```js
{
  cluster_name: "youclusteraddress", 
  status: "green", 
  timed_out: false, 
  number_of_nodes: 1, 
  number_of_data_nodes: 1
  // ...
}
```

## Using ACL for aliases

Note that for the project, I created one index named `bbl_1` and one alias on top of it `bbl`.
So I opened read access to anonymous users on this alias and add a secured one when it comes to write operations.
`OPTIONS` in that case is applied only to the `bbl` alias. I came up with this config:

```yaml
default: deny

auth:
  users:
    readwrite: readwritepassword

rules:
  - paths:
      - '/bbl/.*'
    conditions:
      - method:
          verbs: [OPTIONS]
    action: allow

  - paths:
      - '/bbl/_search'
    conditions:
      - method:
          verbs: [GET, POST]
    action: allow

  - paths: ['/bbl/.*']
    conditions:
      - method:
          verbs: [GET]
    action: allow

  - paths: ['/bbl/.*']
    conditions:
      - method:
          verbs: [PUT, DELETE]
      - basic_auth:
          users: [readwrite]
    action: allow
```

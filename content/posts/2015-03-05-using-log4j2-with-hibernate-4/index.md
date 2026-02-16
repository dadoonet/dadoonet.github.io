---
title: "Using Log4J2 with Hibernate 4"
description: "How to use Log4J2 with Hibernate 4"
author: David Pilato
avatar: /about/david_pilato.avif
tags:
  - hibernate
  - maven
categories:
  - tips
date: 2015-03-05 22:00:00 +0200
nolastmod: true
draft: false
aliases:
  - /blog/2015/03/05/using-log4j2-with-hibernate-4/
  - /blog/2015-03-05-using-log4j2-with-hibernate-4/
---

I was trying to use Hibernate 4.3.8.Final with Log4J2 and I spent some hours to find why Hibernate was not using Log4J2 though it was declared in my pom.xml file.

Actually, I hit issue [JBLOGGING-107](https://issues.jboss.org/browse/JBLOGGING-107).

The workaround is simply to add a more recent jboss-logging dependency than the one shipped by default with Hibernate 4.3.8.Final.

```xml
<dependency>
    <groupId>org.jboss.logging</groupId>
    <artifactId>jboss-logging</artifactId>
    <version>3.2.1.Final</version>
</dependency>
```

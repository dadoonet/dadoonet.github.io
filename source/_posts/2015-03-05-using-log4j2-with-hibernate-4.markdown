---
layout: post
title: "Using Log4J2 with Hibernate 4"
date: 2015-03-05 22:00:00 +0200
comments: true
categories: 
- Hibernate
- Maven
---

I was trying to use Hibernate 4.3.8.Final with Log4J2 and I spent some hours to find why Hibernate was not using Log4J2 though it was declared in my pom.xml file.

Actually, I hit issue [JBLOGGING-107](https://issues.jboss.org/browse/JBLOGGING-107).

The workaround is simply to add a more recent jboss-logging dependency than the one shipped by default with Hibernate 4.3.8.Final.

```xml pom.xml file
<dependency>
    <groupId>org.jboss.logging</groupId>
    <artifactId>jboss-logging</artifactId>
    <version>3.2.1.Final</version>
</dependency>
```

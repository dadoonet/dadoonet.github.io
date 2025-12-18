---
title: "Visualize Your Threats with Elastic SIEM"
conference: 
  name: "stackconf"
  city: "Berlin"
  country: "Germany"
  country_code: "de"
author: David Pilato
avatar: /about/david_pilato.png
tags:
  - elasticsearch
  - conference
  - java
  - cloud
categories:
  - speaker
series:
  - conferences
date: 2020-06-16
nolastmod: true
draft: false
cover: cover.png

# Speaker specific fields
youtube: "BGVPV8CcLEg"
notist: "dadoonet/oBt281"

x:
  - user: "NetwaysEvents"
    id: "1229687755699040256"
  - user: "NetwaysEvents"
    id: "1226084515854024704"
  - user: "dadoonet"
    id: "1272806273826856960"

links:
  - title: "AuditD Rules"
    url: "https://github.com/linux-audit/audit-userspace/tree/master/rules"
    description: "Templates for common auditD rules"
  - title: "Demo repository"
    url: "https://github.com/xeraa/auditbeat-in-action"

aliases:
  - /oBt281
---
Knowing what is going on in your environment is an important part of staying on top of security issues. But how do you capture relevant metrics and visualize them? One widely-used tool for that job is the Elastic Stack, formerly known as the ELK stack. This talk shows how to ingest relevant metrics from your network and hosts as well as how to easily visualize them to find suspicious patterns and behaviors. We will be also using the latest tool named SIEM.

We will use real-world honeypot data for this example:

* The first step is to parse and enrich the data, so we can identify actual attacks, their origin, and more.
* Then we store and explore the data to find meaningful insights.
* Which leads us to visualize specific attributes — like the location of an attacker or patterns in the attacks.
* Building upon this we can combine visualizations into dashboards, giving a broader overview.
* Finally we will use the Kibana SIEM app to see how everything is now getting easy to track for attacks.

Everything done live.

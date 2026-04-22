---
title: "Randomized testing: Gotta Catch 'Em All"
conference: 
  name: "Dev Bcn"
  city: "Barcelona"
  country: "Spain"
  country_code: "es"
  latitude: "41.3718342"
  longitude: "2.1808756"
  url: "https://www.devbcn.com/2026/talks/1152879"
author: David Pilato
avatar: /about/david_pilato.avif
talk: Randomized Testing
date: '2026-06-16'
talk-lang: en
nolastmod: true
draft: false
#pdf: "2026/2026-06-16 - Dev Bcn - Randomized Testing.pdf"

# Speaker specific fields
#youtube: "3AqqS9q27tY"      # ID de la vidéo YouTube (ex: dQw4w9WgXcQ)
links:
  - title: "Demo project"
    url: "https://github.com/dadoonet/randomizedtesting-demo"
    description: "The source code for the demo project"
  - title: "RandomizedTesting framework"
    url: "https://github.com/randomizedtesting/randomizedtesting-jupiter"
    description: "The framework provided by Carrot Search"
  - title: "Ariane 5 launch video"
    url: "https://www.esa.int/ESA_Multimedia/Videos/1996/06/Ariane_501_recording_launch_pad_before_and_at_launch"
    description: "The Ariane 5 first launch on June 4th, 1996"
  - title: "FSCrawler project"
    url: "https://github.com/dadoonet/fscrawler/"
    description: "FSCrawler is running tests with RandomizedTesting framework"
  - title: "A weird CI error in FSCrawler"
    url: "https://github.com/dadoonet/fscrawler/actions/runs/14357866984/job/40251514398#step:4:296"
    description: "The error I could not reproduce locally"
  - title: "Gestalt issue 242"
    url: "https://github.com/gestalt-config/gestalt/issues/242"
    description: "The issue I opened after my findings"

#x:
#  - user: "dadoonet"
#    id: "2018274464362906110"

aliases:
  - /devbcn26
---

> Chance does things well.

If we apply this idea to unit tests or integration tests, we can make our tests much more unpredictable — and as a result, uncover issues that our minds would never have dared to imagine! For example, I recently discovered a [bug](https://github.com/gestalt-config/gestalt/issues/242) in a configuration management library that occurs when the `Locale` is set to `AZ`. 🤦🏼‍♂️

Another, even simpler, example:

```java
int input = generateInteger(Integer.MIN_VALUE, Integer.MAX_VALUE);
int output = Math.abs(input);
```

This can generate `-2147483648`... which is quite unexpected for an absolute value! 😉  
Randomized tests can uncover these twisted edge cases... That's what the Elasticsearch team has been doing for years using the [RandomizedTesting](https://github.com/randomizedtesting/randomizedtesting-jupiter) framework to test all their Java code.

Add to that real integration tests using [TestContainers](https://java.testcontainers.org/modules/elasticsearch/), and you'll have a complete approach to tests that *regularly fail*!

After this talk, you'll never look at the `random()` function the same way again — and you'll discover how (bad) luck can actually help you! 🍀

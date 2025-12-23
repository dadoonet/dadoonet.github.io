---
title: "Randomized testing: Gotta Catch ‘Em All"
conference: 
  name: "Elastic EAH (private event)"
  city: "Las Vegas"
  country: "USA"
  country_code: "us"
  latitude: "36.169941"
  longitude: "-115.139830"
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
date: 2025-05-14
nolastmod: true
draft: false
pdf: "2025/2025-05-14-elastic-eah-private-event.pdf"


# Speaker specific fields
#youtube: ""
notist: "dadoonet/G8rCxd"

aliases:
  - /G8rCxd
---
> Chance does things well.

If we apply this idea to unit tests or integration tests, we can make our tests much more unpredictable — and as a result, uncover issues that our minds would never have dared to imagine! For example, I recently discovered a [bug](https://github.com/gestalt-config/gestalt/issues/242) in a configuration management library that occurs when the `Locale` is set to `AZ`. 🤦🏼‍♂️

Another, even simpler, example:

```
int input = generateInteger(Integer.MIN_VALUE, Integer.MAX_VALUE);
int output = Math.abs(input);
```

This can generate `-2147483648`… which is quite unexpected for an absolute value! 😉

Randomized tests can uncover these twisted edge cases… That’s what the Elasticsearch team has been doing for years using the [RandomizedTesting](https://labs.carrotsearch.com/randomizedtesting.html) framework to test all their Java code.

Add to that real integration tests using [TestContainers](https://java.testcontainers.org/modules/elasticsearch/), and you’ll have a complete approach to tests that *regularly fail*!

After this talk, you’ll never look at the `random()` function the same way again — and you’ll discover how (bad) luck can actually help you! 🍀

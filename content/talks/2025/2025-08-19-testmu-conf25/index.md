---
title: "Randomized testing: Gotta Catch ‘Em All"
conference: 
  name: "Testμ Conf’25"
  url: "https://www.lambdatest.com/testmuconf-2025/david-pilato"
  country: "Online"
  country_code: "Online"
author: David Pilato
avatar: /about/david_pilato.avif
talk: Randomized Testing
date: 2025-08-19
talk-lang: en
nolastmod: true
draft: false
pdf: "2025/2025-08-19-testmu-conf25.pdf"


# Speaker specific fields
youtube: "5Pzq9aRNi3o"
notist: "dadoonet/6DyIt6"
links:
  - title: "TestMu Conference 2025"
    url: "https://www.lambdatest.com/testmuconf-2025/david-pilato"
    description: "The conference website"
  - title: "Demo project"
    url: "https://github.com/dadoonet/randomizedtesting-demo"
    description: "The source code for the demo project"
  - title: "RandomizedTesting framework"
    url: "https://github.com/randomizedtesting/randomizedtesting"
    description: "The framework provided by Carrot Search"
  - title: "A weird CI error in FSCrawler"
    url: "https://github.com/dadoonet/fscrawler/actions/runs/14357866984/job/40251514398#step:4:296"
    description: "The error I could not reproduce locally"
  - title: "Gestalt issue 242"
    url: "https://github.com/gestalt-config/gestalt/issues/242"
    description: "The issue I opened after my findings"

aliases:
  - /6DyIt6
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

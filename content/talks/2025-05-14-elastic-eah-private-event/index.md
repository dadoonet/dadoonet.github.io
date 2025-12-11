---
title: "Randomized testing: Gotta Catch ‘Em All"
description: ""
conference: 
  name: "Elastic EAH (private event)"
  url: ""
  city: "Las Vegas"
  country: "United States"
  country_code: "us"
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
cover: cover.jpg

# Speaker specific fields
#youtube: ""
notist: "dadoonet/G8rCxd"
---

Chance does things well.

If we apply this idea to unit tests or integration tests, we can make our tests much more unpredictable — and as a result, uncover issues that our minds would never have dared to imagine! For example, I recently discovered a bug in a configuration management library that occurs when the Locale is set to AZ. 🤦🏼‍♂️
Another, even simpler, example:
int input = generateInteger(Integer.MIN_VALUE, Integer.MAX_VALUE);
int output = Math.abs(input);

This can generate -2147483648… which is quite unexpected for an absolute value! 😉
Randomized tests can uncover these twisted edge cases… That’s what the Elasticsearch team has been doing for years using the RandomizedTesting framework to test all their Java code.
Add to that real integration tests using TestContainers, and you’ll have a complete approach to tests that regularly fail!
After this talk, you’ll never look at the random() function the same way again — and you’ll discover how (bad) luck can actually help you! 🍀

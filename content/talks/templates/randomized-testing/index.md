---
title: "Randomized testing: Gotta Catch 'Em All"
layout: "template"
talk: Randomized Testing
date: 2026-01-30
nolastmod: true
draft: false

versions:
  - label: "EN"
    flag: "gb"
    title: "Randomized testing: Gotta Catch 'Em All"
    abstract: |
      > Chance does things well.
      
      If we apply this idea to unit tests or integration tests, we can make our tests much more unpredictable — and as a result, uncover issues that our minds would never have dared to imagine! For example, I recently discovered a [bug](https://github.com/gestalt-config/gestalt/issues/242) in a configuration management library that occurs when the `Locale` is set to `AZ`. 🤦🏼‍♂️
      
      Another, even simpler, example:
      
      ```java
      int input = generateInteger(Integer.MIN_VALUE, Integer.MAX_VALUE);
      int output = Math.abs(input);
      ```
      
      This can generate `-2147483648`... which is quite unexpected for an absolute value! 😉  
      Randomized tests can uncover these twisted edge cases... That's what the Elasticsearch team has been doing for years using the [RandomizedTesting](https://labs.carrotsearch.com/randomizedtesting.html) framework to test all their Java code.
      
      Add to that real integration tests using [TestContainers](https://java.testcontainers.org/modules/elasticsearch/), and you'll have a complete approach to tests that *regularly fail*!
      
      After this talk, you'll never look at the `random()` function the same way again — and you'll discover how (bad) luck can actually help you! 🍀
  - label: "FR"
    flag: "fr"
    title: "Le hasard fait bien les tests"
    abstract: |
      > Le hasard fait bien les choses.
      
      Si on applique cette idée aux tests unitaires ou aux tests d'intégration, on peut rendre nos tests beaucoup plus imprévisibles et du coup trouver des problèmes que notre esprit n'aurait jamais osé imaginer ! Par exemple, récemment, j'ai découvert dans une bibliothèque de gestion de configuration, [un bug](https://github.com/gestalt-config/gestalt/issues/242) qui se produit lorsque la `Locale` est configuré en `AZ`. 🤦🏼‍♂️
      
      Un autre exemple encore plus simple :
      
      ```java
      int input = generateInteger(Integer.MIN_VALUE, Integer.MAX_VALUE);
      int output = Math.abs(input);
      ```
      
      Peut générer `-2147483648`... Ce qui est assez inattendu pour une valeur absolue ! 😉
      Les tests aléatoires peuvent découvrir ces cas tordus... C'est ce que l'équipe elasticsearch a mis en place depuis plusieurs années à l'aide du framework [RandomizedTesting](https://labs.carrotsearch.com/randomizedtesting.html) pour tester tout le code Java.
      
      Ajoutez à ça de vrais tests d'intégration à l'aide de [TestContainers](https://java.testcontainers.org/modules/elasticsearch/) et vous aurez une approche complète pour des tests qui échouent régulièrement ! 
      
      Après cette conférence, vous ne verrez plus jamais la fonction `random()` comme avant  et découvrirez comment la (mal)chance peut vous aider ! 🍀

links:
  - title: "Demo project"
    url: "https://github.com/dadoonet/randomizedtesting-demo"
    description: "The source code for the demo project"
  - title: "RandomizedTesting framework"
    url: "http://labs.carrotsearch.com/randomizedtesting-concept.html"
    description: "The framework provided by Carrot Search"
  - title: "FSCrawler project"
    url: "https://github.com/dadoonet/fscrawler/"
    description: "FSCrawler is running tests with RandomizedTesting framework"
---

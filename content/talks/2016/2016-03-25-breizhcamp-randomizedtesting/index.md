---
title: "Le hasard fait bien les tests"
conference: 
  name: "Breizhcamp"
  city: "Rennes"
  country: "France"
  country_code: "fr"
  latitude: "48.1169497"
  longitude: "-1.6413873"
author: David Pilato
avatar: /about/david_pilato.png
talk: Randomized Testing
date: 2016-03-24
nolastmod: true
draft: false

pdf: "2016/2016-03-25 - Le_Hasard_Fait_Bien_Les_Tests.pdf"
attendees: 100
---

> Souvent, "le hasard fait bien les choses".

Si on applique cette idée aux tests unitaires ou aux tests d'intégration, on peut rendre nos tests beaucoup plus imprévisibles et du coup trouver des problèmes que notre esprit n'aurait jamais osé imaginer !

Venez découvrir comment l'équipe elasticsearch a mis en place une stratégie de tests aléatoires en Java à l'aide de [RandomizedTesting](https://labs.carrotsearch.com/randomizedtesting.html) et comment la (mal)chance peut vous aider.

Par exemple:

```java
int input = generateInteger(
            Integer.MIN_VALUE, 
            Integer.MAX_VALUE);
int output = Math.abs(input);
```

Peut générer `-2147483648`... Ce qui est assez inattendu pour une valeur absolue ! :)

Les tests aléatoires peuvent découvrir ces cas tordus...

Ils nécessitent évidemment de tester sans arrêt le code et doivent s'accompagner d'outils d'intégration continue, tel que Jenkins.

Après cette conférence, vous ne verrez plus jamais la fonction `random()` comme avant !

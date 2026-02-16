---
title: "Le hasard fait bien les tests"
conference: 
  name: "DevFest Toulouse"
  url: "https://devfesttoulouse.fr/"
  city: "Toulouse"
  country: "France"
  country_code: "fr"
  latitude: "43.604652"
  longitude: "1.444209"
author: David Pilato
avatar: /about/david_pilato.avif
talk: Randomized Testing
date: 2025-11-13
talk-lang: fr
nolastmod: true
draft: false
pdf: "2025/2025-11-13-devfest-toulouse-2025.pdf"


# Speaker specific fields
youtube: "bJqIfKFYDpE"
notist: "dadoonet/qC8sMm"
links:
  - title: "Demo project"
    url: "https://github.com/dadoonet/randomizedtesting-demo"
    description: "The source code for the demo project"

  - title: "RandomizedTesting framework"
    url: "https://labs.carrotsearch.com/randomizedtesting-concept.html"
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


aliases:
  - /qC8sMm
  - /devfest-toulouse-2025
---
> Le hasard fait bien les choses.

Si on applique cette idée aux tests unitaires ou aux tests d’intégration, on peut rendre nos tests beaucoup plus imprévisibles et du coup trouver des problèmes que notre esprit n’aurait jamais osé imaginer ! Par exemple, récemment, j’ai découvert dans une bibliothèque de gestion de configuration, [un bug](https://github.com/gestalt-config/gestalt/issues/242) qui se produit lorsque la `Locale` est configuré en `AZ`. 🤦🏼‍♂️

Un autre exemple encore plus simple :

```java
int input = generateInteger(Integer.MIN_VALUE, Integer.MAX_VALUE);
int output = Math.abs(input);
```

Peut générer `-2147483648`… Ce qui est assez inattendu pour une valeur absolue ! 😉
Les tests aléatoires peuvent découvrir ces cas tordus… C’est ce que l’équipe elasticsearch a mis en place depuis plusieurs années à l’aide du framework [RandomizedTesting](https://labs.carrotsearch.com/randomizedtesting.html) pour tester tout le code Java.

Après cette conférence, vous ne verrez plus jamais la fonction `random()` comme avant  et découvrirez comment la (mal)chance peut vous aider ! 🍀

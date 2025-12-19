---

title: "Le hasard fait bien les tests"
description: ""
conference: 
  name: "DevFest Toulouse"
  url: "https://devfest.gdgtoulouse.com/"
  city: "Toulouse"
  country: "France"
  country_code: "fr"
  latitude: "43.604652"
  longitude: "1.444209"
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
date: 2025-11-13
nolastmod: true
draft: false
cover: cover.jpg

# Speaker specific fields
#youtube: "sxWTPruEWRU"
notist: "dadoonet/qC8sMm"
aliases:
  - /qC8sMm

---

> Le hasard fait bien les choses.

Si on applique cette idée aux tests unitaires ou aux tests d’intégration, on peut rendre nos tests beaucoup plus imprévisibles et du coup trouver des problèmes que notre esprit n’aurait jamais osé imaginer ! Par exemple, récemment, j’ai découvert dans une bibliothèque de gestion de configuration, [un bug](https://github.com/gestalt-config/gestalt/issues/242) qui se produit lorsque la `Locale` est configuré en `AZ`. 🤦🏼‍♂️

Un autre exemple encore plus simple :

```
int input = generateInteger(Integer.MIN_VALUE, Integer.MAX_VALUE);
int output = Math.abs(input);
```

Peut générer `-2147483648`… Ce qui est assez inattendu pour une valeur absolue ! 😉
Les tests aléatoires peuvent découvrir ces cas tordus… C’est ce que l’équipe elasticsearch a mis en place depuis plusieurs années à l’aide du framework [RandomizedTesting](https://labs.carrotsearch.com/randomizedtesting.html) pour tester tout le code Java.

Après cette conférence, vous ne verrez plus jamais la fonction `random()` comme avant  et découvrirez comment la (mal)chance peut vous aider ! 🍀

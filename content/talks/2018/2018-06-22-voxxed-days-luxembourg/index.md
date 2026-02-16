---
title: "Les Vendredis noirs : même pas peur !"
conference: 
  name: "Voxxed Days Luxembourg"
  city: "Luxembourg"
  country: "Luxembourg"
  country_code: "lu"
  latitude: "49.611621"
  longitude: "6.131935"
  url: "https://voxxeddays.com/luxembourg/"
author: David Pilato
avatar: /about/david_pilato.webp
# talk: conferences
date: 2018-06-22
talk-lang: fr
nolastmod: true
draft: false
pdf: "2018/2018-06-22-voxxed-days-luxembourg.pdf"


# Speaker specific fields
youtube: "xNy4kLm43UA"
notist: "dadoonet/NscrTQ"
attendees: 140

x:
  - user: "voxxed_lu"
    id: "1010075039000072192"
  - user: "dadoonet"
    id: "1010108423697059841"
  - user: "dadoonet"
    id: "1011848627243929600"
  - user: "dadoonet"
    id: "1009741910154543105"
  - user: "voxxed_lu"
    id: "1010050188323540992"

links:
  - title: "Blog: Le Touilleur Express - Voxxed Days Luxembourg 2018"
    url: "https://touilleur-express.fr/2018/06/25/voxxed-luxembourg-2018/"
    description: "Résumé de la conférence par Nicolas Martignole"

aliases:
  - /NscrTQ
---
Surveiller une application complexe n’est pas une tâche aisée, mais avec les bons outils, ce n’est pas si sorcier. Néanmoins, des périodes fortes telles que les opérations de type “Black Friday” (Vendredi noir) ou période de Noël peuvent pousser votre application aux limites de ce qu’elle peut supporter, ou pire, la faire crasher. Parce que le système est fortement sollicité, il génère encore davantage de logs qui peuvent également mettre à mal votre système de supervision.

Dans cette session, j’aborderai les bonnes pratiques d’utilisation de la suite Elastic pour centraliser et monitorer vos logs. Je partagerai également avec vous quelques trucs et astuces pour vous aider à passer sans souci vos Vendredis noirs !

Nous verrons :

* Les architectures de monitoring
* Trouver la taille optimale pour l’API _bulk
* Distribuer la charge
* Taille des index et des shards
* Optimiser les E/S disque

Vous ressortirez de la session avec : des bonnes pratiques pour bâtir son système de monitoring avec la suite Elastic, le tuning avancé pour optimiser les performances d’ingestion et de recherche.

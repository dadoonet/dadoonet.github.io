---
title: "La potion magique pour faire avancer ta carrière"
description: "Voici la transcription d'une présentation que j'ai eu le plaisir à donner lors du Camping des speakers 2022, dont il s'agissait de la première édition."
author: David Pilato
avatar: /about/david_pilato.png
tags:
  - career
  - culture
categories:
  - culture
series:
  - career at elastic
date: 2022-06-10 11:00:00 +01:00
nolastmod: true
cover: featured.jpeg
draft: false
aliases:
  - /blog/2022-06-10-la-potion-magique-pour-faire-avancer-ta-carriere/
---

Voici la transcription d'une présentation que j'ai eu le plaisir à donner lors du [Camping des speakers 2022](https://camping-speakers.fr/), dont il s'agissait de la première édition.

## La potion magique pour faire progresser ta carrière

10h15 - 15 minutes - Autour du Feu

> La recette de la potion magique ne se transmet qu'aux seuls druides, normalement. Mais exceptionnellement, le conseil des druides de la forêt des Carnutes m'a autorisé à vous révéler quelques uns des ingrédients qui constituent ce breuvage.
> Il est même possible que je vous indique l'ingrédient secret !

## Début de carrière

J'ai commencé par une carrière très "classique" dans le monde de l'entreprise, stack technique avec un mélange de produits commerciaux et open-source :

* Base Oracle
* BEA Weblogic
* Java J2EE (EJB, JMS...)
* Eclipse comme IDE

Mais aussi des nouveaux projets lancés sur :

* PostgreSQL
* JBoss
* Spring
* JSP / HTML / JS / CSS

## Douane

En 2005, j'entre à la Douane. Je vais gérer des équipes très diverses au niveau du niveau technique. Certains agents vous apprenent beaucoup. Pour d'autres, vous devez les faire monter en compétence, chacun à son rythme et vous adapter à cette diversité.

Nous consommons beaucoup d'open-source au final mais en temps qu'utilisateur seulement. Cela vient d'ailleurs du fait qu'il y a souvent une confusion entre Open-source et gratuit. Il peut y avoir du "non open-source au sens OSI du terme" et pourtant gratuit et libre d'usage avec éventuellement quelques restrictions ou obligations.

## Paris JUG

Fin 2010, un de mes collègues me parle du [Paris Java User Group (Paris JUG)](https://www.parisjug.org/) et m'y entraine. J'y découvre des passionnés qui partagent **gratuitement** leurs savoirs et leurs connaissances.

{{< figure src="parisjug.png" caption="Paris JUG" >}}

Au début, j'ai mal de crâne car je n'y comprends pas grand chose. Pas à cause d'un abus de Chouchen.
On me parle de GIT ? Mais je fais du CVS moi !!! Comment peut fonctionner ce truc, sans serveur centralisé ?

## Projet Douane avec Hibernate Search

Début 2011, je cherche à voir comment stocker mes index dans une base de données plutôt que sur le disque local. Car j'ai deux serveurs JBoss en équilibrage de charge. Et chacun ne voit que la moitié des données quand je cherche.

J'ai bien vu qu'Emmanuel Bernard dit dans un post que c'est pas bien... Mais je suis têtu. Je veux tester... Je cherche un bout de code... Merci l'open-source, je tombe sur la [classe JdbcDirectory](http://www.compass-project.org/docs/2.0.1/api/org/apache/lucene/store/jdbc/JdbcDirectory.html) du projet Compass. J'essaye d'utiliser cette classe, de l'adapter. Je n'y arrive pas.

## Elasticsearch

Je me souviens que sur la page d'accueil du projet Compass, il y a une référence au "futur" de Compass : Elasticsearch...

{{< figure src="es1.png" caption="Le futur de Compass et Elasticsearch" >}}

Je clique... **Le clic le plus disruptif de ma vie** !

Par Toutatis !

Mon monde s'écroule... Je télécharge. Je lance. Je teste. C'est juste parfait.
Je ne dors pas pendant une semaine... Je me demande :

> Comment un type tout seul a créé ce truc ?

En réalité, il n'a pas tout créé. Je découvre ainsi la stack technique d'Elasticsearch :

* Découverte de HTTP/REST
* Découverte de [Jackson](https://github.com/FasterXML/jackson) / JSON: je faisais au mieux du XML
* Découverte de [Lucene](https://lucene.apache.org/)

## La communauté d'entraide

Je découvre rapidement les [forums de discussion](https://discuss.elastic.co/). Quelques noms reviennent souvent. On s'en souvient facilement parce qu'ils nous aident.

Pour le moment, je consomme le forum... Je ne produis rien.

## Les plugins Elasticsearch

Elasticsearch met à disposition un système de plugins. Il devient donc facile de créer quelque chose sans connaitre tout le détail. Elasticsearch utilise Gradle (déjà en 2011), alors que je suis encore sur Maven et que le reste de la Douane est sur Ant.

Je créé le plugin [RSS River](http://david.pilato.fr/rssriver/), qui indexe un contenu RSS régulièrement.

{{< figure src="rss-river.png" caption="RSS River" >}}

J'en parle en privé avec [Shay Banon](https://twitter.com/kimchy), l'auteur d'Elasticsearch, qui me dit :

> Open Source le !

J'ai honte. Le code n'est pas parfait. Il manque des tests, de la documentation, de la javadoc...

Il me dit :

> On s'en fout. Tu publies ton effort et tu verras naturellement que la communauté va t'aider à l'améliorer.

Il s'agit du **MEILLEUR CONSEIL DE MA VIE DE DEV**.

Alors, mon premier projet, même incomplet, est [publié sur Github](https://github.com/dadoonet/rssriver/commit/7eb5b2a0fe0aa75564d2094bbee70e35c1f441af). Je l'annonce sur Twitter, dans les forums Elasticsearch. Je gagne donc aussi en visibilité. J'apprends que [Tanguy](https://viadeo.journaldunet.com/p/tanguy-leroux-1021827) allait publier aussi son code 1 semaine plus tard. Même projet.

Je suis encouragé par le succès et l'adhésion, et les retours bienveillants Sentir que votre code, même imparfait, est finalement aimé...

Je créé aussi dans la foulée [FS River](https://github.com/dadoonet/fscrawler) puis [Dropbox River](https://github.com/dadoonet/dropbox)...

## La communauté française

Il n'y a pas de communauté française. Je propose donc à Shay d'en créer une avec un compte [Twitter ElasticsearchFR](https://twitter.com/elasticfr) et [un forum en français](https://groups.google.com/g/elasticsearch-fr).

Le succès est assez rapide.

Je communique également sur mon blog, en français, [sur mes découvertes Elasticsearch]({{< ref "2011-03-09-la-recherche-elastique" >}}). Je partage donc de l'information en produisant du contenu utile, sans arrière pensée. Juste un don vers la communauté.

## Devoxx France 2012

Je vais toujours au Paris JUG. J'y rencontre [Emmanuel Bernard](https://twitter.com/emmanuelbernard) et je lui propose de partager mes 9 mois de découverte d'Elasticsearch. Après tout, le Paris JUG m'a tellement appris pendant tout ce temps. Et personne ne parle d'Elasticsearch en France, à part [un article de Nicolas Martignole](https://www.touilleur-express.fr/2011/04/12/elasticsearch-interview-with-shay-banon/), il n'y a rien.

Au final, ça ne se fera pas. Manque de temps. Mais un soir le Paris JUG annonce [Devoxx France](https://www.devoxx.fr/), la première édition...

Je souffre toujours de mon complexe de l'imposteur : tous ces gens sont si brillants. Que pourrais-je donc apporter à ces personnes ?

Mais je me lance. J'envoie un sujet unique au CFP de Devoxx France. Je ne suis pas retenu, ce qui me déçoit mais également me soulage. Après tout, c'était un peu audacieux... J'apprends que Shay lui-même viendra présenter Elasticsearch sur scène. Et donc, je comprends mieux pourquoi je n'ai pas été retenu. Après tout, le papa du projet est là. Et je suis ravi de savoir que je vais le rencontrer à nouveau. Je l'avais déjà vu 6 mois plus tôt lors de [What's Next Paris](https://blog.zenika.com/2010/12/22/whats-next/).

Et finalement, 1 mois avant l'évènement, j'apprends que Shay ne pourra pas venir. Gabriel et Nicolas retiennent alors mon sujet. Après tout, c'est le même contenu, en français, par un agent de la Douane. Ca sonne plutôt bien.

Mais la pression remonte d'un seul coup... Je me lance dans une préparation intensive, avec des répétitions en interne au CID (Centre Informatique Douanier) :

* Juste avec [Malloum](https://twitter.com/TheMalloum), mon collègue le plus proche, qui va m'encourager tout au long de ce processus.
* Juste avec une collègue qui ne connait pas trop les nouvelles technologies mais a des capacités énormes d'apprentissage. Cette répétition est une catastrophe, mais positive. Ses retours sont extrèmement utiles et me font réécrire le talk.
* Puis répétition générale avec 30+ collègues du centre pour ce que nous appellerons désormais le "CID JUG" : partage de connaissance régulier entre les équipes.
* Revue très constructive et bienveillante des slides par Gabriel de Devoxx France entrainant à nouveau une réécriture quelques jours avant le jour J.

Ce grand jour est arrivé. 200 personnes. Moi qui n'ait jamais parlé en public, plutôt garçon réservé, avec ce sentiment d'être un imposteur total.

{{< youtube sxWTPruEWRU >}}

Les retours sont excellents ! Et comme je faisais une démo live sur Twitter, même Shay et les autres membres de la communauté ont vu "le bruit" que nous faisions avec le hashtag [#Elasticsearch](https://twitter.com/search?q=until%3A2012-04-22%20since%3A2012-04-20%20%23elasticsearch&src=typed_query&f=top). A nouveau, entrainant une reconnaissance des membres de la communauté...

{{< figure src="devoxx-tweets.jpeg" caption="Tweets pendant Devoxx France" >}}

## Forum Elasticsearch

J'y participe beaucoup. Je donne des réponses, même fausses. Ce qui est intéressant, c'est que d'autres membres de la communauté corrigent alors vos erreurs. Et vous apprenez beaucoup.

Donner, c'est donc recevoir.

Pendant l'été, les "gros" contributeurs du forum Elasticsearch sont en vacances. Ils ne répondent plus aux questions. Alors je me mets en quête de répondre aux utilisateurs, à tous les utilisateurs.

Je deviens assez rapidement le plus grand contributeur du forum et je me fais remarquer et commence à recevoir des propositions d'entreprises.

## Elasticsearch devient une entreprise

Evidemment, je pense à rejoindre Elastic. Lorsque je passe mes entretiens d'embauche, je n'ai quasiment aucune preuve à donner. Les faits parlent d'eux-mêmes. Il suffit de regarder le forum, Twitter, mon GitHub. Il ne reste plus qu'à vérifier que nous sommes tous dans le même état d'esprit pour développer cette startup.

Vous pouvez lire aussi [Il était une fois : un conte de fées élastique !]({{< ref "2013-01-15-il-etait-une-fois-un-conte-de-fees-elastique" >}}) qui reprend cette histoire.

## Dynamiser sa carrière

En participant au monde open-source, non pas seulement en tant que consommateur, mais en tant qu'acteur, même avec des contributions qui ne sont pas nécessairement du code, vous pouvez complètement dynamiser votre carrière.
D'abord en vous rendant visible. C'est une sorte de marketing sur vous même. Pas besoin d'en faire des caisses. Restez humbles et faites !

Les auteurs de projets OSS aiment tous les contributeurs. Même si c'est pour fixer un README. C'est top.

Mon projet FSRiver est devenu FSCrawler. Il est devenu très populaire. Dans les forums ou les issues, la chose qui me motive le plus, ce sont les remerciements des utilisateurs. Je sais que le code n'est pas top. Mais il rend service.

Il me permet également d'apprendre via les contributions des membres de la communauté. Et donc de rester en éveil. Par exemple, je n'y connaissais pas grand chose à Docker et un membre de la communauté a proposé son implémentation. Et j'ai appris en faisant la revue du code.

Quelque fois, il faut énormément de patience et de bienveillance avec les utilisateurs. Même si cela vous semble difficile, que vous avez envie d'envoyer balader la personne ou de laisser tomber, continuez à aider !

N'oubliez pas que les autres lisent aussi vos communications.

Depuis mes débuts chez Elasticsearch, je fais le métier d'évangéliste, au début à 50% et depuis 5 ans en full time.

## L'ingrédient secret de la potion magique

Savez-vous quel est l'ingrédient secret de ma potion magique ? Pour quelle raison je fais ce métier ?

Pour l'**amour**...

{{< figure src="heart-stickers.jpeg" caption="All you need is love..." >}}

L'amour que vous ressentez en tant que membre de la communauté qui aide les autres.

Anecdote : j'étais à San Francisco pour la première conférence ElasticON. Un membre de la communauté m'a cherché dans les 1200 participants, juste pour me remercier en personne de l'avoir tant aidé dans les forums.

Ou encore à Bangalore en Inde, à la fin d'un meetup, des membres du forum qui viennent à nouveau vous dire merci pour votre aide et votre investissement. Ces émotions hyper positives sont incroyables à ressentir.

L'amour que vous recevez lorsque les utilisateurs vous disent qu'ils aiment votre projet Open Source, et quelque part, même si vous êtes un imposteur, les lignes de code que vous avez écrites.

L'amour des conférenciers que je reçois au stand Elastic, lorsque j'en tiens un.

L'amour de nos produits, de tout ce que nous avons mis gratuitement à disposition de la communauté. En tant qu'évangéliste, en première ligne, vous recevez tout cet amour, même si c'est vos collègues de l'ingénierie qui ont écrit le code.

## La recette de la potion magique

En conclusion, les ingrédients nécessaires pour la recette de la potion magique sont :

* Soyez visible
* N'hésitez pas
* On s'en fout que vous soyez un imposteur ou pas
* Publiez votre code
* Contribuez, quoi que ce soit : de la documentation, des tests, du code, des articles de blogs
* Entraidez-vous
* Soyez bienveillant et patient
* Partagez votre amour avec votre communauté

## Photos du talk

Voici quelques photographies prises pendant ma session. Nous avions choisi un endroit à côté de la piscine, avec un bruit d'eau très apaisant. La session durait 15 minutes, mais nous sommes restés 15 minutes de plus à échanger et débattre sur ces sujets.

{{< figure src="attendees.jpeg" caption="Participants" >}}

{{< figure src="selfie-pool.jpeg" caption="Vue piscine" >}}

{{< figure src="selfie-public.jpeg" caption="Vue participants" >}}

{{< figure src="talking-white-noise.jpeg" caption="Avec la piscine" >}}

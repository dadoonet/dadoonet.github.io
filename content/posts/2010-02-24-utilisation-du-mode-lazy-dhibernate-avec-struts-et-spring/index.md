---
title: Utilisation du mode Lazy d'Hibernate avec Struts et Spring
description: "Lorsqu'on utilise Hibernate pour déléguer la gestion de la persistence, se pose alors le classique problème de l'exception LazyInitialisationException."
author: David Pilato
avatar: /about/david_pilato.webp
tags:
  - java
  - hibernate
  - spring
categories:
  - tutorial
date: 2010-02-24 13:56:56 +00:00
nolastmod: true
draft: false
aliases:
  - /blog/2010/02/24/utilisation-du-mode-lazy-dhibernate-avec-struts-et-spring/
  - /blog/2010-02-24-utilisation-du-mode-lazy-dhibernate-avec-struts-et-spring/
---

Lorsqu'on utilise Hibernate pour déléguer la gestion de la persistence, se pose alors le classique problème de l'exception [LazyInitialisationException](https://www.hibernate.org/hib_docs/v3/api/org/hibernate/LazyInitializationException.html).

<!--more-->

En effet, dans une modélisation assez classique, imaginons le cas suivant :

## Couche Modèle (ou DAO)

### Classe POJO contenant un attribut x et une collection cols

```java
@Entity
@Inheritance(strategy=InheritanceType.SINGLE_TABLE)
public class Dossier {
 @Id
 @GeneratedValue
 private Long id;
 private String x;

 @OneToMany(cascade=CascadeType.ALL)
 private Collections cols;
 // Getter et setters
}
```

### Classe DAO

Utilisation des generics de Java5 afin d'éviter d'avoir à coder toujours les mêmes méthodes CRUD:

```java
@Repository
@Transactional
public class DossierDAO {
 @Autowired
 protected SessionFactory factory;

 public Dossier getOne (Long id) {
  Session session = factory.getCurrentSession();
  return (Dossier)(session.get(Dossier.class,id));
 }
}
```

## Couche Métier (ou Service)

### Classe Service contenant l'injection du DAO

```java
@Transactional
public class DossierServiceImpl implements DossierService {
 @Autowired
 @Qualifier("dossierDao")
 private DossierDAO dossierDao;

 public Dossier read(Long id) {
  return dossierDao.getOne(Dossier.class.getName(), id);
 }
}
```

On voit ici que la transaction peut démarrer au niveau du service et que par défaut, en mode Lazy, seul l'attribut x de Dossier sera chargé.

Pour que l'application Web appelante puisse faire une itération sur la collection, il faudrait que celle-ci soit chargée.
Il est possible de changer le mode LAZY pour dire à Hibernate de tout récupérer mais pour un arbre de données assez profond, cela peut devenir désastreux.
Il est également de modifier la méthode read du service DossierService ainsi :

```java
public Dossier read(Long id) {
 Dossier d = dossierDao.getOne(Dossier.class.getName(), id);
 d.getCols();
 return d;
}
```

Dans ce cas, on a déclenché manuellement la recherche du contenu de la collection...

Autre possibilité, garder la connexion avec Hibernate pendant tout le temps du traitement de la requête Web de l'utilisateur.
Pour se faire, on doit ouvrir la transaction au début du traitement de la requête pour ne la restituer qu'à la fin de la génération de la vue.

On modifie le `web.xml` :

```xml
<filter>
   <filter-name>OpenSessionInViewFilter</filter-name>
   <filter-class>org.springframework.orm.hibernate3.support.OpenSessionInViewFilter</filter-class>
</filter>
<filter-mapping>
   <filter-name>OpenSessionInViewFilter</filter-name>
   <url-pattern>*.do</url-pattern>
</filter-mapping>
```

Dans cette configuration, le filtre [OpenSessionInViewFilter](https://docs.spring.io/spring-framework/docs/2.5.x/javadoc-api/org/springframework/orm/hibernate3/support/OpenSessionInViewFilter.html) mis sur tous les appels `*.do` va déclencher une ouverture de session hibernate jusqu'à la restitution de la vue.
Ainsi, si dans la JSP, on trouve une itération de l'attribut cols du bean `Dossier`, un appel à la base de données via Hibernate sera déclenché à ce moment là (et seulement à ce moment là).
Autrement dit, si pour une autre JSP vous n'avez pas besoin d'afficher la collection, l'appel à la base ne sera pas réalisé.

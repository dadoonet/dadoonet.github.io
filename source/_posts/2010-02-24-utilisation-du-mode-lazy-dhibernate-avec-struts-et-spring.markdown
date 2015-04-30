---
author: admin
comments: true
date: 2010-02-24 13:56:56+00:00
layout: post
slug: utilisation-du-mode-lazy-dhibernate-avec-struts-et-spring
title: Utilisation du mode Lazy d'Hibernate avec Struts et Spring
wordpress_id: 77
categories:
- Java
tags:
- Hibernate
- Java
- Spring
---

Lorsqu'on utilise Hibernate pour déléguer la gestion de la persistence, se pose alors le classique problème de l'exception [LazyInitialisationException](https://www.hibernate.org/hib_docs/v3/api/org/hibernate/LazyInitializationException.html).

En effet, dans une modélisation assez classique, imaginons le cas suivant :


## Couche Modèle (ou DAO)




### Classe POJO contenant un attribut x et une collection cols


[sourcecode language='java']
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
[/sourcecode]



### Classe DAO


Voir le [blog](http://bit.ly/a05odS) pour l'utilisation des generics de Java5 afin d'éviter d'avoir à coder toujours les mêmes méthodes CRUD.

[sourcecode language='java']
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
[/sourcecode]



## Couche Métier (ou Service)




### Classe Service contenant l'injection du DAO



[sourcecode language='java']
@Transactional
public class DossierServiceImpl implements DossierService {
	@Autowired
	@Qualifier("dossierDao")
	private DossierDAO dossierDao;

	public Dossier read(Long id) {
		return dossierDao.getOne(Dossier.class.getName(), id);
	}
}
[/sourcecode]

On voit ici que la transaction peut démarrer au niveau du service et que par défaut, en mode Lazy, seul l'attribut x de Dossier sera chargé.

Pour que l'application Web appelante puisse faire une itération sur la collection, il faudrait que celle-ci soit chargée.
Il est possible de changer le mode LAZY pour dire à Hibernate de tout récupérer mais pour un arbre de données assez profond, cela peut devenir désastreux.
Il est également de modifier la méthode read du service DossierService ainsi :

[sourcecode language='java']
public Dossier read(Long id) {
	Dossier d = dossierDao.getOne(Dossier.class.getName(), id);
	d.getCols();
	return d;
}
[/sourcecode]

Dans ce cas, on a déclenché manuellement la recherche du contenu de la collection...

Autre possibilité, garder la connexion avec Hibernate pendant tout le temps du traitement de la requête Web de l'utilisateur.
Pour se faire, on doit ouvrir la transaction au début du traitement de la requête pour ne la restituer qu'à la fin de la génération de la vue.

On modifie le web.xml :
[sourcecode language='xml']
	
		OpenSessionInViewFilter
		org.springframework.orm.hibernate3.support.OpenSessionInViewFilter
	
	
		OpenSessionInViewFilter
		*.do
	
[/sourcecode]

Dans cette configuration, le filtre [OpenSessionInViewFilter](http://static.springsource.org/spring/docs/2.5.x/api/org/springframework/orm/hibernate3/support/OpenSessionInViewFilter.html) mis sur tous les appels *.do va déclencher une ouverture de session hibernate jusqu'à la restitution de la vue.
Ainsi, si dans la JSP, on trouve une itération de l'attribut cols du bean Dossier, un appel à la base de données via Hibernate sera déclenché à ce moment là (et seulement à ce moment là).
Autrement dit, si pour une autre JSP vous n'avez pas besoin d'afficher la collection, l'appel à la base ne sera pas réalisé.

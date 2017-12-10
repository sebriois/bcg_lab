# -*- encoding: utf8 -*-

STATE_CHOICES = (
	(0, u"Non passée"),
	(1, u"En attente de validation"),
	(2, u"Transmise à la gestion"),
	(3, u"En attente d'envoi"),
	(4, u"Envoyée au fournisseur"),
	(5, u"Commande réceptionnée")
)

ORDERITEM_TYPES = (
	(0, u"Produit"),
	(1, u"Frais"),
	(2, u"Remises"),
	(3, u"Autre")
)

ISSUE_CHOICES = (
	(0, u"Bug"),
	(1, u"Amélioration")
)

ISSUE_SEVERITY_CHOICES = (
	(0, u"Bloquant"),
	(1, u"Majeur"),
	(2, u"Normal"),
	(3, u"Mineur")
)

ISSUE_STATUS_CHOICES = (
	(0, u"En attente"),
	(1, u"En cours"),
	(2, u"Doublon"),
	(3, u"Déjà résolu"),
	(4, u"Résolu"),
	(5, u"Ne sera pas résolu")
)

CATEGORY_CHOICES = (
	(0, u""),
	(1, u"Produit chimique"),
	(2, u"Produit biologique"),
	(3, u"Produit radioactif")
)

SUBCATEGORY_CHOICES = (
	(0, u""),
	(1, u"alcool"),
	(2, u"solvant"),
	(3, u"acide"),
	(4, u"base"),
	(5, u"cellules"),
	(6, u"virus"),
	(7, u"bacteries"),
	(8, u"echantillon de patient")
)


BUDGET_CHOICES = (
	(0, u"CNRS"),
	(1, u"UPS")
)

CREDIT = 0
DEBIT = 1
COST_TYPE_CHOICES = (
	(CREDIT, u"Crédit"),
	(DEBIT, u"Débit")
)

EMPTY_SEL = [("","---------")]
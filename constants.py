# -*- encoding: utf8 -*-

NORMAL = 0
SECRETARY = 1
VALIDATOR = 2
ADMIN = 3

MEMBERTYPE_CHOICES = (
  (NORMAL, u"Normal"),
  (SECRETARY, u"Gestionnaire"),
  (VALIDATOR, u"Validateur"),
  (ADMIN, u"Admin")
)

STATE_CHOICES = (
  (0, u"Non passée"),
  (1, u"En attente de validation"),
  (2, u"Transmise au secrétariat"),
  (3, u"En attente d'envoi"),
  (4, u"Envoyée au fournisseur"),
  (5, u"Commande réceptionnée")
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

BUDGET_CHOICES = (
  (0, u"CNRS"),
  (1, u"UPS")
)

CREDIT_ORDER_CHOICES	= u"Remise;Promotion"
DEBIT_ORDER_CHOICES 	= u"Frais de port;Frais de conditionnement"

CREDIT = 0
DEBIT = 1
COST_TYPE_CHOICES = (
  (CREDIT, u"Crédit"),
  (DEBIT, u"Débit")
)

EMAIL_MAGASIN = 'escaffit@cict.fr'
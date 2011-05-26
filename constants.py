# -*- encoding: utf8 -*-

NORMAL = 0
VALIDATOR = 1
SECRETARY = 2
ADMIN = 3

MEMBERTYPE_CHOICES = (
  (0, "Normal"),
  (1, "Validateur"),
  (2, "Gestionnaire"),
  (3, "Admin")
)

STATE_CHOICES = (
  (0, "Non passée"),
  (1, "En attente de validation"),
  (2, "Transmise au secrétariat"),
  (3, "En attente d'envoi"),
  (4, "Envoyée au fournisseur"),
  (5, "Commande réceptionnée")
)

BUDGET_CHOICES = (
  (0, "CNRS"),
  (1, "UPS")
)

CREDIT = 0
DEBIT = 1
COST_TYPE_CHOICES = (
  (CREDIT, "Crédit"),
  (DEBIT, "Débit")
)

EMAIL_MAGASIN = 'sbriois@cict.fr'
# -*- encoding: utf8 -*-
from django.db import models

from team.models import Team
from constants import BUDGET_CHOICES

class Budget(models.Model):
  team = models.ForeignKey(Team, verbose_name="Equipe")
  name = models.CharField(u"Nom", max_length=100, unique = True)
  budget_type = models.IntegerField(u"Tutelle", choices = BUDGET_CHOICES)
  amount = models.DecimalField(u"Montant initial", max_digits=12, decimal_places=2, default=0)
  default_credit_type = models.CharField(u"Type de crédit", max_length=30, null = True, blank = True)
  default_nature = models.CharField(u"Nature", max_length=20, null = True, blank = True)
  
  class Meta:
    verbose_name = "Budget"
    verbose_name_plural = "Budgets"
  
  def __unicode__(self):
    return u"%s (dispo: %s)" % ( self.name, self.amount )

class BudgetLine(models.Model):
  name        = models.CharField(u"Nom", max_length = 100)
  credit      = models.DecimalField(u"Crédit", max_digits=12, decimal_places=2, null = True, blank = True)
  number    = models.CharField(u"N° de cde", max_length = 30, null = True, blank = True)
  date        = models.DateField(u"Date de l'acte")
  nature      = models.CharField(u"Nature", max_length = 20)
  budget_type = models.IntegerField(u"Tutelle", choices = BUDGET_CHOICES)
  credit_type = models.CharField(u"Type crédit", max_length = 40)
  provider    = models.CharField(u"Fournisseur", max_length = 100)
  offer       = models.CharField(u"Offre", max_length = 100, null = True, blank = True )
  product     = models.CharField(u"Désignation", max_length = 100, null = True, blank = True )
  ref         = models.CharField(u"Réf", max_length = 50, null = True, blank = True )
  quantity    = models.IntegerField(u"Qté", null = True, blank = True)
  product_price = models.DecimalField(u"PU", max_digits=12, decimal_places=2, null = True, blank = True)
  debit       = models.DecimalField(u"Débit", max_digits=12, decimal_places=2, null = True, blank = True)
  amount_left = models.DecimalField(u"Montant dispo", max_digits=12, decimal_places=2, blank = True)
  confidential = models.BooleanField(u"Donnée confidentielle", default = False)
  
  class Meta:
    verbose_name = "Ligne budgétaire"
    verbose_name = "Lignes budgétaires"
    ordering = ("name","date","-amount_left")
  
  def get_total_price(self):
    return self.quantity * self.debit
  

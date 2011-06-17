# -*- encoding: utf8 -*-
from django.db import models

from team.models import Team
from constants import BUDGET_CHOICES

class Budget(models.Model):
  team = models.ForeignKey(Team, verbose_name="Equipe")
  name = models.CharField(u"Nom", max_length=100, unique = True)
  budget_type = models.IntegerField(u"Tutelle", choices = BUDGET_CHOICES)
  default_credit_type = models.CharField(u"Type de crédit", max_length=30, null = True, blank = True)
  default_nature = models.CharField(u"Nature", max_length=20, null = True, blank = True)
  
  class Meta:
    verbose_name = "Budget"
    verbose_name_plural = "Budgets"
    ordering = ("team", "name")
  
  def __unicode__(self):
    return u"%s (dispo: %s)" % ( self.name, self.get_amount_left() )
  
  def get_amount_left(self):
    amount_left = 0
    for line in BudgetLine.objects.filter( team = self.team.name, name = self.name ):
      if line.credit:
        amount_left += line.credit
      
      if line.debit:
        amount_left -= line.debit
      
    return amount_left
  


class BudgetLine(models.Model):
  team          = models.CharField(u"Equipe", max_length = 100)
  name          = models.CharField(u"Nom", max_length = 100)
  number        = models.CharField(u"N° de cde", max_length = 30, null = True, blank = True)
  date          = models.DateField(u"Date de l'acte")
  nature        = models.CharField(u"Nature", max_length = 20)
  budget_type   = models.IntegerField(u"Tutelle", choices = BUDGET_CHOICES)
  credit_type   = models.CharField(u"Type crédit", max_length = 40)
  provider      = models.CharField(u"Fournisseur", max_length = 100)
  offer         = models.CharField(u"Offre", max_length = 100, null = True, blank = True )
  product       = models.CharField(u"Désignation", max_length = 100, null = True, blank = True )
  ref           = models.CharField(u"Réf", max_length = 50, null = True, blank = True )
  quantity      = models.IntegerField(u"Qté", null = True, blank = True)
  product_price = models.DecimalField(u"PU", max_digits=12, decimal_places=2, null = True, blank = True)
  credit        = models.DecimalField(u"Crédit", max_digits=12, decimal_places=2, null = True, blank = True)
  debit         = models.DecimalField(u"Débit", max_digits=12, decimal_places=2, null = True, blank = True)
  confidential  = models.BooleanField(u"Donnée confidentielle", default = False)
  
  class Meta:
    verbose_name = "Ligne budgétaire"
    verbose_name = "Lignes budgétaires"
    ordering = ("team", "name", "date")
  
  def get_amount_left(self):
    amount_left = 0
    for line in BudgetLine.objects.filter( team = self.team, name = self.name ):
      if line.credit:
        amount_left += line.credit
      
      if line.debit:
        amount_left -= line.debit
      
      if line == self:
        break
    
    return amount_left
  
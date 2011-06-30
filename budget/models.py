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
	is_active = models.BooleanField(u"Actif?", default = True)
	
	class Meta:
		verbose_name = "Budget"
		verbose_name_plural = "Budgets"
		ordering = ("team", "name")
	
	def __unicode__(self):
		return u"%s (dispo: %s)" % ( self.name, self.get_amount_left() )
	
	def get_amount_left(self):
		amount_left = 0
		for line in BudgetLine.objects.filter( budget_id = self.id ):
			if line.credit:
				amount_left += line.credit
			
			if line.debit:
				amount_left -= line.debit
			
		return amount_left
	
	def update_budget_lines_team(self):
		for bl in BudgetLine.objects.filter( budget_id = self.id ):
			if bl.team != self.team.name:
				bl.team = self.team.name
				bl.save()
	

class BudgetLine(models.Model):
	team					= models.CharField(u"Equipe", max_length = 100)
	order_id			= models.IntegerField( u"ID de commande", null = True, blank = True )
	orderitem_id	= models.IntegerField( u"ID d'item de commande", null = True, blank = True )
	budget_id			= models.IntegerField( u"ID de budget" )
	budget				= models.CharField(u"Budget", max_length = 100)
	number				= models.CharField(u"N° de cde", max_length = 30, null = True, blank = True)
	date					= models.DateTimeField(u"Date de l'acte", auto_now_add = True)
	nature				= models.CharField(u"Nature", max_length = 20)
	budget_type		= models.IntegerField(u"Tutelle", choices = BUDGET_CHOICES)
	credit_type		= models.CharField(u"Type crédit", max_length = 40)
	provider			= models.CharField(u"Fournisseur", max_length = 100)
	offer					= models.CharField(u"Offre", max_length = 100, null = True, blank = True )
	product				= models.CharField(u"Désignation", max_length = 100, null = True, blank = True )
	ref						= models.CharField(u"Réf", max_length = 50, null = True, blank = True )
	quantity			= models.IntegerField(u"Qté", null = True, blank = True, default = 1)
	product_price = models.DecimalField(u"Montant", max_digits=12, decimal_places=2, null = True, blank = True)
	credit				= models.DecimalField(u"Crédit", max_digits=12, decimal_places=2, null = True, blank = True)
	debit					= models.DecimalField(u"Débit", max_digits=12, decimal_places=2, null = True, blank = True)
	confidential	= models.BooleanField(u"Donnée confidentielle", default = False)
	
	class Meta:
		verbose_name = "Ligne budgétaire"
		verbose_name = "Lignes budgétaires"
		ordering = ("team", "budget_id", "date", "-order_id")
	
	def get_amount_left(self):
		amount_left = 0
		for line in BudgetLine.objects.filter( team = self.team, budget = self.budget ):
			if line.credit:
				amount_left += line.credit
			
			if line.debit:
				amount_left -= line.debit
			
			if line == self:
				break
		
		return amount_left
	

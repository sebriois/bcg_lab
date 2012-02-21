# -*- encoding: utf8 -*-
from django.db import models

from team.models import Team
from constants import BUDGET_CHOICES

class Budget(models.Model):
	team = models.ForeignKey(Team, verbose_name="Equipe")
	name = models.CharField(u"Origine de crédit (Nom)", max_length=100, unique = True)
	default_origin = models.CharField(u"Origine de crédit (Code)", max_length=30, null = True, blank = False)
	budget_type = models.IntegerField(u"Tutelle", choices = BUDGET_CHOICES)
	default_nature = models.CharField(u"Nature", max_length=20, null = True, blank = True)
	tva_code = models.CharField(u"Code TVA", max_length=20, null = True, blank = True )
	domain = models.CharField(u"Domaine fonctionnel", max_length = 100, null = True, blank = True )
	is_active = models.BooleanField(u"Actif?", default = True)
	
	class Meta:
		verbose_name = "Budget"
		verbose_name_plural = "Budgets"
		ordering = ("team", "name")
	
	def __unicode__(self):
		return u"%s (dispo: %s)" % ( self.name, self.get_amount_left() )
	
	@models.permalink
	def get_absolute_url(self):
		return ( 'budget_edit', [self.id] )
	
	def get_amount_left(self):
		return sum([bl.get_total() for bl in BudgetLine.objects.filter(budget_id = self.id)])
	
	def update_budgetlines(self):
		for bl in BudgetLine.objects.filter( budget_id = self.id ):
			bl.team = self.team.name
			bl.budget = self.name
			bl.origin = self.default_origin
			bl.budget_type = self.budget_type
			bl.nature = self.default_nature
			bl.is_active = self.is_active
			bl.save()
	
	def credit(self, value):
		bl = BudgetLine.objects.create(
			team					= self.team.name,
			budget_id			= self.id,
			budget				= self.name,
			nature				= self.default_nature,
			budget_type 	= self.budget_type,
			origin				= self.default_origin,
			product_price	= value,
			quantity			= 1,
			credit				= value,
			debit					= 0
		)
		return bl
	
	def debit(self, value):
		bl = BudgetLine.objects.create(
			team					= self.team.name,
			budget_id			= self.id,
			budget				= self.name,
			nature				= self.default_nature,
			budget_type 	= self.budget_type,
			origin				= self.default_origin,
			product_price	= value,
			quantity			= 1,
			credit				= 0,
			debit					= value
		)
		return bl
	

class BudgetLine(models.Model):
	team					= models.CharField(u"Equipe", max_length = 100)
	order_id			= models.IntegerField( u"ID de commande", null = True, blank = True )
	orderitem_id	= models.IntegerField( u"ID d'item de commande", null = True, blank = True )
	budget_id			= models.IntegerField( u"ID de budget" )
	budget				= models.CharField(u"Budget", max_length = 100 )
	number				= models.CharField(u"N° de commande", max_length = 20, null = True, blank = True )
	date					= models.DateTimeField(u"Date de l'acte", auto_now_add = True )
	nature				= models.CharField(u"Nature", null = True, blank = True, max_length = 20 )
	budget_type		= models.IntegerField(u"Tutelle", choices = BUDGET_CHOICES)
	origin				= models.CharField(u"Origine", max_length = 30, null = True, blank = True )
	provider			= models.CharField(u"Fournisseur", max_length = 100, null = True, blank = True )
	offer					= models.CharField(u"Offre", max_length = 100, null = True, blank = True )
	product				= models.CharField(u"Désignation", max_length = 500, null = True, blank = True )
	reference			= models.CharField(u"Référence", max_length = 50, null = True, blank = True )
	quantity			= models.IntegerField(u"Quantité", null = True, blank = True, default = 1)
	product_price = models.DecimalField(u"Montant", max_digits=12, decimal_places=2, null = True, blank = True)
	credit				= models.DecimalField(u"Crédit", max_digits=12, decimal_places=2, null = True, blank = True)
	debit					= models.DecimalField(u"Débit", max_digits=12, decimal_places=2, null = True, blank = True)
	confidential	= models.BooleanField(u"Ligne confidentielle", default = False)
	is_active			= models.BooleanField(u"Active?", default = True)
	
	class Meta:
		verbose_name = "Ligne budgétaire"
		verbose_name = "Lignes budgétaires"
		ordering = ("team", "budget", "date", "-order_id")
	
	def get_amount_left(self):
		amount_left = 0
		for line in BudgetLine.objects.filter( budget_id = self.budget_id ):
			amount_left += line.get_total()
			
			if line == self:
				break
		
		return amount_left
	
	def get_total(self):
		# should equal product_price actually
		if self.credit:
			return self.credit * self.quantity
		if self.debit:
			return self.debit * self.quantity * -1
		return self.product_price
	
	def get_order_team(self):
		"""
		Returns team that has ordered using this budget
		"""
		from order.models import Order
		from history.models import History
		
		if not self.number: return ""
		
		t = None
		
		# From order
		order_list = Order.objects.filter( number = self.number )
		if order_list.count() > 0:
			t = order_list[0].team
		
		# From history
		history_list = History.objects.filter( number = self.number )
		if history_list.count() > 0:
			team_name = history_list[0].team
			t = Team.objects.get( name = team_name )
		
		if not t:
			return "NOT FOUND"
		
		if t.name != self.team:
			return t.shortname
		
		return ""
	
	def update_budget_relation(self):
		b = Budget.objects.get(id = self.budget_id)
		self.budget = b.name
		self.team = b.team.name
		self.nature = b.default_nature
		self.budget_type = b.budget_type
		self.origin = b.default_origin
		self.save()
	

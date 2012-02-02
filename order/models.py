# -*- encoding: utf8 -*-
from datetime import datetime, date

from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic

from product.models import Product
from provider.models import Provider
from budget.models import Budget, BudgetLine
from team.models import Team, TeamMember
from attachments.models import Attachment

from constants import *

class Order(models.Model):
	number					= models.CharField(u"N° cmde", max_length = 20, null = True, blank = True)
	budget					= models.ForeignKey(Budget, verbose_name="Ligne budgétaire", blank = True, null = True)
	team						= models.ForeignKey(Team, verbose_name = u"Equipe", max_length = 20 )
	provider				= models.ForeignKey(Provider, verbose_name = u"Fournisseur", max_length = 100 )
	status					= models.IntegerField(u"Etat de la commande", choices = STATE_CHOICES, default = 0)
	items						= models.ManyToManyField( "OrderItem", verbose_name = "Produits" )
	notes						= models.TextField( u"Commentaires", null = True, blank = True )
	is_confidential	= models.BooleanField( u"Confidentielle?", default = False )
	is_urgent				= models.BooleanField( u"Urgente?", default = False )
	has_problem			= models.BooleanField( u"Problème?", default = False )
	date_created		= models.DateTimeField(u"Date de création", auto_now_add = True)
	date_delivered	= models.DateTimeField(u"Date de livraison", null = True, blank = True)
	last_change			= models.DateTimeField(u"Dernière modification", auto_now = True)
	attachments			= generic.GenericRelation( Attachment )
	
	class Meta:
		verbose_name = "Commande"
		verbose_name_plural = "Commandes"
		ordering = ('date_created','provider','status')
	
	def __unicode__(self):
		d = datetime.strftime( self.date_created, "%d/%m/%Y %Hh%M" )
		return u"%s (%s) - %s" % ( self.provider, self.team, d )
	
	@models.permalink
	def get_absolute_url(self):
		return ( 'order_item', [self.id] )
	
	def get_full_name(self):
		return u"%s" % self.team
	
	def add(self, product, quantity):
		if self.date_delivered:
			 # TODO: raise an exception instead
			return
		
		item, created = self.items.get_or_create( 
			product_id = product.id,
			defaults = {
				'cost_type':				DEBIT,
				'name':							product.origin and "%s - %s" % (product.origin,product.name) or product.name,
				'provider':					product.provider.name,
				'origin':						product.origin,
				'packaging':				product.packaging,
				'reference':				product.reference,
				'price':						product.price,
				'offer_nb':					product.offer_nb,
				'nomenclature': 		product.nomenclature,
				'quantity':					quantity
			}
		)
		
		if product.category:
			item.category = product.category.name
		if product.sub_category:
			item.sub_category = product.sub_category.name
		item.save()
		
		if not created:
			item.quantity += int(quantity)
			item.save()
		return item
	
	def price(self):
		return sum( [item.total_price() for item in self.items.all()] )
	
	def create_budget_line(self):
		for item in self.items.all():
			item.create_budget_line()
	
	def update_budget_lines(self):
		for bl in BudgetLine.objects.filter( order_id = self.id ):
			bl.number = self.number
			bl.save()
			
		for item in self.items.all():
			item.update_budget_line()
	
	def save_to_history(self, date_delivered = datetime.now()):
		from history.models import History
		
		history = History.objects.create(
			team						= self.team.name,
			provider				= self.provider.name,
			budget					= self.budget and self.budget.name or "",
			number					= self.number,
			price						= self.price(),
			date_delivered	= date_delivered
		)
		for attachment in self.attachments.all():
			attachment.content_object = history
			attachment.save()
		
		for item in self.items.all():
			history.items.add( item )
		self.items.clear()
	


class OrderItem(models.Model):
	username				= models.CharField( u"Utilisateur", max_length = 100 )
	product_id			= models.IntegerField( u'ID produit', blank = True, null = True )
	name						= models.CharField( u'Désignation', max_length = 500 )
	provider				= models.CharField( u'Fournisseur', max_length = 100, blank = True, null = True )
	origin					= models.CharField( u"Fournisseur d'origine", max_length = 100, blank = True, null = True )
	packaging				= models.CharField( u'Conditionnement', max_length = 100, blank = True, null = True)
	reference				= models.CharField( u'Référence', max_length = 100, blank = True, null = True )
	offer_nb				= models.CharField( u'N° Offre', max_length = 100, blank = True, null = True )
	category				= models.CharField( u'Type', max_length = 100, blank = True, null = True )
	sub_category		= models.CharField( u'Sous-type', max_length = 100, blank = True, null = True )
	nomenclature		= models.CharField( u'Nomenclature', max_length = 100, blank = True, null = True )
	price						= models.DecimalField( u'Montant', max_digits = 12, decimal_places = 2 )
	cost_type				= models.IntegerField( u'Type de coût', choices = COST_TYPE_CHOICES )
	quantity				= models.IntegerField( u'Quantité', default = 1 )
	is_confidential	= models.BooleanField( u"Confidentielle?", default = False )
	
	class Meta:
		verbose_name = "Item de commande"
		verbose_name_plural = "Items de commande"
		ordering = ('id',)
	
	def get_order(self):
		return self.order_set.get()
	
	def get_fullname(self):
		users = User.objects.filter( username = self.username )
		if users.count() > 0 and users[0].get_full_name():
			return u"%s" % users[0].get_full_name()
		else:
			return u"%s" % self.username
	
	def total_price(self):
		if self.cost_type == DEBIT:
			return self.price * self.quantity
		
		if self.cost_type == CREDIT:
			return self.price * self.quantity * -1
	
	def create_budget_line(self):
		if self.order_set.all().count() == 0:
			# TODO: raise error instead
			return
		order = self.order_set.get()
		bl = BudgetLine.objects.create(
			team					= order.team.name,
			order_id			= order.id,
			orderitem_id	= self.id,
			budget_id			= order.budget.id,
			budget				= order.budget.name,
			number				= order.number,
			nature				= order.budget.default_nature,
			budget_type		= order.budget.budget_type,
			origin				= order.budget.default_origin,
			provider			= order.provider.name,
			offer					= self.offer_nb,
			product				= self.name,
			product_price = self.total_price(),
			reference			= self.reference,
			quantity			= self.quantity
		)
		if self.cost_type == DEBIT:
			bl.credit = 0
			bl.debit = self.price
		elif self.cost_type == CREDIT:
			bl.credit = self.price
			bl.debit = 0
		bl.save()
	
	def update_budget_line(self):
		bl = BudgetLine.objects.get( orderitem_id = self.id )
		
		if self.cost_type == DEBIT:
			bl.credit = 0
			bl.debit = self.price
		elif self.cost_type == CREDIT:
			bl.credit = self.price
			bl.debit = 0
		else:
			raise Exception("COST TYPE SHOULD NOT BE NULL")
		
		bl.provider = bl.provider and bl.provider or self.provider
		bl.offer = self.offer_nb
		bl.product = self.name
		bl.product_price = self.total_price()
		bl.reference = self.reference
		bl.quantity = self.quantity
		bl.save()
	
	def update_product(self):
		if self.product_id:
			product = Product.objects.get( id = self.product_id )
			product.name = self.name
			product.packaging = self.packaging
			product.reference = self.reference
			product.offer_nb = self.offer_nb
			product.nomenclature = self.nomenclature
			product.price = self.price
			product.save()
		
	

class OrderComplement(models.Model):
	name = models.CharField( u"Nom du complément", max_length = 50 )
	type_comp = models.IntegerField( u"Type de complément", choices = ((CREDIT, u"Crédit"), (DEBIT, u"Débit")) )


# -*- encoding: utf8 -*-
from datetime import datetime, date

from django.db import models
from django.contrib.auth.models import User

from product.models import Product
from provider.models import Provider
from budget.models import Budget, BudgetLine
from team.models import Team, TeamMember

from constants import *

class Order(models.Model):
  number          = models.CharField(u"N° cmde", max_length = 20, null = True, blank = True)
  budget          = models.ForeignKey(Budget, verbose_name="Ligne budgétaire", blank = True, null = True)
  team            = models.ForeignKey(Team, verbose_name = u"Equipe", max_length = 20 )
  user            = models.ForeignKey(User, verbose_name = u"Utilisateur", max_length = 100 )
  provider        = models.ForeignKey(Provider, verbose_name = u"Fournisseur", max_length = 100 )
  status          = models.IntegerField(u"Etat de la commande", choices = STATE_CHOICES, default = 0)
  items           = models.ManyToManyField( "OrderItem", verbose_name = "Produits" )
  date_created    = models.DateTimeField(u"Date de création", auto_now_add = True)
  date_delivered  = models.DateTimeField(u"Date de livraison", null = True, blank = True)
  last_change     = models.DateTimeField(u"Dernière modification", auto_now = True)
  
  class Meta:
    verbose_name = "Commande"
    verbose_name_plural = "Commandes"
    ordering = ('last_change', 'date_created')
  
  def __unicode__(self):
    d = datetime.strftime( self.date_created, "%d/%m/%Y %Hh%M" )
    return u"%s (%s) - %s" % ( self.provider, self.team, d )
  
  @models.permalink
  def get_absolute_url(self):
    return ( 'order_item', [self.id] )
  
  def get_full_name(self):
    fullname = self.user.get_full_name()
    return fullname and fullname or self.user.username
  
  def add(self, product, quantity):
    if self.date_delivered: return # TODO: raise an exception instead
    
    item, created = self.items.get_or_create( 
      product_id = product.id,
      defaults = {
        'cost_type':    DEBIT,
        'name':         product.name,
        'provider':     product.provider.name,
        'packaging':    product.packaging,
        'reference':    product.reference,
        'price':        product.price,
        'offer_nb':     product.offer_nb,
        'nomenclature': product.nomenclature,
        'quantity':     quantity
      }
    )
    
    if not created:
      item.quantity += int(quantity)
      item.save()
  
  def price(self):
    return sum( [item.total_price() for item in self.items.all()] )
  
  def create_budget_line(self):
    for item in self.items.all():
      BudgetLine.objects.create(
        team        = self.budget.team.name,
        name        = self.budget.name,
        credit      = 0,
        number      = self.number,
        date        = self.date_created,
        nature      = self.budget.default_nature,
        budget_type = self.budget.budget_type,
        credit_type = self.budget.default_credit_type,
        provider    = self.provider.name,
        offer       = item.offer_nb,
        product     = item.name,
        ref         = item.reference,
        quantity    = item.quantity,
        debit       = item.price
      )
  
  def save_to_history(self):
    from history.models import History
    
    history = History.objects.create(
      team      = self.team.name,
      user      = self.user,
      provider  = self.provider.name,
      budget    = self.budget.name,
      number    = self.number,
      price     = self.price(),
    )
    
    for item in self.items.all():
      history.items.add( item )
    self.items.clear()
  


class OrderItem(models.Model):
  product_id    = models.IntegerField( u'ID produit', blank = True, null = True )
  name          = models.CharField( u'Désignation', max_length = 500 )
  provider      = models.CharField( u'Fournisseur', max_length = 100, blank = True, null = True )
  packaging     = models.CharField( u'Conditionnement', max_length = 100, blank = True, null = True)
  reference     = models.CharField( u'Référence', max_length = 100, blank = True, null = True )
  offer_nb      = models.CharField( u'N° Offre', max_length = 100, blank = True, null = True )
  nomenclature  = models.CharField( u'Nomenclature', max_length = 100, blank = True, null = True )
  price         = models.DecimalField( u'Prix', max_digits = 12, decimal_places = 2 )
  cost_type     = models.IntegerField( u'Type de coût', choices = COST_TYPE_CHOICES )
  quantity      = models.IntegerField( default = 1 )
  
  class Meta:
    verbose_name = "Item de commande"
    verbose_name_plural = "Items de commande"
    ordering = ('id',)
  
  def total_price(self):
    if self.cost_type == DEBIT:
      return self.price * self.quantity
    
    if self.cost_type == CREDIT:
      return self.price * self.quantity * -1
  

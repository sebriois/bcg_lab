# -*- encoding: utf8 -*-
from datetime import datetime

from django.db import models
from django.contrib.auth.models import User

from product.models import Product
from provider.models import Provider
from history.models import History, HistoryItem
from secretary.models import Budget, BudgetLine
from team.models import Team, TeamMember
from constants import STATE_CHOICES, BUDGET_CHOICES

class Order(models.Model):
  number          = models.CharField(u"N° cmde", max_length = 20, null = True, blank = True)
  team            = models.ForeignKey(Team, verbose_name="Equipe")
  username        = models.CharField("Utilisateur", max_length = 100)
  items           = models.ManyToManyField( "OrderItem", verbose_name = "Produits")
  budget          = models.ForeignKey(Budget, verbose_name="Ligne budgétaire", blank = True, null = True)
  provider        = models.ForeignKey(Provider, verbose_name="Fournisseur")
  provider_ref    = models.CharField(u"Réf fournisseur", max_length = 100, null = True, blank = True)
  price           = models.DecimalField(u"Prix total", max_digits=12, decimal_places=2, null = True, blank = True)
  status          = models.IntegerField(u"Etat de la commande", choices = STATE_CHOICES, default = 0)
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
    user = User.objects.get( username = self.username )
    fullname = user.get_full_name()
    return fullname and fullname or self.username
  
  def update_price(self):
      self.price = sum( [item.total_price() for item in self.items.all()] )
      self.save()
  
  def create_history_line(self):
    history = History.objects.create(
                team          = self.team.name,
                user          = self.username,
                provider      = self.provider.name,
                order_nb      = self.number,
                price         = self.price,
                budget        = self.budget.name,
                date_created  = self.date_delivered
              )
    for item in self.items.all():
      HistoryItem.objects.create(
        history       = history,
        product       = item.product.name,
        quantity      = item.quantity,
        packaging     = item.product.packaging,
        reference     = item.product.reference,
        price         = item.product.price,
        offer_nb      = item.product.offer_nb
      )
  
  def create_budget_line(self):
    for item in self.items.all():
      self.budget.amount -= item.total_price()
      self.budget.save()
      
      BudgetLine.objects.create(
        name        = self.budget.name,
        credit      = 0,
        order_nb    = self.order_nb,
        date        = self.date_created,
        nature      = self.budget.default_nature,
        budget_type = self.budget.budget_type,
        credit_type = self.budget.default_credit_type,
        provider    = self.provider.name,
        offer       = item.product.offer_nb,
        product     = item.product.name,
        ref         = item.product.reference,
        quantity    = item.quantity,
        debit       = item.product.price,
        amount_left = self.budget.amount
      )
    
  

class OrderItem(models.Model):
  product   = models.ForeignKey(Product)
  quantity  = models.IntegerField(default = 0)
  
  class Meta:
    verbose_name = "Item de commande"
    verbose_name_plural = "Items de commande"
  
  def total_price(self):
    return self.product.price * self.quantity

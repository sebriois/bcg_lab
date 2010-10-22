# -*- encoding: utf8 -*-

from django.db import models
from django.contrib.auth.models import User
from order_manager.product.models import Product
from order_manager.provider.models import Provider
from order_manager.constants import STATE_CHOICES

class Order(models.Model):
  user          = models.ForeignKey(User)
  provider      = models.ForeignKey(Provider)
  products      = models.ManyToManyField(Product)
  state         = models.IntegerField("Etat de la commande", choices = STATE_CHOICES)
  date_created  = models.DateTimeField("Date de création", auto_now_add = True)
  date_delivered = models.DateTimeField("Date de livraison", null = True, blank = True)
  last_change   = models.DateTimeField("Dernière modification", auto_now = True)
  
  class Meta:
    verbose_name = "Commande"
    verbose_name_plural = "Commandes"
    ordering = ('last_change', 'date_created')
  
  def __unicode__(self):
    return u"%s - %s" % ( self.user, self.date_created )
  

class Cart(models.Model):
  user      = models.ForeignKey(User, unique = True)
  products  = models.ManyToManyField(Product)
  
  class Meta:
    verbose_name = "Panier"
    verbose_name_plural = "Paniers"
  
  def turn_into_orders(self):
    pass
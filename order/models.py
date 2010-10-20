# -*- encoding: utf8 -*-

from django.db import models
from django.contrib.auth.models import User
from product.models import Product
from constants import STATE_CHOICES

class Order(models.Model):
  user          = models.ForeignKey(User)
  products      = models.ManyToManyField(Product)
  state         = models.IntegerField("Etat de la commande", choices = STATE_CHOICES)
  date_created  = models.DateTimeField("Date de création", auto_now_add = True)
  last_change   = models.DateTimeField("Dernière modification", auto_now = True)
  
  class Meta:
    verbose_name = "Commande"
    verbose_name_plural = "Commandes"
  
  def __unicode__(self):
    return u"%s - %s" % ( self.user, self.date_created )
  

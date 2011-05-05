# -*- encoding: utf8 -*-
from datetime import datetime, date
from django.db import models

class History(models.Model):
  """
  History should be completely independant from any other table so 
  that when a deletion is made in the DB, it won't affect the history
  """
  team         = models.CharField(u"Equipe", max_length=100)
  user         = models.CharField(u"Utilisateur", max_length=100)
  provider     = models.CharField(u"Fournisseur", max_length=100)
  order_nb     = models.CharField(u"N° cde", max_length = 100, null = True, blank = True)
  price        = models.DecimalField(u"Prix total", max_digits=12, decimal_places=2)
  budget       = models.CharField(u"Ligne budgétaire", max_length = 100)
  date_created = models.DateField(u"Date", default=date.today())
  
  class Meta:
    verbose_name = "Historique d'une cde"
    verbose_name_plural = "Historique"
    ordering = ('date_created',)
  
  def __unicode__(self):
    d = datetime.strftime( self.date_created, "%d/%m/%Y %Hh%M" )
    return u"%s - %s" % ( self.provider, d )
  
  @models.permalink
  def get_absolute_url(self):
    return ( 'history_detail', [self.id] )
  
  def items(self):
    return self.historyitem_set
  

class HistoryItem(models.Model):
  history   = models.ForeignKey(History)
  product   = models.CharField(u"Produit", max_length=100)
  quantity  = models.IntegerField(u"Quantité")
  price     = models.DecimalField(u"Prix unitaire", max_digits=12, decimal_places=2)
  packaging = models.CharField(u"Conditionnement", max_length=100, null=True, blank=True)
  reference = models.CharField(u"Référence", max_length=100, null=True, blank=True)
  offer_nb  = models.CharField(u"Offre", max_length=100, null=True, blank=True)
  
  class Meta:
    verbose_name = "Item d'historique"
    verbose_name_plural = "Items d'historique"
  
  def total_price(self):
    return self.price * self.quantity
  

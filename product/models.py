# -*- encoding: utf8 -*-

from django.db import models
from django.contrib.auth.models import User
from provider.models import Provider

class Product(models.Model):
  provider      = models.ForeignKey( Provider, verbose_name = 'Fournisseur' )
  name          = models.CharField( 'Nom', blank = False, null = False, max_length = 500 )
  packaging     = models.CharField('Conditionnement', blank = True, null = True, max_length = 100)
  reference     = models.CharField(u"Référence", max_length = 100)
  price         = models.DecimalField(u"Prix", max_digits=12, decimal_places=2, null = True, blank = True)
  offer_nb      = models.CharField(u"N° Offre", blank=True, null=True, max_length = 100)
  nomenclature  = models.CharField('Nomenclature', blank=True, null=True, max_length = 100)
  last_change   = models.DateTimeField(u"Dernière modification", auto_now = True)
  
  class Meta:
    verbose_name = "Produit"
    verbose_name_plural = "Produits"
    ordering = ('provider', 'name')
  
  def __unicode__(self):
    return self.name
  
  def __repr__(self):
    return self.name
  

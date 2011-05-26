# -*- encoding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User

class Provider(models.Model):
  name            = models.CharField( 'Nom', max_length = 100, unique = True)
  users_in_charge = models.ManyToManyField( User, verbose_name = "Responsables", blank = True, null = True )
  reseller        = models.ForeignKey( "Provider", verbose_name = "Revendeur", blank = True, null = True )
  notes           = models.TextField( 'Notes', blank = True, null = True )
  is_local        = models.BooleanField( u'Magasin ?', default = False )
  
  class Meta:
    verbose_name = "Fournisseur"
    verbose_name_plural = "Fournisseurs"
    ordering = ('name',)
  
  def __unicode__(self):
    if self.reseller:
      return u"%s (revendeur: %s)" % ( self.name, self.reseller )
    return self.name

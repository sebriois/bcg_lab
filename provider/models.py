# -*- encoding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User

class Provider(models.Model):
  name             = models.CharField( 'Nom', max_length = 100, unique = True)
  users_in_charge  = models.ManyToManyField( User, verbose_name = "Personnes en charge", blank = True, null = True )
  notes            = models.TextField( 'Notes', blank = True, null = True )
  
  class Meta:
    verbose_name = "Fournisseur"
    verbose_name_plural = "Fournisseurs"
    ordering = ('name',)
  
  def __unicode__(self):
    return self.name
  

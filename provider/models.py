# -*- encoding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User

class Provider(models.Model):
  name    = models.CharField('Nom', blank = True, max_length = 100, unique = True)
  manager = models.ForeignKey( User )
  contact = models.TextField( blank = True )
  
  def __unicode__(self):
    return self.name
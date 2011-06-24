# coding: utf-8

from django.db import models

class Info(models.Model):
  text = models.TextField(u"Commentaire" )
  expiration = models.DateField(u"Expire le" )

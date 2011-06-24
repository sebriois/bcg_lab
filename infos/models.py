# coding: utf-8

from django.db import models

class Info(models.Model):
	text = models.TextField(u"Information" )
	expiry = models.DateField(u"Date d'expiration", help_text = 'Format: jj/mm/aaaa')
	date_created = models.DateField(u"Date", auto_now_add = True)

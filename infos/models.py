# coding: utf-8

from django.db import models

class Info(models.Model):
	text = models.TextField(u"Information" )
	expiry = models.DateField(u"Expire le" )
	date_created = models.DateField(u"Date", auto_now_add = True)

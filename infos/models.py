# coding: utf-8

from datetime import date, timedelta
from django.db import models

class Info(models.Model):
	text = models.TextField(u"Information" )
	expiry = models.DateField(u"Date d'expiration", help_text = 'Format: jj/mm/aaaa')
	date_created = models.DateField(u"Date", auto_now_add = True)
	
	class Meta:
		ordering = ('expiry',)
	
	def has_expired(self):
		return self.expiry <= date.today()
	
	def soon_expired(self):
		delta = timedelta( days = 10 )
		return self.expiry - delta <= date.today()
	

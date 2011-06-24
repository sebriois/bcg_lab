# -*- encoding: utf8 -*-
from datetime import datetime, timedelta
from django.db import models
from django.contrib.auth.models import User
from provider.models import Provider

class Product(models.Model):
	provider			= models.ForeignKey( Provider, verbose_name = 'Fournisseur' )
	name					= models.CharField( u'Désignation', max_length = 500 )
	packaging			= models.CharField( u'Conditionnement', blank = True, null = True, max_length = 100)
	reference			= models.CharField( u'Référence', max_length = 100)
	price					= models.DecimalField( u'Prix', max_digits=12, decimal_places=2)
	offer_nb			= models.CharField( u'N° Offre', blank = True, null = True, max_length = 100)
	nomenclature	= models.CharField( u'Nomenclature', blank = True, null = True, max_length = 100)
	expiry				= models.DateTimeField( u"Date d'expiration", help_text = u"Format jj/mm/aaaa", blank = True, null = True )
	last_change		= models.DateTimeField( u'Dernière modification', auto_now = True)
	
	class Meta:
		verbose_name = "Produit"
		verbose_name_plural = "Produits"
		ordering = ('provider', 'name')
	
	def __unicode__(self):
		return self.name
	
	def __repr__(self):
		return self.name
	
	@models.permalink
	def get_absolute_url(self):
		return ( 'product_item', [self.id] )
	
	def has_expired(self):
		return self.expiry and self.expiry < datetime.now()
	
	def soon_expired(self):
		delta = timedelta( days = 10 )
		return self.expiry - delta <= datetime.now()
	

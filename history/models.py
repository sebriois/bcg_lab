# -*- encoding: utf8 -*-
from datetime import datetime, date
from django.db import models
from django.contrib.contenttypes import generic
from order.models import Order, OrderItem
from attachments.models import Attachment

class History(models.Model):
	"""
	History should be completely independant from any other table so 
	that when a deletion is made in the DB, it won't affect the history
	"""
	team						= models.CharField(u"Equipe", max_length=100)
	provider				= models.CharField(u"Fournisseur", max_length=100)
	number					= models.CharField(u"N° cde", max_length = 100, null = True, blank = True)
	price						= models.DecimalField(u"Montant total", max_digits=12, decimal_places=2)
	budget					= models.CharField(u"Budget", max_length = 100)
	date_delivered	= models.DateTimeField(u"Date de réception")
	date_created		= models.DateTimeField(u"Date", auto_now_add = True)
	items						= models.ManyToManyField( OrderItem, verbose_name = "Produits" )
	# TODO: comments = models.TextField(u"Commentaires", null = True, blank = True)
	attachments			= generic.GenericRelation( Attachment )
	
	class Meta:
		verbose_name = "Historique"
		verbose_name_plural = "Historique"
		ordering = ('-date_delivered',)
	
	def __unicode__(self):
		d = datetime.strftime( self.date_created, "%d/%m/%Y %Hh%M" )
		return u"%s - %s" % ( self.provider, d )
	
	@models.permalink
	def get_absolute_url(self):
		return ( 'history_detail', [self.id] )
	
	def get_notes(self):
		if not self.number: return ""
		
		order_list = Order.objects.filter( number = self.number, team__name = self.team )
		if order_list.count() > 0:
			return order_list[0].notes
		
		return ""
	

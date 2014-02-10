# -*- encoding: utf8 -*-
import sys
from datetime import datetime, timedelta

from django.db import models
from django.db.models.signals import post_save, pre_save
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic

from provider.models import Provider
from attachments.models import Attachment
from solr import Solr

class ProductType(models.Model):
    name = models.CharField( u"Type", max_length=200 )
    
    class Meta:
        verbose_name = u"Type de produit"
        verbose_name_plural = u"Types de produit"
    
    def __unicode__(self):
        return self.name

class ProductSubType(models.Model):
    category = models.ForeignKey( ProductType, verbose_name = "Type" )
    name = models.CharField( u"Sous-type", max_length=200 )
    
    class Meta:
        verbose_name = u"Sous-type de produit"
        verbose_name_plural = u"Sous-types de produit"
    
    def __unicode__(self):
        return self.name

class ProductCode(models.Model):
    code = models.CharField( u"Code", max_length = 10 )
    title = models.CharField( u"Libellé", max_length = 250 )
    
    class Meta:
        verbose_name = u"Nomenclature"
        ordering = ('code',)
    
    def __unicode__(self):
        return "%s - %s" % (self.code, self.title)

class Product(models.Model):
    provider        = models.ForeignKey( Provider, verbose_name = 'Fournisseur' )
    origin          = models.CharField( u"Fournisseur d'origine", max_length = 100, null = True, blank = True )
    name            = models.CharField( u'Désignation', max_length = 500 )
    packaging       = models.CharField( u'Conditionnement', blank = True, null = True, max_length = 100)
    reference       = models.CharField( u'Référence', max_length = 100)
    price           = models.DecimalField( u'Prix', max_digits=12, decimal_places=2)
    offer_nb        = models.CharField( u'N° Offre', blank = True, null = True, max_length = 100)
    nomenclature    = models.CharField( u'Nomenclature', blank = True, null = True, max_length = 100)
    category        = models.ForeignKey( ProductType, verbose_name = "Type", blank = True, null = True )
    sub_category    = models.ForeignKey( ProductSubType, verbose_name = "Sous-type", blank = True, null = True )
    expiry          = models.DateTimeField( u"Date d'expiration", help_text = u"Format jj/mm/aaaa", blank = True, null = True )
    last_change     = models.DateTimeField( u'Dernière modification', auto_now = True)
    attachments     = generic.GenericRelation( Attachment )
    
    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        ordering = ('provider', 'name')
        # unique_together = ('provider', 'reference')
    
    class Admin:
        pass
    
    def __unicode__(self):
        return self.name
    
    def __repr__(self):
        return self.name
    
    @models.permalink
    def get_absolute_url(self):
        return ( 'product_item', [self.id] )
    
    def has_expired(self):
        return (self.expiry and self.expiry < datetime.now())
    
    def soon_expired(self):
        delta = timedelta( days = 10 )
        return (self.expiry - delta <= datetime.now())
    
    def post_to_solr(self):
        print >> sys.stderr, "POSTing product ID %s to Solr ..." % self.id
        data = {
            'id': "%s" % self.id,
            'product': self.name,
            'reference': self.reference,
            'provider': self.provider.name,
            'origin': self.origin,
            'price': str(self.price),
            'packaging': self.packaging,
            'offer_nb': self.offer_nb,
            'nomenclature': self.nomenclature,
            'category': self.category and self.category.name or None,
            'sub_category': self.sub_category and self.sub_category.name or None,
            'last_change': self.last_change.strftime("%d/%m/%Y"),
            'expiry': self.expiry and self.expiry.strftime("%d/%m/%Y") or None
        }
        
        solr = Solr()
        solr.post( data )
    
    def clean_packaging(self):
        unit_mapping = {
            'ul' : 'µL',
            'uL' : 'µL',
            'µl' : 'µL',
            'ug' : 'µg',
            'ml' : 'mL',
            'ML' : 'mL'
        }
        for old_unit, new_unit in unit_mapping.items():
            self.packaging = self.packaging(k, v)
            self.packaging = self.packaging(" %s" % k, v)
        self.save()

# method for updating solr when a product is saved (after creation or after update)
def update_solr(sender, instance, **kwargs):
    instance.post_to_solr()

def update_expiry(sender, instance, **kwargs):
    if not instance.expiry and not 'expiry' in kwargs:
        year = datetime.now().year
        instance.expiry = datetime(year, 12, 31)
    

# register the signal
# post_save.connect(update_solr, sender=Product, dispatch_uid="update_solr")
pre_save.connect(update_expiry, sender=Product, dispatch_uid="update_expiry")

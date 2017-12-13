# -*- encoding: utf8 -*-
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.utils import timezone
from elasticsearch import Elasticsearch

from provider.models import Provider
from attachments.models import Attachment


class ProductType(models.Model):
    name = models.CharField(u"Type", max_length=200)
    
    class Meta:
        db_table = "product_type"
        verbose_name = u"Type de produit"
        verbose_name_plural = u"Types de produit"
    
    def __str__(self):
        return self.name


class ProductSubType(models.Model):
    category = models.ForeignKey(ProductType, verbose_name = "Type", on_delete=models.CASCADE)
    name = models.CharField(u"Sous-type", max_length=200)
    
    class Meta:
        db_table = "product_subtype"
        verbose_name = u"Sous-type de produit"
        verbose_name_plural = u"Sous-types de produit"
    
    def __str__(self):
        return self.name


class ProductCode(models.Model):
    code = models.CharField(u"Code", max_length = 10)
    title = models.CharField(u"Libellé", max_length = 250)
    
    class Meta:
        db_table = "product_code"
        verbose_name = u"Nomenclature"
        ordering = ('code',)
    
    def __str__(self):
        return "%s - %s" % (self.code, self.title)


class Product(models.Model):
    provider = models.ForeignKey(Provider, verbose_name = 'Fournisseur', on_delete = models.CASCADE)
    origin = models.CharField(u"Fournisseur d'origine", max_length = 100, null = True, blank = True)
    name = models.CharField(u'Désignation', max_length = 500)
    packaging = models.CharField(u'Conditionnement', blank = True, null = True, max_length = 100)
    reference = models.CharField(u'Référence', max_length = 100)
    price = models.DecimalField(u'Prix', max_digits=12, decimal_places=2)
    offer_nb = models.CharField(u'N° Offre', blank = True, null = True, max_length = 100)
    nomenclature = models.CharField(u'Nomenclature', blank = True, null = True, max_length = 100)
    category = models.ForeignKey(ProductType, verbose_name = "Type", blank = True, null = True, on_delete = models.SET_NULL)
    sub_category = models.ForeignKey(ProductSubType, verbose_name = "Sous-type", blank = True, null = True, on_delete = models.SET_NULL)
    expiry = models.DateTimeField(u"Date d'expiration", help_text = u"Format jj/mm/aaaa", blank = True, null = True)
    last_change = models.DateTimeField(u'Dernière modification', auto_now = True)
    attachments = GenericRelation(Attachment)
    
    class Meta:
        db_table = 'product'
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        ordering = ('provider', 'name')
        # unique_together = ('provider', 'reference')
    
    class Admin:
        pass
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.name
    
    @models.permalink
    def get_absolute_url(self):
        return ('product_item', [self.id])
    
    def has_expired(self):
        return (self.expiry and self.expiry < timezone.now())
    
    def soon_expired(self):
        delta = timedelta(days = 10)
        return (self.expiry - delta <= timezone.now())

    def clean_packaging(self):
        unit_mapping = {
            'ul' : 'µL',
            'uL' : 'µL',
            'µl' : 'µL',
            'ug' : 'µg',
            'ml' : 'mL',
            'ML' : 'mL'
        }
        if self.packaging in unit_mapping:
            self.packaging = unit_mapping[self.packaging]
            self.save()


def post_product_save(sender, instance, **kwargs):
    print("indexing product id %s into Elasticsearch ... " % instance.id, end = "")
    es = Elasticsearch()
    es.index(
        settings.SITE_NAME.lower(),
        "products",
        {
            '_id': "%s" % instance.id,
            'provider': instance.provider.name,
            'origin': instance.origin,
            'name': instance.name,
            'reference': instance.reference,
            'offer_nb': instance.offer_nb,
            'nomenclature': instance.nomenclature,
            'category': instance.category and instance.category.name or None,
            'sub_category': instance.sub_category and instance.sub_category.name or None
        }
    )
    print("ok")


def update_expiry(sender, instance, **kwargs):
    if not instance.expiry and not 'expiry' in kwargs:
        year = timezone.now().year
        instance.expiry = datetime(year, 12, 31)
    

# register the signal
post_save.connect(post_product_save, sender=Product, dispatch_uid="post_product_save")
pre_save.connect(update_expiry, sender=Product, dispatch_uid="update_expiry")

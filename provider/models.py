# -*- encoding: utf-8 -*-
import os
from xml.etree.ElementTree import Element, SubElement, tostring
import commands

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

class Provider(models.Model):
    name             = models.CharField( 'Nom', max_length = 100, unique = True)
    users_in_charge  = models.ManyToManyField( User, verbose_name = "Responsables", blank = True, null = True )
    reseller         = models.ForeignKey( "Provider", verbose_name = "Revendeur", blank = True, null = True )
    notes            = models.TextField( 'Notes', blank = True, null = True )
    is_local         = models.BooleanField( u'Magasin ?', default = False )
    is_service       = models.BooleanField( u'Type service ?', default = False )
    direct_reception = models.BooleanField( u'Réception automatique ?', default = False )
    
    class Meta:
        verbose_name = "Fournisseur"
        verbose_name_plural = "Fournisseurs"
        ordering = ('name',)
    
    def __unicode__(self):
        if self.reseller:
            return u"%s (revendeur: %s)" % ( self.name, self.reseller )
        return self.name
    
    def update_solr(self):
        root = Element('add')
        
        for product in self.product_set.all():
            doc = SubElement( root, 'doc' )
            id = SubElement( doc, 'id' )
            id.text = product.id
            
            product = SubElement( doc, 'product' )
            product.text = product.name
            
            reference = SubElement( doc, 'reference' )
            reference.text = product.reference
            
            provider = SubElement( doc, 'provider' )
            provider.text = self.name
            
            origin = SubElement( doc, 'origin' )
            origin.text = product.origin
            
            packaging = SubElement( doc, 'packaging' )
            packaging.text = product.packaging
            
            offer = SubElement( doc, 'offer_nb' )
            offer.text = product.offer_nb
            
            nomenclature = SubElement( doc, 'nomenclature' )
            nomenclature.text = product.nomenclature
            
            if product.category:
                category = SubElement( doc, 'category' )
                category.text = product.category.name
            
            if product.sub_category:
                sub_category = SubElement( doc, 'sub_category' )
                sub_category.text = product.sub_category.name
        
        xml = tostring( root )
        command = "curl %s/update -H 'Content-Type: text/xml' --data-binary '%s'" % ( settings.SOLR_URL, xml )
        commands.getoutput(command)
    
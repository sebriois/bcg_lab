# -*- encoding: utf-8 -*-
import subprocess
from xml.etree.ElementTree import Element, SubElement, tostring

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User


class Provider(models.Model):
    name             = models.CharField('Nom', max_length = 100, unique = True)
    users_in_charge  = models.ManyToManyField(User, verbose_name = "Responsables", blank = True)
    reseller         = models.ForeignKey("Provider", verbose_name = "Revendeur", blank = True, null = True)
    notes            = models.TextField('Notes', blank = True, null = True)
    is_local         = models.BooleanField(u'Magasin ?', default = False)
    is_service       = models.BooleanField(u'Type service ?', default = False)
    direct_reception = models.BooleanField(u'Réception automatique ?', default = False)
    
    class Meta:
        verbose_name = "Fournisseur"
        verbose_name_plural = "Fournisseurs"
        ordering = ('name',)
    
    def __str__(self):
        if self.reseller:
            return u"%s (revendeur: %s)" % (self.name, self.reseller)
        return self.name
    
    def update_solr(self):
        if not settings.SOLR_URL:
            print("settings.SOLR_URL was not set, won't update provider in SolR")
            return

        root = Element('add')
        
        for p in self.product_set.all():
            doc = SubElement(root, 'doc')
            id = SubElement(doc, 'id')
            id.text = str(p.id)
            
            product = SubElement(doc, 'product')
            product.text = p.name
            
            reference = SubElement(doc, 'reference')
            reference.text = p.reference
            
            provider = SubElement(doc, 'provider')
            provider.text = self.name
            
            origin = SubElement(doc, 'origin')
            origin.text = p.origin
            
            packaging = SubElement(doc, 'packaging')
            packaging.text = p.packaging
            
            offer = SubElement(doc, 'offer_nb')
            offer.text = p.offer_nb
            
            nomenclature = SubElement(doc, 'nomenclature')
            nomenclature.text = p.nomenclature
            
            if p.category:
                category = SubElement(doc, 'category')
                category.text = p.category.name
            
            if p.sub_category:
                sub_category = SubElement(doc, 'sub_category')
                sub_category.text = p.sub_category.name
        
        xml = tostring(root)
        
        update_url = "%s/update" % settings.SOLR_URL
        command = "curl %s -H 'Content-Type: text/xml' --data-binary '%s'" % (update_url, xml)
        subprocess.check_output(command, shell = True)
        
        command = "curl %s?commit=true" % update_url
        subprocess.check_output(command, shell = True)

from django.db import models
from provider.models import Provider

class Product(models.Model):
  name          = models.CharField( 'Nom', blank = True, max_length = 100 )
  provider      = models.ForeignKey(Provider)
  packaging     = models.CharField('Conditionnement', blank = True, null = True, max_length = 100)
  reference     = models.CharField('Référence', max_length = 100)
  price         = models.FloatField('Prix', blank=True, null=True, default = 0)
  offer_nb      = models.CharField('N° Offre', blank=True, null=True, max_length = 100)
  code          = models.CharField('Code', blank=True, null=True, max_length = 100)
  nomenclature  = models.CharField('Nomenclature', blank=True, null=True, max_length = 100)
  
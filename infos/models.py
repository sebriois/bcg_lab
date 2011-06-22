from django.db import models

# Create your models here.
class Info(models.Model):
  text = models.TextField(u"Commentaire" )
  expiration = models.DateField(u"Expire le" )

# coding: utf-8
from datetime import timedelta

from django.db import models
from django.utils import timezone


class Info(models.Model):
    text = models.TextField(u"Information" )
    expiry = models.DateField(u"Date d'expiration", help_text = 'NE PAS REMPLIR POUR UNE INFO PERMANENTE', null = True, blank = True)
    date_created = models.DateField(u"Date", auto_now_add = True)

    class Meta:
        db_table = 'info'
        ordering = ('expiry',)

    def has_expired(self):
        return self.expiry and self.expiry <= timezone.now() or False

    def soon_expired(self):
        if not self.expiry:
            return False

        delta = timedelta(days = 10)
        return self.expiry - delta <= timezone.now()

# coding: utf-8
from django.db import models

from bcg_lab.constants import ISSUE_CHOICES, ISSUE_SEVERITY_CHOICES, ISSUE_STATUS_CHOICES


class Issue(models.Model):
    username = models.CharField(u"Utilisateur", max_length=100)
    title = models.CharField(u"Titre", max_length=100)
    description = models.TextField(u"Description", null = True, blank = True)
    issue_type = models.IntegerField(u"Type", choices = ISSUE_CHOICES, default = 0)
    severity = models.IntegerField(u"Sévérité", choices = ISSUE_SEVERITY_CHOICES, default = 1)
    status = models.IntegerField(u"Statut", choices = ISSUE_STATUS_CHOICES, default = 0)
    date_created = models.DateTimeField( u"Date ouverture", auto_now_add = True )
    date_closed = models.DateTimeField( u"Date fermeture", null = True, blank = True )

    class Meta:
        db_table = 'issue'
        verbose_name = u"Bug"
        verbose_name_plural = u"Bugs"
        ordering = ('severity', 'issue_type', 'title')


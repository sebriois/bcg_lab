# encoding: utf8

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

class Attachment(models.Model):
	content_type = models.ForeignKey(ContentType)
	object_id = models.PositiveIntegerField()
	content_object = generic.GenericForeignKey('content_type', 'object_id')
	filename = models.CharField( u"Désignation", max_length = 100 )
	attached_file = models.FileField( verbose_name = u"Pièce jointe", upload_to = "attachments/%Y/%m/%d")

# encoding: utf8
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Attachment(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    filename = models.CharField(u"Désignation", max_length = 500)
    attached_file = models.FileField(verbose_name = u"Pièce jointe", upload_to = "attachments/%Y/%m/%d")

    class Meta:
        db_table = "attachment"

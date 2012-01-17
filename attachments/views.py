# encoding: utf8

from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.simple import direct_to_template

from attachments.forms import AttachmentForm
from attachments.models import Attachment
from utils import *

@login_required
@transaction.commit_on_success
def new(request):
	if request.method == 'GET':
		form = AttachmentForm()
		content_type = request.GET['content_type']
		object_id = request.GET['object_id']
		next = request.GET['next']
	elif request.method == 'POST':
		data = request.POST
		content_type = ContentType.objects.get(id = data['content_type'])
		object_id = data['object_id']
		next = data['next']
		
		form = AttachmentForm( data = data, files = request.FILES )
		if form.is_valid():
			attachment = form.save( commit = False )
			attachment.content_type = content_type
			attachment.object_id = object_id
			attachment.save()
			info_msg( request, "Pièce jointe ajoutée avec succès." )
			return redirect( next )
	
	return direct_to_template( request, "attachments/form.html", {
		'form': form,
		'content_type': content_type,
		'object_id': object_id,
		'next': reverse(next)
	})

@login_required
def delete(request, attachment_id):
	attachment = get_object_or_404( Attachment, id = attachment_id )
	attachment.attached_file.delete()
	attachment.delete()
	
	info_msg(request, "Pièce jointe supprimée avec succès.")
	return redirect( request.GET['next'] )

# coding: utf-8
from datetime import date

from django.shortcuts import get_object_or_404, redirect
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.views.generic.simple import direct_to_template

from infos.models import Info
from infos.forms import InfoForm

from constants import *
from utils import *

@login_required
@team_required
@transaction.commit_on_success
def index(request):
	if request.method == 'GET':
		Info.objects.filter( expiry__lt = date.today() ).delete()
		form = InfoForm()
		
	if request.method == 'POST':
		data = request.POST.copy()
		
		if in_team_secretary( request.user ):
			data['text'] = u'<strong><u>INFO GESTION:</u></strong> %s' % data['text']
		
		form = InfoForm( data = data )
		if form.is_valid():
			form.save()
			form = InfoForm()
	
	return direct_to_template( request, 'homepage.html', {
		'infos': Info.objects.all(),
		'info_form': form
	})

@login_required
@transaction.commit_on_success
def delete(request, info_id):
	info = get_object_or_404( Info, id = info_id )
	info.delete()
	
	return redirect('home')

# coding: utf-8
from datetime import date

from django.shortcuts import get_object_or_404, redirect
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from infos.models import Info
from infos.forms import InfoForm

from bcg_lab.constants import *
from utils import *

@login_required
@transaction.commit_on_success
def index(request):
	Info.objects.filter( expiry__lt = date.today() ).delete()
	return render( request, 'homepage.html', {
		'infos': Info.objects.all()
	})

@login_required
@transaction.commit_on_success
def new(request):
	if request.method == 'GET':
		form = InfoForm()
	elif request.method == 'POST':
		data = request.POST.copy()
		if in_team_secretary( request.user ):
			data['text'] = u'<strong><u>INFO GESTION:</u></strong> %s' % data['text']
		if 'provider' in data.keys() and data['provider']:
			data['text'] = data['provider'] + " : " + data['text']
		
		form = InfoForm( data = data )
		if form.is_valid():
			form.save()
		return redirect('info_index')
	
	return render(request, 'infos/new.html', {
		'form': form
	})

@login_required
@transaction.commit_on_success
def item(request, info_id):
	info = get_object_or_404( Info, id = info_id )
	
	if request.method == 'GET':
		form = InfoForm( instance = info )
	elif request.method == 'POST':
		data = request.POST.copy()
		if 'provider' in data.keys() and data['provider']:
			data['text'] = data['provider'] + " : " + data['text']
		
		form = InfoForm( instance = info, data = data )
		if form.is_valid():
			form.save()
			return redirect( 'info_index' )
	
	return render( request, 'infos/item.html', {
		'form': form,
		'info': info
	})

@login_required
@transaction.commit_on_success
def delete(request, info_id):
	info = get_object_or_404( Info, id = info_id )
	info.delete()
	
	return redirect('info_index')

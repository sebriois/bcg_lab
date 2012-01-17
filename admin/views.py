# coding: utf8
from django.contrib.auth.models import Group, Permission
from django.views.generic.simple import direct_to_template
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction

from admin.forms import GroupForm
from utils import *

@login_required
@transaction.commit_on_success
def group_index(request):
	if request.method == 'GET':
		return direct_to_template( request, 'admin/group_index.html', {
			'groups': Group.objects.all()
		})
	elif request.method == 'POST':
		form = GroupForm(request.POST)
		if form.is_valid():
			data = form.cleaned_data
			group = form.save()
			
			for user in data['users']:
				user.groups.add( group )
			
			for key, value in data.items():
				if key.startswith('custom_') and value == True:
					permission = Permission.objects.get(codename = key)
					group.permissions.add( permission )
			
			info_msg( request, "Groupe ajouté avec succès")
			return redirect( 'group_index' )
		else:
			error_msg( request, "Impossible de créer le groupe." )
			return direct_to_template( request, 'group_new', {
				'form': form
			})

@login_required
@transaction.commit_on_success
def group_item(request, group_id):
	group = get_object_or_404( Group, id = group_id )
	
	if request.method == "GET":
		form = GroupForm( instance = group )
	elif request.method == "POST":
		form = GroupForm( instance = group, data = request.POST )
		if form.is_valid():
			data = form.cleaned_data
			form.save()
			
			group.user_set.clear()
			group.permissions.clear()
			group.save()
			
			for user in data['users']:
				user.groups.add( group )
			
			for key, value in data.items():
				if key.startswith('custom_') and value == True:
					permission = Permission.objects.get(codename = key)
					group.permissions.add( permission )
			
			info_msg( request, "Groupe modifié avec succès")
			return redirect( "group_index" )
		else:
			error_msg( request, "Impossible de modifier le groupe." )
	
	return direct_to_template( request, 'admin/group_item.html', {
		'form': form,
		'group': group
	})

@login_required
def group_new(request):
	return direct_to_template( request, 'admin/group_new.html', {
		'form': GroupForm()
	})

@login_required
@transaction.commit_on_success
def group_delete(request, group_id):
	group = get_object_or_404( Group, id = group_id )
	group.delete()
	
	info_msg( request, "Groupe supprimé avec succès.")
	
	return redirect('group_index')

	
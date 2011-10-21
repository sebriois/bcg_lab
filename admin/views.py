from django.contrib.auth.models import Group, Permission
from django.views.generic.simple import direct_to_template
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction

from admin.forms import GroupForm

def group_index(request):
	if request.method == 'GET':
		return direct_to_template( request, 'admin/group_index.html', {
			'groups': Group.objects.all()
		})
	elif request.method == 'POST':
		form = GroupForm(request.POST)
		if form.is_valid():
			form.save()
			return redirect( 'group_index' )
		else:
			return direct_to_template( request, 'group_new', {
				'form': form
			})
	

def group_item(request, group_id):
	group = get_object_or_404( Group, id = group_id )
	
	if request.method == "GET":
		form = GroupForm( instance = group )
	elif request.method == "POST":
		form = GroupForm( instance = group, data = request.POST )
		if form.is_valid():
			form.save()
			return redirect( "group_index" )
	
	return direct_to_template( request, 'admin/group_item.html', {
		'form': form,
		'group': group
	})

def group_new(request):
	return direct_to_template( request, 'admin/group_new.html', {
		'form': GroupForm()
	})

def perm_index(request):
	return direct_to_template( request, 'admin/perm_index.html', {
		'permissions': Permission.objects.all()
	})

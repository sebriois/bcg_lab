# coding: utf-8
from django.shortcuts import get_object_or_404, redirect
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.views.generic.simple import direct_to_template

from provider.models import Provider
from provider.forms import ProviderForm

from constants import *
from utils import *

@login_required
@transaction.commit_on_success
def index(request):
	if request.method == 'GET':
		return direct_to_template(request, 'provider/index.html',{
			'provider_list': Provider.objects.filter(is_service = False)
		})
	elif request.method == 'POST':
		form = ProviderForm(request.POST)
		if form.is_valid():
			form.save()
			info_msg( request, u"Fournisseur ajouté avec succès." )
			return redirect( 'provider_index' )
		else:
			return direct_to_template(request, 'provider/form.html',{
					'form': form
			})

@login_required
@transaction.commit_on_success
def item(request, provider_id):
	provider = get_object_or_404(Provider, id = provider_id)
	if request.method == 'GET':
		form = ProviderForm(instance = provider)
	elif request.method == 'POST':
		form = ProviderForm(instance = provider, data = request.POST)
		if form.is_valid():
			form.save()
			
			for product in provider.product_set.all():
				if not product.origin: product.origin = provider.name
				product.provider = provider.reseller
				product.save()
			
			info_msg( request, u"Fournisseur modifié avec succès." )
			return redirect( 'provider_index' )
	
	return direct_to_template(request, 'provider/item.html',{
		'provider': provider,
		'form': form
	})

@login_required
def new(request):
	return direct_to_template(request, 'provider/form.html', {
		'form': ProviderForm()
	})

@login_required
@transaction.commit_on_success
def delete(request, provider_id):
	provider = get_object_or_404(Provider, id = provider_id)
	
	if request.method == 'GET':
		return direct_to_template(request, "provider/delete.html", {
			'provider': provider
		})
	elif request.method == 'POST':
		provider.delete()
		info_msg( request, u"Fournisseur supprimé avec succès." )
		return redirect( 'provider_index' )

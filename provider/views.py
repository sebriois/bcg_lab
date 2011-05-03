# coding: utf-8
from datetime import datetime, date

from django.shortcuts import get_object_or_404, redirect
from django.db.models.query import Q
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.views.generic.simple import direct_to_template

from provider.models import Provider
from provider.forms import ProviderForm

from constants import *
from utils import info_msg, error_msg, warn_msg, superuser_required


@login_required
@transaction.commit_on_success
def index(request):
    if request.method == 'GET':   return _provider_list(request)
    if request.method == 'POST':  return _provider_creation(request)

@login_required
@transaction.commit_on_success
def item(request, provider_id):
    provider = get_object_or_404(Provider, id = provider_id)
    if request.method == 'GET':     return _provider_detail(request, provider)
    if request.method == 'PUT':     return _provider_update(request, provider)
    if request.method == 'DELETE':  return _provider_delete(request, provider)

@login_required
@superuser_required
def new(request):
    return direct_to_template(request, 'provider/form.html', { 'form': ProviderForm() })

@login_required
@superuser_required
def delete(request, provider_id):
    """ Confirmation page for deletion. """
    provider = get_object_or_404(Provider, id = provider_id)
    return direct_to_template(request, "provider/delete.html", { 'provider': provider })

#--- Private views
def _provider_list(request):
    return direct_to_template(request, 'provider/index.html',{
        'provider_list': Provider.objects.all()
    })

def _provider_detail(request, provider):
    form = ProviderForm(instance = provider)
    return direct_to_template(request, 'provider/item.html',{
        'provider': provider,
        'form': form
    })

def _provider_creation(request):
  form = ProviderForm(request.POST)
  if form.is_valid():
    provider = form.save()
    
    info_msg( request, u"Fournisseur ajouté avec succès." )
    return redirect( 'provider_index' )
  else:
    return direct_to_template(request, 'provider/form.html',{
        'form': form
    })

def _provider_update(request, provider):
    form = ProviderForm(instance = provider, data = request.REQUEST)
    if form.is_valid():
        provider = form.save()
        
        info_msg( request, u"Fournisseur modifié avec succès." )
        return redirect( 'provider_index' )
    else:
        return direct_to_template(request, 'provider/item.html',{
            'provider': provider,
            'form': form
        })

def _provider_delete(request, provider):
    provider.delete()
    info_msg( request, u"Fournisseur supprimé avec succès." )
    return redirect( 'provider_index' )

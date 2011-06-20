# coding: utf-8

import datetime
import csv
from decimal import Decimal

from django.utils import simplejson as json
from django.views.generic.simple import direct_to_template
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.db import transaction

from provider.models import Provider
from product.models import Product
from provider.forms import ImportForm

from constants import *
from utils import *

class ImportCSVException(Exception):
  """
  Raised on any error found when processing CSV file
  """


@login_required
def export_csv( request, provider_id ):
  provider = get_object_or_404( Provider, id = provider_id )
  
  response = render_to_response("provider/export.csv", {
      'products': provider.product_set.all()
  })
  filename = "%s.csv" % (provider.name)
  response['Content-Disposition'] = 'attachment; filename='+filename
  response['Content-Type'] = 'application/vnd.ms-excel; charset=utf-8'
  
  return response

@login_required
def import_csv( request, provider_id ):
  provider = get_object_or_404( Provider, id = provider_id )
  
  if request.method == 'GET':
    form = ImportForm()
    data = None
  elif request.method == 'POST':
    form = ImportForm(data = request.POST, files = request.FILES)
    data = None
    
    if form.is_valid():
      try:
        data = check_uploaded_file( request.FILES['csv_file'] )
        request.session['import_csv_data'] = json.dumps({ 'data': data }).encode('utf8')
        info_msg( request, u'Fichier accepté. Veuillez valider la mise à jour des produits.' )
      except ImportCSVException, e:
        error_msg( request, str(e) )
        return redirect( reverse('import_products', args=[provider_id]) )
  
  return direct_to_template(request, 'provider/import.html', {
    'form': form,
    'data': data,
    'provider': provider
  })
  


def check_uploaded_file( file ):
  """
  Validate uploaded file.
  """
  if not file.name.endswith('.csv'):
    raise ImportCSVException, "Ce fichier n'est pas au format csv."
  
  result_table = []
  errors = []
  header = {}
  expected_headers = [
    'designation',
    'reference',
    'prix',
    'conditionnement',
    'offre',
    'nomenclature'
  ]
  
  for num_line, line in enumerate( file ):
    base_error = "Ligne %s - " % (num_line + 1)
    line = line.decode('utf8').encode('utf8').rstrip('\n').split(";")
    # line = line.decode('latin').encode('utf8').rstrip('\n').split(";")
    
    if len(line) != 6:
      error = "%s colonnes trouvées sur 6 attendues." % len(line)
      errors.append( base_error + error )
      break
    
    if num_line == 0:
      for i, head in enumerate(line):
        kept_head = head.lower().strip().replace('é', 'e')
        
        if kept_head in expected_headers:
          header[kept_head] = i
        else:
          error = "cette entête (%s) ne fait pas partie des entêtes acceptées. %s" % (head, kept_head)
          errors.append( base_error + error )
          raise ImportCSVException( "Veuillez corriger les erreurs suivantes:<br />" + "<br />".join(errors) )
        
      result_table.append( line )
      continue
    
    
    if not line[header['designation']]:
      errors.append( base_error + "une désignation est requise."  )
    
    if not line[header['reference']]:
      errors.append( base_error + "une référence est requise."  )
    
    try:
      price = Decimal(line[header['prix']].replace(" ","").replace(",",".").replace('€',''))
      if not price or price <= 0:
        errors.append( base_error + "un prix strictement positif est requis."  )
    except:
      errors.append( base_error + "le prix doit être un nombre décimal strictement positif et ne doit pas contenir de sigle '€'.")
    
    if not errors:
      result_table.append( line )
  
  if errors:
    raise ImportCSVException( "Veuillez corriger les erreurs suivantes:<br />" + "<br />".join(errors) )
  else:
    return result_table


@login_required
@GET_method
@transaction.commit_on_success
def perform_import_csv( request, provider_id ):
  provider = get_object_or_404( Provider, id = provider_id )
  provider.product_set.all().delete()
  
  if not 'import_csv_data' in request.session:
    warn_msg( request, "Une erreur de session est survenue. Veuillez \
d'abord vérifier votre historique pour savoir si l'import CSV a été \
effectué. Autrement, essayez à nouveau (cette erreur est relative à \
votre navigateur)." )
    return redirect( reverse('import_products', args=[provider_id]) )
  
  # Loads data from cookie - dumped as json when the file was imported
  csv_data = json.loads( request.session['import_csv_data'] )
  
  header = {}
  for num_line, line in enumerate(csv_data['data']):
    if num_line == 0:
      for i, head in enumerate(line):
        head = head.lower().strip().replace(u'é', u'e')
        header[head] = i
      continue
    
    price = Decimal(line[header['prix']].replace(" ","").replace(",",".").replace(u'€',u''))
    
    Product.objects.create(
      provider      = provider,
      name          = line[header['designation']],
      reference     = line[header['reference']],
      packaging     = line[header['conditionnement']],
      price         = price,
      offer_nb      = line[header['offre']],
      nomenclature  = line[header['nomenclature']]
    )
  
  del request.session['import_csv_data']
  
  info_msg(request, u'La mise à jour des produits a bien été effectuée.')
  return redirect( 'provider_index' )

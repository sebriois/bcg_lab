# coding: utf-8

import datetime
import xlrd
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


@login_required
def import_xls( request, provider_id ):
	provider = get_object_or_404( Provider, id = provider_id )
	
	if request.method == 'GET':
		form = ImportForm()
	elif request.method == 'POST':
		form = ImportForm(data = request.POST, files = request.FILES)
		
		if form.is_valid():
			head_str = request.POST['column_order'].lower().replace('*','').replace(u"é",'e')
			header = head_str.split(';')
			data = []
			
			errors = read_xls( header, data, request.FILES['xls_file'] )
			
			request.session['import_data'] = json.dumps({
				'header': header,
				'data': data
			}).encode('utf8')
			
			if errors:
				msg = u"Les lignes suivantes seront ignorées lors de l'import:<br />"
				msg += u"<br />".join(errors)
				warn_msg( request, msg )
			else:
				info_msg( request, u'Fichier accepté. Veuillez valider la mise à jour des produits.' )
			return direct_to_template(request, 'provider/import_preview.html', {
				'header': header,
				'data': data,
				'provider': provider,
				'replace_all': request.POST.get('replace_all',False)
			})
	
	return direct_to_template(request, 'provider/import.html', {
		'form': form,
		'provider': provider
	})

def read_xls( header, data, input_excel ):
	book = xlrd.open_workbook( file_contents = input_excel.read() )
	sheet = book.sheet_by_index(0)
	
	errors = []
	
	for row_idx in range(sheet.nrows):
		row = sheet.row(row_idx)
		is_valid = 'true'
		base_error = u"Ligne %s - " % (row_idx + 1)
		
		# CHECK NAME
		name_idx = header.index(u"designation")
		name = row[name_idx].value
		if not name:
			is_valid = 'false'
			errors.append( base_error + u"Colonne 'désignation' - la désignation est manquante." )
		
		# CHECK REFERENCE
		ref_idx = header.index(u"reference")
		ref = row[ref_idx].value
		if not ref:
			is_valid = 'false'
			errors.append( base_error + u"Colonne 'référence' - la référence est manquante." )
		
		# CHECK PRICE
		price_idx = header.index(u"prix")
		price = row[price_idx].value
		
		if isinstance(price, str):
			price = price.replace(" ","").replace(",",".").replace('€','')
		try:
			price = Decimal(price)
		except:
			is_valid = 'false'
			errors.append( base_error + u"Colonne 'prix' - impossible de lire une valeur décimale. Valeur reçue: '%s'." % price)
		
		if price:
			if price <= 0:
				is_valid = 'false'
				errors.append( base_error + u"Colonne 'prix' - le prix est négatif ou nul, il doit être strictement positif." )
		else:
			is_valid = 'false'
			errors.append( base_error + u"Colonne 'prix' - la colonne prix est vide." )
		
		row = [is_valid] + [col.value for col in row[0:6]]
		data.append( row )
	
	return errors


@login_required
@GET_method
@transaction.commit_on_success
def do_import( request, provider_id ):
	provider = get_object_or_404( Provider, id = provider_id )
	if not 'import_data' in request.session:
		warn_msg( request, "Une erreur de session est survenue. Veuillez \
d'abord vérifier votre historique pour savoir si l'import CSV a été \
effectué. Autrement, essayez à nouveau (cette erreur est relative à \
votre navigateur)." )
		return redirect( reverse('import_products', args=[provider_id]) )
	
	# Loads data from cookie - dumped as json when the file was imported
	xls_data = json.loads( request.session['import_data'] )
	kept_items = map(int, request.GET['items'].split(','))
	
	if request.GET['replace_all'] == 'on':
		provider.product_set.all().delete()
	
	header = xls_data['header']
	name_idx = header.index(u'designation') + 1
	ref_idx = header.index(u'reference') + 1
	price_idx = header.index(u'prix') + 1
	pack_idx = header.index(u'conditionnement') + 1
	offer_idx = header.index(u"n° d'offre") + 1
	nom_idx = header.index(u'nomenclature') + 1
	origin_idx = header.index(u"fournisseur d'origine") + 1
	
	for i in kept_items:
		if xls_data['data'][0] == 'false': continue # ie. is_valid = false, invalid line
		
		line = xls_data['data'][i]
		
		price = line[price_idx]
		if isinstance(price, str):
			price = price.replace(" ","").replace(",",".").replace('€','')
		price = Decimal(price)
		
		product, created = Product.objects.get_or_create(
			provider = provider,
			reference = line[ref_idx],
			defaults = {
				'name' : line[name_idx],
				'price' : price
			}
		)
		
		if len(line) > pack_idx and line[pack_idx]:
			product.packaging = line[pack_idx]
		
		if len(line) > offer_idx and line[offer_idx]:
			product.offer_nb = line[offer_idx]
		
		if len(line) > nom_idx and line[nom_idx]:
			product.nomenclature = line[nom_idx]
		
		if len(line) > origin_idx and line[origin_idx]:
			product.origin = line[origin_idx]
		
		if not created:
			product.name = line[name_idx]
			product.price = price
		
		product.save()
	
	del request.session['import_data']
	
	info_msg(request, u'La mise à jour des produits a bien été effectuée.')
	return redirect( 'provider_index' )

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
			header, data = [], []
			for i, column in enumerate(request.POST['column_order'].split(';')):
				header.append( column.lower().replace('*','') )
			data.append(header)
			
			errors = read_xls( header, data, request.FILES['xls_file'] )
			request.session['import_data'] = json.dumps({ 'data': data }).encode('utf8')
			
			if errors:
				msg = "Veuillez corriger les erreurs suivantes:<br />" + "<br />".join(errors)
				error_msg( request, msg )
				# return redirect( reverse('import_products', args=[provider_id]) )
			else:
				info_msg( request, u'Fichier accepté. Veuillez valider la mise à jour des produits.' )
				return direct_to_template(request, 'provider/import_preview.html', {
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
		base_error = "Ligne %s - " % (row_idx + 1)
		
		# CHECK NAME
		name_idx = header.index(u"désignation")
		name = row[name_idx].value
		if not name:
			errors.append( base_error + "Colonne %s/%s - la désignation est manquante." % (name_idx+1, len(row)))
			continue
		
		# CHECK REFERENCE
		ref_idx = header.index(u"référence")
		ref = row[ref_idx].value
		if not name:
			errors.append( base_error + "Colonne %s/%s - la référence est manquante." % (ref_idx+1, len(row)))
			continue
		
		# CHECK PRICE
		price_idx = header.index(u"prix")
		price = row[price_idx].value
		
		if isinstance(price, str):
			price = price.replace(" ","").replace(",",".").replace('€','')
		try:
			price = Decimal(price)
		except InvalidOperation:
			errors.append( base_error + "Colonne %s/%s - ce prix n'est pas lisible: %s." % (price_idx+1,len(row),price))
		
		if price:
			if price <= 0:
				errors.append( base_error + "Colonne %s/%s - le prix est négatif ou nul, il doit être strictement positif." % (price_idx+1,len(row)) )
				continue
		else:
			errors.append( base_error + "Colonne %s/%s - la colonne prix est vide." % (price_idx+1, len(row)) )
			continue
		
		data.append( [col.value for col in row[0:6]] )
	
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
	
	header = {}
	for num_line, line in enumerate(xls_data['data']):
		if num_line == 0:
			for i, head in enumerate(line):
				head = head.lower().strip().replace(u'é', u'e')
				header[head] = i
			continue

		# Skip this line if not checked
		if not num_line in kept_items: continue

		price = line[header['prix']]
		if isinstance(price, str):
			price = price.replace(" ","").replace(",",".").replace('€','')
		price = Decimal(price)

		product, created = Product.objects.get_or_create(
			provider = provider,
			reference = line[header['reference']],
			defaults = {
				'name' : line[header['designation']],
				'price' : price
			}
		)
		
		if len(line) > header['conditionnement'] and line[header['conditionnement']]:
			product.packaging = line[header['conditionnement']]
		
		if len(line) > header[u"n° d'offre"] and line[header[u"n° d'offre"]]:
			product.offer_nb = line[header[u"n° d'offre"]]
		
		if len(line) > header['nomenclature'] and line[header['nomenclature']]:
			product.nomenclature = line[header['nomenclature']]
		
		if len(line) > header["fournisseur d'origine"] and line[header["fournisseur d'origine"]]:
			product.origin = line[header["fournisseur d'origine"]]
		
		if not created:
			product.name = line[header['designation']]
			product.price = price
		
		product.save()
	
	del request.session['import_data']
	
	info_msg(request, u'La mise à jour des produits a bien été effectuée.')
	return redirect( 'provider_index' )

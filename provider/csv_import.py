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
			header = {column.lower().replace('*','') : i for i, column in enumerate(request.POST['column_order'].split(';'))}
			try:
				data = check_uploaded_file( header, request.FILES['csv_file'] )
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
	


def check_uploaded_file( header, file ):
	"""
	Validate uploaded file.
	"""
	if not file.name.endswith('.csv'):
		raise ImportCSVException, "Ce fichier n'est pas au format csv."
	
	result_table = []
	errors = []
	
	sorted_vals = sorted(header.values())
	sorted_keys = []
	for val in sorted_vals:
		for h, pos in header.items():
			if pos == val:
				sorted_keys.append( h )
	result_table.append(sorted_keys)
	
	# pre-process file by removing annoying microsoft's ^M shit end of line
	lines = file.readlines()
	if len(lines) == 1:
		lines = lines[0].split("\r")
	
	for num_line, line in enumerate( lines ):
		base_error = "Ligne %s - " % (num_line + 1)
		try:
			line = line.decode('utf8').encode('utf8').split(";")
		except:
			line = line.decode('latin').encode('utf8').split(";")
		
		try:
			price_str = line[header['prix']].replace(" ","").replace(",",".").replace('€','')
			
			if not price_str:
				errors.append( base_error + "Colonne %s/%s - la colonne prix est vide." % (str(header['prix'] + 1),len(line)) )
			
			else:
				price = Decimal( price_str )
				if price <= 0:
					errors.append( base_error + "Colonne %s/%s - le prix est \
négatif ou nul, il doit être strictement positif." % (str(header['prix'] + 1),len(line)) )
		except:
			errors.append( base_error + "Colonne %s/%s - impossible de lire \
une valeur décimale (prix) dans cette colonne. \
Valeur lue: %s" % (str(header['prix'] + 1),len(line),price_str) )
		
		if not errors:
			result_table.append( line[0:6] )
	
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
		
		product = Product.objects.create(
			provider			= provider,
			name					= line[header['designation']],
			reference			= line[header['reference']],
			price					= price
		)
		
		if len(line) > header['conditionnement']:
			product.packaging = line[header['conditionnement']]
		
		if len(line) > header[u"n° d'offre"]:
			product.offer_nb = line[header[u"n° d'offre"]]
		
		if len(line) > header['nomenclature']:
			product.nomenclature = line[header['nomenclature']]
		
		if len(line) > header["fournisseur d'origine"]:
			product.origin = line[header["fournisseur d'origine"]]
		
		product.save()
	
	del request.session['import_csv_data']
	
	info_msg(request, u'La mise à jour des produits a bien été effectuée.')
	return redirect( 'provider_index' )

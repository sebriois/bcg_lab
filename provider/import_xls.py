# coding: utf-8
# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)
from django.utils.encoding import smart_unicode

from datetime import datetime
import xlrd
from decimal import Decimal

from django.utils import simplejson as json
from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.db import transaction

from provider.models import Provider
from product.models import Product
from provider.forms import ImportForm

from bcg_lab.constants import *
from utils import *


@login_required
def import_xls( request, provider_id ):
    provider = get_object_or_404( Provider, id = provider_id )
    
    if request.method == 'GET':
        form = ImportForm()
    elif request.method == 'POST':
        form = ImportForm(data = request.POST, files = request.FILES)
        
        if form.is_valid():
            form_data = form.cleaned_data
            head_str = request.POST['column_order'].lower().replace('*','').replace(u"é",'e')
            header = head_str.split(';')
            data = []
            
            errors = read_xls( header, data, request.FILES['xls_file'] )
            
            request.session['import_data'] = json.dumps({
                'header': header,
                'data': data,
                'offer_nb': form_data.get('offer_nb', None),
                'expiry': form_data.get('expiry', None)
            }).encode('utf8')
            
            if errors:
                msg = u"Les lignes suivantes seront ignorées lors de l'import:<br />"
                msg += u"<br />".join(errors)
                warn_msg( request, msg )
            else:
                info_msg( request, u'Fichier accepté. Veuillez valider la mise à jour des produits.' )
            return render(request, 'provider/import_preview.html', {
                'header': header,
                'data': data,
                'provider': provider,
                'replace_all': request.POST.get('replace_all',False)
            })
    
    return render(request, 'provider/import.html', {
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
            errors.append( base_error + u"Colonne 'désignation' - valeur manquante." )
        if len(name) >= 500:
            is_valid = 'false'
            errors.append( base_error + u"Colonne 'désignation' - valeur trop longue (%s/500 charactères)" % len(name))
        
        # CHECK REFERENCE
        ref_idx = header.index(u"reference")
        ref = unicode(row[ref_idx].value)
        if not ref:
            is_valid = 'false'
            errors.append( base_error + u"Colonne 'référence' - valeur est manquante." )
        if len(ref) >= 100:
            is_valid = 'false'
            errors.append( base_error + u"Colonne 'référence' - valeur trop longue (%s/100 charactères)" % len(ref))
        
        # CHECK PACKAGING
        pack_idx = header.index(u"conditionnement")
        pack = unicode(row[pack_idx].value)
        if len(pack) >= 100:
            is_valid = 'false'
            errors.append( base_error + u"Colonne 'conditionnement' - valeur trop longue (%s/100 charactères)" % len(pack))
        
        # CHECK EXPIRY
        expiry_idx = header.index(u"expiration")
        expiry_str = row[expiry_idx].value
        
        if expiry_str:
            try:
                expiry = datetime.strptime(expiry_str, "%d/%m/%Y")
            except:
                is_valid = 'false'
                errors.append( base_error + u"Colonne 'expiration' - date invalide : %s (format accepté: jj/mm/aaaa)" % expiry_str)
        
        # CHECK PRICE
        price_idx = header.index(u"prix")
        price = unicode(row[price_idx].value)
        price = price.replace(' ','').replace(',','.').replace(u"€",'')
        if not price:
            is_valid = 'false'
            errors.append( base_error + u"Colonne 'prix' - valeur manquante." )
        else:
            try:
                price = Decimal(price)
                if price <= 0:
                    is_valid = 'false'
                    errors.append( base_error + u"Colonne 'prix' - le prix est négatif ou nul, il doit être strictement positif." )
            except:
                is_valid = 'false'
                errors.append( base_error + u"Colonne 'prix' - impossible de lire une valeur décimale. Valeur reçue: '%s'." % row[price_idx].value)
        
        new_row = [is_valid]
        for colIdx, col in enumerate(row[0:8]): 
            col = col.value
            
            if colIdx in (pack_idx, ref_idx):
                new_row.append( unicode(col).rstrip(",0").rstrip(".") )
            elif colIdx == price_idx:
                price = unicode(col).replace(' ','').replace(',','.').replace(u"€",'')
                new_row.append( price )
            else:
                new_row.append( col )
        
        data.append( new_row )
    
    return errors


@login_required
@transaction.commit_on_success
def do_import( request, provider_id ):
    provider = get_object_or_404( Provider, id = provider_id )
    
    if not 'import_data' in request.session:
        warn_msg( request, "Une erreur de session est survenue. Veuillez \
d'abord vérifier votre historique pour savoir si l'import Excel a été \
effectué. Autrement, essayez à nouveau (cette erreur est relative à \
votre navigateur)." )
        return redirect( reverse('import_products', args=[provider_id]) )
    
    # Loads data from cookie - dumped as json when the file was imported
    json_data = json.loads( request.session['import_data'] )
    
    if request.POST['replace_all'] == 'on':
        provider.product_set.all().delete()
    
    # First index in header is "is_valid" (true/false)
    name_idx   = json_data['header'].index(u'designation') + 1
    ref_idx    = json_data['header'].index(u'reference') + 1
    price_idx  = json_data['header'].index(u'prix') + 1
    pack_idx   = json_data['header'].index(u'conditionnement') + 1
    nom_idx    = json_data['header'].index(u'nomenclature') + 1
    origin_idx = json_data['header'].index(u"fournisseur d'origine") + 1
    offer_idx  = json_data['header'].index(u"offre") + 1
    expiry_idx = json_data['header'].index(u"expiration") + 1
    
    # For each checked item
    for item in filter( lambda key: key.startswith("item_"), request.POST.keys() ):
        line = json_data['data'][int(item.split("_")[1])]
        
        price = line[price_idx]
        if isinstance(price, str):
            price = unicode(price).replace(' ','').replace(',','.').replace(u"€",'')
        price = Decimal(price)
        
        if len(line) > pack_idx and line[pack_idx]:
            packaging = line[pack_idx]
        else:
            packaging = None
        
        if len(line) > nom_idx and line[nom_idx]:
            nomenclature = line[nom_idx]
        else:
            nomenclature = None
        
        if len(line) > origin_idx and line[origin_idx]:
            origin = line[origin_idx]
        else:
            origin = None
        
        product, created = Product.objects.get_or_create(
            provider = provider,
            reference = line[ref_idx],
            defaults = {
                'name' : line[name_idx],
                'price' : price,
                'packaging': packaging,
                'nomenclature': nomenclature,
                'origin': origin
            }
        )
        if not created:
            product.price = price
        
        if len(line) > offer_idx and line[offer_idx]:
            product.offer_nb = line[offer_idx]
        elif 'offer_nb' in json_data and json_data['offer_nb']:
            product.offer_nb = json_data['offer_nb']
        
        if len(line) > expiry_idx and line[expiry_idx]:
            product.expiry = datetime.strptime(line[expiry_idx], "%d/%m/%Y")
        elif 'expiry' in json_data and json_data['expiry']:
            product.expiry = datetime.strptime(json_data['expiry'], "%d/%m/%Y")
        
        product.save()
    
    del request.session['import_data']
    
    provider.users_in_charge.add( request.user )
    provider.save()
    info_msg(request, u'La mise à jour des produits a bien été effectuée.')
    return redirect( reverse('product_index') + "?provider=%s&connector=OR" % provider.id )

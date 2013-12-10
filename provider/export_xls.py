# coding: utf-8

import xlwt

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from provider.models import Provider

@login_required
def export_xls( request, provider_id ):
    provider = get_object_or_404( Provider, id = provider_id )
    
    xls = xlwt.Workbook()
    sheet = xls.add_sheet('Produits')
    
    sheet.write(0,0,u"Désignation")
    sheet.write(0,1,u"Référence")
    sheet.write(0,2,u"Prix")
    sheet.write(0,3,u"Conditionnement")
    sheet.write(0,4,u"Nomenclature")
    sheet.write(0,5,u"Fournisseur d'origine")
    sheet.write(0,6,u"N° d'offre")
    sheet.write(0,7,u"Expiration")
    sheet.write(0,8,u"Mise à jour")
    
    for row, product in enumerate(provider.product_set.all()):
        sheet.write(row+1,0,product.name)
        sheet.write(row+1,1,product.reference)
        sheet.write(row+1,2,product.price)
        sheet.write(row+1,3,product.packaging)
        sheet.write(row+1,4,product.nomenclature)
        sheet.write(row+1,5,product.origin)
        sheet.write(row+1,6,product.offer_nb)
        if product.expiry:
            sheet.write(row+1,7,product.expiry.strftime("%d/%m/%Y"))
        else:
            sheet.write(row+1,7,'')
        sheet.write(row+1,8,product.last_change.strftime("%d/%m/%Y"))
        
    
    response = HttpResponse(mimetype="application/ms-excel")
    response['Content-Disposition'] = u"attachment; filename=export_produits_%s.xls" % provider.name.lower()
    response['Content-Type'] = 'application/vnd.ms-excel; charset=utf-8'
    xls.save(response)
    
    return response

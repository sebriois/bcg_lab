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
	sheet.write(0,1,u"Réference")
	sheet.write(0,2,u"Prix")
	sheet.write(0,3,u"Conditionnement")
	sheet.write(0,4,u"Offre")
	sheet.write(0,5,u"Nomenclature")
	for row, product in enumerate(provider.product_set.all()):
		sheet.write(row+1,0,product.name)
		sheet.write(row+1,1,product.reference)
		sheet.write(row+1,2,product.price)
		sheet.write(row+1,3,product.packaging)
		sheet.write(row+1,4,product.offer_nb)
		sheet.write(row+1,5,product.nomenclature)
	
	response = HttpResponse(mimetype="application/ms-excel")
	response['Content-Disposition'] = 'attachment; filename=%s.xls' % provider.name
	response['Content-Type'] = 'application/vnd.ms-excel; charset=utf-8'
	xls.save(response)
	
	return response

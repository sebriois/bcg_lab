# coding: utf8

import xlwt

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from provider.models import Provider
from budget.models import BudgetLine
from history.models import History

@login_required
def export_all_budgets(request):
	return _export_budgets(request, is_active = True)

@login_required
def export_history_budgets(request):
	return _export_budgets(request, is_active = False)

def _export_budgets(request, is_active):
	xls = xlwt.Workbook()
	
	header = [u"BUDGET", u"N°CMDE",u"DATE", u"NATURE", 
	u"TUTELLE", u"FOURNISSEUR", u"COMMENTAIRE", u"DESIGNATION", 
	u"CREDIT", u"DEBIT", u"QUANTITE", u"TOTAL", u"MONTANT DEPENSE", 
	u"MONTANT DISPO"]
	prev_budget = None
	prev_team = None
	row = 0
	
	for bl in BudgetLine.objects.filter(is_active = is_active).order_by("team","budget"):
		if prev_team != bl.team:
			prev_team = bl.team
			prev_budget = None
			if len( bl.team ) >= 32:
				sheet = xls.add_sheet(u"%s..." % bl.team[0:28])
			else:
				sheet = xls.add_sheet(u"%s" % bl.team)
			row = 0
			for col, title in enumerate(header): sheet.write(row, col, title)
		
		if prev_budget != bl.budget:
			row += 1
			prev_budget = bl.budget
		
		sheet.write( row, 0, bl.budget )
		sheet.write( row, 1, bl.number )
		sheet.write( row, 2, bl.date.strftime("%d/%m/%Y") )
		sheet.write( row, 3, bl.nature )
		sheet.write( row, 4, bl.get_budget_type_display() )
		sheet.write( row, 5, bl.provider )
		sheet.write( row, 6, bl.offer )
		sheet.write( row, 7, bl.product )
		sheet.write( row, 8, bl.credit )
		sheet.write( row, 9, bl.debit )
		sheet.write( row, 10, bl.quantity )
		sheet.write( row, 11, bl.product_price )
		sheet.write( row, 12, str(bl.get_amount_spent()) )
		sheet.write( row, 13, str(bl.get_amount_left()) )
		row += 1
	
	if is_active:
		filename = "export_all_budgets.xls"
	else:
		filename = "export_history_budgets.xls"
	
	response = HttpResponse(mimetype='application/ms-excel')
	response['Content-Disposition'] = "attachment; filename=%s" % filename
	response['Content-Type'] = 'application/vnd.ms-excel; charset=utf-8'
	xls.save(response)
	
	return response


@login_required
def export_all_products(request):
	xls = xlwt.Workbook()
	
	for provider in Provider.objects.filter( is_service = False ):
		if len( provider.name ) >= 32:
			sheet = xls.add_sheet(u"%s..." % provider.name[0:28] )
		else:
			sheet = xls.add_sheet(u"%s" % provider.name )
		sheet.write(0,0,u"Désignation")
		sheet.write(0,1,u"Conditionnement")
		sheet.write(0,2,u"Réference")
		sheet.write(0,3,u"Prix")
		sheet.write(0,4,u"Offre")
		sheet.write(0,5,u"Expiration")
		sheet.write(0,6,u"Nomenclature")
		
		for row, product in enumerate(provider.product_set.all()):
			if product.expiry:
				expiry = product.expiry.strftime("%d/%m/%Y")
			else:
				expiry = u""
			
			sheet.write(row+1,0,product.name)
			sheet.write(row+1,1,product.packaging)
			sheet.write(row+1,2,product.reference)
			sheet.write(row+1,3,product.price)
			sheet.write(row+1,4,product.offer_nb)
			sheet.write(row+1,5,expiry)
			sheet.write(row+1,6,product.nomenclature)
	
	response = HttpResponse(mimetype="application/ms-excel")
	response['Content-Disposition'] = 'attachment; filename=export_all_products.xls'
	response['Content-Type'] = 'application/vnd.ms-excel; charset=utf-8'
	xls.save(response)
	
	return response

@login_required
def export_history_orders(request):
	xls = xlwt.Workbook()
	header = [
	u"DATE RECEPTION",u"COMMANDE PAR",u"RECEPTIONNE PAR",
	u"FOURNISSEUR",u"N°CMDE",u"DESIGNATION",u"CONDITIONNEMENT",u"RÉFÉRENCE",
	u"N° OFFRE",u"PRIX UNITAIRE",u"QUANTITE",u"PRIX TOTAL",u"MONTANT CDE"]
	
	prev_team = None
	
	for history in History.objects.all().order_by('team'):
		if prev_team != history.team:
			prev_team = history.team
			if len( history.team ) >= 32:
				sheet = xls.add_sheet( u"%s..." % history.team[0:28] )
			else:
				sheet = xls.add_sheet( u"%s" % history.team )
			for col, title in enumerate(header): sheet.write(0, col, title)
			row = 1
		
		for item in history.items.all().order_by('date_delivered'):
			sheet.write( row, 0, history.date_delivered.strftime("%d/%m/%Y") )
			sheet.write( row, 1, item.get_fullname() )
			sheet.write( row, 2, item.get_fullname_recept() )
			sheet.write( row, 3, history.provider )
			sheet.write( row, 4, history.number )
			sheet.write( row, 5, item.name )
			sheet.write( row, 6, item.packaging )
			sheet.write( row, 7, item.reference )
			sheet.write( row, 8, item.offer_nb )
			sheet.write( row, 9, item.price )
			sheet.write( row, 10, item.quantity )
			sheet.write( row, 11, item.total_price() )
			sheet.write( row, 12, history.price )
			row += 1
	
	response = HttpResponse(mimetype="application/ms-excel")
	response['Content-Disposition'] = 'attachment; filename=export_history_orders.xls'
	response['Content-Type'] = 'application/vnd.ms-excel; charset=utf-8'
	xls.save(response)
	
	return response

# encoding: utf-8
import xlwt

from django.utils.http import urlencode
from django.db.models.query import Q
from django.db import transaction
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import render

from history.models import History
from history.forms import HistoryFilterForm, BudgetHistoryFilterForm
from order.models import OrderItem
from budget.models import Budget, BudgetLine

from bcg_lab.constants import *
from utils import *

def search_orders(request):
    # Get initial history_list
    if request.user.has_perm('team.custom_view_teams'):
        history_list = History.objects.all()
    elif request.user.has_perm('order.custom_view_local_provider'):
        history_list = History.objects.filter( provider__iexact = "magasin" )
    else:
        history_list = History.objects.filter(
            Q(items__username = request.user.username) |
            Q(team__in = [t.name for t in get_teams(request.user)])
        )
    
    # Filter history_list depending on received GET data
    form = HistoryFilterForm( user = request.user, data = request.GET )
    if len(request.GET.keys()) > 0 and form.is_valid():
        data = form.cleaned_data
        for key, value in data.items():
            if not value:
                del data[key]
        
        if 'team' in data:
            data['team'] = data['team'].name
        
        Q_obj = Q()
        Q_obj.connector = data.pop("connector")
        Q_obj.children  = data.items()
        
        history_list = history_list.filter( Q_obj )
    
    search_name = request.GET.get("items__name__icontains",None)
    search_ref = request.GET.get("items__reference",None)
    search_type = request.GET.get("items__category",None)
    search_subtype = request.GET.get("items__sub_category",None)
    
    if search_name or search_ref or search_type or search_subtype:
        display = "by_product"
        
        search_dict = {}
        if search_name:
            search_dict['name__icontains'] = search_name
        if search_ref:
            search_dict['reference'] = search_ref
        if search_type:
            search_dict['category'] = search_type
        if search_subtype:
            search_dict['sub_category'] = search_subtype
        
        Q_obj = Q()
        Q_obj.connector = request.GET['connector']
        Q_obj.children = search_dict.items()
        
        items_id = []
        for h in history_list:
            for item in h.items.filter( Q_obj ):
                if not item.id in items_id:
                    items_id.append( item.id )
        
        objects = OrderItem.objects.filter( id__in = items_id ).distinct()
        objects = objects.order_by('-history__date_delivered')
    else:
        display = "by_order"
        objects = history_list.distinct()
    
    return display, objects, form


@login_required
def history_orders(request):
    display, objects, form = search_orders( request )
    if display == "by_product":
        total = sum( [item.total_price() for item in objects] )
    else:
        total = sum( [history.price for history in objects.distinct()] )
    
    return render( request, "history/orders.html", {
        'filter_form': form,
        'objects': paginate( request, objects.distinct() ),
        'display': display,
        'url_args': urlencode(request.GET),
        'total': total
    })

@login_required
def item(request, item_id):
    item = get_object_or_404( History, id = item_id )
    
    return render( request, 'history/item.html', {
        'history': item
    })

@login_required
def export_orders_to_xls( request ):
    display, objects, form = search_orders( request )
    
    if display == "by_order":
        items = []
        for history in objects:
            for item in history.items.all():
                if not item in items:
                    items.append( item )
    else:
        items = objects
    
    wb = xlwt.Workbook()
    ws = wb.add_sheet("export")

    header = [
    u"DATE RECEPTION",u"EQUIPE",u"COMMANDE PAR",u"RECEPTIONNE PAR",
    u"FOURNISSEUR",u"N°CMDE",u"DESIGNATION",u"CONDITIONNEMENT",u"RÉFÉRENCE",
    u"N° OFFRE",u"PRIX UNITAIRE",u"QUANTITE",u"PRIX TOTAL",u"MONTANT CDE"]
    for col, title in enumerate(header): ws.write(0, col, title)
    row = 1
    
    for item in items:
        history = item.history_set.get()
        
        ws.write( row, 0, history.date_delivered.strftime("%d/%m/%Y") )
        ws.write( row, 1, history.team )
        ws.write( row, 2, item.get_fullname() )
        ws.write( row, 3, item.get_fullname_recept() )
        ws.write( row, 4, history.provider )
        ws.write( row, 5, history.number )
        ws.write( row, 6, item.name )
        ws.write( row, 7, item.packaging )
        ws.write( row, 8, item.reference )
        ws.write( row, 9, item.offer_nb )
        ws.write( row, 10, item.price )
        ws.write( row, 11, item.quantity )
        ws.write( row, 12, item.total_price() )
        ws.write( row, 13, history.price )
        row += 1
    
    response = HttpResponse(mimetype="application/ms-excel")
    response['Content-Disposition'] = 'attachment; filename=export_historique_commandes.xls'
    response['Content-Type'] = 'application/vnd.ms-excel; charset=utf-8'
    wb.save(response)
    
    return response

@login_required
def history_budgets(request):
    if not request.user.has_perm("budget.custom_view_budget"):
        not_allowed_msg( request )
        return redirect("home")
    
    budgets = Budget.objects.filter( is_active = False )
    
    if not request.user.has_perm('team.custom_view_teams'):
        budgets = budgets.filter( team__in = get_teams(request.user) )
    
    # 
    # Filter history_list depending on received GET data
    form = BudgetHistoryFilterForm( user = request.user, data = request.GET )
    if len(request.GET.keys()) > 0 and form.is_valid():
        data = form.cleaned_data
        for key, value in data.items():
            if not value:
                del data[key]
        
        if 'team' in data:
            data['team'] = data['team'].name
        
        Q_obj = Q()
        Q_obj.connector = data.pop("connector")
        Q_obj.children  = data.items()
        
        budget_lines = BudgetLine.objects.filter( 
            budget_id__in = budgets.values_list("id", flat=True) 
        ).filter( Q_obj )
    else:
        budget_lines = BudgetLine.objects.none()
    
    return render( request, 'history/budgets.html', {
        'filter_form': form,
        'budgets': paginate( request, budgets ),
        'budget_lines': paginate( request, budget_lines ),
        'url_args': urlencode(request.GET)
    })


@login_required
@GET_method
def export_budget_to_xls(request):
    if len(request.GET.keys()) > 0:
        return export_budgetlines( request )
    
    return export_budgets( request )

@login_required
@GET_method
def export_budgetlines( request ):
    # 
    # Filter budget_lines depending on received GET data
    form = BudgetHistoryFilterForm( user = request.user, data = request.GET )
    if form.is_valid():
        data = form.cleaned_data
        for key, value in data.items():
            if not value:
                del data[key]
        
        if 'team' in data:
            data['team'] = data['team'].name
                
        Q_obj = Q()
        Q_obj.connector = data.pop("connector")
        Q_obj.children  = data.items()
        
        budget_lines = BudgetLine.objects.filter(is_active = False).filter( Q_obj )
    else:
        error_msg(request, "Impossible d'exporter cette page.")
        return redirect( reverse("history_budgets") )
    
    wb = xlwt.Workbook()    
    ws = wb.add_sheet("export")
        
    header = [u"EQUIPE", u"BUDGET", u"N°CMDE",u"DATE", u"NATURE", 
    u"TUTELLE", u"FOURNISSEUR", u"COMMENTAIRE", u"DESIGNATION", 
    u"CREDIT", u"DEBIT", u"QUANTITE", u"TOTAL", u"MONTANT DISPO"]
    for col, title in enumerate(header): ws.write(0, col, title)
    
    prev_budget = None
    row = 1
    
    for bl in budget_lines.order_by("budget"):
        if prev_budget != bl.budget:
            if prev_budget: row += 1
            prev_budget = bl.budget
        
        ws.write( row, 0, bl.team )
        ws.write( row, 1, bl.budget )
        ws.write( row, 2, bl.number )
        ws.write( row, 3, bl.date.strftime("%d/%m/%Y") )
        ws.write( row, 4, bl.nature )
        ws.write( row, 5, bl.get_budget_type_display() )
        ws.write( row, 6, bl.provider )
        ws.write( row, 7, bl.offer )
        ws.write( row, 8, bl.product )
        ws.write( row, 9, bl.credit )
        ws.write( row, 10, bl.debit )
        ws.write( row, 11, bl.quantity )
        ws.write( row, 12, bl.product_price )
        ws.write( row, 13, str(bl.get_amount_left()) )
        row += 1
    
    response = HttpResponse(mimetype="application/ms-excel")
    response['Content-Disposition'] = 'attachment; filename=export_historique_budget.xls'
    response['Content-Type'] = 'application/vnd.ms-excel; charset=utf-8'
    wb.save(response)
    
    return response

@login_required
@GET_method
def export_budgets( request ):
    budgets = Budget.objects.filter( is_active = False )
    
    if not request.user.has_perm('team.custom_view_teams'):
        budgets = budgets.filter( team__in = get_teams(request.user) )
    
    wb = xlwt.Workbook()    
    ws = wb.add_sheet("export")
    
    header = [u"EQUIPE", u"BUDGET", u"TUTELLE", u"NATURE"]
    for col, title in enumerate(header): ws.write(0, col, title)
    
    row = 1
    for budget in budgets:
        ws.write( row, 0, budget.team.name )
        ws.write( row, 1, budget.name )
        ws.write( row, 2, budget.get_budget_type_display() )
        ws.write( row, 3, budget.default_nature )
        row += 1
    
    response = HttpResponse(mimetype="application/ms-excel")
    response['Content-Disposition'] = 'attachment; filename=export_historique_budget.xls'
    response['Content-Type'] = 'application/vnd.ms-excel; charset=utf-8'
    wb.save(response)
    
    return response


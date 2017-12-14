# coding: utf-8
from decimal import Decimal
import xlwt

from django.db import transaction
from django.db.models.query import Q
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render

from budget.models import Budget, BudgetLine
from budget.forms import BudgetLineForm, BudgetLineFilterForm
from team.utils import get_teams
from utils import GET_method
from utils.request_messages import not_allowed_msg


@login_required
@GET_method
def index(request):
    if request.user.has_perms(['team.custom_view_teams','budget.custom_view_budget']):
        budget_lines = BudgetLine.objects.filter(is_active = True)
    elif request.user.has_perm('budget.custom_view_budget'):
        budget_lines = BudgetLine.objects.filter(
            is_active = True,
            team__in = [t.name for t in get_teams(request.user)]
    )
    else:
        not_allowed_msg(request)
        return redirect('home')
    
    # 
    # Filter budget_lines depending on received GET data
    form = BudgetLineFilterForm(user = request.user, data = request.GET)
    if len(request.GET.keys()) > 0 and form.is_valid():
        Q_obj = Q()
        Q_obj.connector = form.cleaned_data.pop("connector")
        Q_obj.children  = []
        for key, value in form.cleaned_data.items():
            if value:
                Q_obj.children.append((key,value))
        
        budget_lines = budget_lines.filter(Q_obj)
    
    budgets = list(set(budget_lines.values_list('budget_id',flat=True)))
    if len(budgets) == 1:
        budget = Budget.objects.get(id = budgets[0], is_active = True)
    else:
        budget = Budget.objects.none()
    
    return render(request, "budgetlines/index.html", {
        'budget': budget,
        'budget_lines' : budget_lines,
        'filter_form': form,
        'url_args': request.GET.urlencode()
    })


@login_required
@GET_method
def export_to_xls(request):
    # 
    # Filter budget_lines depending on received GET data
    form = BudgetLineFilterForm(user = request.user, data = request.GET)
    if len(request.GET.keys()) > 0 and form.is_valid():
        Q_obj = Q()
        Q_obj.connector = form.cleaned_data.pop("connector")
        Q_obj.children  = []
        for key, value in form.cleaned_data.items():
            if value:
                Q_obj.children.append((key, value))

        budget_lines = BudgetLine.objects.filter(Q_obj)
    else:
        budget_lines = BudgetLine.objects.none()
    
    wb = xlwt.Workbook()
    ws = wb.add_sheet("export")
    
    header = [u"EQUIPE", u"BUDGET", u"N°CMDE",u"DATE", u"NATURE", 
    u"TUTELLE", u"FOURNISSEUR", u"COMMENTAIRE", u"DESIGNATION", 
    u"CREDIT", u"DEBIT", u"QUANTITE", u"TOTAL"]
    
    for col, title in enumerate(header): 
        ws.write(0, col, title)
    
    row = 1    
    total = 0
    for bl in budget_lines.filter(number__isnull = False).exclude(number = ''):
        total += bl.get_total()
        
        ws.write(row, 0, bl.team)
        ws.write(row, 1, bl.budget)
        ws.write(row, 2, bl.number)
        ws.write(row, 3, bl.date.strftime("%d/%m/%Y"))
        ws.write(row, 4, bl.nature)
        ws.write(row, 5, bl.get_budget_type_display())
        ws.write(row, 6, bl.provider)
        ws.write(row, 7, bl.offer)
        ws.write(row, 8, bl.product)
        ws.write(row, 9, bl.credit)
        ws.write(row, 10, bl.debit)
        ws.write(row, 11, bl.quantity)
        if bl.debit:
            ws.write(row, 12, "%s" % (bl.debit * bl.quantity * -1))
        else:
            ws.write(row, 12, "%s" % (bl.credit * bl.quantity))
        row += 1
    
    if row != 1:
        ws.write(row, 12, total)
        row += 2
    
    total = 0
    for bl in budget_lines.filter(Q(number__isnull = True) | Q(number = '')):
        total += bl.get_total()
        
        ws.write(row, 0, bl.team)
        ws.write(row, 1, bl.budget)
        ws.write(row, 2, bl.number)
        ws.write(row, 3, bl.date.strftime("%d/%m/%Y"))
        ws.write(row, 4, bl.nature)
        ws.write(row, 5, bl.get_budget_type_display())
        ws.write(row, 6, bl.provider)
        ws.write(row, 7, bl.offer)
        ws.write(row, 8, bl.product)
        ws.write(row, 9, bl.credit)
        ws.write(row, 10, bl.debit)
        ws.write(row, 11, bl.quantity)
        if bl.debit:
            ws.write(row, 12, "%s" % (bl.debit * bl.quantity * -1))
        else:
            ws.write(row, 12, "%s" % (bl.credit * bl.quantity))
        row += 1
    ws.write(row, 12, total)
    
    budget_ids = budget_lines.values_list('budget_id', flat = True).distinct()
    if budget_ids.count() == 1:
        budget = Budget.objects.get(id = budget_ids[0])
        ws.write(row + 1, 0, "MONTANT DISPONIBLE:")
        ws.write(row + 1, 1, budget.get_amount_left())
    
    response = HttpResponse(mimetype="application/ms-excel")
    response['Content-Disposition'] = 'attachment; filename=export_budget.xls'
    response['Content-Type'] = 'application/vnd.ms-excel; charset=utf-8'
    wb.save(response)
    
    return response


@login_required
@transaction.atomic
def item(request, bl_id):
    bl = get_object_or_404(BudgetLine, id = bl_id)
    form = BudgetLineForm(instance = bl)
    
    if request.method == 'POST':
        data = request.POST.copy()
        data['budget_id'] = int(data['budget'])
        form = BudgetLineForm(instance = bl, data = data)
        if form.is_valid():
            bl = form.save()
            bl.update_budget_relation()
            
            bl.is_active = True
            
            if 'cost_type' in data:
                if data["cost_type"] == "credit":
                    bl.credit = Decimal(data["cost"])
                    bl.debit = 0
                    bl.product_price = bl.credit * bl.quantity
                elif data["cost_type"] == "debit":
                    bl.credit = 0
                    bl.debit = Decimal(data["cost"])
                    bl.product_price = bl.debit * bl.quantity
            elif 'cost' in data and data['cost'] == 0:
                bl.credit = 0
                bl.debit = 0
                bl.product_price = 0
            
            bl.save()
            return redirect(reverse('budget_line:list') + "?budget_id=%s&connector=OR" % data['budget_id'])
    
    return render(request, 'budgetlines/item.html', {
        'form': form,
        'bl': bl,
        'url_args': request.GET.urlencode()
    })


@login_required
@GET_method
def delete(request, bl_id):
    bl = get_object_or_404(BudgetLine, id = bl_id)
    budget_name = bl.budget
    bl.delete()
    return redirect('budgets')


# coding: utf-8
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render

from budget.models import Budget, BudgetLine
from budget.forms import BudgetForm, BudgetLineFilterForm
from budget.forms import CreditBudgetForm, DebitBudgetForm
from budget.forms import TransferForm
from team.utils import get_teams
from utils.request_messages import not_allowed_msg, error_msg, info_msg


@login_required
def index(request):
    if request.user.has_perms(['team.custom_view_teams','budget.custom_view_budget']):
        budget_list = Budget.objects.filter(is_active = True)
    elif request.user.has_perm("budget.custom_view_budget"):
        budget_list = Budget.objects.filter(
            is_active = True,
            team__in = get_teams(request.user)
    )
    else:
        not_allowed_msg(request)
        return redirect('home')
    
    return render(request, 'budget/index.html',{
        'budgets': budget_list,
        'filter_form': BudgetLineFilterForm(user = request.user, data = request.GET)
    })


@login_required
@transaction.atomic
def item(request, budget_id):
    budget = get_object_or_404(Budget, id = budget_id)
    
    if request.method == 'GET':
        form = BudgetForm(instance = budget)
    elif request.method == 'POST':
        form = BudgetForm(data = request.POST, instance = budget)
        if form.is_valid():
            data = form.cleaned_data
            form.save()
            budget.update_budgetlines()
            
            sum_natures = 0
            for n in ['fo','mi','sa','eq']:
                if n in data and data[n]:
                    sum_natures += data[n]
            
            if sum_natures > budget.get_amount_left():
                error_msg(request, u"Montant disponible insuffisant pour cette répartition.")
            else:
                for nature in ['fo','mi','sa','eq']:
                    if data[nature] or data[nature] == 0:
                        sub_budget, created = Budget.objects.get_or_create(
                            team = budget.team,
                            name = "%s - %s" % (budget.name, nature.upper()),
                            default_origin = budget.default_origin,
                            budget_type = budget.budget_type,
                            tva_code = budget.tva_code,
                            domain = budget.domain,
                            default_nature = nature.upper()
                        )
                        if data[nature] > 0:
                            bl = sub_budget.credit(data[nature])
                            bl.product = u"Répartition"
                            bl.save()
                        
                            bl = budget.debit(data[nature])
                            bl.product = u"Répartition vers %s" % nature.upper()
                            bl.save()

                info_msg(request, "Budget modifié avec succès.")
                return redirect('budget:list')
    else:
        return redirect('error')
    
    return render(request, 'budget/item.html', {
        'budget': budget,
        'form': form
    })


@login_required
@transaction.atomic
def new(request):
    if request.method == 'GET':
        form = BudgetForm()
    elif request.method == 'POST':
        form = BudgetForm(data = request.POST)
        if form.is_valid():
            data = form.cleaned_data

            if data.get('all_natures', None) and data['all_natures'] >= 0:
                budget = form.save(commit = False)
                budget.name = "[%s] %s [%s]" % (
                    data['team'].shortname,
                    data['name'],
                    data['default_origin']
                )
                budget.save()
                if data['all_natures'] > 0:
                    bl = budget.credit(data["all_natures"])
                    bl.product = u"Initial"
                    bl.save()
                info_msg(request, "Budget '%s' ajouté avec succès." % budget.name)
            else:
                for nature in ['fo','mi','sa','eq']:
                    if data.get(nature, None) >= 0:
                        budget = Budget.objects.create(
                            team = data['team'],
                            name = "[%s] %s - %s [%s]" % (
                                data['team'].shortname,
                                data['name'],
                                nature.upper(),
                                data['default_origin']
                            ),
                            default_origin = data['default_origin'],
                            budget_type = data['budget_type'],
                            tva_code = data['tva_code'],
                            domain = data['domain'],
                            default_nature = nature.upper()
                        )
                        info_msg(request, "Budget '%s' ajouté avec succès." % budget.name)
                        if data[nature] > 0:
                            bl = budget.credit(data[nature])
                            bl.product = u"Initial"
                            bl.save()

            return redirect('budget:list')
    else:
        return redirect('error')
        
    return render(request, 'budget/form.html',{
        'form': form
    })


@login_required
@transaction.atomic
def credit(request, budget_id):
    budget = get_object_or_404(Budget, id = budget_id)
    
    if request.method == "GET":
        return render(request, "budget/form_credit.html",{
            'budget': budget,
            'form': CreditBudgetForm(budget),
            'prev': request.META.get('HTTP_REFERER','') + request.GET.urlencode()
        })
    
    data = request.POST.copy()
    data.update({ 'budget': budget.name }) # otherwise, form is not valid
    
    form = CreditBudgetForm(budget, data = data)
    
    if form.is_valid():
        bl = form.save(commit = False)
        bl.team         = budget.team.name
        bl.budget_id    = budget.id
        bl.nature       = budget.default_nature
        bl.budget_type  = budget.budget_type
        bl.origin       = budget.default_origin
        bl.quantity     = 1
        bl.credit       = bl.product_price
        bl.debit        = 0
        bl.save()
        
        info_msg(request, "Ligne de crédit ajoutée avec succès.")
        return redirect('budget:list')
        # return redirect(reverse('budget_line:list') + "?budget_name=%s" % budget.name)
    else:
        return render(request, 'budget/form_credit.html',{
            'budget': budget,
            'form': form
        })


@login_required
@transaction.atomic
def debit(request, budget_id):
    budget = get_object_or_404(Budget, id = budget_id)
    
    if request.method == "GET":
        return render(request, "budget/form_debit.html",{
            'budget': budget,
            'form': DebitBudgetForm(budget),
            'prev': request.META.get('HTTP_REFERER','') + request.GET.urlencode()
        })
    
    data = request.POST.copy()
    data.update({ 'budget': budget.name }) # otherwise, form is not valid
    
    form = DebitBudgetForm(budget, data = data)
    if form.is_valid():
        bl = form.save(commit = False)
        bl.team         = budget.team.name
        bl.budget_id    = budget.id
        bl.nature       = budget.default_nature
        bl.budget_type  = budget.budget_type
        bl.origin       = budget.default_origin
        bl.quantity     = 1
        bl.credit       = 0
        bl.debit        = bl.product_price
        bl.save()
        
        info_msg(request, "Ligne de débit ajoutée avec succès!")
        return redirect('budget:list')
        # return redirect(reverse('budget_line:list') + "?budget_name=%s" % budget.name)
    else:
        return render(request, 'budget/form_debit.html',{
            'budget': budget,
            'form': form
        })


@login_required
@transaction.atomic
def transfer(request):
    form = TransferForm(user = request.user)

    if request.method == 'POST':
        form = TransferForm(user = request.user, data = request.POST)
        if form.is_valid():
            data = form.cleaned_data
            title1 = data.get('title1',None)
            title2 = data.get('title2',None)
            budget1 = data['budget1']
            budget2 = data['budget2']
            amount  = data['amount']
            
            bl = budget1.debit(amount)
            bl.product = u"Virement vers %s" % budget2.name
            if title1: bl.offer = title1
            bl.save()
            
            bl = budget2.credit(amount)
            bl.product = u"Virement reçu de %s" % budget1.name
            if title2: bl.offer = title2
            bl.save()
            return redirect('budget:list')
            
    return render(request, 'budget/transfer.html', {
        'form': form
    })


@login_required
@transaction.atomic
def toggle(request, budget_id):
    budget = get_object_or_404(Budget, id = budget_id)
    budget.is_active = not budget.is_active
    budget.save()
    
    for bl in BudgetLine.objects.filter(budget_id = budget.id):
        bl.is_active = budget.is_active
        bl.save()
    
    return redirect('budget:list')


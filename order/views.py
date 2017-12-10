# encoding: utf-8
import xlwt

from django.db.models.query import Q
from django.db import transaction
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import get_object_or_404, redirect
from django.template import Context, loader
from django.shortcuts import render

from product.models import Product
from budget.models import Budget, BudgetLine
from order.models import Order, OrderItem
from order.forms import OrderItemForm, AddDebitForm, AddCreditForm, FilterForm

from team.models import Team, TeamMember
from team.utils import get_teams
from utils import GET_method, paginate, POST_method, AJAX_method
from utils.request_messages import info_msg, warn_msg, not_allowed_msg, error_msg


@login_required
@GET_method
def tab_cart(request):
    orders = Order.objects.filter(status = 0)
    orders = orders.filter(
        Q(items__username = request.user.username) |
        Q(team__in = get_teams(request.user))
   ).distinct()
    if not request.user.has_perm('budget.custom_view_budget'):
        orders = orders.filter(
            Q(items__is_confidential = False) |
            Q(items__username = request.user.username)
       ).distinct()
    
    return render(request, "tab_cart.html", { 
        'order_list': orders.distinct().order_by('provider__name'),
        'credit_form': AddCreditForm(),
        'debit_form': AddDebitForm(),
        'team_choices': [(team.id,team.name) for team in Team.objects.all()],
        'next': 'tab_cart'
    })

@login_required
@GET_method
def tab_orders(request):
    # Commandes à saisir
    if request.user.has_perm('order.custom_goto_status_4') and not request.user.is_superuser:
        order_list = Order.objects.exclude(provider__is_local = True)
        order_list = order_list.filter(
            Q(status__in = [2,3,4]) |
            Q(status = 1, team = get_teams(request.user)[0]) |
            Q(status = 1, items__username = request.user.username)
       ).distinct()
    # Commandes en cours - toutes équipes
    elif request.user.has_perm("team.custom_view_teams") and not request.user.is_superuser:
        order_list = Order.objects.filter(
            status__in = [2,3,4]
       ).distinct()
    # Commandes en cours - par équipe
    else:
        order_list = Order.objects.filter(status__in = [1,2,3,4])
        order_list = order_list.filter(
            Q(items__username = request.user.username) |
            Q(team__in = get_teams(request.user))
       ).distinct()
    
    # Exclude confidential orders
    if not request.user.has_perm('budget.custom_view_budget'):
        order_list = order_list.filter(
            Q(items__is_confidential = False) |
            Q(items__username = request.user.username)
       ).distinct()
    
    # 
    # Filter order depending on received GET data
    form = FilterForm(data = request.GET)
    if len(request.GET.keys()) > 0 and form.is_valid():
        Q_obj = Q()
        Q_obj.connector = form.cleaned_data.pop("connector")
        Q_obj.children = []

        for key, value in form.cleaned_data.items():
            if value:
                Q_obj.children.append((key, value))
        
        order_list = order_list.filter(Q_obj)
    
    return render(request, "order/index.html", {
        'orders': paginate(request, order_list),
        'filter_form': form,
        'next': 'tab_orders',
        'next_page': 'page' in request.GET and request.GET['page'] or 1
    })


@login_required
@GET_method
def tab_validation(request):
    teams = get_teams(request.user)
    
    # ORDERS THAT CAN BE SEEN
    see_all_teams = 'see_all_teams' in request.GET and request.GET['see_all_teams'] == '1'
    
    if request.user.has_perms(['team.custom_view_teams','order.custom_validate']):
        order_list = Order.objects.filter(status = 1).order_by('-date_created')
        if see_all_teams:
            order_list = order_list.exclude(team__in = teams)
        else:
            order_list = order_list.filter(team__in = teams)
    elif request.user.has_perm('order.custom_validate'):
        order_list = Order.objects.filter(team__in = teams, status = 1).order_by('-date_created')
    else:
        not_allowed_msg(request)
        return redirect('home')
    
    # BUDGETS THAT CAN BE SELECTED
    if request.user.has_perms(['team.custom_view_teams','budget.custom_view_budget']):
        budget_list = Budget.objects.filter(is_active = True)
    elif request.user.has_perm('budget.custom_view_budget'):
        budget_list = Budget.objects.filter(team__in = teams, is_active = True)
    else:
        budget_list = Budget.objects.none()
        
    # TEAMS THAT CAN BE SELECTED
    if request.user.has_perm("order.custom_order_any_team") or request.user.has_perm("team.custom_is_admin"):
        team_choices = [(team.id, team.name) for team in Team.objects.all()]
    else:
        team_choices = []
    
    return render(request, 'tab_validation.html', {
        'orders': paginate(request, order_list.distinct()),
        'budgets': budget_list.distinct(),
        'team_choices': team_choices,
        'credit_form': AddCreditForm(),
        'debit_form': AddDebitForm(),
        'see_all_teams': see_all_teams,
        'next': 'tab_validation'
    })

@login_required
@GET_method
def order_detail(request, order_id):
    order = get_object_or_404(Order, id = order_id)
    
    if request.user.has_perms(['team.custom_view_teams','budget.custom_view_budget']):
        budget_list = Budget.objects.filter(is_active = True)
    elif request.user.has_perm('budget.custom_view_budget'):
        budget_list = Budget.objects.filter(
            team__in = get_teams(request.user),
            is_active = True
       )
    else:
        budget_list = Budget.objects.none()
    
    # if not order.provider.is_service:
    #   budget_list = budget_list.filter(
    #       Q(default_nature__isnull = True) |
    #       Q(default_nature='FO') |
    #       Q(default_nature='')
    #  )
    
    return render(request, 'order/item.html', {
        'order': order,
        'budgets': budget_list.distinct(),
        'credit_form': AddCreditForm(),
        'debit_form': AddDebitForm(),
        'team_choices': [(team.id,team.name) for team in Team.objects.all()],
        'next': order.get_absolute_url(),
        'next_page': 'page' in request.GET and request.GET['page'] or 1
    })


@login_required
@GET_method
def order_export(request, order_id):
    order = get_object_or_404(Order, id = order_id)
    
    xls = xlwt.Workbook()
    sheet = xls.add_sheet('export')
    
    row = 0
    for order_item in order.items.all():
        if order_item.reference:
            lo = 0
            hi = 40 - len(" #") - len(order_item.reference)
            title = u"%s #%s" % (order_item.name[lo:hi], order_item.reference)
        else:
            lo, hi = 0, 40
            title = order_item.name[lo:hi]
        sheet.write(row, 0, title)
        sheet.write(row, 1, order_item.quantity)
        sheet.write(row, 4, order_item.price)
        row += 1
    
    response = HttpResponse(mimetype="application/ms-excel")
    response['Content-Disposition'] = 'attachment; filename=export_commande.xls'
    response['Content-Type'] = 'application/vnd.ms-excel; charset=utf-8'
    xls.save(response)
    
    return response
    

@login_required
@transaction.atomic
def orderitem_detail(request, orderitem_id):
    orderitem = get_object_or_404(OrderItem, id = orderitem_id)
    
    if request.method == 'GET':
        return _orderitem_get(request, orderitem)
    
    if request.method == 'POST':
        return _orderitem_update(request, orderitem)


def _orderitem_get(request, orderitem):
    return render(request, 'order/orderitem_detail.html', {
        'form': OrderItemForm(instance = orderitem),
        'orderitem': orderitem,
        'order': orderitem.order_set.get()
    })

def _orderitem_update(request, orderitem):
    order = orderitem.order_set.get()
    
    data = request.POST.copy()
    data['provider'] = order.provider.name
    
    form = OrderItemForm(instance = orderitem, data = data)
    if form.is_valid():
        form.save()
        
        if order.budget:
            orderitem.update_budget_line()
        
        if orderitem.product_id:
            orderitem.update_product()
        
        info_msg(request, "Commande modifiée avec succès.")
        return redirect(order)
    
    return render(request, 'order/orderitem_detail.html', {
        'form': form,
        'orderitem': orderitem,
        'order': order
    })


@login_required
@POST_method
@transaction.atomic
def add_orderitem(request, order_id):
    order = get_object_or_404(Order, id = order_id)
    info_msg(request, request.POST.items())
    form = OrderItemForm(data = request.POST)
    if form.is_valid():
        item = form.save(commit = False)
        item.cost_type = request.POST['cost_type']
        item.save()
        order.items.add(item)
        
        if order.budget:
            item.create_budget_line()
        
        info_msg(request, u"'%s' ajouté à la commande avec succès." % item.name)
    else:
        error_msg(request, "Le formulaire n'est pas valide, veuillez remplir les champs obligatoires. %s %s" % (form.errors, request.POST.items()))
    
    return redirect(request.POST.get('next', order))


@login_required
@transaction.atomic
def add_credit(request, order_id):
    order = get_object_or_404(Order, id = order_id)
    next = request.POST.get('next', 'tab_orders')
    form = AddCreditForm(data = request.POST)
    if form.is_valid():
        item = form.save(commit = False)
        item.item_type = 2
        item.username = request.POST['username']
        item.provider = order.provider.name
        item.save()
        order.items.add(item)
        
        if order.budget:
            item.create_budget_line()
        
        info_msg(request, u"'%s' ajouté à la commande avec succès." % item.name)
    else:
        error_msg(request, u"Une erreur s'est produite lors de l'ajout de la remise. \
Merci de vérifier que tous les champs obligatoires ont bien été remplis.")
    return redirect(next)


@login_required
@POST_method
@transaction.atomic
def add_debit(request, order_id):
    order = get_object_or_404(Order, id = order_id)
    next = request.POST.get('next', 'tab_orders')
    form = AddDebitForm(data = request.POST)
    if form.is_valid():
        item = form.save(commit = False)
        item.item_type = 1
        item.username = request.POST['username']
        item.provider = order.provider.name
        item.save()
        order.items.add(item)
        
        if order.budget:
            item.create_budget_line()
        
        info_msg(request, u"'%s' ajouté à la commande avec succès." % item.name)
    else:
        error_msg(request, u"Une erreur s'est produite lors de l'ajout de frais. \
Merci de vérifier que tous les champs obligatoires ont bien été remplis.")
    
    return redirect(next)


@login_required
@GET_method
@transaction.atomic
def orderitem_delete(request, orderitem_id):
    item = get_object_or_404(OrderItem, id = orderitem_id)
    order = item.order_set.get()
    info_msg(request, u"'%s' supprimé avec succès." % item.name)
    
    if order.status == 0:
        next_page = request.GET.get('next', 'tab_cart')
    elif order.status == 1 and request.user.has_perm('order.custom_validate'):
        next_page = request.GET.get('next', 'tab_validation')
    elif order.status == 4:
        BudgetLine.objects.filter(orderitem_id = item.id).delete()
        next_page = request.GET.get('next', 'tab_orders')
    else:
        next_page = request.GET.get('next', order)
    
    # SEND EMAIL TO ITEM OWNER - if set in preferences
    if request.user.username != item.username:
        tm = TeamMember.objects.filter(
            user__username = item.username,
            send_on_edit = True,
            user__email__isnull = False
       )
        if tm.count() > 0:
            subject = u"[BCG-Lab %s] Item supprimé (%s)" % (settings.SITE_NAME, item.name)
            template = loader.get_template("email_delete_item.txt")
            message = template.render({
                'item': item,
                'user': request.user,
                'order': item.get_order()
            })
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [tm[0].user.email])
    
    item.delete()
    
    if order.items.all().count() == 0:
        warn_msg(request, "La commande ne contenant plus d'article, elle a également été supprimée.")
        order.delete()
        next_page = 'tab_orders'
    
    return redirect(next_page)

@login_required
@GET_method
@transaction.atomic
def orderitem_disjoin(request, orderitem_id):
    item = get_object_or_404(OrderItem, id = orderitem_id)
    order = item.get_order()
    
    new_order = order.copy()
    new_order.items.add(item)
    new_order.save()
    
    order.items.remove(item)
    order.save()
    
    return redirect(order)

@login_required
@GET_method
@transaction.atomic
def order_delete(request, order_id):
    order = get_object_or_404(Order, id = order_id)
    BudgetLine.objects.filter(order_id = order.id).delete()
    
    if order.status == 0:
        next_page = request.GET.get('next', 'tab_cart')
    elif order.status == 1 and request.user.has_perm('order.custom_validate'):
        next_page = request.GET.get('next', 'tab_validation')
    else:
        next_page = 'tab_orders'
    
    order.delete()
    
    info_msg(request, "Commande supprimée avec succès.")
    return redirect(next_page)



  #################
  # AJAX REQUESTS #
  #################

@login_required
@transaction.atomic
@AJAX_method
def set_team(request, order_id):
    team_id = request.GET.get("team_id", None)
    if not team_id:
        return HttpResponseServerError('team_id is missing.')
    
    order = get_object_or_404(Order, id = order_id)
    order.team = get_object_or_404(Team, id = int(team_id))
    order.save()
    
    return HttpResponse('ok')


@login_required
@AJAX_method
@transaction.atomic
def set_notes(request, order_id):
    order = get_object_or_404(Order, id = order_id)
    if 'notes' in request.GET:
        order.notes = request.GET['notes']
        order.save()
    
    return HttpResponse('ok')


@login_required
@AJAX_method
@transaction.atomic
def set_number(request, order_id):
    number = request.GET.get("number", None)
    if not number:
        return HttpResponseServerError('number is missing.')
    
    order = get_object_or_404(Order, id = order_id)
    order.number = number
    order.save()
    
    order.update_budget_lines()
    
    return HttpResponse('ok')


@login_required
@AJAX_method
@transaction.atomic
def set_budget(request, order_id):
    budget_id = request.GET.get("budget_id", None)
    if not budget_id:
        return HttpResponseServerError('budget_id is missing.')
    
    order = get_object_or_404(Order, id = order_id)
    budget_id = int(budget_id)
    if budget_id > 0:
        new_budget = get_object_or_404(Budget, id = budget_id)
        if not order.budget:
            order.budget = new_budget
            order.save()
            order.create_budget_line()
        elif order.budget.id != new_budget.id:
            if BudgetLine.objects.filter(order_id = order.id).count() == 0:
                order.create_budget_line()
            else:
                for bl in BudgetLine.objects.filter(order_id = order.id):
                    bl.budget_id = new_budget.id
                    bl.budget = new_budget.name
                    bl.origin = new_budget.default_origin
                    bl.budget_type = new_budget.budget_type
                    bl.nature = new_budget.default_nature
                    bl.save()
        
        order.budget = new_budget
    
    if budget_id == 0:
        # bugdet will be set by secretary
        order.budget = None
        BudgetLine.objects.filter(order_id = order.id).delete()
    
    order.save()
    return HttpResponse('ok')


@login_required
@AJAX_method
@transaction.atomic
def set_is_urgent(request, order_id):
    order = get_object_or_404(Order, id = order_id)
    order.is_urgent = request.GET['is_urgent'] == 'true'
    order.save()
    return HttpResponse('ok')


@login_required
@AJAX_method
@transaction.atomic
def set_has_problem(request, order_id):
    order = get_object_or_404(Order, id = order_id)
    order.has_problem = request.GET['has_problem'] == 'true'
    order.save()
    return HttpResponse('ok')


@login_required
@AJAX_method
@transaction.atomic
def set_item_quantity(request):
    orderitem_id = request.GET.get('orderitem_id', None)
    quantity = request.GET.get('quantity', None)
    
    if not orderitem_id or not quantity:
        return HttpResponseServerError('orderitem_id and/or quantity are missing.')
    
    quantity = int(quantity)
    if quantity <= 0:
        return HttpResponseServerError(u"Veuillez saisir une quantité entière positive.")
    
    item = get_object_or_404(OrderItem, id = orderitem_id)
    item.delivered = quantity
    item.quantity = quantity
    item.save()
    
    if item.get_order().number:
        item.update_budget_line()
    
    return HttpResponse('ok')


###############
# CART VIEWS  #
###############

@login_required
@POST_method
@transaction.atomic
def cart_add(request):
    member = request.user.teammember_set.get()
    product = get_object_or_404(Product, id = request.POST.get('product_id'))
    quantity = request.POST.get('quantity')
    
    order, created = Order.objects.get_or_create(
        team = member.team,
        provider = product.provider,
        status = 0
    )
    item = order.add(product, quantity)
    item.username = request.user.username
    item.save()
    
    url_arg = request.POST.get('url_params', '')
    url = reverse('product_index', current_app="product") + "?" + url_arg
    
    info_msg(request, u"Produit ajouté au panier avec succès.")
    return redirect(url)


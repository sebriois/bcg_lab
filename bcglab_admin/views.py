# coding: utf8
from django.utils import timezone
from django.contrib.auth.models import User, Group, Permission
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Max

from bcglab_admin.forms import GroupForm
from product.models import Product
from order.models import OrderItem
from history.models import History
from budget.models import Budget, BudgetLine
from utils.request_messages import info_msg, error_msg


@login_required
@transaction.atomic
def group_index(request):
    if request.method == 'GET':
        return render(request, 'admin/group_index.html', {
            'groups': Group.objects.all()
        })
    elif request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            group = form.save()

            for user in data['users']:
                user.groups.add(group)

            for key, value in data.items():
                if key.startswith('custom_') and value == True:
                    permission = Permission.objects.get(codename = key)
                    group.permissions.add(permission)

            info_msg(request, "Groupe ajouté avec succès")
            return redirect('bcglab_admin:group_index')
        else:
            error_msg(request, "Impossible de créer le groupe.")
            return render(request, 'group_new', {
                'form': form
            })

@login_required
@transaction.atomic
def group_item(request, group_id):
    group = get_object_or_404(Group, id = group_id)
    form = GroupForm(instance = group)

    if request.method == "POST":
        form = GroupForm(instance = group, data = request.POST)
        if form.is_valid():
            data = form.cleaned_data
            form.save()

            group.user_set.clear()
            group.permissions.clear()
            group.save()

            for user in data['users']:
                user.groups.add(group)

            for key, value in data.items():
                if key.startswith('custom_') and value == True:
                    permission = Permission.objects.get(codename = key)
                    group.permissions.add(permission)

            info_msg(request, "Groupe modifié avec succès")
            return redirect("bcglab_admin:group_index")
        else:
            error_msg(request, "Impossible de modifier le groupe.")

    return render(request, 'admin/group_item.html', {
        'form': form,
        'group': group
    })

@login_required
def group_new(request):
    return render(request, 'admin/group_new.html', {
        'form': GroupForm()
    })

@login_required
@transaction.atomic
def group_delete(request, group_id):
    group = get_object_or_404(Group, id = group_id)
    group.delete()

    info_msg(request, "Groupe supprimé avec succès.")

    return redirect('bcglab_admin:group_index')

@login_required
@transaction.atomic
def maintenance(request):
    if request.method == "POST":
        for key in request.POST.keys():
            if key == "inactive_all":
                inactive_all_users(request)

            if key == "active_all":
                active_all_users(request)

            if key == "delete_non_members":
                delete_non_members(request)

            if key == "delete_duplicates":
                delete_duplicates(request)

            if key == "delete_expired":
                delete_expired(request)

            if key == "clean_history":
                clean_history(request)

            if key == "clean_budgets":
                clean_budgets(request)

    return render(request, "admin/maintenance.html", {})

def inactive_all_users(request):
    for user in User.objects.filter(is_active = True):
        if user.has_perm("team.custom_is_admin"): continue
        user.is_active = False
        user.save()
    info_msg(request, u"Les comptes utilisateurs ont été inactivés.")

def active_all_users(request):
    for user in User.objects.filter(is_active = False):
        if user.has_perm("team.custom_is_admin"): continue
        user.is_active = True
        user.save()
    info_msg(request, u"Les comptes utilisateurs ont été activés.")

def delete_non_members(request):
    for user in User.objects.all():
        if user.has_perm("team.custom_is_admin"): continue
        if user.teammember_set.all().count() == 0:
            user.delete()
    info_msg(request, u"Les utilisateurs n'appartenant à aucune équipe ont été supprimés.")

def delete_duplicates(request):
    #
    # LOOKING AT PRODUCT HAVING SAME NAMES
    del_ids = []
    for p in Product.objects.all():
        if p.id in del_ids: continue

        duplicates = Product.objects.filter(name__iexact = p.name)
        if duplicates.count() > 1:
            kept_id = duplicates.aggregate(Max('id'))['id__max']
            for dup in duplicates.exclude(id = kept_id):
                del_ids.append(dup.id)
    del_ids = list(set(del_ids))

    Product.objects.filter(id__in = del_ids).delete()

    for item in OrderItem.objects.filter(product_id__in = del_ids):
        item.product_id = None
        item.save()
    info_msg(request, u"%s doublons ont été supprimés (même désignation)." % len(del_ids))

    #
    # LOOKING AT PRODUCTS HAVING SAME REF
    del_ids = []
    for p in Product.objects.all():
        if p.id in del_ids: continue

        duplicates = Product.objects.filter(reference = p.reference)
        if duplicates.count() > 1:
            kept_id = duplicates.aggregate(Max('id'))['id__max']
            for dup in duplicates.exclude(id = kept_id):
                del_ids.append(dup.id)
    del_ids = list(set(del_ids))

    Product.objects.filter(id__in = del_ids).delete()

    for item in OrderItem.objects.filter(product_id__in = del_ids):
        item.product_id = None
        item.save()

    info_msg(request, u"%s doublons ont été supprimés (même référence)." % len(del_ids))

def delete_expired(request):
    removed = Product.objects.filter(expiry__lte = timezone.now()).count()
    Product.objects.filter(expiry__lte = timezone.now()).delete()
    info_msg(request, u"%s produits expirés ont été supprimés." % removed)

def clean_history(request):
    history_list = History.objects.all()
    now = timezone.now()
    for i in range(2):
        history_list = history_list.exclude(date_created__year = now.year - i)
    nb_deleted = history_list.count()

    for history in history_list:
        for item in history.items.all():
            item.delete()
        history.delete()

    info_msg(request, u"%s commandes ont été supprimées de l'historique." % nb_deleted)

def clean_budgets(request):
    budget_lines = BudgetLine.objects.filter(is_active = False)

    now = timezone.now()
    for i in range(2):
        budget_lines = budget_lines.exclude(date__year = now.year - i)

    budget_ids = set(budget_lines.values_list("budget_id", flat = True))
    budget_lines.delete()

    Budget.objects.filter(id__in = budget_ids).delete()

    info_msg(request, "%s budgets archivés ont été supprimés de l'historique." % len(list(budget_ids)))

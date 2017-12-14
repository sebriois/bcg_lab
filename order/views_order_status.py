# encoding: utf-8
from datetime import datetime

from django.db import transaction
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core.mail import send_mail
from django.urls import reverse
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.template import loader

from budget.models import Budget, BudgetLine
from order.models import Order
from team.models import TeamMember
from utils import GET_method
from utils.request_messages import error_msg, info_msg, warn_msg


@login_required
@GET_method
@transaction.atomic
def set_next_status(request, order_id):
    order = get_object_or_404(Order, id = order_id)
    
    if order.status == 0:
        return _move_to_status_1(request, order)
    
    elif order.status == 1 and request.user.has_perm('order.custom_validate'):
        if request.user.has_perm('team.custom_view_teams'):
            return _move_to_status_2(request, order)
        elif order.team.members.filter(user = request.user):
            return _move_to_status_2(request, order)
        else:
            error_msg(request, "Vous ne disposez pas des permissions nécessaires pour valider cette commande")
            return redirect('tab_validation')
    
    elif order.status == 2 and request.user.has_perm('order.custom_goto_status_3'):
        return _move_to_status_3(request, order)
    
    elif order.status == 3 and request.user.has_perm('order.custom_goto_status_4'):
        return _move_to_status_4(request, order)
    
    elif order.status == 4:
        return _move_to_status_5(request, order)
    
    else:
        error_msg(request, "Vous n'avez pas les permissions nécessaires pour modifier le statut de cette commande")
    
    return redirect('tab_orders')


def _move_to_status_1(request, order):
    missing_nomenclature = order.items.filter(
        Q(nomenclature__isnull = True) |
        Q(nomenclature = '')
    )
    if missing_nomenclature.count() > 0:
        for item in missing_nomenclature:
            error_msg(request, "Veuillez saisir une nomenclature pour l'item '%s' de la commande %s en cliquant sur "
                               "le bouton 'modifier' de la ligne correspondante." % (item.name, order.provider.name))
        return redirect('tab_cart')

    order.status = 1
    order.save()
    info_msg(request, "Nouveau statut: '%s'." % order.get_status_display())

    if not settings.DEBUG:
        emails = []
        for member in order.team.members.all():
            user = member.user
            if user.has_perm('order.custom_validate') and not user.is_superuser and user.email and user.email not in emails:
                emails.append(user.email)

        if emails:
            subject = "[BCG-Lab %s] Validation d'une commande (%s)" % (settings.SITE_NAME, order.get_full_name())
            template = loader.get_template('order/validation_email.txt')
            context = {
                'order': order,
                'url': request.build_absolute_uri(reverse('order:tab_validation'))
            }
            message = template.render(context)
            for email in emails:
                try:
                    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
                except:
                    continue
        else:
            warn_msg(request, "Aucun email de validation n'a pu être \
            envoyé puisqu'aucun validateur n'a renseigné d'adresse email.")
    
    if request.user.has_perm('order.custom_validate'):
        return redirect('tab_validation')
    
    return redirect('tab_cart')


def _move_to_status_2(request, order):
    if order.provider.is_local:
        subject = "[BCG-Lab %s] Nouvelle commande magasin" % settings.SITE_NAME
        template = loader.get_template('email_local_provider.txt')
        url = request.build_absolute_uri(reverse('order:tab_reception_local_provider'))
        message = template.render({'order': order, 'url': url})
        emails = Group.objects.filter(permissions__codename="custom_view_local_provider").values_list("user__email", flat=True)
        
        for email in emails:
            try:
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
            except:
                continue
        
        order.status = 4
        order.save()
        
        for item in order.items.all():
            item.delivered = item.quantity
            item.save()
        
        info_msg(request, "Un email a été envoyé au magasin pour la livraison de la commande.")
    else:
        budget_id = request.GET.get("budget", None)
        if budget_id:
            order.budget = Budget.objects.get(id = budget_id)
        
        if order.budget and BudgetLine.objects.filter(order_id = order.id).count() == 0:
            order.create_budget_line()
        
        order.status = 2
        order.save()
        
        usernames = []
        for item in order.items.all():
            if not item.username in usernames:
                usernames.append(item.username)

        members = TeamMember.objects.filter(
            user__username__in = usernames,
            send_on_validation = True,
            user__email__isnull = False
        ).exclude(
            user__email = ''
        )
        for tm in members:
            subject = u"[BCG-Lab %s] Votre commande %s a été validée" % (settings.SITE_NAME, order.provider.name)
            template = loader.get_template("email_order_detail.txt")
            message = template.render({ 'order': order })
            try:
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [tm.user.email])
            except:
                continue
        
        info_msg(request, "Nouveau statut: '%s'." % order.get_status_display())
    return redirect(request.GET.get('next','tab_validation'))


def _move_to_status_3(request, order):
    if order.budget:
        order.status = 3
        order.save()
        
        if BudgetLine.objects.filter(order_id = order.id).count() == 0:
            order.create_budget_line()
        
        info_msg(request, "Nouveau statut: '%s'." % order.get_status_display())
        return redirect('tab_orders')
    else:
        error_msg(request, "Veuillez choisir un budget à imputer")
        return redirect(order.get_absolute_url())
    

def _move_to_status_4(request, order):
    if not order.number:
        if not order.budget:
            msg = "Veuillez sélectionner un budget."
        else:
            if order.budget.budget_type == 0: # ie. CNRS
                msg = "Commande CNRS, veuillez saisir le numéro de commande SILAB."
            else:
                msg = "Commande UPS, veuillez saisir le numéro de commande SIFAC."
        
        error_msg(request, msg)
        return redirect(order.get_absolute_url())
    
    order.status = 4
    order.is_urgent = False
    order.save()
    
    # order.create_budget_line()
    
    for item in order.items.all():
        item.delivered = item.quantity
        item.save()
    
    # Prepare emails to be sent
    usernames = list(set(order.items.values_list("username", flat=True)))
    for tm in TeamMember.objects.filter(user__username__in = usernames, send_on_sent = True, user__email__isnull = False):
        subject = u"[BCG-Lab %s] Votre commande %s a été envoyée" % (settings.SITE_NAME, order.provider.name)
        template = loader.get_template("email_order_detail.txt")
        message = template.render({ 'order': order })
        try:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [tm.user.email])
        except:
            continue
    
    info_msg(request, "Nouveau statut: '%s'." % order.get_status_display())
    
    # return redirect(reverse('order:tab_orders') + "?page=%s" % request.GET.get("page","1"))
    return redirect(order)


def _move_to_status_5(request, order):
    try:
        delivery_date = request.GET.get('delivery_date', None)
        delivery_date = datetime.strptime(delivery_date, "%d/%m/%Y")
        if delivery_date < order.date_created:
            error_msg(request, u"Veuillez saisir une date de livraison supérieure à la date de création de la commande.")
            return redirect(order)
    except:
        error_msg(request, u"Veuillez saisir une date valide (format jj/mm/aaaa).")
        return redirect('tab_orders')
    
    order.save_to_history(delivery_date)
    order.delete()
    
    info_msg(request, "La commande a été enregistrée dans l'historique.")
    return redirect('tab_orders')


# coding: utf-8
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template import Context, loader
from django.shortcuts import redirect, render
from django.conf import settings

from team.utils import in_team_secretary
from utils import POST_method
from utils.request_messages import warn_msg, info_msg


@login_required
def home(request):
    if in_team_secretary( request.user ) and not request.user.is_superuser:
        return redirect('order:tab_orders')

    if request.user.has_perm('order.custom_view_local_provider'):
        return redirect('order:tab_reception_local_provider')

    if request.user.has_perm('order.custom_validate'):
        return redirect('order:tab_validation')

    return redirect('infos:index')


def error(request):
    return render( request, '500.html', {} )


@login_required
@POST_method
def send_message(request):
    subject = "[BCG-Lab %s] %s" % (settings.SITE_NAME, request.POST.get('subject', 'Nouveau message'))
    message = request.POST.get('message', '')
    emails = []
    for user_id in request.POST.get('to', None).split(','):
        user = User.objects.get(id = user_id)
        if user.email:
            emails.append(user.email)
        else:
            warn_msg(request, "Le message n'a pas pu être envoyé à %s, faute d'adresse email valide." % user)
  
    default_from = request.user.email and request.user.email or settings.DEFAULT_FROM_EMAIL

    template = loader.get_template('email_empty.txt')
    message = template.render({'message': message})
    send_mail( subject, message, default_from, emails )
    info_msg(request, "Message envoyé avec succès.")

    return redirect(request.POST.get('next','home'))

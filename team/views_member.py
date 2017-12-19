# coding: utf-8
from django.shortcuts import get_object_or_404, redirect
from django.db import transaction
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import SetPasswordForm
from django.shortcuts import render
from django.urls import reverse
from django.core.mail import send_mail
from django.template import loader

from team.models import TeamMember
from team.forms import TeamMemberForm, SignUpForm
from utils.request_messages import info_msg, error_msg


@login_required
@transaction.atomic
def item(request, member_id):
    member = get_object_or_404(TeamMember, id = member_id)
    if request.method == 'GET':
        return _member_detail(request, member)
    if request.method == 'POST':
        return _member_update(request, member)


@transaction.atomic
def new_user(request):
    form = SignUpForm()

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            team = form.cleaned_data.get('team')
            new_user = form.save(commit = False)
            new_user.is_active = False
            new_user.save()

            new_member = TeamMember.objects.create(user = new_user, team = team)

            if not settings.DEBUG:
                # SEND EMAIL FOR ACTIVATING ACCOUNT...
                subject = "[BCG-Lab %s] Demande d'ouverture de compte" % settings.SITE_NAME
                emails = set()
                for user in User.objects.filter(teammember__team = team).exclude(email__isnull = True):
                    if user.has_perm('team.custom_activate_account'):
                        emails.add(user.email)

                if emails:
                    template = loader.get_template('email_new_member.txt')
                    message = template.render({
                        'member': new_member,
                        'url': request.build_absolute_uri(reverse('team:index'))
                    })
                    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, list(emails))
                    info_msg(request, u"Votre demande a bien été prise en compte mais votre compte reste INACTIF en attendant sa validation.")

            return redirect('login')
        else:
            error_msg(request, u"Impossible de créer votre compte pour le moment")

    return render(request, 'auth/register.html',{
        'form': form
    })


@login_required
@transaction.atomic
def toggle_active(request, user_id):
    user = get_object_or_404(User, id = user_id)
    user.is_active = not user.is_active
    user.save()

    if not user.email:
        return redirect('team:index')

    if user.is_active:
        subject = "[BCG-Lab %s] Votre compte vient d'être activé" % settings.SITE_NAME
        content = "Vous pouvez désormais vous connecter à l`application."
    else:
        subject = "[BCG-Lab %s] Votre compte vient d'être inactivé" % settings.SITE_NAME
        content = "Vous ne pouvez plus vous connecter à l`application pour le moment."

    emails = [user.email]
    template = loader.get_template('email_empty.txt')
    message = template.render({ 'message': content })
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, emails)
    return redirect('team:index')


@login_required
@transaction.atomic
def set_password(request, user_id):
    user = get_object_or_404(User, id = user_id)

    if request.method == 'GET':
        form = SetPasswordForm(user = user)

        return render(request, 'auth/set_password.html', {
            'form': form,
            'user_id': user_id
        })
    elif request.method == 'POST':
        form = SetPasswordForm(user = user, data = request.POST)

        if form.is_valid():
            form.save()
            info_msg(request, 'Nouveau mot de passe enregistré.')
        else:
            return render(request, 'auth/set_password.html', {
                'form': form,
                'user_id': user_id
            })

    return redirect('team:index')

@login_required
@transaction.atomic
def delete(request, user_id):
    from order.models import Order
    user = get_object_or_404(User, id = user_id)

    for order in Order.objects.filter(number__isnull = True, items__username = user.username):
        for item in order.items.filter(username = user.username):
            item.delete()
        if order.items.all().count() == 0:
            order.delete()

    user.delete()
    info_msg(request, u"Utilisateur supprimé avec succès.")

    return redirect('team:index')


#--- Private views
def _member_detail(request, member):
    form = TeamMemberForm(instance = member, is_admin = request.user.has_perm('team.custom_edit_member'))
    return render(request, 'member/item.html',{
        'member': member,
        'form': form
    })


def _member_update(request, member):
    data = request.POST.copy()

    # Need to do that cause field are disabled in HTML, so values are not
    # sent over.
    if not request.user.has_perm('team.custom_edit_member'):
        data.update({
            'team': member.team.id,
            'username': member.user.username
        })

    form = TeamMemberForm(
        instance = member,
        is_admin = request.user.has_perm('team.custom_edit_member'),
        data = data
    )

    if form.is_valid():
        data = form.cleaned_data
        member.team = data['team']
        member.user.username = data['username']
        member.user.first_name = data['first_name']
        member.user.last_name = data['last_name']
        member.user.email = data['email']
        member.user.save()
        member.save()

        info_msg(request, u"Utilisateur modifié avec succès.")
        return redirect('team:index')
    else:
        return render(request, 'member/item.html',{
            'member': member,
            'form': form
        })

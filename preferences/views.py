# coding: utf-8
from django.shortcuts import redirect
from django.db import transaction
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from preferences.forms import UserPrefForm, EmailPrefForm

from utils.request_messages import info_msg


@login_required
@transaction.atomic
def index(request):
    member = request.user.teammember_set.get()
    user_form = UserPrefForm(instance = request.user)
    try:
        email_form = EmailPrefForm(instance = member)
    except:
        email_form = None

    if request.method == 'POST':
        data = request.POST.copy()
        form_name = data['form_name']
        del data['form_name']
        
        if form_name == 'user_form':
            user_form = UserPrefForm(instance = request.user, data = data)
            if user_form.is_valid():
                user_form.save()
                info_msg(request, "Préférences enregistrées!")
            
            try:
                email_form = EmailPrefForm(instance = member)
            except:
                email_form = None
        
        elif form_name == 'email_form':
            email_form = EmailPrefForm(instance = member, data = data)
            if email_form.is_valid():
                email_form.save()
                info_msg(request, "Préférences enregistrées!")
            user_form = UserPrefForm(instance = request.user)
    
    return render(request, "preferences/index.html", {
        'user_form': user_form,
        'email_form': email_form
    })

@login_required
@transaction.atomic
def change_password(request):
    form = PasswordChangeForm(user = request.user)

    if request.method == 'POST':
        form = PasswordChangeForm(user = request.user, data = request.POST)
        if form.is_valid():
            form.save()
            info_msg(request, "Nouveau mot de passe enregistré!")
            return redirect('change_password')
    
    return render(request, "preferences/change_password.html", {
        'form': form
    })

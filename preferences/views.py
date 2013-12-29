# coding: utf-8
from django.shortcuts import get_object_or_404, redirect
from django.db import transaction
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from preferences.forms import UserPrefForm, EmailPrefForm

from bcg_lab.constants import *
from utils import *

@login_required
@transaction.commit_on_success
def index(request):
    if request.method == 'GET':
        user_form = UserPrefForm( instance = request.user )
        try:
            email_form = EmailPrefForm( instance = get_team_member(request) )
        except:
            email_form = None
    elif request.method == 'POST':
        data = request.POST.copy()
        form_name = data['form_name']
        del data['form_name']
        
        if form_name == 'user_form':
            user_form = UserPrefForm( instance = request.user, data = data )
            if user_form.is_valid():
                user_form.save()
                info_msg( request, "Préférences enregistrées!")
            
            try:
                email_form = EmailPrefForm( instance = get_team_member(request) )
            except:
                email_form = None
        
        elif form_name == 'email_form':
            email_form = EmailPrefForm( instance = get_team_member(request), data = data )
            if email_form.is_valid():
                email_form.save()
                info_msg( request, "Préférences enregistrées!" )
            user_form = UserPrefForm( instance = request.user )
    
    return render( request, "preferences/index.html", {
        'user_form': user_form,
        'email_form': email_form
    })

@login_required
@transaction.commit_on_success
def change_password(request):
    if request.method == 'GET':
        form = PasswordChangeForm( user = request.user )
    elif request.method == 'POST':
        form = PasswordChangeForm( user = request.user, data = request.POST )
        if form.is_valid():
            form.save()
            info_msg( request, "Nouveau mot de passe enregistré!" )
            return redirect( 'change_password' )
    
    return render( request, "preferences/change_password.html", {
        'form': form
    })
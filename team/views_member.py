# coding: utf-8
from datetime import datetime, date

from django.shortcuts import get_object_or_404, redirect
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.views.generic.simple import direct_to_template
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm

from team.models import Team, TeamMember
from team.forms import TeamForm, TeamMemberForm

from constants import *
from utils import info_msg, error_msg, warn_msg, superuser_required

@login_required
@transaction.commit_on_success
def item(request, member_id):
    member = get_object_or_404(TeamMember, id = member_id)
    if request.method == 'GET': return _member_detail(request, member)
    if request.method == 'PUT': return _member_update(request, member)

def new_user(request):
    form = UserCreationForm()
    
    if 'member_user' in request.session:
      return direct_to_template( request, 'member/form.html', {
        'form': TeamMemberForm()
      })
    
    if request.method == 'POST':
      form = UserCreationForm( data = request.POST )
      if form.is_valid():
        user = form.save()
        user.is_active = False
        user.save()
        
        request.session['member_user'] = user
        request.session.save()
        return direct_to_template( request, 'member/form.html', {
          'form': TeamMemberForm()
        })
    
    return direct_to_template( request, 'auth/register.html', { 'form': form })

def new_member(request):
  if not 'member_user' in request.session:
    return redirect('new_user')
  
  user = request.session.get('member_user')
  
  if TeamMember.objects.filter( user = user ).count() > 0:
    try:
      del request.session['member_user']
    except KeyError:
      pass
    return redirect('new_user')
  
  if request.method == 'POST':
    user = request.session.get('member_user')
    data = request.POST.copy()
    data.update({ 'username': user.username })
    
    form = TeamMemberForm( data = data )
    if form.is_valid():
      data = form.cleaned_data
      member = TeamMember.objects.create(
        team = data['team'],
        user = user
      )
      user.first_name = data['first_name']
      user.last_name = data['last_name']
      user.email = data['email']
      user.save()
      
      del request.session['member_user']
      
      info_msg( request, u"Votre demande de création de compte a bien été envoyée. Vous serez informé(e) par email dès qu'elle aura été validée.")
      return redirect( 'home' )
  else:
    form = TeamMemberForm()
  
  return direct_to_template(request, 'member/form.html',{
      'form': form,
      'user_id': user.id
  })

@login_required
@transaction.commit_on_success
def toggle_active( request, user_id ):
  user = get_object_or_404( User, id = user_id )
  user.is_active = not user.is_active
  user.save()
  return redirect('team_index')

@login_required
def change_password(request, user_id):
  if request.method == 'GET':
    return direct_to_template(request, 'auth/change_password.html', {
      'form': PasswordChangeForm( user = user_id )
    })
  elif request.method == 'POST':
    form = PasswordChangeForm( user = user_id, data = request.POST )
    if form.is_valid():
      form.save()
      info_msg( request, 'Votre nouveau mot de passe a été enregistré.')
    else:
      return direct_to_template(request, 'auth/change_password.html', {
        'form': form
      })
  
  return redirect('home')

@login_required
@superuser_required
def delete(request, user_id):
    User.objects.get(id = user_id).delete()
    info_msg( request, u"Utilisateur supprimé avec succès." )
    return redirect( 'team_index' )


#--- Private views
def _member_detail(request, member):
    form = TeamMemberForm(instance = member)
    return direct_to_template(request, 'member/item.html',{
        'member': member,
        'form': form
    })

def _member_update(request, member):
    form = TeamMemberForm(instance = member, data = request.REQUEST)
    
    if form.is_valid():
        data = form.cleaned_data
        member.team = data['team']
        member.user.username = data['username']
        member.user.first_name = data['first_name']
        member.user.last_name = data['last_name']
        member.user.email = data['email']
        member.user.save()
        
        member.member_type = data['member_type']
        member.save()
        
        info_msg( request, u"Utilisateur modifié avec succès." )
        return redirect( 'team_index' )
    else:
        return direct_to_template(request, 'member/item.html',{
            'member': member,
            'form': form
        })

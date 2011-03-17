# coding: utf-8
from datetime import datetime, date

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.views.generic.simple import direct_to_template

from team.models import Team, TeamMember
from team.forms import TeamForm

from constants import *
from utils import info_msg, error_msg, warn_msg
from utils import superuser_required, teamchief_required


@login_required
@transaction.commit_on_success
def index(request):
    if request.method == 'GET':   return _team_list(request)
    if request.method == 'POST':  return _team_creation(request)

@login_required
@transaction.commit_on_success
def item(request, team_id):
    team = get_object_or_404(Team, id = team_id)
    if request.method == 'GET':     return _team_detail(request, team)
    if request.method == 'PUT':     return _team_update(request, team)

@login_required
@superuser_required
def new(request):
    return direct_to_template(request, 'team/form.html', { 'form': TeamForm() })

#--- Private views
def _team_list(request):
    noteam = []
    for user in User.objects.all():
      if user.teammember_set.all().count() == 0:
        noteam.append( user )
    
    if user.is_superuser:
      teams = Team.objects.all()
    else:
      teams = [m.team for m in user.teammember_set.all()]
    
    return direct_to_template(request, 'team/index.html',{
        'team_list': teams,
        'noteam': noteam
    })

@teamchief_required
def _team_detail(request, team):
    form = TeamForm(instance = team)
    return direct_to_template(request, 'team/item.html',{
        'team': team,
        'form': form
    })

def _team_creation(request):
  form = TeamForm(request.POST)
  if form.is_valid():
    team = form.save()
    
    info_msg( request, u"Equipe ajoutée avec succès." )
    return redirect( 'team_index' )
  else:
    return direct_to_template(request, 'team/form.html',{
        'form': form
    })

def _team_update(request, team):
    form = TeamForm(instance = team, data = request.REQUEST)
    if form.is_valid():
        team = form.save()
        
        info_msg( request, u"Equipe modifiée avec succès." )
        return redirect( 'team_index' )
    else:
        return direct_to_template(request, 'team/item.html',{
            'team': team,
            'form': form
        })
# coding: utf-8
from datetime import datetime, date

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from team.models import Team, TeamMember
from team.forms import TeamForm
from history.models import History

from bcg_lab.constants import *
from utils import *


@login_required
@transaction.commit_on_success
def index(request):
	if request.method == 'GET':	 return _team_list(request)
	if request.method == 'POST': return _team_creation(request)

@login_required
@transaction.commit_on_success
def item(request, team_id):
	team = get_object_or_404(Team, id = team_id)
	if request.method == 'GET':	 return _team_detail(request, team)
	if request.method == 'POST': return _team_update(request, team)

@login_required
def new(request):
	return render(request, 'team/form.html', {
		'form': TeamForm()
	})

@login_required
def add_user_to_team(request, user_id):
	user = get_object_or_404( User, id = user_id )
	
	team_id = request.GET.get( 'team_id', None )
	if team_id:
		team = get_object_or_404( Team, id = team_id )
		member = TeamMember.objects.create(
			user = user,
			team = team
		)
	return redirect( 'team_index' )


#--- Private views
def _team_list(request):
	noteam = []
	for user in User.objects.all():
		if user.teammember_set.all().count() == 0:
			noteam.append( user )
	
	if request.user.has_perm("team.custom_view_teams"):
		teams = Team.objects.all()
	else:
		teams = get_teams( request.user )
	
	return render(request, 'team/index.html',{
		'team_list': teams,
		'noteam': noteam
	})

def _team_detail(request, team):
	form = TeamForm(instance = team)
	return render(request, 'team/item.html',{
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
		return render(request, 'team/form.html',{
				'form': form
		})

def _team_update(request, team):
	form = TeamForm(instance = team, data = request.POST)
	name_before = team.name
	
	if form.is_valid():
		team = form.save()
		
		if name_before != team.name:
			for budget in team.budget_set.all():
				budget.update_budgetlines() # Will update bl.team
			for history in History.objects.filter( team = name_before ):
				history.team = team.name
				history.save()
		
		info_msg( request, u"Equipe modifiée avec succès." )
		return redirect( 'team_index' )
	else:
		return render(request, 'team/item.html',{
				'team': team,
				'form': form
		})
	

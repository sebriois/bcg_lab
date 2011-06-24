# coding: utf-8
from django.shortcuts import get_object_or_404, redirect
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.views.generic.simple import direct_to_template

from issues.models import Issue
from issues.forms import IssueForm

from constants import *
from utils import *

@login_required
@transaction.commit_on_success
def index(request):
	if request.method == 'POST':
		form = IssueForm( data = request.POST )
		if form.is_valid(): form.save()
		return redirect('home')

@login_required
@transaction.commit_on_success
def item(request, issue_id):
	issue = get_object_or_404( Issue, id = issue_id )
	if request.method == 'GET':
		form = IssueForm( instance = issue )
	elif request.method == 'POST':
		form = IssueForm( data = request.POST, instance = issue )
		if form.is_valid():
			form.save()
			return redirect('home')
	
	return direct_to_template( request, 'issues/item.html', {
		'form': form,
		'issue': issue
	})

@login_required
@transaction.commit_on_success
def delete(request, issue_id):
	issue = get_object_or_404( Issue, id = issue_id )
	issue.delete()
	return redirect('home')

@login_required
@transaction.commit_on_success
def set_status(request, issue_id, status):
	issue = get_object_or_404( Issue, id = issue_id )
	issue.status = int(status)
	issue.save()
	return redirect('home')
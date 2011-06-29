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
	if request.method == 'GET':
		if request.GET.get('fixed',False):
			issues = Issue.objects.filter( status = 4 )
		else:
			issues = Issue.objects.exclude( status = 4 )
		
		return direct_to_template( request, 'issues/index.html', {
			'issues': issues
		})
	
	elif request.method == 'POST':
		form = IssueForm( data = request.POST )
		if form.is_valid():
			form.save()
			return redirect('issue_index')
		else:
			return direct_to_template( request, 'issues/new.html', {
				'form': form
			})


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
			return redirect('issue_index')
	
	return direct_to_template( request, 'issues/item.html', {
		'form': form,
		'issue': issue
	})

@login_required
def new(request):
	return direct_to_template( request, "issues/new.html", {
		'form': IssueForm()
	})

@login_required
@transaction.commit_on_success
def delete(request, issue_id):
	issue = get_object_or_404( Issue, id = issue_id )
	issue.delete()
	return redirect('issue_index')

@login_required
@transaction.commit_on_success
def set_status(request, issue_id, status):
	issue = get_object_or_404( Issue, id = issue_id )
	issue.status = int(status)
	issue.save()
	return redirect('issue_index')
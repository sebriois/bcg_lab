# coding: utf-8
from datetime import datetime

from django.shortcuts import get_object_or_404, redirect
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from issues.models import Issue
from issues.forms import IssueForm

from bcg_lab.constants import *
from utils import *

@login_required
@transaction.commit_on_success
def index(request):
	if request.method == 'GET':
		if request.GET.get('fixed',False):
			issues = Issue.objects.filter( status__in = [2,4] ).order_by('-date_closed','-date_created')
		else:
			issues = Issue.objects.exclude( status__in = [2,4] )
		
		return render( request, 'issues/index.html', {
			'issues': issues,
			'show_fixed': 'fixed' in request.GET.keys()
		})
	
	elif request.method == 'POST':
		form = IssueForm( data = request.POST )
		if form.is_valid():
			issue = form.save()
			issue.username = request.user.username
			issue.save()
			return redirect('issue_index')
		else:
			return render( request, 'issues/new.html', {
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
	
	return render( request, 'issues/item.html', {
		'form': form,
		'issue': issue
	})

@login_required
@transaction.commit_on_success
def new(request):
	return render( request, "issues/new.html", {
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
	
	if issue.status == 4:
		issue.date_closed = datetime.now()
	
	issue.save()
	return redirect('issue_index')
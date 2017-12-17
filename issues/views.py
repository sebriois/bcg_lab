# coding: utf-8
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from issues.models import Issue
from issues.forms import IssueForm


@login_required
@transaction.atomic
def index(request):
    if request.method == 'GET':
        if request.GET.get('fixed',False):
            issues = Issue.objects.filter(status__in = [2,4]).order_by('-date_closed','-date_created')
        else:
            issues = Issue.objects.exclude(status__in = [2,4])

        return render(request, 'issues/index.html', {
            'issues': issues,
            'show_fixed': 'fixed' in request.GET.keys()
        })

    elif request.method == 'POST':
        form = IssueForm(data = request.POST)
        if form.is_valid():
            issue = form.save()
            issue.username = request.user.username
            issue.save()
            return redirect('issues:index')
        else:
            return render(request, 'issues/new.html', {
                'form': form
            })


@login_required
@transaction.atomic
def item(request, issue_id):
    issue = get_object_or_404(Issue, id = issue_id)
    form = IssueForm(instance = issue)

    if request.method == 'POST':
        form = IssueForm(data = request.POST, instance = issue)
        if form.is_valid():
            form.save()
            return redirect('issues:index')

    return render(request, 'issues/item.html', {
        'form': form,
        'issue': issue
    })


@login_required
@transaction.atomic
def new(request):
    return render(request, "issues/new.html", {
        'form': IssueForm()
    })


@login_required
@transaction.atomic
def delete(request, issue_id):
    issue = get_object_or_404(Issue, id = issue_id)
    issue.delete()
    return redirect('issues:index')


@login_required
@transaction.atomic
def set_status(request, issue_id, status):
    issue = get_object_or_404(Issue, id = issue_id)
    issue.status = int(status)

    if issue.status == 4:
        issue.date_closed = timezone.now()

    issue.save()
    return redirect('issues:index')
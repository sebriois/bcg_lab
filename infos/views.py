# coding: utf-8
from django.shortcuts import get_object_or_404, redirect
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.views.generic.simple import direct_to_template

from infos.models import Info
from infos.forms import InfoForm

from constants import *
from utils import *

@login_required
@team_required
@transaction.commit_on_success
def index(request):
	if request.method == 'POST':
		form = InfoForm( data = request.POST )
		
		if form.is_valid():
			form.save()
		
		return redirect('home')

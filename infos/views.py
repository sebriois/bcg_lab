# coding: utf-8
from django.shortcuts import get_object_or_404, redirect
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone

from infos.models import Info
from infos.forms import InfoForm

from team.utils import in_team_secretary


@login_required
@transaction.atomic
def index(request):
    Info.objects.filter(expiry__lt = timezone.now()).delete()
    return render(request, 'homepage.html', {
        'infos': Info.objects.all()
    })


@login_required
@transaction.atomic
def new(request):
    form = InfoForm()

    if request.method == 'POST':
        data = request.POST.copy()
        if in_team_secretary(request.user):
            data['text'] = u'<strong><u>INFO GESTION:</u></strong> %s' % data['text']
        if 'provider' in data.keys() and data['provider']:
            data['text'] = data['provider'] + " : " + data['text']

        form = InfoForm(data = data)
        if form.is_valid():
            form.save()
        return redirect('info_index')

    return render(request, 'infos/new.html', {
        'form': form
    })


@login_required
@transaction.atomic
def item(request, info_id):
    info = get_object_or_404( Info, id = info_id )
    form = InfoForm(instance = info)

    if request.method == 'POST':
        data = request.POST.copy()
        if 'provider' in data.keys() and data['provider']:
            data['text'] = data['provider'] + " : " + data['text']

        form = InfoForm(instance = info, data = data)
        if form.is_valid():
            form.save()
            return redirect( 'info_index' )

    return render( request, 'infos/item.html', {
        'form': form,
        'info': info
    })


@login_required
@transaction.atomic
def delete(request, info_id):
    info = get_object_or_404( Info, id = info_id )
    info.delete()

    return redirect('info_index')

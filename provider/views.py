# coding: utf-8
from django.shortcuts import get_object_or_404, redirect
from django.db import transaction
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from provider.models import Provider
from provider.forms import ProviderForm
from utils.request_messages import info_msg, error_msg, not_allowed_msg


@login_required
@transaction.atomic
def index(request):
    if request.method == 'GET':
        return render(request, 'provider/index.html',{
            'provider_list': Provider.objects.filter(is_service = False)
        })
    elif request.method == 'POST':
        form = ProviderForm(user = request.user, data = request.POST)
        if form.is_valid():
            form.save()
            info_msg(request, u"Fournisseur ajouté avec succès.")
            return redirect('provider_index')
        else:
            error_msg(request, "Impossible de créer le fournisseur.")
            return render(request, 'provider/form.html',{
                'form': form
            })

@login_required
@transaction.atomic
def item(request, provider_id):
    from product.models import Product

    provider = get_object_or_404(Provider, id = provider_id)
    form = ProviderForm(user = request.user, instance = provider)

    if request.method == 'POST':
        form = ProviderForm(user = request.user, instance = provider, data = request.POST)
        if form.is_valid():
            form.save()

            if provider.reseller:
                for product in provider.product_set.all():
                    if not product.origin: product.origin = provider.name
                    product.provider = provider.reseller
                    product.save()

                for product in Product.objects.filter(origin = provider.name):
                    product.provider = provider.reseller
                    product.save()
            else:
                for product in Product.objects.filter(origin = provider.name):
                    product.provider = provider
                    product.origin = None
                    product.save()

            info_msg(request, u"Fournisseur modifié avec succès.")
            return redirect('provider_index')

    return render(request, 'provider/item.html', {
        'provider': provider,
        'form': form
    })


@login_required
def new(request):
    return render(request, 'provider/form.html', {
        'form': ProviderForm(user = request.user)
    })


@login_required
@transaction.atomic
def delete(request, provider_id):
    provider = get_object_or_404(Provider, id = provider_id)

    if request.method == 'GET':
        return render(request, "provider/delete.html", {
            'provider': provider
        })
    elif request.method == 'POST':
        provider.delete()
        info_msg(request, u"Fournisseur supprimé avec succès.")
        return redirect('provider_index')


@login_required
@transaction.atomic
def set_notes(request, provider_id):
    if not request.is_ajax():
        not_allowed_msg(request)
        return redirect("provider_index")

    provider = get_object_or_404(Provider, id = provider_id)
    provider.notes = request.GET['notes']
    provider.save()

    return HttpResponse("ok")

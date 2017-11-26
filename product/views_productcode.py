#coding: utf-8
import xlrd
import json

from django.shortcuts import redirect, render
from django.db import transaction
from django.db.models.query import Q
from django.http import HttpResponse

from product.models import ProductCode
from product.forms import ProductCodeForm
from utils.request_messages import info_msg


@transaction.atomic
def import_product_codes(request):
    if request.method == 'POST':
        form = ProductCodeForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'])
            info_msg(request, "File imported successfully")
            return redirect('import_product_codes')
    else:
        form = ProductCodeForm()
    
    return render(request, 'product/import_codes.html', {'form': form})


def handle_uploaded_file(f):
    book = xlrd.open_workbook( file_contents = f.read() )
    sheet = book.sheet_by_index(0)
    
    errors = []
    
    for row_idx in range(sheet.nrows):
        row = sheet.row(row_idx)
        ProductCode.objects.get_or_create(
            code = row[0].value,
            title = row[1].value
        )


def autocomplete_product_codes(request):
    q = request.GET.get('query', None)
    suggestions = []
    if q and len(q) >= 2:
        product_codes = ProductCode.objects.filter( Q(code__icontains = q) | Q(title__icontains = q) )
        suggestions = ["%s - %s" % (pc.code, pc.title) for pc in product_codes]
    response_dict = {
        'query': q,
        'suggestions': suggestions
    }
    return HttpResponse(json.dumps(response_dict))

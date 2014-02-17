import json

from django.db.models.query import Q
from django.http import HttpResponse

from order.models import Order
from budget.models import BudgetLine
from history.models import History

def autocomplete_order_number(request):
    q = request.GET.get('query', None)
    suggestions = []
    if q and len(q) >= 2:
        order_numbers = list(Order.objects.filter( number__icontains = q ).only('number').values_list('number', flat = True))
        budgetline_numbers = list(BudgetLine.objects.filter( number__icontains = q ).only('number').values_list('number', flat = True))
        history_numbers = list(History.objects.filter( number__icontains = q ).only('number').values_list('number', flat = True))
        suggestions = list(set(order_numbers + budgetline_numbers))
        suggestions.sort()
        
    response_dict = {
        'query': q,
        'suggestions': suggestions
    }
    return HttpResponse(json.dumps(response_dict))

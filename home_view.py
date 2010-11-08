from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from order_manager.order.models import Order

@login_required
def home(request):
  return direct_to_template( request, 'homepage.html', {
    'user_orders': Order.objects.filter( user = request.user, date_delivered__isnull = True ),
    'other_orders': Order.objects.exclude( user = request.user ).filter( date_delivered__isnull = True ),
    'user_list': User.objects.all()
  })

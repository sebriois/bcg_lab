# coding: utf-8

from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail

from order.models import Order

@login_required
def home(request):
  MONTHS = {
    1: "Janvier",
    2: "Février",
    3: "Mars",
    4: "Avril",
    5: "Mai",
    6: "Juin",
    7: "Juillet",
    8: "Aout",
    9: "Septembre",
    10: "Octobre",
    11: "Novembre",
    12: "Décembre"
  }
  
  data, months = [], []
  for month in range(1,13):
    nb_orders = Order.objects.filter( date_delivered__year = 2010, date_delivered__month = month ).count()
    if nb_orders == 0: continue
    
    data.append(str(nb_orders))
    months.append(MONTHS[month])
  
  args = []
  args.append( "cht=p3" )
  args.append( "chs=250x100" )
  args.append( "chd=t:%s" % ",".join(data) )
  # args.append( "chdl=2010")
  args.append( "chl=%s" % "|".join(months) )
  
  # return redirect('provider_index')
  return direct_to_template( request, 'homepage.html', {
    # 'url_args': "&amp;".join(args)
    'url_args': "&".join(args)
  })

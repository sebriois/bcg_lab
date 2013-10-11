# -*- coding: utf8 -*-
from django.core.management.base import BaseCommand
from django.conf import settings

from datetime import datetime, timedelta

from order.models import Order

class Command(BaseCommand):
    can_import_settings = True
    help = 'Send alerts for order having a non changed status for 21 days and 31 days'
    
    def handle(self, *args, **options):
        verbose = options.get('verbosity', 0)
        
        orders = Order.objects.filter(
            provider__direct_reception = True, 
            last_change__lte = datetime.now() - timedelta(days = 7)
        )
        
        for order in orders:
            if order.items.filter( delivered__gt = 0 ).count() == 0:
                print u"Commande %s (%s) receptionnee et archivee." % ( order.number, order.provider.name )
                order.save_to_history()
                order.delete()
        
    

# -*- coding: utf8 -*-
import sys
from optparse import make_option
from django.core.management.base import BaseCommand
from django.conf import settings

from datetime import datetime, timedelta

from product.models import Product

class Command(BaseCommand):
    can_import_settings = True
    help = 'Update SolR index with last_modified products'
    
    option_list = BaseCommand.option_list + (
        make_option(
            "-d", 
            "--date", 
            dest = "date",
            help = "index products modified after this date",
        ),
    )

    option_list = option_list + (
        make_option(
            "-p", 
            "--provider", 
            dest = "provider",
            help = "only index products for this provider", 
        ),
    )
    
    def handle(self, *args, **options):
        ref_date = options.get('date', None)
        if not ref_date:
            date_obj = datetime.now() - timedelta(days = 1)
        else:
            try:
                date_obj = datetime.strptime(ref_date, "%d/%m/%Y")
            except:
                raise Exception("Date format: dd/mm/yyyy")
        products = Product.objects.filter( last_change__gte = date_obj )
        
        provider = options.get('provider', None)
        if provider:
            products = products.filter( provider__name = provider )

        print >> sys.stderr, "%s modified products found after %s." % (products.count(), date_obj.strftime("%d/%m/%Y %H:%M"))
        
        for product in products:
            product.post_to_solr()
        
    

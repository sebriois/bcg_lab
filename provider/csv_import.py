# coding: utf-8

import datetime
import csv
import xlrd
from decimal import Decimal

from django.utils import simplejson as json
from django.views.generic.simple import direct_to_template
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.db import transaction

from provider.models import Provider
from product.models import Product
from provider.forms import ImportForm

from constants import *
from utils import *

class ImportCSVException(Exception):
	"""
	Raised on any error found when processing CSV file
	"""


@login_required
def export_csv( request, provider_id ):
	provider = get_object_or_404( Provider, id = provider_id )
	
	response = render_to_response("provider/export.csv", {
			'products': provider.product_set.all()
	})
	filename = "%s.csv" % (provider.name)
	response['Content-Disposition'] = 'attachment; filename='+filename
	response['Content-Type'] = 'application/vnd.ms-excel; charset=utf-8'
	
	return response

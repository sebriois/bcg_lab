# coding: utf8

from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.contrib import messages
from django.shortcuts import redirect

def info_msg( request, message ):
  return messages.add_message( request, messages.INFO, message )

def error_msg( request, message ):
  return messages.add_message( request, messages.ERROR, message )

def warn_msg( request, message ):
  return messages.add_message( request, messages.WARNING, message )

def superuser_required( view ):
  """
  Decorator for views that checks the user is a superuser, redirecting
  to the home page if necessary.
  """
  def _wrapped_view( request, *args, **kwargs ):
    if not request.user.is_superuser:
      error_msg( request, u"Vous ne pouvez pas accéder à cette page." )
      return redirect('home')
    return view(request, *args, **kwargs)
  return _wrapped_view

def paginate( request, object_list, nb_items = 40 ):
  paginator = Paginator(object_list, nb_items ) # Show nb_items per page
  
  # Make sure page request is an int. If not, deliver first page.
  try:
    page = int(request.GET.get('page', '1'))
  except ValueError:
    page = 1
  
  # If page request (9999) is out of range, deliver last page of results.
  try:
    return paginator.page(page)
  except (EmptyPage, InvalidPage):
    return paginator.page(paginator.num_pages)

# coding: utf8

from urllib import quote_plus, urlencode
from urllib2 import Request, urlopen
from urllib2 import HTTPError

from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.contrib import messages
from django.shortcuts import redirect
from team.models import Team, TeamMember

def info_msg( request, message ):
    return messages.add_message( request, messages.INFO, message )

def error_msg( request, message ):
    return messages.add_message( request, messages.ERROR, message )

def warn_msg( request, message ):
    return messages.add_message( request, messages.WARNING, message )

def in_team_secretary(user):
    return user.has_perm('order.custom_goto_status_4') and not user.is_superuser

def GET_method(view):
    """
    Decorator that checks whether the view is called using the GET method
    """
    def _wrapped_view( request, *args, **kwargs ):
        if not request.method == 'GET':
            error_msg( request, "This request method (%s) is not handled on this page" % request.method )
            return redirect( 'error' )
        return view(request, *args, **kwargs)
    
    return _wrapped_view

def POST_method(view):
    """
    Decorator that checks whether the view is called using the POST method
    """
    def _wrapped_view( request, *args, **kwargs ):
        if not request.method == 'POST':
            error_msg( request, "This request method (%s) is not handled on this page" % request.method )
            return redirect( 'error' )
        return view(request, *args, **kwargs)
    
    return _wrapped_view

def AJAX_method(view):
    """
    Decorator that checks whether the view is called using AJAX
    """
    def _wrapped_view( request, *args, **kwargs ):
        if not request.is_ajax():
            error_msg(request, 'Method %s not allowed at this URL' % request.method )
            return redirect( 'error' )
        return view(request, *args, **kwargs)
    
    return _wrapped_view
    

def superuser_required( view ):
    """
    Decorator that checks whether the user is a superuser, redirecting
    to the error page if not.
    """
    def _wrapped_view( request, *args, **kwargs ):
        if not request.user.is_superuser:
            error_msg( request, u"Vous ne pouvez pas accéder à cette page." )
            return redirect('error')
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

def get_team_member( request ):
    return request.user.teammember_set.get()

def get_teams( user ):
    return Team.objects.filter( teammember__user = user )

def not_allowed_msg( request ):
    error_msg(request, "Vous ne disposez pas des permissions nécessaires pour accéder à cette page.")

def send_request( url, args ):
    if not 'wt' in args:
        args['wt'] = 'python'
    print url + '?' + urlencode(args)
    req = Request( url, urlencode(args) )
    
    try:
        f = urlopen( req )
        return f.read()
    except HTTPError as error:
        print error.code, error.reason
        return False

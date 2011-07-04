# coding: utf8

from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.contrib import messages
from django.shortcuts import redirect
from team.models import Team, TeamMember
from constants import NORMAL, VALIDATOR, SECRETARY, ADMIN

def info_msg( request, message ):
	return messages.add_message( request, messages.INFO, message )

def error_msg( request, message ):
	return messages.add_message( request, messages.ERROR, message )

def warn_msg( request, message ):
	return messages.add_message( request, messages.WARNING, message )

def is_normal(user):
	if not user or user.is_anonymous(): return False
	return user.teammember_set.filter(member_type__in = [NORMAL, VALIDATOR, ADMIN]).count() > 0

def is_validator(user):
	if not user or user.is_anonymous(): return False
	return user.teammember_set.filter(member_type__in = [VALIDATOR, ADMIN]).count() > 0

def is_secretary(user):
	if not user or user.is_anonymous(): return False
	return user.teammember_set.filter(member_type__in = [SECRETARY, ADMIN]).count() > 0

def is_secretary_valid(user):
	if not user or user.is_anonymous(): return False
	return user.teammember_set.filter(member_type__in = [SECRETARY_VALID, ADMIN]).count() > 0

def is_admin(user):
	if not user or user.is_anonymous(): return False
	return user.teammember_set.filter(member_type = ADMIN).count() > 0

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
	Decorator that checks whether the view is called using the GET method
	"""
	def _wrapped_view( request, *args, **kwargs ):
		if not request.method == 'POST':
			error_msg( request, "This request method (%s) is not handled on this page" % request.method )
			return redirect( 'error' )
		return view(request, *args, **kwargs)
	
	return _wrapped_view
	

def PUT_method(view):
	"""
	Decorator that checks whether the view is called using the PUT method
	"""
	def _wrapped_view( request, *args, **kwargs ):
		if not request.method == 'PUT':
			error_msg( request, "This request method (%s) is not handled on this page" % request.method )
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

def team_required( view ):
	"""
	Decorator that checks whether the user belongs to a team, redirecting
	to the error page if not.
	"""
	def _wrapped_view( request, *args, **kwargs ):
		if not TeamMember.objects.filter( user = request.user ).count() > 0:
			warn_msg( request, u"Vous devez appartenir à une équipe pour accéder à cette page." )
			return redirect('error')
		return view(request, *args, **kwargs)
	return _wrapped_view

def validator_required( view ):
	"""
	Decorator that checks whether the user is a validator, redirecting
	to the error page if not.
	"""
	def _wrapped_view( request, *args, **kwargs ):
		if not is_validator(request.user):
			warn_msg( request, u"Vous devez être validateur pour accéder à cette page." )
			return redirect('error')
		return view(request, *args, **kwargs)
	return _wrapped_view
	
def secretary_required( view ):
	"""
	Decorator that checks whether the user belongs to a team, redirecting
	to the error page if not.
	"""
	def _wrapped_view( request, *args, **kwargs ):
		if not is_secretary(request.user):
			warn_msg( request, u"Vous devez être gestionnaire pour accéder à cette page." )
			return redirect('error')
		return view(request, *args, **kwargs)
	return _wrapped_view
	

def admin_required( view ):
	"""
	Decorator that checks whether the user belongs to a team, redirecting
	to the error page if not.
	"""
	def _wrapped_view( request, *args, **kwargs ):
		if not is_admin(request.user):
			warn_msg( request, u"Vous devez être administrateur pour accéder à cette page." )
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
	
# coding: utf-8
from datetime import datetime, date

from django.shortcuts import get_object_or_404, redirect
from django.db import transaction
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.forms import SetPasswordForm
from django.views.generic.simple import direct_to_template
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.template import Context, loader

from team.models import Team, TeamMember
from team.forms import TeamForm, TeamMemberForm

from constants import *
from utils import *

@login_required
@transaction.commit_on_success
def item(request, member_id):
		member = get_object_or_404(TeamMember, id = member_id)
		if request.method == 'GET':  return _member_detail(request, member)
		if request.method == 'POST': return _member_update(request, member)

@transaction.commit_on_success
def new_user(request):
		form = UserCreationForm()
		
		if 'member_user' in request.session:
			return direct_to_template( request, 'member/form.html', {
				'form': TeamMemberForm( is_admin = is_admin(request.user) )
			})
		
		if request.method == 'POST':
			form = UserCreationForm( data = request.POST )
			if form.is_valid():
				user = form.save()
				user.is_active = False
				user.save()
				
				request.session['member_user'] = user
				request.session.save()
				return direct_to_template( request, 'member/form.html', {
					'form': TeamMemberForm( is_admin = is_admin(request.user) )
				})
		
		return direct_to_template( request, 'auth/register.html', { 'form': form })

@transaction.commit_on_success
def new_member(request):
	if not 'member_user' in request.session:
		return redirect('new_user')
	
	user = request.session.get('member_user')
	
	if TeamMember.objects.filter( user = user ).count() > 0:
		try:
			del request.session['member_user']
		except KeyError:
			pass
		return redirect('new_user')
	
	if request.method == 'POST':
		user = request.session.get('member_user')
		data = request.POST.copy()
		data.update({ 'username': user.username })
		
		form = TeamMemberForm( data = data )
		if form.is_valid():
			data = form.cleaned_data
			member = TeamMember.objects.create(
				team = data['team'],
				user = user
			)
			user.first_name = data['first_name']
			user.last_name = data['last_name']
			user.email = data['email']
			user.save()
			
			del request.session['member_user']
			
			# SEND MAIL TO VALIDATORS ...
			subject = "[Commandes LBCMCP] Demande d'ouverture de compte"
			emails = []
			for m in member.team.members.filter(member_type__in = [VALIDATOR,SECRETARY]):
				if m.user.email:
					emails.append(m.user.email)
			# ... and ADMINS
			for m in TeamMember.objects.filter( member_type = ADMIN ):
				if m.user.email:
					emails.append(m.user.email)
			
			if emails:
				template = loader.get_template('email_new_member.txt')
				message = template.render( Context({ 
					'member': member, 
					'url': request.build_absolute_uri(reverse('team_index'))
				}) )
				send_mail( subject, message, settings.DEFAULT_FROM_EMAIL, emails )
				info_msg( request, u"Votre demande de création de compte a bien été envoyée mais votre compte reste INACTIF en attendant sa validation.")
			else:
				warn_msg( request, u"Votre demande a bien été prise en compte mais votre compte reste INACTIF en attendant sa validation.")
			return redirect( 'home' )
	else:
		form = TeamMemberForm(is_admin = is_admin(request.user))
	
	return direct_to_template(request, 'member/form.html',{
			'form': form,
			'user_id': user.id
	})

@login_required
@transaction.commit_on_success
def toggle_active( request, user_id ):
	user = get_object_or_404( User, id = user_id )
	user.is_active = not user.is_active
	user.save()
	
	if user.is_active:
		subject = "[Commandes LBCMCP] Votre compte vient d'être activé"
		content = "Vous pouvez désormais vous connecter à l`application."
	else:
		subject = "[Commandes LBCMCP] Votre compte vient d'être inactivé"
		content = "Vous ne pouvez plus vous connecter à l`application pour le moment."
	
	emails = [user.email]
	template = loader.get_template('email_empty.txt')
	message = template.render( Context({ 'message': content }) )
	send_mail( subject, message, settings.DEFAULT_FROM_EMAIL, emails )
	return redirect('team_index')

@login_required
@transaction.commit_on_success
def set_password(request, user_id):
	user = get_object_or_404( User, id = user_id )
	
	if request.method == 'GET':
		form = SetPasswordForm( user = user )
		
		return direct_to_template(request, 'auth/set_password.html', {
			'form': form,
			'user_id': user_id
		})
	elif request.method == 'POST':
		form = SetPasswordForm( user = user, data = request.POST )
		
		if form.is_valid():
			form.save()
			info_msg( request, 'Nouveau mot de passe enregistré.')
		else:
			return direct_to_template(request, 'auth/set_password.html', {
				'form': form,
				'user_id': user_id
			})
	
	return redirect('team_index')

@login_required
@transaction.commit_on_success
def delete(request, user_id):
	from order.models import Order
	user = get_object_or_404( User, id = user_id )
	
	for order in Order.objects.filter( number__isnull = True, items__username = user.username ):
		for item in order.items.filter( username = user.username ):
			item.delete()
		if order.items.all().count() == 0:
			order.delete()
	
	user.delete()
	info_msg( request, u"Utilisateur supprimé avec succès." )
	
	return redirect( 'team_index' )


#--- Private views
def _member_detail(request, member):
		form = TeamMemberForm(instance = member,is_admin = is_admin(request.user))
		return direct_to_template(request, 'member/item.html',{
				'member': member,
				'form': form
		})

def _member_update(request, member):
	data = request.POST.copy()
	
	# Need to do that cause field are disabled in HTML, so values are not
	# sent over.
	if not is_admin( request.user ):
		data.update({
			'team': member.team.id,
			'username': member.user.username,
			'member_type': member.member_type
		})
	
	form = TeamMemberForm(instance = member, is_admin = is_admin(request.user), data = data)
	
	if form.is_valid():
		data = form.cleaned_data
		member.team = data['team']
		member.user.username = data['username']
		member.user.first_name = data['first_name']
		member.user.last_name = data['last_name']
		member.user.email = data['email']
		member.user.save()
		
		member.member_type = data['member_type']
		member.save()
		
		info_msg( request, u"Utilisateur modifié avec succès." )
		return redirect( 'team_index' )
	else:
		return direct_to_template(request, 'member/item.html',{
				'member': member,
				'form': form
		})

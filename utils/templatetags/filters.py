# encoding: utf8
from django import template

from utils import get_teams

register = template.Library()

@register.filter
def has_perm(user, perm):
	return user.has_perm(perm)

@register.filter
def has_perms(user, perms):
	return user.has_perms(perms.split(";"))

@register.filter
def total_price(cart, provider):
	return cart.total_price(provider)

@register.filter
def in_team_secretary(user):
	return user.has_perm('order.custom_goto_status_4')

@register.filter
def is_in_charge(product, user):
	return user in product.provider.users_in_charge.all()

@register.filter
def team(user):
	return user.teammember_set.get().team

@register.filter
def dialogClass(order):
	if order.status == 3:
		return "setOrderNb"
	
	if order.status == 4:
		return "setDeliveryDate"
	

@register.filter
def has_multiple_teams(user):
	return len(get_teams(user)) > 1

@register.filter
def asId(objects):
	return [o.id for o in objects]

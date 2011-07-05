# encoding: utf8
from django import template

from constants import NORMAL, VALIDATOR, SECRETARY, ADMIN
from utils import get_teams

register = template.Library()

@register.filter
def total_price(cart, provider):
	return cart.total_price(provider)

@register.filter
def is_normal(user):
	if not user or user.is_anonymous(): return False
	return user.teammember_set.filter(member_type__in = [NORMAL, VALIDATOR, ADMIN]).count() > 0

@register.filter
def is_validator(user):
	if not user or user.is_anonymous(): return False
	return user.teammember_set.filter(member_type__in = [VALIDATOR, ADMIN]).count() > 0

@register.filter
def is_secretary(user):
	if not user or user.is_anonymous(): return False
	return user.teammember_set.filter(member_type__in = [SECRETARY, ADMIN]).count() > 0

@register.filter
def is_secretary_valid(user):
	if not user or user.is_anonymous(): return False
	return user.teammember_set.filter(member_type__in = [SECRETARY_VALID, ADMIN]).count() > 0

@register.filter
def is_admin(user):
	if not user or user.is_anonymous(): return False
	return user.teammember_set.filter(member_type = ADMIN).count() > 0

@register.filter
def is_in_charge(product, user):
	return user in product.provider.users_in_charge.all()

@register.filter
def team(user):
	return user.teammember_set.get().team

@register.filter
def dialogClass(order):
	if order.status == 2 and order.budget.budget_type == 0: #ie. CNRS
		return "setOrderNb"
	
	if order.status == 3 and order.budget.budget_type != 0: #ie. pas CNRS
		return "setOrderNb"
	
	if order.status == 4:
		return "setDeliveryDate"
	

@register.filter
def has_multiple_teams(user):
	return len(get_teams(user)) > 1

@register.filter
def asId(objects):
	return [o.id for o in objects]
# encoding: utf8
from django import template
from django.contrib.contenttypes.models import ContentType

from utils import get_teams

register = template.Library()

@register.filter
def has_perm(user, perm):
    if not user:
        return True
    return user.has_perm(perm)

@register.filter
def has_perms(user, perms):
	return user.has_perms(perms.split(";"))

@register.filter
def is_admin(user):
	return user.has_perm("team.custom_is_admin")

@register.filter
def can_edit(user, order):
	if order.status <= 1:
		return True
	
	if order.status <= 2 and user.has_perm("order.custom_validate"):
		return True
	
	if user.has_perm("order.custom_goto_status_4"):
		return True

@register.filter
def total_price(cart, provider):
	return cart.total_price(provider)

@register.filter
def in_team_secretary(user):
	return user.has_perm('order.custom_goto_status_4') and not user.is_superuser

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

@register.filter
def get_content_type( my_object ):
	return ContentType.objects.get_for_model( my_object ).id

@register.filter
def isinstance( my_object, my_type ):
	app_label, model = my_type.split('.')
	my_ct_id = ContentType.objects.get( model = model.lower(), app_label = app_label ).id
	obj_ct_id = ContentType.objects.get_for_model( my_object ).id
	return my_ct_id == obj_ct_id

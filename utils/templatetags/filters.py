# encoding: utf8
from django import template

from constants import NORMAL, VALIDATOR, SECRETARY, ADMIN

register = template.Library()

@register.filter
def total_price(cart, provider):
  return cart.total_price(provider)

@register.filter
def is_normal(user):
  return user.teammember_set.filter(member_type__in = [NORMAL, VALIDATOR, ADMIN]).count() > 0

@register.filter
def is_validator(user):
  return user.teammember_set.filter(member_type__in = [VALIDATOR, ADMIN]).count() > 0

@register.filter
def is_secretary(user):
  return user.teammember_set.filter(member_type__in = [SECRETARY, ADMIN]).count() > 0

@register.filter
def is_admin(user):
  return user.teammember_set.filter(member_type = ADMIN).count() > 0

@register.filter
def is_in_charge(product, user):
  return user in product.provider.users_in_charge.all()
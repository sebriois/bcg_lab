# coding: utf8
from django import template

register = template.Library()

@register.filter
def total_price(cart, provider):
  return cart.total_price(provider)

@register.filter
def is_chief(team, user):
  return user.teammember_set.filter(is_chief = True, team = team).count() > 0

@register.filter
def is_secretary(user):
  return user.teammember_set.filter(team__is_secretary = True).count() > 0

@register.filter
def is_in_charge(product, user):
  return user in product.provider.users_in_charge.all()
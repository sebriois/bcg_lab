from django.template import Library

register = Library()

def is_in_charge(product, user):
  """
  Returns True or False whether user is in charge of this products's provider
  """
  return user in product.provider.users_in_charge.all()
register.filter('is_in_charge', is_in_charge)

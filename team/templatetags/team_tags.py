from django.template import Library

register = Library()

def is_chief(team, user):
  """
  Returns True or False whether user is in charge of this products's provider
  """
  return user.teammember_set.filter(is_chief = True, team = team).count() > 0
register.filter('is_chief', is_chief)

# coding: utf-8
from django.db import models
from django.contrib.auth.models import User, Group

class Team(models.Model):
  name = models.CharField("Nom", max_length=100)
  is_secretary = models.BooleanField("Equipe Secrétariat?", default = False)
  
  def __unicode__(self):
    return u"%s" % self.name
  
  def chief(self):
    return self.members().get(is_chief = True)
  
  def members(self):
    return self.teammember_set.all()

class TeamMember(models.Model):
  team      = models.ForeignKey(Team, verbose_name="Equipe", null = True, blank = True)
  user      = models.ForeignKey(User, verbose_name="Utilisateur")
  is_chief  = models.BooleanField(u"Chef d'équipe", default = False)
  
  def __unicode__(self):
    return unicode(self.user)
  
  def __repr__(self):
    return unicode(self.user)
  
  def get_full_name(self):
    if ( self.user.get_full_name() ):
      return self.user.get_full_name()
    return self.user.username
  
  def is_active(self):
    return self.user.is_active
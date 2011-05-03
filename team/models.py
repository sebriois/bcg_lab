# -*- encoding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User, Group

from constants import MEMBERTYPE_CHOICES
from constants import NORMAL, VALIDATOR, SECRETARY, ADMIN

class Team(models.Model):
  name = models.CharField("Nom", max_length=100)
  
  def __unicode__(self):
    return u"%s" % self.name
  
  def get_members(self):
    return self.teammember_set
  members = property(get_members)

class TeamMember(models.Model):
  team = models.ForeignKey(Team, verbose_name="Equipe", null = True, blank = True)
  user = models.ForeignKey(User, verbose_name="Utilisateur")
  member_type = models.IntegerField(u"Type d'utilisateur", choices = MEMBERTYPE_CHOICES, default = 0)
  
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
  
  def is_normal(self):
    return self.member_type in NORMAL
  
  def is_validator(self):
    return self.member_type == VALIDATOR
  
  def is_secretary(self):
    return self.member_type == SECRETARY
  
  def is_admin( self ):
    return self.member_type == ADMIN
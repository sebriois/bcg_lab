# -*- encoding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User, Group

from constants import MEMBERTYPE_CHOICES
from constants import NORMAL, VALIDATOR, SECRETARY, ADMIN

class Team(models.Model):
	name = models.CharField(u"Nom", max_length=100)
	fullname = models.CharField(u"Nom complet", max_length=100)
	is_active = models.BooleanField(u"Actif?", default = True)
	
	class Meta:
		verbose_name = u'Equipe'
		verbose_name_plural = u'Equipes'
		ordering = ('name',)
	
	def __unicode__(self):
		return u"%s" % self.fullname and self.fullname or self.name
	
	def get_members(self):
		return self.teammember_set
	members = property(get_members)

class TeamMember(models.Model):
	team = models.ForeignKey(Team, verbose_name="Equipe", null = True, blank = True)
	user = models.ForeignKey(User, verbose_name="Utilisateur")
	member_type = models.IntegerField(u"Type d'utilisateur", choices = MEMBERTYPE_CHOICES, default = 0)
	
	class Meta:
		verbose_name = u'Membre équipe'
		verbose_name_plural = u'Membres équipe'
		ordering = ('team', '-member_type', 'user__username')
	
	def __unicode__(self):
		return unicode(self.user)
	
	def __repr__(self):
		return unicode(self.user)
	
	def get_full_name(self):
		if ( self.user.get_full_name() ):
			return self.user.get_full_name()
		return self.user.username
	

# coding: utf8
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.dispatch import dispatcher
from django.db.models.signals import post_syncdb

import provider.models
import product.models
import order.models
import team.models
import budget.models

def make_permissions( appname, permissions ):
	ct, created = ContentType.objects.get_or_create(
		model = '',
		app_label = appname,
		defaults = {'name': appname}
	)
	
	if created: print u"Adding custom content type '%s'" % ct
	
	# create permissions
	for codename, name in permissions:
		p, created = Permission.objects.get_or_create(
			codename = codename,
			content_type__pk = ct.id,
			defaults = { 'name': name, 'content_type': ct }
		)
		if created:
			print u"Adding custom permission '%s'" % p

#
# Important: always use a codename starting with "custom_" so you
# can use Permission.objects.filter( codename__startswith = "custom_" )
#

def create_custom_order_permission(sender, **kwargs):
	make_permissions( u"order", (
		('custom_validate', u"Valider une commande"),
		('custom_edit_order', u"Editer une commande"),
		('custom_edit_number', u"Modifier le n°commande"),
		('custom_edit_order_budget', u"Modifier l'imputation"),
		('custom_goto_status_3', u"Transmettre pour saisie SIFAC/XLAB"),
		('custom_goto_status_4', u"Effectuer une saisie SIFAC/XLAB"),
		('custom_order_any_team', u"Commander pour toutes les équipes")
	))


def create_custom_budget_permissions(sender, **kwargs):
	make_permissions( u"budget", (
		('custom_view_budget', u"Voir un budget"),
		('custom_add_budget', u"Ajouter un budget"),
		('custom_edit_budget', u"Editer un budget"),
		('custom_history_budget', u"Voir l'historique des budgets")
	))


def create_custom_team_permissions(sender, **kwargs):
	make_permissions( u"team", (
		('custom_view_teams', u"Voir toutes les équipes"),
		('custom_edit_member', u"Editer un membre d'équipe"),
		('custom_activate_account', u"Activer un nouveau compte"),
		('custom_add_group', u"Créer un groupe utilisateur"),
		('custom_add_team', u"Créer une équipe")
	))

post_syncdb.connect(create_custom_order_permission, sender=order.models)
post_syncdb.connect(create_custom_budget_permissions, sender=budget.models)
post_syncdb.connect(create_custom_team_permissions, sender=team.models)

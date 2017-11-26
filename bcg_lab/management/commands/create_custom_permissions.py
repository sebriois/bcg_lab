# coding: utf8
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    can_import_settings = True
    help = 'Create custom permissions for BCG Lab users privileges'

    def handle(self, *args, **options):
        verbose = options.get('verbosity', 0)

        self.make_permissions(u"order", "order", (
            ('custom_validate', u"Valider une commande"),
            ('custom_edit_order', u"Editer une commande"),
            ('custom_edit_number', u"Modifier le n°commande"),
            ('custom_edit_order_budget', u"Modifier l'imputation"),
            ('custom_goto_status_3', u"Transmettre pour saisie SIFAC/SILAB"),
            ('custom_goto_status_4', u"Effectuer une saisie SIFAC/SILAB"),
            ('custom_order_any_team', u"Commander pour toutes les équipes"),
            ('custom_view_local_provider', u"Gestionnaire magasin")
        ))
        self.make_permissions(u"budget", "budget", (
            ('custom_view_budget', u"Voir un budget"),
            ('custom_add_budget', u"Ajouter un budget"),
            ('custom_edit_budget', u"Editer un budget"),
            ('custom_can_transfer', u"Effectuer un virement"),
            ('custom_history_budget', u"Voir l'historique des budgets")
        ))
        self.make_permissions(u"team", "team", (
            ('custom_is_admin', u"Administrateur"),
            ('custom_view_teams', u"Voir toutes les équipes"),
            ('custom_edit_member', u"Editer un membre d'équipe"),
            ('custom_activate_account', u"Activer un nouveau compte"),
            ('custom_add_group', u"Créer un groupe utilisateur"),
            ('custom_add_team', u"Créer une équipe")
        ))

    @transaction.atomic
    def make_permissions(self, app_label, model, permissions):
        ct = ContentType.objects.get(model = model, app_label = app_label)

        # create permissions
        for codename, name in permissions:
            p, created = Permission.objects.get_or_create(
                codename = codename,
                content_type__pk = ct.id,
                defaults = {
                    'name': name,
                    'content_type': ct
                }
            )
            if created:
                print(u"Adding custom permission '%s'" % p.codename)

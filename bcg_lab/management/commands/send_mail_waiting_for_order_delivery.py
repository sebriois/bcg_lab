# -*- coding: utf8 -*-
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.conf import settings
from django.template import loader, Context
from django.utils import timezone

from datetime import timedelta

from order.models import Order


class Command(BaseCommand):
    can_import_settings = True
    help = "Send weekly alerts for order that haven't been received yet"

    def handle(self, *args, **options):
        now = timezone.now()

        email_from = settings.DEFAULT_FROM_EMAIL
        email_subject = u"[BCG-Lab %s] Commande %s - en attente de réception depuis %s jours"
        email_content = loader.get_template('email_not_delivered.txt')

        orders = Order.objects.filter(
            date_delivered__isnull = True,
            status = 4,  # sent to provider
            last_change__lte = now - timedelta(days = 14)
        )

        for order in orders:

            days_delta = now.day - order.last_change.day

            # warn every 7 days
            if days_delta % 7 != 0:
                continue

            recipient_list = set()
            for username in order.items.values_list('username',flat = True).distinct():
                try:
                    user = User.objects.get(username = username)
                    if user.email:
                        recipient_list.add(user.email)
                except User.DoesNotExist:
                    continue

            print("--- commande #%s (last modification: %s) ---" % (order.number, order.last_change))
            print(order.get_absolute_url())
            print("To: %s" % ", ".join(list(recipient_list)))

            subject = email_subject % (settings.SITE_NAME, order.provider.name, days_delta)
            message = email_content.render({
                'order': order,
                'days': days_delta
            })
            send_mail(subject, message, email_from, list(recipient_list))

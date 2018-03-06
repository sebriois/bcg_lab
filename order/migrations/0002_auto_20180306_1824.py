# Generated by Django 2.0 on 2018-03-06 17:24

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='delivered',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0, message='Veuillez saisir une quantité > 0')], verbose_name='Quantité à livrer'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='price',
            field=models.DecimalField(decimal_places=2, error_messages={'invalid': 'Nombre invalide (utiliser le point comme séparateur)'}, max_digits=12, validators=[django.core.validators.MinValueValidator(0, message='Veuillez saisir un nombre décimal positif')], verbose_name='Montant'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='quantity',
            field=models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(0, message='Veuillez saisir une quantité > 1')], verbose_name='Quantité'),
        ),
    ]

# Generated by Django 2.0 on 2017-12-14 18:10

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Info',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(verbose_name='Information')),
                ('expiry', models.DateTimeField(blank=True, help_text='NE PAS REMPLIR POUR UNE INFO PERMANENTE', null=True, verbose_name="Date d'expiration")),
                ('date_created', models.DateField(auto_now_add=True, verbose_name='Date')),
            ],
            options={
                'db_table': 'info',
                'ordering': ('expiry',),
            },
        ),
    ]

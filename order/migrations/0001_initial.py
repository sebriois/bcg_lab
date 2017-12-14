# Generated by Django 2.0 on 2017-12-14 18:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('budget', '0001_initial'),
        ('team', '0001_initial'),
        ('provider', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(blank=True, max_length=20, null=True, verbose_name='N° cmde')),
                ('status', models.IntegerField(choices=[(0, 'Non passée'), (1, 'En attente de validation'), (2, 'Transmise à la gestion'), (3, "En attente d'envoi"), (4, 'Envoyée au fournisseur'), (5, 'Commande réceptionnée')], default=0, verbose_name='Etat de la commande')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='Commentaires')),
                ('is_confidential', models.BooleanField(default=False, verbose_name='Confidentielle?')),
                ('is_urgent', models.BooleanField(default=False, verbose_name='Urgente?')),
                ('has_problem', models.BooleanField(default=False, verbose_name='Problème?')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='Date de création')),
                ('date_delivered', models.DateTimeField(blank=True, null=True, verbose_name='Date de livraison')),
                ('last_change', models.DateTimeField(auto_now=True, verbose_name='Dernière modification')),
                ('budget', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='budget.Budget', verbose_name='Ligne budgétaire')),
            ],
            options={
                'verbose_name': 'Commande',
                'verbose_name_plural': 'Commandes',
                'db_table': 'order',
                'ordering': ('status', '-date_created', 'provider'),
            },
        ),
        migrations.CreateModel(
            name='OrderComplement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Nom du complément')),
                ('type_comp', models.IntegerField(choices=[(0, 'Crédit'), (1, 'Débit')], verbose_name='Type de complément')),
            ],
            options={
                'db_table': 'order_complement',
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_type', models.IntegerField(choices=[(0, 'Produit'), (1, 'Frais'), (2, 'Remises'), (3, 'Autre')], default=0, verbose_name="Type d'item")),
                ('username', models.CharField(max_length=100, verbose_name='Commandé par')),
                ('username_recept', models.CharField(blank=True, max_length=100, null=True, verbose_name='Réceptionné par')),
                ('product_id', models.IntegerField(blank=True, null=True, verbose_name='ID produit')),
                ('name', models.CharField(max_length=500, verbose_name='Désignation')),
                ('provider', models.CharField(blank=True, max_length=100, null=True, verbose_name='Fournisseur')),
                ('origin', models.CharField(blank=True, max_length=100, null=True, verbose_name="Fournisseur d'origine")),
                ('packaging', models.CharField(blank=True, max_length=100, null=True, verbose_name='Conditionnement')),
                ('reference', models.CharField(blank=True, max_length=100, null=True, verbose_name='Référence')),
                ('offer_nb', models.CharField(blank=True, max_length=100, null=True, verbose_name='N° Offre')),
                ('category', models.CharField(blank=True, max_length=100, null=True, verbose_name='Type')),
                ('sub_category', models.CharField(blank=True, max_length=100, null=True, verbose_name='Sous-type')),
                ('nomenclature', models.CharField(blank=True, max_length=100, null=True, verbose_name='Nomenclature')),
                ('price', models.DecimalField(decimal_places=2, max_digits=12, verbose_name='Montant')),
                ('cost_type', models.IntegerField(choices=[(0, 'Crédit'), (1, 'Débit')], verbose_name='Type de coût')),
                ('quantity', models.IntegerField(default=1, verbose_name='Quantité')),
                ('delivered', models.IntegerField(default=0, verbose_name='Quantité à livrer')),
                ('is_confidential', models.BooleanField(default=False, verbose_name='Confidentielle?')),
            ],
            options={
                'verbose_name': 'Item de commande',
                'verbose_name_plural': 'Items de commande',
                'db_table': 'order_item',
                'ordering': ('id',),
            },
        ),
        migrations.AddField(
            model_name='order',
            name='items',
            field=models.ManyToManyField(to='order.OrderItem', verbose_name='Produits'),
        ),
        migrations.AddField(
            model_name='order',
            name='provider',
            field=models.ForeignKey(max_length=100, on_delete=django.db.models.deletion.CASCADE, to='provider.Provider', verbose_name='Fournisseur'),
        ),
        migrations.AddField(
            model_name='order',
            name='team',
            field=models.ForeignKey(max_length=20, on_delete=django.db.models.deletion.CASCADE, to='team.Team', verbose_name='Equipe'),
        ),
    ]

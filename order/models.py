# -*- encoding: utf8 -*-
from datetime import datetime

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from bcg_lab.constants import STATE_CHOICES, DEBIT, COST_TYPE_CHOICES, CREDIT
from product.models import Product
from provider.models import Provider
from budget.models import Budget, BudgetLine
from team.models import Team
from attachments.models import Attachment


class Order(models.Model):
    number = models.CharField(u"N° cmde", max_length = 20, null = True, blank = True)
    budget = models.ForeignKey(Budget, verbose_name="Ligne budgétaire", blank = True, null = True)
    team = models.ForeignKey(Team, verbose_name = u"Equipe", max_length = 20 )
    provider = models.ForeignKey(Provider, verbose_name = u"Fournisseur", max_length = 100 )
    status = models.IntegerField(u"Etat de la commande", choices = STATE_CHOICES, default = 0)
    items = models.ManyToManyField( "OrderItem", verbose_name = "Produits" )
    notes = models.TextField( u"Commentaires", null = True, blank = True )
    is_confidential = models.BooleanField( u"Confidentielle?", default = False )
    is_urgent = models.BooleanField( u"Urgente?", default = False )
    has_problem = models.BooleanField( u"Problème?", default = False )
    date_created = models.DateTimeField(u"Date de création", auto_now_add = True)
    date_delivered = models.DateTimeField(u"Date de livraison", null = True, blank = True)
    last_change = models.DateTimeField(u"Dernière modification", auto_now = True)
    attachments = GenericRelation( Attachment )
    
    class Meta:
        db_table = 'order'
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"
        ordering = ('status', '-date_created', 'provider')
    
    def __str__(self):
        d = datetime.strftime( self.date_created, "%d/%m/%Y %Hh%M" )
        return u"%s (%s) - %s" % ( self.provider, self.team, d )
    
    @models.permalink
    def get_absolute_url(self):
        return ('order_item', [self.id])
    
    def get_full_name(self):
        return u"%s" % self.team
    
    def copy(self):
        return Order.objects.create(
            number = self.number,
            budget = self.budget,
            team = self.team,
            provider = self.provider,
            status = self.status,
            notes = self.notes,
            is_confidential = self.is_confidential,
            is_urgent = self.is_urgent,
            has_problem = self.has_problem
        )
    
    def add(self, product, quantity):
        if self.date_delivered:
             # TODO: raise an exception instead
            return
        
        item, created = self.items.get_or_create( 
            product_id = product.id,
            defaults = {
                'cost_type':    DEBIT,
                'name':         product.origin and "%s - %s" % (product.origin,product.name) or product.name,
                'provider':     product.provider.name,
                'origin':       product.origin,
                'packaging':    product.packaging,
                'reference':    product.reference,
                'price':        product.price,
                'offer_nb':     product.offer_nb,
                'nomenclature': product.nomenclature,
                'quantity':     quantity,
                'delivered':    quantity
            }
        )
        
        if product.category:
            item.category = product.category.name
        if product.sub_category:
            item.sub_category = product.sub_category.name
        item.save()
        
        if not created:
            item.quantity += int(quantity)
            item.save()
        return item
    
    def price(self):
        return sum( [item.total_price() for item in self.items.all()] )
    
    def create_budget_line(self):
        if self.status >= 1:
            for item in self.items.all():
                item.create_budget_line()
    
    def update_budget_lines(self):
        for bl in BudgetLine.objects.filter( order_id = self.id ):
            bl.number = self.number
            bl.save()
            
        for item in self.items.all():
            item.update_budget_line()
    
    def save_to_history(self, date_delivered = timezone.now()):
        from history.models import History
        
        # Create history object that is a copy of this order
        history = History.objects.create(
            team = self.team.name,
            provider = self.provider.name,
            budget = self.budget and self.budget.name or "",
            number = self.number,
            price = self.price(),
            comments = self.notes,
            date_delivered = date_delivered
        )
        
        # Move attachments to history
        for attachment in self.attachments.all():
            attachment.content_object = history
            attachment.save()
        
        # Move order's items to the new history object
        for item in self.items.all():
            history.items.add( item )
        self.items.clear()
    

class OrderItem(models.Model):
    username        = models.CharField( u"Commandé par", max_length = 100 )
    username_recept = models.CharField( u"Réceptionné par", max_length = 100, null = True, blank = True )
    product_id      = models.IntegerField( u'ID produit', blank = True, null = True )
    name            = models.CharField( u'Désignation', max_length = 500 )
    provider        = models.CharField( u'Fournisseur', max_length = 100, blank = True, null = True )
    origin          = models.CharField( u"Fournisseur d'origine", max_length = 100, blank = True, null = True )
    packaging       = models.CharField( u'Conditionnement', max_length = 100, blank = True, null = True)
    reference       = models.CharField( u'Référence', max_length = 100, blank = True, null = True )
    offer_nb        = models.CharField( u'N° Offre', max_length = 100, blank = True, null = True )
    category        = models.CharField( u'Type', max_length = 100, blank = True, null = True )
    sub_category    = models.CharField( u'Sous-type', max_length = 100, blank = True, null = True )
    nomenclature    = models.CharField( u'Nomenclature', max_length = 100, blank = True, null = True )
    price           = models.DecimalField( u'Montant', max_digits = 12, decimal_places = 2 )
    cost_type       = models.IntegerField( u'Type de coût', choices = COST_TYPE_CHOICES )
    quantity        = models.IntegerField( u'Quantité', default = 1 )
    delivered       = models.IntegerField( u'Quantité à livrer', default = 0 )
    is_confidential = models.BooleanField( u"Confidentielle?", default = False )
    
    class Meta:
        db_table = 'order_item'
        verbose_name = "Item de commande"
        verbose_name_plural = "Items de commande"
        ordering = ('id',)
    
    def get_order(self):
        return self.order_set.get()
    
    def get_history(self):
        return self.history_set.get()
    
    def get_fullname(self):
        users = User.objects.filter( username = self.username )
        if users.count() > 0 and users[0].get_full_name():
            return u"%s" % users[0].get_full_name()
        else:
            return u"%s" % self.username
    
    def get_fullname_recept(self):
        users = User.objects.filter( username = self.username_recept )
        if users.count() > 0 and users[0].get_full_name():
            return u"%s" % users[0].get_full_name()
        elif self.username_recept:
            return u"%s" % self.username_recept
        else:
            return None
    
    def total_price(self):
        if self.cost_type == DEBIT:
            return self.price * self.quantity
        
        if self.cost_type == CREDIT:
            return self.price * self.quantity * -1
    
    def create_budget_line(self):
        if self.order_set.all().count() == 0:
            # TODO: raise error instead
            return
        order = self.order_set.get()
        bl = BudgetLine.objects.create(
            team            = order.budget.team.name,
            order_id        = order.id,
            orderitem_id    = self.id,
            budget_id       = order.budget.id,
            budget          = order.budget.name,
            number          = order.number,
            nature          = order.budget.default_nature,
            budget_type     = order.budget.budget_type,
            origin          = order.budget.default_origin,
            provider        = order.provider.name,
            offer           = self.offer_nb,
            product         = self.name,
            product_price   = self.total_price(),
            reference       = self.reference,
            quantity        = self.quantity
        )
        if self.cost_type == DEBIT:
            bl.credit = 0
            bl.debit = self.price
        elif self.cost_type == CREDIT:
            bl.credit = self.price
            bl.debit = 0
        bl.save()
    
    def update_budget_line(self):
        try:
            bl = BudgetLine.objects.get( orderitem_id = self.id )
        except:
            return
        
        if self.cost_type == DEBIT:
            bl.credit = 0
            bl.debit = self.price
        elif self.cost_type == CREDIT:
            bl.credit = self.price
            bl.debit = 0
        else:
            raise Exception("COST TYPE SHOULD NOT BE NULL")
        
        bl.provider = bl.provider and bl.provider or self.provider
        bl.offer = self.offer_nb
        bl.product = self.name
        bl.product_price = self.total_price()
        bl.reference = self.reference
        bl.quantity = self.quantity
        bl.save()
    
    def update_product(self):
        if self.product_id:
            product = Product.objects.get( id = self.product_id )
            
            orig_price = product.price
            if orig_price != self.price and product.has_expired():
                product.expiry = datetime( timezone.now().year, 12, 31 )
            
            product.name = self.name
            product.packaging = self.packaging
            product.reference = self.reference
            product.offer_nb = self.offer_nb
            product.nomenclature = self.nomenclature
            product.price = self.price
            product.save()
        

class OrderComplement(models.Model):
    name = models.CharField( u"Nom du complément", max_length = 50 )
    type_comp = models.IntegerField( u"Type de complément", choices = ((CREDIT, u"Crédit"), (DEBIT, u"Débit")) )

    class Meta:
        db_table = "order_complement"

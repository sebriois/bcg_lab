from django.contrib import admin
from order_manager.order.models import Order

class OrderAdmin(admin.ModelAdmin):
    list_display = ( 'date_created', 'user', 'joined_products', 'state', 'last_change' )
    
    def joined_products(self, obj):
      return ", ".join( [p.name for p in obj.products.all()] )
    joined_products.short_description = 'Products'
admin.site.register(Order, OrderAdmin)

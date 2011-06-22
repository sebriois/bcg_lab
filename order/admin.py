from django.contrib import admin
from order.models import Order, OrderItem

class OrderAdmin(admin.ModelAdmin):
    list_display = (
      'id', 'team', 'date_created', 'provider', 'status', 'last_change'
    )
admin.site.register(Order, OrderAdmin)

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ( 
      'id', 'product_id', 'provider', 'username', 'name', 'quantity',
      'price', 'packaging', 'reference', 'offer_nb', 'nomenclature'
    )
admin.site.register(OrderItem, OrderItemAdmin)

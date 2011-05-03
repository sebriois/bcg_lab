from django.contrib import admin
from order.models import Order, OrderItem

class OrderAdmin(admin.ModelAdmin):
    list_display = ( 'id', 'team', 'username', 'date_created', 'provider', 'status', 'last_change' )
admin.site.register(Order, OrderAdmin)

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ( 'id', 'product', 'quantity' )
admin.site.register(OrderItem, OrderItemAdmin)

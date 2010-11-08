from django.contrib import admin
from order_manager.provider.models import Provider

class ProviderAdmin(admin.ModelAdmin):
  list_display = ('name', 'joined_users')
  
  def joined_users(self, obj):
    return ", ".join( [u for u in obj.users_in_charge.all()] )
  joined_users.short_description = 'Responsables'
admin.site.register(Provider, ProviderAdmin)
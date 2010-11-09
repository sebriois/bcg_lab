from django.contrib import admin
from provider.models import Provider

class ProviderAdmin(admin.ModelAdmin):
  list_display = ('name', 'joined_users')
  
  def joined_users(self, obj):
    return ", ".join( [unicode(u) for u in obj.users_in_charge.all()] )
  joined_users.short_description = 'Responsables'
admin.site.register(Provider, ProviderAdmin)
from django.contrib import admin
from provider.models import Provider

class ProviderAdmin(admin.ModelAdmin):
  list_display = ('name', 'user_in_charge')
admin.site.register(Provider, ProviderAdmin)
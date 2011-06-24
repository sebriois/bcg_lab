from django.contrib import admin
from history.models import History

class HistoryAdmin(admin.ModelAdmin):
    list_display = (
      'date_created', 'team', 'provider', 'number', 'price', 'budget'
    )
admin.site.register(History, HistoryAdmin)
